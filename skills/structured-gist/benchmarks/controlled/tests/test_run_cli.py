"""run.py exit codes and gate wiring (tasks T018), per DC/runner-cli.md.

``run.main(argv)`` runs in process against a temporary git repository
(``SG_BENCH_ROOT``). Nothing here reaches a model: the conftest guard fails
the test on any attempt to spawn a model CLI or open a socket.
"""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

import run
from bench import prereg
from tests import prereg_fixture as fx

GATED = [
    ["verify-prereg"],
    ["estimate"],
    ["preflight"],
    ["preflight", "--canary"],
    ["preflight", "--judge-canary"],
    ["generate", "--confirm", "x"],
    ["judge", "--judge", "sol", "--confirm", "x"],
    ["judge", "--judge", "sol", "--confirm", "x"],
    ["judge", "--judge", "gemini", "--confirm", "x"],
    ["judge", "--judge", "openrouter", "--confirm", "x"],
    ["annotate", "--confirm", "x"],
    ["grade"],
    ["report"],
    ["all", "--confirm", "x"],
]

MODEL_CALLING = [
    ["generate"],
    ["judge", "--judge", "sol"],
    ["judge", "--judge", "sol"],
    ["judge", "--judge", "gemini"],
    ["judge", "--judge", "openrouter"],
    ["annotate"],
    ["all"],
]


@pytest.fixture
def root(tmp_path, monkeypatch):
    r = fx.make_root(tmp_path)
    monkeypatch.setenv("SG_BENCH_ROOT", str(r))
    return r


def _dirty(root):
    p = root / "PREREGISTRATION.md"
    p.write_bytes(p.read_bytes() + b"\nedit\n")


def test_exit_code_constants():
    assert (run.EXIT_OK, run.EXIT_ERROR, run.EXIT_USAGE, run.EXIT_GATE, run.EXIT_CONFIRM,
            run.EXIT_ISOLATION, run.EXIT_MODEL_POLICY, run.EXIT_QUOTA) == (0, 1, 2, 3, 4, 5, 6, 75)


def test_help_exits_zero(capsys):
    assert run.main(["--help"]) == 0
    out = capsys.readouterr().out
    for sub in ("prereg-hash", "verify-prereg", "build-items", "estimate", "preflight",
                "generate", "judge", "annotate", "grade", "report", "all"):
        assert sub in out


def test_help_as_a_script():
    # A real subprocess of this Python (not a model CLI).
    res = subprocess.run([sys.executable, str(run.__file__), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "prereg-hash" in res.stdout


@pytest.mark.parametrize("argv", [
    [],
    ["no-such-subcommand"],
    ["judge", "--confirm", "x"],
    ["judge", "--judge", "claude", "--confirm", "x"],
    ["generate", "--bogus"],
    ["build-items", "--run-id"],
])
def test_usage_errors_exit_2(root, argv):
    assert run.main(argv) == 2


def test_prereg_hash_prints_hash_without_gate(root, capsys):
    _dirty(root)
    assert run.main(["prereg-hash"]) == 0
    assert capsys.readouterr().out.strip() == fx.expected_prereg_sha256(root)


def test_prereg_hash_missing_files_is_an_error(tmp_path, monkeypatch):
    r = fx.make_root(tmp_path, with_prereg=False)
    monkeypatch.setenv("SG_BENCH_ROOT", str(r))
    assert run.main(["prereg-hash"]) == 1


@pytest.mark.parametrize("argv", GATED, ids=lambda a: " ".join(a))
def test_gated_subcommands_exit_3_on_dirty_prereg(root, argv, capsys):
    _dirty(root)
    assert run.main(argv) == 3
    assert "PREREGISTRATION.md" in capsys.readouterr().err


@pytest.mark.parametrize("argv", GATED, ids=lambda a: " ".join(a))
def test_gated_subcommands_exit_3_on_manifest_mismatch(root, argv):
    fx.write_manifest(root, "other-run", "0" * 64)
    assert run.main([*argv, "--run-id", "other-run"]) == 3


@pytest.mark.parametrize("argv", MODEL_CALLING, ids=lambda a: " ".join(a))
def test_model_calling_without_confirm_exits_4(root, argv):
    assert run.main(argv) == 4


@pytest.mark.parametrize("argv", MODEL_CALLING, ids=lambda a: " ".join(a))
def test_model_calling_with_unmatched_confirm_exits_4(root, argv):
    assert run.main([*argv, "--confirm", "0" * 64]) == 4


@pytest.mark.parametrize("flag", ["--canary", "--judge-canary"])
def test_canary_is_exempt_from_confirm(root, flag):
    # Exempt from --confirm (pre-registered); not implemented until its story.
    assert run.main(["preflight", flag]) == 2


@pytest.mark.parametrize("argv", [["estimate"], ["preflight"], ["grade"], ["report"]])
def test_unimplemented_subcommands_exit_2_after_gate(root, argv, capsys):
    assert run.main(argv) == 2
    assert "not implemented" in capsys.readouterr().err


def test_verify_prereg_ok(root):
    assert run.main(["verify-prereg"]) == 0


def test_verify_prereg_named_run_ids(root):
    fx.write_manifest(root, "a", prereg.prereg_sha256(root))
    fx.write_manifest(root, "b", "5" * 64)
    fx.commit(root.parent, "runs")
    assert run.main(["verify-prereg", "--run-id", "a"]) == 0
    assert run.main(["verify-prereg", "--run-id", "a", "--run-id", "b"]) == 3


def test_build_items_default_run_id(root, capsys):
    assert run.main(["build-items"]) == 0
    rid = "pr-" + fx.expected_prereg_sha256(root)[:12]
    out = root / "runs" / rid / "items.jsonl"
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 42
    assert json.loads(lines[0])["item"]["dataset"] == "qmsum"
    text = capsys.readouterr().out
    assert rid in text
    assert '"qmsum": 50' in text or "qmsum 50" in text


def test_build_items_is_not_gated(root):
    _dirty(root)
    assert run.main(["build-items", "--run-id", "t1"]) == 0


def test_build_items_without_prereg_needs_run_id(tmp_path, monkeypatch):
    r = fx.make_root(tmp_path, with_prereg=False)
    monkeypatch.setenv("SG_BENCH_ROOT", str(r))
    assert run.main(["build-items"]) == 2
    assert run.main(["build-items", "--run-id", "t0"]) == 0
    assert (r / "runs" / "t0" / "items.jsonl").is_file()


@pytest.mark.parametrize("dotted", ["corpus.corpus_manifest_sha256", "corpus.derived_manifest_sha256",
                                    "corpus.gold_relation_counts.qmsum"])
def test_build_items_refuses_corpus_mismatch(root, dotted):
    obj = fx.mutate(fx.make_prereg(root), dotted, 49 if dotted.endswith("qmsum") else "c" * 64)
    fx.write_prereg(root, obj)
    assert run.main(["build-items", "--run-id", "t2"]) == 3
    assert not (root / "runs" / "t2" / "items.jsonl").exists()


def test_build_items_is_deterministic(root):
    assert run.main(["build-items", "--run-id", "d1"]) == 0
    assert run.main(["build-items", "--run-id", "d2"]) == 0
    assert (root / "runs" / "d1" / "items.jsonl").read_bytes() == (root / "runs" / "d2" / "items.jsonl").read_bytes()


def test_default_run_id_used_by_gate(root):
    rid = "pr-" + fx.expected_prereg_sha256(root)[:12]
    fx.write_manifest(root, rid, "6" * 64)
    assert run.main(["grade"]) == 3


def test_no_calls_directory_is_created(root):
    for argv in (["build-items", "--run-id", "c1"], ["generate"], ["judge", "--judge", "sol"]):
        run.main(argv)
    assert not list(root.rglob("calls"))
