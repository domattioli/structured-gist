#!/usr/bin/env python3
"""
Model backends for the model-effort sweep.

One entry point, `call(backend, model, effort, prompt, cwd)`, returns a plain
dict:

    {text, input_tokens, output_tokens, cost_usd, duration_s,
     exit_code, stderr_tail}

plus `raw_stdout` (the unparsed reply, kept for raw.txt) when a process ran.

Two backends exist:

claude
    Runs the Claude Code CLI in print mode with every source of ambient
    context switched off: no tools, no MCP servers, no settings files (so no
    user or project AGENTS.md / CLAUDE.md instructions), no session
    persistence, and a fixed one-line system prompt. The prompt goes on stdin.
    Token counts and cost come from the CLI's JSON output. The CLI's
    usage.input_tokens excludes cached input, so input_tokens here is
    input_tokens + cache_creation_input_tokens + cache_read_input_tokens,
    and the two cache counts are also returned as separate keys.

codex
    Runs `agents-inc run` with the model alias (luna, terra, sol, astra) and
    CODEX_HOME pointed at a dedicated benchmark home (default
    ~/.codex-bench) so the operator's normal Codex configuration and
    instructions are not loaded. The prompt goes on stdin and the reply is
    stdout. Token usage is parsed best-effort from a `tokens used` line on
    stderr; that line reports one total, so it is stored as `total_tokens`
    and input/output stay None. Unknown is always None, never 0.

Before a codex call runs, `<codex_home>/auth.json` must exist. This module
only checks that the path exists (os.path.exists); it never opens, reads,
prints, or copies that file.

Every call runs in an empty temporary directory, never inside the
repository, so the model cannot pick up project files or instructions.

Nothing in this module runs at import time. Tests replace `runner` with a
fake, so no test ever starts a real model process.
"""
import json
import os
import re
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
# skills/structured-gist/benchmarks/model-effort-sweep -> repository root
REPO_ROOT = HERE.parents[3]

SYSTEM_PROMPT = "You are a careful assistant."
STDERR_TAIL_CHARS = 2000
DEFAULT_CODEX_HOME = "~/.codex-bench"
DEFAULT_TIMEOUT_S = 600


class BackendError(RuntimeError):
    """Raised when a call is refused before any process starts."""


class CodexAuthMissing(BackendError):
    """Raised when <codex_home>/auth.json does not exist."""


def expand_codex_home(codex_home=None) -> str:
    return os.path.abspath(os.path.expanduser(codex_home or DEFAULT_CODEX_HOME))


def codex_auth_present(codex_home=None) -> bool:
    """Existence check only. The file is never opened."""
    return os.path.exists(os.path.join(expand_codex_home(codex_home), "auth.json"))


def build_argv(backend: str, model: str, effort: str, cwd: str) -> list:
    if backend == "claude":
        return [
            "claude", "-p",
            "--model", model,
            "--effort", effort,
            "--tools", "",
            "--strict-mcp-config",
            "--setting-sources", "",
            "--no-session-persistence",
            "--output-format", "json",
            "--system-prompt", SYSTEM_PROMPT,
        ]
    if backend == "codex":
        return ["agents-inc", "run", "--model", model, "--effort", effort, "--cwd", str(cwd)]
    raise BackendError(f"unknown backend: {backend!r}")


def _check_cwd(cwd) -> None:
    if cwd is None:
        raise BackendError("cwd is required: pass an empty temporary directory")
    p = Path(cwd).resolve()
    if not p.is_dir():
        raise BackendError(f"cwd does not exist: {p}")
    if p == REPO_ROOT or REPO_ROOT in p.parents:
        raise BackendError(f"cwd must be outside the repository, got {p}")


def _int_or_none(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return None


def parse_claude_stdout(stdout: str) -> dict:
    """Parse `claude -p --output-format json` stdout. Missing fields stay None."""
    try:
        data = json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        return {"text": "", "input_tokens": None, "output_tokens": None,
                "cache_creation_input_tokens": None, "cache_read_input_tokens": None,
                "cost_usd": None, "is_error": True, "parse_error": True}
    if not isinstance(data, dict):
        return {"text": "", "input_tokens": None, "output_tokens": None,
                "cache_creation_input_tokens": None, "cache_read_input_tokens": None,
                "cost_usd": None, "is_error": True, "parse_error": True}
    usage = data.get("usage")
    has_usage = isinstance(usage, dict) and bool(usage)
    usage = usage if has_usage else {}

    def _part(key):
        # A missing key counts 0 only when the usage block itself is present.
        if not has_usage:
            return None
        return _int_or_none(usage.get(key, 0))

    uncached, cache_create, cache_read = (_part("input_tokens"),
                                          _part("cache_creation_input_tokens"),
                                          _part("cache_read_input_tokens"))
    parts = (uncached, cache_create, cache_read)
    # usage.input_tokens excludes cached input, so the total prompt size is
    # input + cache creation + cache read.
    input_total = sum(parts) if has_usage and None not in parts else None
    cost = data.get("total_cost_usd")
    result = data.get("result")
    return {
        "text": result if isinstance(result, str) else "",
        "input_tokens": input_total,
        "cache_creation_input_tokens": cache_create,
        "cache_read_input_tokens": cache_read,
        "output_tokens": _int_or_none(usage.get("output_tokens")),
        "cost_usd": float(cost) if isinstance(cost, (int, float)) and not isinstance(cost, bool) else None,
        "is_error": bool(data.get("is_error", False)),
        "parse_error": False,
    }


_TOKENS_RE = re.compile(r"tokens used\s*[:=]?\s*([0-9][0-9,_]*)", re.IGNORECASE)
_NUMBER_RE = re.compile(r"^\s*([0-9][0-9,_]*)\s*$")


def parse_codex_tokens(stderr: str):
    """Best-effort total from a `tokens used` line (same line or the next one)."""
    if not stderr:
        return None
    lines = stderr.splitlines()
    for i, line in enumerate(lines):
        if "tokens used" not in line.lower():
            continue
        m = _TOKENS_RE.search(line)
        if m:
            return int(m.group(1).replace(",", "").replace("_", ""))
        if i + 1 < len(lines):
            m = _NUMBER_RE.match(lines[i + 1])
            if m:
                return int(m.group(1).replace(",", "").replace("_", ""))
    return None


def _tail(s) -> str:
    if not s:
        return ""
    if isinstance(s, bytes):
        s = s.decode("utf-8", "replace")
    return s[-STDERR_TAIL_CHARS:]


def call(backend, model, effort, prompt, cwd, *, codex_home=None,
         timeout_s=DEFAULT_TIMEOUT_S, runner=subprocess.run) -> dict:
    """Run one prompt through one backend. See the module docstring."""
    _check_cwd(cwd)
    argv = build_argv(backend, model, effort, cwd)
    env = os.environ.copy()
    if backend == "codex":
        home = expand_codex_home(codex_home)
        if not codex_auth_present(home):
            raise CodexAuthMissing(
                f"{home}/auth.json does not exist; log in to the benchmark Codex home "
                f"first (CODEX_HOME={home}). Refusing to run codex."
            )
        env["CODEX_HOME"] = home

    out = {"text": "", "input_tokens": None, "output_tokens": None, "cost_usd": None,
           "duration_s": None, "exit_code": None, "stderr_tail": ""}
    if backend == "codex":
        out["total_tokens"] = None
    else:
        out["cache_creation_input_tokens"] = None
        out["cache_read_input_tokens"] = None

    t0 = time.monotonic()
    try:
        proc = runner(argv, input=prompt, capture_output=True, text=True,
                      cwd=str(cwd), env=env, timeout=timeout_s)
    except subprocess.TimeoutExpired as e:
        out["duration_s"] = round(time.monotonic() - t0, 3)
        out["exit_code"] = 124
        out["stderr_tail"] = _tail(e.stderr) or f"timeout after {timeout_s}s"
        return out
    except FileNotFoundError as e:
        out["duration_s"] = round(time.monotonic() - t0, 3)
        out["exit_code"] = 127
        out["stderr_tail"] = f"executable not found: {e}"
        return out
    out["duration_s"] = round(time.monotonic() - t0, 3)
    out["exit_code"] = proc.returncode
    out["stderr_tail"] = _tail(proc.stderr)
    out["raw_stdout"] = proc.stdout or ""

    if backend == "claude":
        parsed = parse_claude_stdout(proc.stdout or "")
        out["text"] = parsed["text"]
        out["input_tokens"] = parsed["input_tokens"]
        out["cache_creation_input_tokens"] = parsed["cache_creation_input_tokens"]
        out["cache_read_input_tokens"] = parsed["cache_read_input_tokens"]
        out["output_tokens"] = parsed["output_tokens"]
        out["cost_usd"] = parsed["cost_usd"]
        if out["exit_code"] == 0 and (parsed["is_error"] or parsed["parse_error"]):
            # The CLI exited cleanly but reported an error or produced
            # unparseable output: record a failure, never a fake success.
            out["exit_code"] = 1
            reason = "unparseable JSON on stdout" if parsed["parse_error"] else "is_error=true"
            out["stderr_tail"] = (out["stderr_tail"] + f"\n[sweep] claude {reason}").strip()
    else:
        out["text"] = proc.stdout or ""
        out["total_tokens"] = parse_codex_tokens(proc.stderr or "")
    return out
