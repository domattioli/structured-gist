#!/usr/bin/env python3
"""
Run stages: manifest, scope, generation (with the length rule) and judging.

Every model call goes through ``CallCache.run_attempts`` so a rerun repeats no
finished call. Pacing (``bench.pacing``) is checked only on a cache miss.
Backends are injected through the ``RUNNER`` hooks in ``bench.generate`` and
``bench.judge``; nothing here spawns a process itself.
"""
from __future__ import annotations

import datetime as _dt
import statistics
from pathlib import Path

from bench import baselines, estimate as est, generate, items as items_mod, judge, pacing
from bench import prereg as prereg_mod
from bench import records, words
from bench.cache import CallCache

METHODS = ("skill", "plain_prose", "plain_bullets", "lead_n", "textrank")
GEN_ARMS = ("plain_prose", "plain_bullets")


class QuotaStop(RuntimeError):
    def __init__(self, backend: str, detail: str):
        super().__init__(f"quota exhausted on {backend}: {detail}; records kept, rerun later to resume from cache")


class PolicyStop(RuntimeError):
    pass


def run_dir(root: Path, run_id: str) -> Path:
    return Path(root) / "runs" / run_id


def is_dry(run_id: str) -> bool:
    return run_id.startswith("dryrun-")


# ---------------------------------------------------------------------------
# scope
# ---------------------------------------------------------------------------

def scope_items(prereg_obj: dict, run_id: str, all_items: list[dict], dataset=None, cases=None) -> list[dict]:
    if is_dry(run_id):
        want = {f"{ds}/{cid}" for ds, cid in prereg_obj["dry_run"]["cases"].items()}
        return [i for i in all_items if i["item_id"] in want]
    out = all_items
    if dataset:
        out = [i for i in out if i["dataset"] == dataset]
    if cases:
        cs = set(cases)
        out = [i for i in out if i["case_id"] in cs or i["item_id"] in cs]
    return out


def items_of_ids(all_items: list[dict], ids: list[str]) -> list[dict]:
    s = set(ids)
    return [i for i in all_items if i["item_id"] in s]


# ---------------------------------------------------------------------------
# manifest
# ---------------------------------------------------------------------------

def write_manifest(root: Path, run_id: str, prereg_obj: dict, estimate_sha: str | None, est_body: dict | None,
                   canary_passed: bool = False) -> None:
    p = run_dir(root, run_id) / "manifest.json"
    if p.is_file():
        return
    gen, main = prereg_obj["generator"], prereg_obj["judges"]["main"]
    man = {
        "run_id": run_id,
        "prereg_sha256": prereg_mod.prereg_sha256(root),
        "prereg_commit": prereg_mod.prereg_commit(root) or "0" * 40,
        "created_at": generate.now_iso(),
        "state": "created",
        "models": {"generator": {"requested": gen["model"], "effort": gen["effort"], "backend": generate.BACKEND},
                   "judge": {"requested": main["model"], "effort": main["effort"], "backend": judge.BACKEND}},
        "seeds": {"master_seed": prereg_obj["master_seed"]},
        "cost": {"estimate_sha": estimate_sha, "estimate_tokens": (est_body or {}).get("per_backend", {}),
                 "confirmed_at": generate.now_iso()},
        "isolation": {"generator_backend": "claude-isolated-config", "canary_passed": canary_passed,
                      "judge_cwd_outside_git": True, "codex_global_agents_md_sha256": None},
        "counts": {},
    }
    records.validate_or_raise(man, "RunManifest")
    records.write_json(p, man)


def update_manifest(root: Path, run_id: str, **fields) -> None:
    p = run_dir(root, run_id) / "manifest.json"
    if not p.is_file():
        return
    man = records.read_json(p)
    for k, v in fields.items():
        if isinstance(v, dict) and isinstance(man.get(k), dict):
            man[k].update(v)
        else:
            man[k] = v
    records.validate_or_raise(man, "RunManifest")
    records.write_json(p, man)


# ---------------------------------------------------------------------------
# generation
# ---------------------------------------------------------------------------

def _window(cfg: dict, k: int) -> tuple[int, int]:
    a = 1 + cfg["failure_retries"]
    return k * a + 1, (k + 1) * a


def _sample(item: dict, method: str, text: str, status: str, **kw) -> dict:
    s = {
        "sample_id": f"{item['item_id']}/{method}", "item_id": item["item_id"], "method": method,
        "status": status, "output_text": text, "words": words.count_words(text) if text else 0,
        "n_target": kw.get("n_target"), "band": kw.get("band"), "length_flags": kw.get("flags", []),
        "call_keys": kw.get("call_keys", []), "attempts": kw.get("attempts", 0),
    }
    if text:
        s["output_sha256"] = generate.sha256_text(text)
    if kw.get("n_source"):
        s["n_source"] = kw["n_source"]
    if kw.get("trim"):
        s["trim"] = kw["trim"]
    records.validate_or_raise(s, "Sample")
    return s


class Generator:
    def __init__(self, root: Path, prereg_obj: dict, run_id: str, pacer: pacing.Pacer, runner=None):
        self.root, self.pre, self.run_id = Path(root), prereg_obj, run_id
        self.cache = CallCache(run_dir(root, run_id) / "calls")
        self.pacer, self.runner = pacer, runner
        self.gen = prereg_obj["generator"]
        self.n_attempts = 0

    def logical_call(self, arm: str, item: dict, n: int | None, k: int) -> dict | None:
        system_text = generate.system_prompt(arm, self.root)
        user_text = generate.user_message(arm, item, self.root, n)
        spec = {"backend": generate.BACKEND, "model": self.gen["model"], "effort": self.gen["effort"],
                "system_prompt_sha256": generate.sha256_text(system_text),
                "prompt_sha256": generate.sha256_text(user_text)}
        first, last = _window(self.gen, k)
        sid = f"{item['item_id']}/{arm}"

        def call_fn(spec_a: dict, key: str) -> dict:
            self.pacer.check("anthropic")
            rec = generate.call_record(spec_a, key, system_text, user_text, runner=self.runner, sample_id=sid)
            self.pacer.add("anthropic", pacing.record_tokens(rec))
            return rec

        rec = self.cache.run_attempts(spec, call_fn, last, generate.STOP_OUTCOMES, first_attempt=first)
        if rec is not None:
            self.n_attempts += 1
            if rec["outcome"] == "model_policy_violation":
                raise PolicyStop(rec.get("error_text") or "model policy violation")
            if rec["outcome"] == "quota_exhausted":
                raise QuotaStop("anthropic", rec.get("error_text") or "")
        return rec

    def skill(self, item: dict) -> dict:
        rec = self.logical_call("skill", item, None, 0)
        if rec is None or rec["outcome"] != "ok":
            return _sample(item, "skill", "", "failed", attempts=self._att(rec))
        return _sample(item, "skill", rec["stdout"], "generated", call_keys=[rec["key"]], attempts=self._att(rec))

    @staticmethod
    def _att(rec):
        return rec["attempt"] if rec else 0

    def plain(self, item: dict, arm: str, n: int, n_source: str) -> dict:
        lo, hi = generate.band(n)
        flags: list[str] = []
        if item["source_words"] < lo:
            flags.append("source_shorter_than_band")
        maxr = self.gen["max_regenerations"]
        best, keys, att = None, [], 0
        for k in range(maxr + 1):
            rec = self.logical_call(arm, item, n, k)
            att = self._att(rec) or att
            if rec is None or rec["outcome"] != "ok":
                break  # a failed window ends regeneration; keep the best text so far
            best = rec["stdout"]
            keys.append(rec["key"])
            w = words.count_words(best)
            if lo <= w <= hi:
                break
            if k < maxr:
                if "regenerated" not in flags:
                    flags.append("regenerated")
        if best is None:
            return _sample(item, arm, "", "failed", n_target=n, band=[lo, hi], flags=flags, attempts=att,
                           n_source=n_source)
        w = words.count_words(best)
        trim = None
        if w > hi:
            cut = baselines.trim_to_words(best, hi)
            trim = {"words_before": w, "words_after": words.count_words(cut)}
            best = cut
            flags.append("trimmed")
        elif w < lo:
            flags.append("length_violation")
        return _sample(item, arm, best, "generated", n_target=n, band=[lo, hi], flags=flags, call_keys=keys,
                       attempts=att, trim=trim, n_source=n_source)

    def baseline(self, item: dict, method: str, n: int, n_source: str, stop) -> dict:
        lo, hi = generate.band(n)
        src = generate.items_mod.source_text(item)
        flags = ["source_shorter_than_band"] if item["source_words"] < lo else []
        if method == "lead_n":
            text = baselines.lead_n(src, n)
        else:
            tr = self.pre["textrank"]
            text = baselines.textrank(src, n, lo, hi, stop, damping=tr["damping"], tol=tr["tol"],
                                      max_iter=tr["max_iter"])
        return _sample(item, method, text, "generated", n_target=n, band=[lo, hi], flags=flags,
                       n_source=n_source)

    def run(self, case_items: list[dict]) -> list[dict]:
        case_items = sorted(case_items, key=lambda i: i["item_id"])
        skills = {i["item_id"]: self.skill(i) for i in case_items}
        by_ds: dict = {}
        for i in case_items:
            if skills[i["item_id"]]["status"] == "generated":
                by_ds.setdefault(i["dataset"], []).append(skills[i["item_id"]]["words"] / i["source_words"])
        med_ds = {}
        for ds in {i["dataset"] for i in case_items}:
            r = by_ds.get(ds) or [est.projected_n(i) / i["source_words"] for i in case_items if i["dataset"] == ds]
            med_ds[ds] = statistics.median(r) if r else 1.0
        stop = baselines.load_stopwords(self.root / "bench" / "stopwords.txt")
        out = []
        for it in case_items:
            sk = skills[it["item_id"]]
            out.append(sk)
            if sk["status"] == "generated":
                n, nsrc = sk["words"], "skill_sample"
            else:
                n, nsrc = max(1, round(it["source_words"] * med_ds[it["dataset"]])), "fallback_median_ratio"
            for arm in GEN_ARMS:
                out.append(self.plain(it, arm, n, nsrc))
            for m in ("lead_n", "textrank"):
                out.append(self.baseline(it, m, n, nsrc, stop))
        return out


def write_samples(root: Path, run_id: str, samples: list[dict]) -> Path:
    p = run_dir(root, run_id) / "samples.jsonl"
    records.write_jsonl(p, samples)
    return p


# ---------------------------------------------------------------------------
# judging
# ---------------------------------------------------------------------------

LABELS_FILE = "graders/judge_labels.sol.jsonl"


def judge_samples(root: Path, prereg_obj: dict, run_id: str, samples: list[dict], items_by_id: dict,
                  pacer: pacing.Pacer, runner=None) -> list[dict]:
    """Runs sol over every generated sample; returns judge_labels rows. On a
    stop (quota/policy/pacing) the rows so far are written, then the stop
    exception propagates."""
    main = prereg_obj["judges"]["main"]
    cache = CallCache(run_dir(root, run_id) / "calls")
    notice_sha = generate.sha256_text(judge.read_notice(root))
    rows: list[dict] = []
    path = run_dir(root, run_id) / LABELS_FILE

    def row(s, status, labels=None, rec=None):
        r = {"grader": "judge_labels.sol", "grader_type": "label_model", "sample_id": s["sample_id"],
             "status": status, "score": None, "labels": labels, "call_key": rec["key"] if rec else None}
        if status == "incomplete" and rec:
            r["detail"] = {"outcome": rec["outcome"]}
        records.validate_or_raise(r, "GraderResult")
        return r

    try:
        for s in samples:
            if s["status"] != "generated":
                continue
            item = items_by_id[s["item_id"]]
            prompt = judge.build_prompt(root, item, s["output_text"])
            spec = {"backend": judge.BACKEND, "model": main["model"], "effort": main["effort"],
                    "system_prompt_sha256": None, "prompt_sha256": generate.sha256_text(prompt)}

            def call_fn(spec_a, key, prompt=prompt, item=item, sid=s["sample_id"]):
                pacer.check("openai")
                rec = judge.call_record(spec_a, key, prompt, item, prereg_obj=prereg_obj, notice_sha=notice_sha,
                                        runner=runner, sample_id=sid)
                pacer.add("openai", pacing.record_tokens(rec))
                return rec

            rec = cache.run_attempts(spec, call_fn, main["max_attempts"], judge.STOP_OUTCOMES)
            if rec is not None and rec["outcome"] == "ok":
                rows.append(row(s, "scored", judge.labels_from_record(rec), rec))
                continue
            if rec is not None and rec["outcome"] == "quota_exhausted":
                raise QuotaStop("openai", rec.get("error_text") or "")
            if rec is not None and rec["outcome"] == "model_policy_violation":
                raise PolicyStop(rec.get("error_text") or "model policy violation")
            rows.append(row(s, "incomplete", None, rec))
    finally:
        records.write_jsonl(path, rows)
    return rows


# ---------------------------------------------------------------------------
# grading glue
# ---------------------------------------------------------------------------

def load_items(root: Path, run_id: str) -> list[dict]:
    p = run_dir(root, run_id) / "items.jsonl"
    return [r["item"] for r in records.read_jsonl(p)]


def read_calls(root: Path, run_id: str) -> list[dict]:
    out = []
    d = run_dir(root, run_id) / "calls"
    if d.is_dir():
        for p in sorted(d.rglob("*.json")):
            if not p.name.startswith("."):
                out.append(records.read_json(p))
    return out
