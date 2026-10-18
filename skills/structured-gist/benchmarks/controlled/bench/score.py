#!/usr/bin/env python3
"""
Deterministic grading and the report (T029). No model calls.

``grade``: for every sample, fact_retention.sol and relation_retention.sol
(from ``scoring/combine.py:score_semantic`` over the sol judge labels), the
dataset's secondary score, ``words`` and ``lint``. Every GraderResult is
validated against the records schema before it is written.

``report``: per-dataset DatasetResults plus REPORT.md. Cases with an
incomplete main score are listed in ``incomplete_cases`` and left out of every
mean, difference and test. A failed generation is scored zero (prereg length
section) and counted separately.
"""
from __future__ import annotations

import hashlib
import math
import random
import re
import string
import sys
from pathlib import Path

from bench import items as items_mod, prereg as prereg_mod, records, words

_SC = prereg_mod.SC / "scoring"
for _p in (_SC, prereg_mod.SG / "tests"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
_dwb = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    import combine  # noqa: E402 -- SC/scoring/combine.py
    import lint_outline  # noqa: E402 -- skills/structured-gist/tests/lint_outline.py
finally:
    sys.dont_write_bytecode = _dwb

FR022 = ("Plain bullets were not significantly worse than the skill on this dataset, so any gain here may "
         "come from list format alone and not from the skill's rules.")
METHODS = ("skill", "plain_prose", "plain_bullets", "lead_n", "textrank")
JUDGE = "sol"
LABELS_GRADER = f"judge_labels.{JUDGE}"
FACT_GRADER = f"fact_retention.{JUDGE}"
REL_GRADER = f"relation_retention.{JUDGE}"
MAIN_GRADERS = (FACT_GRADER, REL_GRADER)


# ---------------------------------------------------------------------------
# secondary scorers
# ---------------------------------------------------------------------------

_ARTICLES = re.compile(r"\b(a|an|the)\b", re.IGNORECASE)


def squad_normalize(s: str) -> str:
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = _ARTICLES.sub(" ", s)
    return " ".join(s.split())


def _lcs(a: list[str], b: list[str]) -> int:
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


def rouge_l(candidate: str, reference: str) -> dict:
    c = re.findall(r"\w+", candidate.lower())
    r = re.findall(r"\w+", reference.lower())
    lcs = _lcs(c, r)
    p = lcs / len(c) if c else 0.0
    rec = lcs / len(r) if r else 0.0
    f = 2 * p * rec / (p + rec) if p + rec else 0.0
    return {"precision": p, "recall": rec, "f": f}


def answer_token_recall(candidate: str, reference: str) -> float:
    ref = squad_normalize(reference).split()
    if not ref:
        return 0.0
    pool: dict[str, int] = {}
    for t in squad_normalize(candidate).split():
        pool[t] = pool.get(t, 0) + 1
    common = 0
    for t in ref:
        if pool.get(t, 0) > 0:
            pool[t] -= 1
            common += 1
    return common / len(ref)


def answer_containment(candidate: str, reference: str) -> float:
    ref = squad_normalize(reference)
    if not ref:
        return 0.0
    return 1.0 if f" {ref} " in f" {squad_normalize(candidate)} " else 0.0


# ---------------------------------------------------------------------------
# grading
# ---------------------------------------------------------------------------

def _row(grader, gtype, sample_id, status, score=None, labels=None, detail=None, call_key=None) -> dict:
    row = {"grader": grader, "grader_type": gtype, "sample_id": sample_id, "status": status,
           "score": score, "labels": labels, "detail": detail, "call_key": call_key}
    records.validate_or_raise(row, "GraderResult")
    return row


def secondary_name(prereg_obj: dict, dataset: str) -> str:
    return prereg_obj["secondary"][dataset]


def grade(prereg_obj: dict, samples: list[dict], items_by_id: dict, label_rows: dict) -> dict[str, list[dict]]:
    """grader name -> rows. `label_rows`: sample_id -> judge_labels GraderResult."""
    out: dict[str, list[dict]] = {}

    def add(row):
        out.setdefault(row["grader"], []).append(row)

    for s in samples:
        item = items_by_id[s["item_id"]]
        sid = s["sample_id"]
        has_rel = bool(item["relations"])
        if s["status"] == "failed":
            add(_row(FACT_GRADER, "python", sid, "failed_generation", 0.0))
            add(_row(REL_GRADER, "python", sid, "failed_generation" if has_rel else "not_applicable",
                     0.0 if has_rel else None))
        else:
            lab = label_rows.get(sid)
            if lab is None or lab["status"] != "scored" or not lab.get("labels"):
                add(_row(FACT_GRADER, "python", sid, "incomplete"))
                add(_row(REL_GRADER, "python", sid, "incomplete" if has_rel else "not_applicable"))
            else:
                sc = combine.score_semantic(items_mod.gold_view(item), lab["labels"])
                add(_row(FACT_GRADER, "python", sid, "scored", sc["task_weighted_fact_retention"],
                         call_key=lab.get("call_key")))
                add(_row(REL_GRADER, "python", sid, "scored" if has_rel else "not_applicable",
                         sc["relation_retention"] if has_rel else None, call_key=lab.get("call_key")))
        # secondary
        ds = item["dataset"]
        name = secondary_name(prereg_obj, ds)
        ref = item.get("reference_answer")
        gtype = {"rouge_l_recall": "text_similarity"}.get(name, "python")
        if ref is None:
            add(_row(name, gtype, sid, "not_applicable"))
        elif s["status"] == "failed":
            add(_row(name, gtype, sid, "failed_generation", 0.0))
        elif name == "rouge_l_recall":
            r = rouge_l(s["output_text"], ref)
            add(_row(name, gtype, sid, "scored", r["recall"], detail=r))
        elif name == "answer_token_recall":
            add(_row(name, gtype, sid, "scored", answer_token_recall(s["output_text"], ref)))
        else:
            add(_row(name, gtype, sid, "scored", answer_containment(s["output_text"], ref)))
        add(_row("words", "python", sid, "scored", float(s["words"])))
        if s["method"] == "skill" and s["status"] == "generated":
            viol = lint_outline.lint_text(s["output_text"])
            add(_row("lint", "python", sid, "scored", float(len(viol)),
                     detail={"lint_violations": [list(v) for v in viol]}))
        else:
            add(_row("lint", "python", sid, "not_applicable"))
    return out


# ---------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------

def seed_int(seed_string: str) -> int:
    return int(hashlib.sha256(seed_string.encode("utf-8")).hexdigest()[:16], 16)


def seed_for(template: str, master: str, **vals: str) -> int:
    """Fills a colon-separated seed template; unknown tokens stay literal."""
    parts = [master if t == "master_seed" else vals.get(t, t) for t in template.split(":")]
    return seed_int(":".join(parts))


def sign_flip_p(d: list[float], tol: float, exact_max_n: int, draws: int, seed: int) -> tuple[float, float, str]:
    """One-sided paired sign-flip permutation p-values (greater, less) for
    the mean of `d`. Exact when n <= exact_max_n, else Monte Carlo."""
    n = len(d)
    if n == 0:
        return 1.0, 1.0, "exact"
    t_obs = sum(d) / n
    if n <= exact_max_n:
        sums = [0.0]
        for x in d:
            sums = [s + x for s in sums] + [s - x for s in sums]
        total = len(sums)
        ge = sum(1 for s in sums if s / n >= t_obs - tol)
        le = sum(1 for s in sums if s / n <= t_obs + tol)
        return ge / total, le / total, "exact"
    rng = random.Random(seed)
    ge = le = 0
    for _ in range(draws):
        bits = rng.getrandbits(n)
        s = 0.0
        for i, x in enumerate(d):
            s += x if (bits >> i) & 1 else -x
        t = s / n
        ge += t >= t_obs - tol
        le += t <= t_obs + tol
    return (1 + ge) / (1 + draws), (1 + le) / (1 + draws), "monte_carlo"


def bootstrap_ci(values: list[float], resamples: int, level: float, seed: int) -> list[float]:
    n = len(values)
    if n == 0:
        return [0.0, 0.0]
    rng = random.Random(seed)
    means = sorted(sum(values[int(rng.random() * n)] for _ in range(n)) / n for _ in range(resamples))
    a = (1 - level) / 2
    lo = means[int(math.floor(a * resamples))]
    hi = means[min(resamples - 1, int(math.ceil((1 - a) * resamples)) - 1)]
    return [lo, hi]


def holm(ps: list[float]) -> list[float]:
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj = [0.0] * m
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * ps[i]))
        adj[i] = run
    return adj


def _mean(v: list[float]) -> float:
    return sum(v) / len(v) if v else 0.0


def comparison(pairs: list[tuple[str, float, float]], excluded: list[str], pre: dict, ds: str,
               control: str, score: str) -> dict:
    ws, bs = pre["win_rule"], pre["bootstrap"]
    seed_master = pre["master_seed"]
    d = [a - b for _i, a, b in pairs]
    perm_seed = seed_for(bs["seed_permutation"], seed_master, dataset=ds, control=control, score=score)
    diff_seed = seed_for(bs["seed_diff"], seed_master, dataset=ds, control=control)
    pg, pl, test = sign_flip_p(d, ws["tie_tolerance"], ws["exact_max_n"], ws["monte_carlo_draws"], perm_seed)
    return {
        "n_pairs": len(pairs), "excluded_ids": sorted(excluded),
        "mean_skill": _mean([a for _i, a, _b in pairs]), "mean_control": _mean([b for _i, _a, b in pairs]),
        "mean_diff": _mean(d),
        "ci95": bootstrap_ci(d, bs["resamples"], bs["level"], diff_seed),
        "p_greater": pg, "p_less": pl, "p_greater_holm": pg, "p_less_holm": pl,
        "test": test, "seed": perm_seed,
    }


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def _per_model_usage(calls: list[dict], dataset: str) -> list[dict]:
    agg: dict[str, dict] = {}
    for c in calls:
        sid = c.get("sample_id") or ""
        if not sid.startswith(dataset + "/"):
            continue
        name = c.get("model_resolved") or c.get("model_requested")
        a = agg.setdefault(name, {"model_name": name, "invocation_count": 0, "prompt_tokens": 0,
                                  "completion_tokens": 0, "cached_tokens": 0, "total_tokens": 0})
        t = c["tokens"]
        a["invocation_count"] += 1
        a["prompt_tokens"] += t["input"]
        a["completion_tokens"] += t["output"]
        a["cached_tokens"] += t.get("cached") or 0
        a["total_tokens"] += t["input"] + t["output"] + (t.get("reasoning") or 0)
    return [agg[k] for k in sorted(agg)]


def build_results(prereg_obj: dict, samples: list[dict], items_by_id: dict, graded: dict,
                  calls: list[dict]) -> dict[str, dict]:
    """dataset -> DatasetResults dict (plus extra keys)."""
    pre = prereg_obj
    status = {(g, r["sample_id"]): r for g, rows in graded.items() for r in rows}
    by_item: dict[str, dict[str, dict]] = {}
    for s in samples:
        by_item.setdefault(s["item_id"], {})[s["method"]] = s
    datasets = [ds for ds in items_mod.DATASETS if any(items_by_id[i]["dataset"] == ds for i in by_item)]
    results: dict[str, dict] = {}
    thr = pre["corpus"]["relation_check_threshold"]
    base = list(pre["win_rule"]["controls"])
    first = pre["report"]["first_row_control"]
    controls = sorted(base, key=lambda c: (c != first, base.index(c)))
    for ds in datasets:
        ids = sorted(i for i in by_item if items_by_id[i]["dataset"] == ds)
        incomplete = []
        for i in ids:
            sids = [by_item[i][m]["sample_id"] for m in by_item[i]]
            if len(by_item[i]) < len(METHODS) or any(
                    status[(g, sid)]["status"] == "incomplete" for g in MAIN_GRADERS for sid in sids):
                incomplete.append(i)
        inc = set(incomplete)
        included = [i for i in ids if i not in inc]

        def val(i, m, g):
            r = status[(g, by_item[i][m]["sample_id"])]
            return r["score"] if r["status"] in ("scored", "failed_generation") else None

        fact = {m: {i: val(i, m, FACT_GRADER) for i in included} for m in METHODS}
        rel = {m: {i: val(i, m, REL_GRADER) for i in included if items_by_id[i]["relations"]} for m in METHODS}
        bs = pre["bootstrap"]
        methods_out = {}
        for m in METHODS:
            seed = seed_for(bs["seed_mean"], pre["master_seed"], dataset=ds, method=m)
            fv = [v for v in fact[m].values() if v is not None]
            rv = [v for v in rel[m].values() if v is not None]
            methods_out[m] = {
                "fact_retention": {"mean": _mean(fv) if fv else None, "n": len(fv),
                                   "ci95": bootstrap_ci(fv, bs["resamples"], bs["level"], seed) if fv else None},
                "relation_retention": {"mean": _mean(rv) if rv else None, "n": len(rv),
                                       "ci95": bootstrap_ci(rv, bs["resamples"], bs["level"], seed) if rv else None},
            }
        relations_total = pre["corpus"]["gold_relation_counts"][ds]
        apply_rel = relations_total >= thr
        fact_cmp = {}
        rel_cmp = {}
        for c in controls:
            pairs = [(i, fact["skill"][i], fact[c][i]) for i in included]
            fact_cmp[c] = comparison(pairs, incomplete, pre, ds, c, "fact_retention")
            if apply_rel:
                rp = [(i, rel["skill"][i], rel[c][i]) for i in rel["skill"]]
                cm = comparison(rp, incomplete, pre, ds, c, "relation_retention")
                cm["p_greater_holm"] = None
                cm["p_less_holm"] = cm["p_less"]
                rel_cmp[c] = cm
        hg = holm([fact_cmp[c]["p_greater"] for c in controls])
        hl = holm([fact_cmp[c]["p_less"] for c in controls])
        alpha = pre["win_rule"]["alpha"]
        labels = pre["win_rule"]["verdict_labels"]
        verdicts = []
        for k, c in enumerate(controls):
            fact_cmp[c]["p_greater_holm"], fact_cmp[c]["p_less_holm"] = hg[k], hl[k]
            ahead, behind = hg[k] < alpha, hl[k] < alpha
            guard_fail = apply_rel and rel_cmp[c]["p_less"] < alpha
            if ahead and not guard_fail:
                v = labels[0]
            elif ahead:
                v = labels[1]
            elif behind:
                v = labels[3]
            else:
                v = labels[2]
            entry = {"control": c, "fact": fact_cmp[c], "relation": rel_cmp.get(c),
                     "relation_check_applied": apply_rel, "verdict": v,
                     "relation_check_reason": (f"gold relations {relations_total} >= {thr}: guard applied" if apply_rel
                                               else f"gold relations {relations_total} < {thr}: fact retention alone")}
            if c == "plain_bullets":
                entry["fr022_sentence"] = not ahead
            records.validate_or_raise(entry, "Verdict")
            verdicts.append(entry)

        counts = {"total": 0, "passed": 0, "failed": 0, "errored": 0}
        crit = []
        names = [LABELS_GRADER, FACT_GRADER, REL_GRADER, secondary_name(pre, ds), "words", "lint"]
        ds_sids = {s["sample_id"]: s for s in samples if items_by_id[s["item_id"]]["dataset"] == ds}
        for g in names:
            rows = [status[(g, sid)] for sid in ds_sids if (g, sid) in status]
            passed = sum(r["status"] == "scored" for r in rows)
            failed = sum(r["status"] == "failed_generation" for r in rows)
            errored = sum(r["status"] == "incomplete" for r in rows)
            vals = [r["score"] for r in rows if r["status"] in ("scored", "failed_generation")
                    and r["score"] is not None and items_by_id[ds_sids[r["sample_id"]]["item_id"]]["item_id"] not in inc]
            crit.append({"testing_criteria": g, "passed": passed, "failed": failed, "errored": errored,
                         "mean": _mean(vals) if vals and g != LABELS_GRADER else None})
            if g == FACT_GRADER:
                counts = {"total": len(rows), "passed": passed, "failed": failed, "errored": errored}
        flags: dict = {}
        for s in ds_sids.values():
            for fl in s["length_flags"]:
                flags.setdefault(s["method"], {}).setdefault(fl, 0)
                flags[s["method"]][fl] += 1
        sec = secondary_name(pre, ds)
        sec_means = {}
        for m in METHODS:
            v = [status[(sec, by_item[i][m]["sample_id"])]["score"] for i in included
                 if status[(sec, by_item[i][m]["sample_id"])]["score"] is not None]
            sec_means[m] = _mean(v) if v else None
        res = {
            "dataset": ds,
            "early_signal": ds in pre["report"]["early_signal"],
            "result_counts": counts,
            "per_testing_criteria_results": crit,
            "per_model_usage": _per_model_usage(calls, ds),
            "verdicts": verdicts,
            "incomplete_cases": incomplete,
            "cases_scored": included,
            "methods": methods_out,
            "secondary": {"name": sec, "mean": sec_means},
            "failed_generations": {m: sum(1 for s in ds_sids.values() if s["method"] == m and s["status"] == "failed")
                                   for m in METHODS},
            "length_flags": flags,
            "zero_relation_cases": sum(1 for i in ids if not items_by_id[i]["relations"]),
        }
        records.validate_or_raise(res, "DatasetResults")
        results[ds] = res
    return results


def render_report(run_id: str, prereg_obj: dict, results: dict[str, dict]) -> str:
    L = [f"# Controlled benchmark report: {run_id}", "",
         "No pooled cross-dataset number. Cases with an incomplete main score are listed and left out of every mean.", ""]
    for ds, r in results.items():
        L += [f"## {ds}" + (" (early signal: small case count)" if r["early_signal"] else ""), ""]
        L += [f"Cases scored: {len(r['cases_scored'])}. Incomplete cases (excluded): "
              + (", ".join(r["incomplete_cases"]) if r["incomplete_cases"] else "none") + ".", ""]
        L += ["| control | verdict | mean diff (facts) | 95% CI | p (greater, Holm) | relation guard |",
              "|---|---|---|---|---|---|"]
        for v in r["verdicts"]:
            f = v["fact"]
            L.append(f"| {v['control']} | {v['verdict']} | {f['mean_diff']:.4f} | "
                     f"[{f['ci95'][0]:.4f}, {f['ci95'][1]:.4f}] | {f['p_greater_holm']:.4f} | "
                     f"{'applied' if v['relation_check_applied'] else 'not applied'} |")
        L += ["", "| method | fact retention | relation retention | " + r["secondary"]["name"] + " |", "|---|---|---|---|"]
        for m, mv in r["methods"].items():
            fm, rm, sm = mv["fact_retention"]["mean"], mv["relation_retention"]["mean"], r["secondary"]["mean"][m]
            L.append(f"| {m} | {'n/a' if fm is None else format(fm, '.4f')} | {'n/a' if rm is None else format(rm, '.4f')} | "
                     f"{'n/a' if sm is None else format(sm, '.4f')} |")
        L += ["", "Failed generations: " + ", ".join(f"{m} {n}" for m, n in r["failed_generations"].items()) + ".",
              f"Zero-relation cases (left out of the relation mean): {r['zero_relation_cases']}.", ""]
        bullets = next((v for v in r["verdicts"] if v["control"] == "plain_bullets"), None)
        if bullets and bullets.get("fr022_sentence"):
            L += [prereg_obj["report"].get("fr022_sentence") or FR022, ""]
    return "\n".join(L) + "\n"
