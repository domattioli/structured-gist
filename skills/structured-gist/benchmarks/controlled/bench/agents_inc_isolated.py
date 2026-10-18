#!/usr/bin/env python3
"""
Shim run with the agents-inc interpreter: one sol call in an isolated
CODEX_HOME (``run_codex(..., isolate_home=True)``), which symlinks auth.json
(never copied or read) and writes a one-line config.toml, so no MCP servers,
plugins or hooks config reach the judge. The ``agents-inc run`` CLI does not
expose this. Mirrors agents_inc/install/dispatch.py. Stdlib only; it must not
import the benchmark's own modules (it runs under another interpreter).

    python3.x agents_inc_isolated.py --model sol --effort medium --cwd DIR < prompt
"""
import argparse
import os
import sys
from pathlib import Path

DEFAULT_LAUNCHER = "/Users/domattioli/.local/bin/agents-inc"


def install_root() -> Path:
    env = os.environ.get("SG_BENCH_AGENTS_INC_ROOT")
    if env:
        return Path(env)
    launcher = os.environ.get("SG_BENCH_AGENTS_INC") or DEFAULT_LAUNCHER
    return Path(launcher).resolve().parents[1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--effort", required=True)
    ap.add_argument("--cwd", required=True)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(install_root()))
    from agents_inc.install.cli import _efforts, _paths
    from agents_inc.install.receipt import InstallReceipt
    from agents_inc.install.runtime import run_codex
    paths = _paths()
    receipt = InstallReceipt.load(paths.receipt)
    return run_codex(a.model, a.effort, Path(a.cwd), sys.stdin, receipt, _efforts(paths.current.resolve()),
                     no_tools=True, isolate_home=True)


if __name__ == "__main__":
    raise SystemExit(main())
