#!/usr/bin/env python3
"""
Claude generation adapter (research R3, FR-021, FR-024).

One call = ``claude -p`` in headless mode with an isolated config directory,
no tools, no slash commands, no MCP, no session persistence, JSON output. The
user message goes on stdin; the system prompt goes through a file. The
adapter never passes ``--fallback-model``.

``subprocess.run`` is injectable: every public function takes ``runner`` (or
uses the module-level ``RUNNER`` hook when it is None, then
``subprocess.run`` looked up at call time). Tests fake it. This module never
runs a real model by itself; only the CLI subcommands do, after the gate and
the confirmation check.

Python 3.11+ stdlib only.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from bench import items as items_mod
from bench import prereg as prereg_mod
from bench import records, words

BACKEND = "claude-isolated-config"
RUNNER = None  # test hook: a callable shaped like subprocess.run
STOP_OUTCOMES = frozenset({"model_policy_violation", "quota_exhausted"})

_QUOTA = re.compile(r"\b429\b|quota|rate[ _-]?limit|usage limit|too many requests", re.IGNORECASE)
_PLACEHOLDER = "{source.md contents with HTML comments removed}"

ARM_FILES = {
    "skill": "skill_instruction.md",
    "plain_prose": "prose_instruction.md",
    "plain_bullets": "bullets_instruction.md",
}
LLM_ARMS = tuple(ARM_FILES)


class BackendUnavailable(RuntimeError):
    """The claude binary cannot be found."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _runner(runner):
    return runner or RUNNER or subprocess.run


def claude_bin() -> str:
    b = os.environ.get("SG_BENCH_CLAUDE_BIN") or shutil.which("claude")
    if not b:
        raise BackendUnavailable("claude binary not found (set SG_BENCH_CLAUDE_BIN)")
    return b


def config_dir() -> Path:
    d = Path(os.environ.get("SG_BENCH_CLAUDE_CONFIG_DIR") or (Path.home() / ".cache" / "sg-bench" / "claude-config"))
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# prompts
# ---------------------------------------------------------------------------

def _read(p: Path) -> str:
    return Path(p).read_text(encoding="utf-8")


def system_prompt(arm: str, root: Path) -> str:
    """Skill arm: SKILL.md + blank line + render-modes.md, verbatim. Plain
    arms: prompts/plain_system.md."""
    if arm == "skill":
        return _read(prereg_mod.SG / "SKILL.md") + "\n\n" + _read(prereg_mod.SG / "reference" / "render-modes.md")
    return _read(Path(root) / "prompts" / "plain_system.md")


def band(n: int) -> tuple[int, int]:
    """[ceil(0.9 N), floor(1.1 N)] computed in integers (tolerance 10%)."""
    return -((-9 * n) // 10), (11 * n) // 10


def user_message(arm: str, item: dict, root: Path, n: int | None = None) -> str:
    """shared_user.md with the arm instruction and the source filled in.
    Plain arms need `n` for {N}, {LO}, {HI}."""
    shared = _read(Path(root) / "prompts" / "shared_user.md")
    instr = _read(Path(root) / "prompts" / ARM_FILES[arm]).rstrip("\n")
    if arm != "skill":
        if n is None:
            raise ValueError("plain arms need N")
        lo, hi = band(n)
        instr = instr.replace("{N}", str(n)).replace("{LO}", str(lo)).replace("{HI}", str(hi))
    if "{ARM_INSTRUCTION}" not in shared or _PLACEHOLDER not in shared:
        raise ValueError("shared_user.md placeholders not found")
    src = words.strip_html_comments(items_mod.source_text(item))
    return shared.replace("{ARM_INSTRUCTION}", instr).replace(_PLACEHOLDER, src.rstrip("\n"))


# ---------------------------------------------------------------------------
# the call
# ---------------------------------------------------------------------------

def build_argv(model: str, effort: str, system_file: str) -> list[str]:
    return [claude_bin(), "-p", "--model", model, "--effort", effort,
            "--system-prompt-file", system_file, "--tools", "", "--disable-slash-commands",
            "--strict-mcp-config", "--no-session-persistence", "--output-format", "json"]


def _tokens(usage: dict | None) -> dict:
    if not isinstance(usage, dict):
        return {"input": 0, "output": 0, "source": "estimated"}
    parts = [usage.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")]
    return {"input": int(sum(parts)), "output": int(usage.get("output_tokens") or 0), "reasoning": None,
            "cached": int(usage.get("cache_read_input_tokens") or 0), "source": "reported"}


def invoke(system_text: str, user_text: str, *, model: str, effort: str, runner=None,
           timeout: int = 600) -> dict:
    """One claude call. Returns {outcome, text, usage, model_usage, resolved,
    error, cost}. Never raises for call failures."""
    tmp_sys = tempfile.mkdtemp(prefix="sgb-sys-")
    cwd = tempfile.mkdtemp(prefix="sgb-cwd-")
    out = {"outcome": "error", "text": "", "usage": None, "model_usage": None, "resolved": None,
           "error": None, "cost": None}
    try:
        sf = Path(tmp_sys) / "system.md"
        sf.write_text(system_text, encoding="utf-8")
        env = dict(os.environ)
        env["CLAUDE_CONFIG_DIR"] = str(config_dir())
        try:
            proc = _runner(runner)(build_argv(model, effort, str(sf)), input=user_text, env=env, cwd=cwd,
                                   capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            out.update(outcome="timeout", error=f"timeout after {timeout}s")
            return out
        except (FileNotFoundError, PermissionError) as e:
            out.update(outcome="error", error=f"cannot run claude: {e}")
            return out
        stdout, stderr = proc.stdout or "", proc.stderr or ""
        try:
            data = json.loads(stdout)
            if not isinstance(data, dict):
                raise ValueError("not an object")
        except ValueError:
            data = None
        blob = f"{stdout}\n{stderr}"
        if data is None:
            if proc.returncode != 0:
                out.update(outcome="quota_exhausted" if _QUOTA.search(blob) else "error",
                           error=f"exit {proc.returncode}: {blob.strip()[:400]}")
            else:
                out.update(outcome="malformed", error="stdout is not one JSON object")
            return out
        text = data.get("result") if isinstance(data.get("result"), str) else ""
        out.update(text=text, usage=data.get("usage"), model_usage=data.get("modelUsage"),
                   cost=data.get("total_cost_usd"))
        if data.get("is_error") or proc.returncode != 0:
            quota = _QUOTA.search(f"{text}\n{blob}") is not None
            out.update(outcome="quota_exhausted" if quota else "error",
                       error=f"exit {proc.returncode}: {(text or blob).strip()[:400]}")
            return out
        mu = data.get("modelUsage")
        if isinstance(mu, dict) and mu:
            resolved = ",".join(sorted(mu))
        else:
            resolved = data.get("model") if isinstance(data.get("model"), str) else None
        out["resolved"] = resolved
        if resolved != model:
            out.update(outcome="model_policy_violation",
                       error=f"resolved model {resolved!r} != requested {model!r}")
            return out
        if not text.strip():
            out.update(outcome="refusal", error="empty result")
            return out
        out["outcome"] = "ok"
        return out
    finally:
        shutil.rmtree(tmp_sys, ignore_errors=True)
        shutil.rmtree(cwd, ignore_errors=True)


def make_record(res: dict, spec: dict, key: str, started: str, *, purpose: str = "generate",
                sample_id: str | None = None) -> dict:
    rec = {
        "key": key, "purpose": purpose, "backend": BACKEND,
        "model_requested": spec["model"], "model_resolved": res["resolved"], "effort": spec["effort"],
        "prompt_sha256": spec["prompt_sha256"], "system_prompt_sha256": spec["system_prompt_sha256"],
        "attempt": spec["attempt"], "started_at": started, "finished_at": now_iso(),
        "outcome": res["outcome"], "error_text": (res["error"] or None) and res["error"][:600],
        "stdout": res["text"], "tokens": _tokens(res["usage"]),
    }
    if sample_id:
        rec["sample_id"] = sample_id
    if isinstance(res.get("cost"), (int, float)):
        rec["cost_usd_reported"] = res["cost"]
    records.validate_or_raise(rec, "CallRecord")
    return rec


def call_record(spec: dict, key: str, system_text: str, user_text: str, *, runner=None,
                sample_id: str | None = None, timeout: int = 600) -> dict:
    """The call_fn for ``CallCache.run_attempts``."""
    started = now_iso()
    res = invoke(system_text, user_text, model=spec["model"], effort=spec["effort"], runner=runner,
                 timeout=timeout)
    return make_record(res, spec, key, started, sample_id=sample_id)


# ---------------------------------------------------------------------------
# canary
# ---------------------------------------------------------------------------

CANARY_SYSTEM = "You are a test endpoint."
CANARY_USER = "Reply with the single word OK."


def canary(prereg_obj: dict, *, runner=None) -> dict:
    """One tiny call. Raises RuntimeError with the outcome when it fails."""
    gen = prereg_obj["generator"]
    res = invoke(CANARY_SYSTEM, CANARY_USER, model=gen["model"], effort=gen["effort"], runner=runner)
    if res["outcome"] != "ok":
        raise CanaryFailed(res["outcome"], res["error"] or "")
    sent = len(CANARY_SYSTEM) + len(CANARY_USER)
    tok = _tokens(res["usage"])
    return {
        "backend": "anthropic",
        "sent_chars": sent,
        "sent_tokens_chars4": sent / 4,
        "reported_input_tokens": tok["input"],
        "output_tokens": tok["output"],
        "overhead": int(round(tok["input"] - sent / 4)),
        "raw_usage": {"usage": res["usage"], "modelUsage": res["model_usage"]},
        "model_resolved": res["resolved"],
    }


class CanaryFailed(RuntimeError):
    def __init__(self, outcome: str, detail: str):
        super().__init__(f"canary failed: {outcome}: {detail}")
        self.outcome = outcome


def ceil_div4(chars: int) -> int:
    return math.ceil(chars / 4)
