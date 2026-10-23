"""CLI tests for claim_list: --help, --version and a stdin round trip."""
import json
import os
import subprocess
import sys
from pathlib import Path

RENDER = Path(__file__).resolve().parent.parent / "render"
TESTS = Path(__file__).resolve().parent


def _run(args, stdin=""):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(RENDER), str(TESTS), env.get("PYTHONPATH", "")]
    )
    return subprocess.run(
        [sys.executable, "-m", "claim_list", *args],
        input=stdin, capture_output=True, text=True, env=env,
    )


def test_help_exits_zero():
    result = _run(["--help"])
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout


def test_version_exits_zero():
    result = _run(["--version"])
    assert result.returncode == 0, result.stderr
    assert "0.9.1" in result.stdout


def test_stdin_round_trip_one_record():
    outline = "```text\n- Concept\n    ↪ One full explanation sentence here.\n```\n"
    result = _run([], stdin=outline)
    assert result.returncode == 0, result.stderr
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    assert len(lines) == 1, result.stdout
    json.loads(lines[0])
