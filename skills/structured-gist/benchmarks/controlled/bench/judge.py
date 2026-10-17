#!/usr/bin/env python3
"""
Main-judge adapter: sol through the agents-inc launcher only (FR-021, FR-024).

    <agents-inc python> bench/agents_inc_isolated.py --model sol --effort <prereg> --cwd <empty tmp dir>

The shim calls agents-inc's own ``run_codex(..., isolate_home=True)`` (isolated
CODEX_HOME, no tools), which the ``agents-inc run`` CLI does not expose.

The prompt goes on stdin. The judge never sees the source, the method, or the
case id: only the provider notice, judge.md, the gold checklist
(``items.judge_view``) and the short version. Free judges are not part of this
module's scope: their adapters raise NotImplementedError.

``RUNNER`` is a test hook, as in ``bench.generate``. Python 3.11+ stdlib only.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from bench import items as items_mod
from bench import records
from bench.generate import STOP_OUTCOMES, now_iso, sha256_text  # noqa: F401 -- re-exported

RUNNER = None
BACKEND = "agents-inc-codex"
DEFAULT_BIN = "/Users/domattioli/.local/bin/agents-inc"
FREE_JUDGE_MSG = "free judges route via gask.sh/oask.sh through agents-inc; not in Phase 4 scope"

_QUOTA_STDERR = re.compile(r"usage or rate limit", re.IGNORECASE)
_QUOTA_ANY = re.compile(r"\b429\b|quota|rate[ _-]?limit", re.IGNORECASE)
_TOKENS = re.compile(r"tokens used[:\s]*([\d][\d,]*)", re.IGNORECASE)
_RECORD = re.compile(r"agents-inc run: record\s+(\{.*\})")
_FENCE = re.compile(r"^\s*```[a-zA-Z0-9_-]*\s*\n(.*?)\n\s*```\s*$", re.DOTALL)


def _runner(runner):
    return runner or RUNNER or subprocess.run


def agents_inc_bin() -> str:
    return os.environ.get("SG_BENCH_AGENTS_INC") or DEFAULT_BIN


SHIM = Path(__file__).resolve().parent / "agents_inc_isolated.py"


def agents_inc_python() -> str:
    """Interpreter of the agents-inc install: env override, else the
    launcher's shebang line."""
    env = os.environ.get("SG_BENCH_AGENTS_INC_PYTHON")
    if env:
        return env
    with open(agents_inc_bin(), "r", encoding="utf-8") as fh:
        first = fh.readline().strip()
    if not first.startswith("#!"):
        raise FileNotFoundError(f"{agents_inc_bin()} has no shebang line")
    return first[2:].split()[0]


def free_judge(*_a, **_k):
    raise NotImplementedError(FREE_JUDGE_MSG)


def read_notice(root: Path) -> str:
    return (Path(root) / "prompts" / "provider_notice.txt").read_text(encoding="utf-8")


def build_prompt(root: Path, item: dict, sample_text: str) -> str:
    judge_md = (Path(root) / "prompts" / "judge.md").read_text(encoding="utf-8")
    checklist = json.dumps(items_mod.judge_view(item), indent=2, sort_keys=True, ensure_ascii=False)
    return (read_notice(root).rstrip("\n") + "\n\n" + judge_md.rstrip("\n")
            + "\n\nCHECKLIST:\n" + checklist + "\n\nSHORT VERSION:\n" + sample_text.rstrip("\n") + "\n")


def parse_total_tokens(stderr: str) -> int | None:
    m = _TOKENS.findall(stderr or "")
    if not m:
        return None
    return int(m[-1].replace(",", ""))


def parse_slug(stderr: str) -> str | None:
    for line in (stderr or "").splitlines():
        m = _RECORD.search(line)
        if m:
            try:
                rec = json.loads(m.group(1))
            except ValueError:
                continue
            if isinstance(rec, dict):
                slug = rec.get("slug") or rec.get("model")
                if isinstance(slug, str):
                    return slug
    return None


def parse_judge_json(stdout: str) -> dict | None:
    text = (stdout or "").strip()
    m = _FENCE.match(text)
    if m:
        text = m.group(1).strip()
    try:
        obj = json.loads(text)
    except ValueError:
        return None
    return obj if isinstance(obj, dict) else None


def check_labels(obj: dict, item: dict) -> list[str]:
    """Schema problems plus exact id-set equality with the checklist."""
    problems = records.validate(obj, None, "judge-output")
    if problems:
        return problems
    if set(obj["facts"]) != {f["id"] for f in item["facts"]}:
        problems.append("fact ids differ from the checklist")
    if set(obj["relations"]) != {r["id"] for r in item["relations"]}:
        problems.append("relation ids differ from the checklist")
    return problems


def _expected(main: dict) -> str | None:
    return main["model"] if main.get("check_resolved_model", True) else None


def invoke(prompt: str, *, effort: str, runner=None, timeout: int = 600) -> dict:
    cwd = tempfile.mkdtemp(prefix="sgb-judge-")
    out = {"returncode": None, "stdout": "", "stderr": "", "timeout": False, "missing": None}
    try:
        try:
            argv = [agents_inc_python(), str(SHIM), "--model", "sol", "--effort", effort, "--cwd", cwd]
            proc = _runner(runner)(argv, input=prompt, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            out["timeout"] = True
            return out
        except (FileNotFoundError, PermissionError, OSError) as e:
            out["missing"] = str(e)
            return out
        out.update(returncode=proc.returncode, stdout=proc.stdout or "", stderr=proc.stderr or "")
        return out
    finally:
        shutil.rmtree(cwd, ignore_errors=True)


def _tokens(prompt: str, raw: dict) -> dict:
    out_est = round(len(raw["stdout"]) / 4)
    total = parse_total_tokens(raw["stderr"])
    if total is None:
        return {"input": round(len(prompt) / 4), "output": out_est, "source": "estimated"}
    return {"input": max(total - out_est, 0), "output": out_est, "source": "estimated"}


def classify(raw: dict, item: dict | None, expected_model: str | None = None) -> tuple[str, str | None, dict | None, str | None]:
    """(outcome, error_text, labels, slug)."""
    if raw["missing"]:
        return "error", f"cannot run agents-inc: {raw['missing']}"[:600], None, None
    if raw["timeout"]:
        return "timeout", "timeout", None, None
    stderr = raw["stderr"]
    slug = parse_slug(stderr)
    if _QUOTA_STDERR.search(stderr) or (raw["returncode"] != 0 and _QUOTA_ANY.search(stderr + raw["stdout"])):
        return "quota_exhausted", stderr.strip()[-400:], None, slug
    if raw["returncode"] != 0:
        return "error", f"exit {raw['returncode']}: {stderr.strip()[-400:]}", None, slug
    if expected_model is not None and slug != expected_model:
        return "model_policy_violation", f"resolved model slug {slug!r} != pre-registered {expected_model!r}", None, slug
    if item is None:
        return "ok", None, None, slug
    obj = parse_judge_json(raw["stdout"])
    if obj is None:
        return "malformed", "stdout is not one JSON object", None, slug
    problems = check_labels(obj, item)
    if problems:
        return "malformed", "; ".join(problems)[:600], None, slug
    return "ok", None, obj, slug


def call_record(spec: dict, key: str, prompt: str, item: dict, *, prereg_obj: dict, notice_sha: str,
                runner=None, sample_id: str | None = None) -> dict:
    started = now_iso()
    main = prereg_obj["judges"]["main"]
    raw = invoke(prompt, effort=main["effort"], runner=runner, timeout=prereg_obj["judges"]["call_timeout_seconds"])
    outcome, err, _labels, slug = classify(raw, item, _expected(main))
    rec = {
        "key": key, "purpose": "judge", "backend": BACKEND, "model_requested": spec["model"],
        "model_resolved": slug, "effort": spec["effort"], "prompt_sha256": spec["prompt_sha256"],
        "system_prompt_sha256": None, "notice_sha256": notice_sha, "attempt": spec["attempt"],
        "started_at": started, "finished_at": now_iso(), "outcome": outcome, "error_text": err,
        "stdout": raw["stdout"], "tokens": _tokens(prompt, raw),
    }
    if sample_id:
        rec["sample_id"] = sample_id
    records.validate_or_raise(rec, "CallRecord")
    return rec


def labels_from_record(rec: dict) -> dict | None:
    obj = parse_judge_json(rec.get("stdout") or "")
    return obj


CANARY_PROMPT = "Reply with the single word OK."


class CanaryFailed(RuntimeError):
    def __init__(self, outcome: str, detail: str):
        super().__init__(f"judge canary failed: {outcome}: {detail}")
        self.outcome = outcome


def judge_canary(prereg_obj: dict, *, runner=None) -> dict:
    main = prereg_obj["judges"]["main"]
    raw = invoke(CANARY_PROMPT, effort=main["effort"], runner=runner)
    outcome, err, _l, slug = classify(raw, None, _expected(main))
    if outcome != "ok":
        raise CanaryFailed(outcome, err or "")
    sent = len(CANARY_PROMPT)
    out_chars = len(raw["stdout"])
    total = parse_total_tokens(raw["stderr"])
    res = {
        "backend": BACKEND,
        "codex_home": "isolated",
        "sent_chars": sent,
        "reported_total_tokens": total,
        "output_chars": out_chars,
        "overhead": None if total is None else total - round(sent / 4) - round(out_chars / 4),
        "raw_stderr_tail": raw["stderr"][-2000:],
        "model_resolved": slug,
    }
    if total is None:
        res["note"] = "no 'tokens used' count found in stderr; overhead not computed"
    return res
