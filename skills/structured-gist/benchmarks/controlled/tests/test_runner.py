"""Runner stages with fake backends only (T026, T029, T030a, canaries).

The adapters' ``RUNNER`` hooks point at ``tests.fakes``; the conftest guard
still blocks any real CLI or socket. Everything is written under tmp_path.
"""
from __future__ import annotations

import json

import pytest

import run
from bench import generate as gen, items as items_mod, judge as jd, pacing, pipeline, records
from tests import prereg_fixture as fx
from tests.fakes import FakeAgentsInc, FakeClaude

THREE = ["--dataset", "hotpotqa", "--case", "hotpotqa-01", "--case", "hotpotqa-02", "--case", "hotpotqa-03"]
ONE = ["--dataset", "hotpotqa", "--case", "hotpotqa-01"]


@pytest.fixture
def root(tmp_path, monkeypatch):
    r = fx.make_root(tmp_path)
    monkeypatch.setenv("SG_BENCH_ROOT", str(r))
    return r


@pytest.fixture
def fakes(monkeypatch, tmp_path):
    c, a = FakeClaude(), FakeAgentsInc()
    monkeypatch.setattr(gen, "RUNNER", c)
    monkeypatch.setattr(jd, "RUNNER", a)
    monkeypatch.setenv("SG_BENCH_CLAUDE_BIN", "/fake/claude")
    monkeypatch.setenv("SG_BENCH_AGENTS_INC", "/fake/agents-inc")
    monkeypatch.setenv("SG_BENCH_AGENTS_INC_PYTHON", "/fake/python3.14")
    monkeypatch.setenv("SG_BENCH_CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))
    return c, a


def repin(root, **muts):
    obj = fx.make_prereg(root)
    for k, v in muts.items():
        obj = fx.mutate(obj, k.replace("__", "."), v)
    fx.write_prereg(root, obj)
    fx.commit(root.parent, "repin")


def est(root, rid, scope, capsys=None):
    assert run.main(["estimate", "--run-id", rid, *scope]) == 0
    return records.read_json(root / "runs" / rid / "estimate.json")["estimate_sha"]


def full(root, rid, scope):
    sha = est(root, rid, scope)
    assert run.main(["generate", "--run-id", rid, "--confirm", sha, *scope]) == 0
    return sha


# ---------------------------------------------------------------- estimate

def test_estimate_is_deterministic(root, capsys):
    s1 = est(root, "e1", THREE)
    b1 = (root / "runs" / "e1" / "estimate.json").read_bytes()
    s2 = est(root, "e1", THREE)
    b2 = (root / "runs" / "e1" / "estimate.json").read_bytes()
    assert s1 == s2 and b1 == b2
    f = json.loads(b1)
    assert f["per_backend"]["anthropic"]["calls"] == 9
    assert f["per_backend"]["openai"]["calls"] == 15
    assert f["within_ceiling"] is True
    assert "estimate_sha" in capsys.readouterr().out
    body = {k: v for k, v in f.items() if k not in ("estimate_sha", "run_id")}
    assert not any("time" in k or k.endswith("_at") for k in body)


def test_estimate_sha_covers_scope(root):
    assert est(root, "e2", ONE) != est(root, "e3", THREE)


def test_estimate_missing_keys_exit_3(root, capsys):
    obj = fx.delete(fx.make_prereg(root), "cost.estimate_params")
    fx.write_prereg(root, obj)
    fx.commit(root.parent, "no params")
    assert run.main(["estimate", "--run-id", "e4"]) == 3
    assert "estimate_params" in capsys.readouterr().err


def test_dry_run_scope_uses_prereg_cases(root):
    est(root, "dryrun-abc", [])
    f = records.read_json(root / "runs" / "dryrun-abc" / "estimate.json")
    assert f["scope"]["cases"] == ["hotpotqa/hotpotqa-01", "qasper/qasper-01", "qmsum/qmsum-01"]


# ---------------------------------------------------------------- confirm

@pytest.mark.parametrize("cmd", ["generate", "judge", "all"])
def test_missing_estimate_file_exits_4(root, fakes, cmd):
    argv = [cmd, "--run-id", "c1", "--confirm", "0" * 64]
    if cmd == "judge":
        argv += ["--judge", "sol"]
    assert run.main(argv) == 4
    assert not list(root.rglob("calls"))


def test_wrong_confirm_exits_4(root, fakes):
    est(root, "c2", ONE)
    assert run.main(["generate", "--run-id", "c2", "--confirm", "1" * 64, *ONE]) == 4
    assert not (root / "runs" / "c2" / "calls").exists()
    assert fakes[0].calls == []


def test_over_ceiling_exits_4(root, fakes):
    repin(root, cost__ceiling_paid_tokens=10)
    sha = est(root, "c3", ONE)
    assert run.main(["generate", "--run-id", "c3", "--confirm", sha, *ONE]) == 4
    assert fakes[0].calls == []


def test_scope_change_after_estimate_exits_4(root, fakes):
    sha = est(root, "c4", ONE)
    assert run.main(["generate", "--run-id", "c4", "--confirm", sha, *THREE]) == 4


# ---------------------------------------------------------------- generate

def test_generate_writes_valid_samples_and_calls(root, fakes):
    claude, _ = fakes
    full(root, "g1", THREE)
    rd = root / "runs" / "g1"
    samples = records.read_jsonl(rd / "samples.jsonl")
    assert len(samples) == 15
    for s in samples:
        records.validate_or_raise(s, "Sample")
    assert {s["method"] for s in samples} == {"skill", "plain_prose", "plain_bullets", "lead_n", "textrank"}
    assert len(claude.calls) == 9
    for c in claude.calls:
        a = c["argv"]
        assert a[0] == "/fake/claude" and "--fallback-model" not in a
        assert a[a.index("--tools") + 1] == ""
        assert c["env"]["CLAUDE_CONFIG_DIR"] == str(root.parent.parent / "cfg")
    recs = pipeline.read_calls(root, "g1")
    assert len(recs) == 9
    for r in recs:
        records.validate_or_raise(r, "CallRecord")
        assert r["purpose"] == "generate" and r["tokens"]["source"] == "reported"
    records.validate_or_raise(records.read_json(rd / "manifest.json"), "RunManifest")
    assert len(records.read_jsonl(rd / "items.jsonl")) == 42
    # Rerun is a pure cache hit.
    n = len(claude.calls)
    sha = records.read_json(rd / "estimate.json")["estimate_sha"]
    assert run.main(["generate", "--run-id", "g1", "--confirm", sha, *THREE]) == 0
    assert len(claude.calls) == n


def test_length_rule_trims_and_regenerates(root, fakes):
    claude, _ = fakes
    claude.plain_words = lambda lo, hi: hi + 50
    full(root, "g2", ONE)
    s = {x["method"]: x for x in records.read_jsonl(root / "runs" / "g2" / "samples.jsonl")}
    p = s["plain_prose"]
    assert p["words"] == p["band"][1]
    assert {"regenerated", "trimmed"} <= set(p["length_flags"])
    assert p["trim"]["words_before"] == p["band"][1] + 50
    assert len(p["call_keys"]) == 3  # 1 + max_regenerations
    assert len(claude.calls) == 1 + 3 + 3


def test_length_violation_when_too_short(root, fakes):
    claude, _ = fakes
    claude.plain_words = lambda lo, hi: 3
    full(root, "g3", ONE)
    s = {x["method"]: x for x in records.read_jsonl(root / "runs" / "g3" / "samples.jsonl")}
    assert "length_violation" in s["plain_bullets"]["length_flags"]


def test_model_policy_violation_exits_6(root, fakes):
    claude, _ = fakes
    claude.resolved = "claude-sonnet-4"
    sha = est(root, "m1", ONE)
    assert run.main(["generate", "--run-id", "m1", "--confirm", sha, *ONE]) == 6
    assert len(claude.calls) == 1
    rec = pipeline.read_calls(root, "m1")[0]
    assert rec["outcome"] == "model_policy_violation"


def test_adapter_flags_wrong_resolved_model():
    c = FakeClaude()
    c.resolved = "other-model"
    res = gen.invoke("s", "u", model="claude-opus-5-5", effort="medium", runner=c)
    assert res["outcome"] == "model_policy_violation"


def test_claude_error_and_quota_outcomes(monkeypatch, tmp_path):
    monkeypatch.setenv("SG_BENCH_CLAUDE_BIN", "/fake/claude")
    monkeypatch.setenv("SG_BENCH_CLAUDE_CONFIG_DIR", str(tmp_path / "cfg"))
    c = FakeClaude()
    c.is_error = True
    assert gen.invoke("s", "u", model="claude-opus-5-5", effort="medium", runner=c)["outcome"] == "error"
    c.fail_with = (1, "Error 429 rate limit")
    assert gen.invoke("s", "u", model="claude-opus-5-5", effort="medium", runner=c)["outcome"] == "quota_exhausted"


# ---------------------------------------------------------------- judge, grade, report

def _item_fact(item_id):
    it = next(i for i in items_mod.build_items() if i["item_id"] == item_id)
    return it["facts"][0]["text"]


def test_judge_failure_is_incomplete_and_excluded(root, fakes):
    claude, sol = fakes
    ftext = _item_fact("hotpotqa/hotpotqa-02")
    sol.fail_when = lambda p: ftext in p and p.rstrip().endswith("w59")
    sha = full(root, "j1", THREE)
    assert run.main(["judge", "--run-id", "j1", "--judge", "sol", "--confirm", sha]) == 0
    rd = root / "runs" / "j1"
    rows = records.read_jsonl(rd / "graders" / "judge_labels.sol.jsonl")
    assert len(rows) == 15
    bad = [r for r in rows if r["status"] == "incomplete"]
    assert [r["sample_id"] for r in bad] == ["hotpotqa/hotpotqa-02/skill"]
    for r in rows:
        records.validate_or_raise(r, "GraderResult")
    judge_calls = [r for r in pipeline.read_calls(root, "j1") if r["purpose"] == "judge"]
    # Identical texts share a cache key (plain_prose == plain_bullets here): 11 unique ok calls
    # plus three failed attempts on the failing sample.
    assert sorted(r["outcome"] for r in judge_calls) == ["malformed"] * 3 + ["ok"] * 11
    assert all(r["tokens"]["source"] == "estimated" for r in judge_calls)
    assert run.main(["grade", "--run-id", "j1"]) == 0
    assert run.main(["report", "--run-id", "j1"]) == 0
    res = records.read_json(rd / "results" / "hotpotqa.json")
    records.validate_or_raise(res, "DatasetResults")
    assert res["incomplete_cases"] == ["hotpotqa/hotpotqa-02"]
    assert res["cases_scored"] == ["hotpotqa/hotpotqa-01", "hotpotqa/hotpotqa-03"]
    assert all(m["fact_retention"]["n"] == 2 for m in res["methods"].values())
    assert "hotpotqa/hotpotqa-02" in (rd / "REPORT.md").read_text(encoding="utf-8")
    for g in (rd / "graders").glob("*.jsonl"):
        for r in records.read_jsonl(g):
            records.validate_or_raise(r, "GraderResult")
    # All retained: every control comparison is a zero difference.
    assert all(v["fact"]["mean_diff"] == 0 for v in res["verdicts"])


def test_all_runs_every_stage(root, fakes):
    sha = est(root, "a1", THREE)
    assert run.main(["all", "--run-id", "a1", "--confirm", sha, *THREE]) == 0
    rd = root / "runs" / "a1"
    assert (rd / "REPORT.md").is_file() and (rd / "results" / "hotpotqa.json").is_file()
    assert records.read_json(rd / "manifest.json")["state"] == "reported"
    res = records.read_json(rd / "results" / "hotpotqa.json")
    assert res["incomplete_cases"] == []
    assert {u["model_name"] for u in res["per_model_usage"]} >= {"claude-opus-5-5", "gpt-6.1-sol"}


def test_judge_quota_exits_75_keeps_records(root, fakes):
    _, sol = fakes
    sha = full(root, "q1", ONE)
    sol.quota_when = lambda p: True
    assert run.main(["judge", "--run-id", "q1", "--judge", "sol", "--confirm", sha]) == 75
    assert (root / "runs" / "q1" / "graders" / "judge_labels.sol.jsonl").is_file()
    assert any(r["outcome"] == "quota_exhausted" for r in pipeline.read_calls(root, "q1"))


def test_wrong_judge_slug_is_policy_violation(root, fakes):
    _, sol = fakes
    sol.slug = "gpt-5.6-mini"
    sha = full(root, "q2", ONE)
    assert run.main(["judge", "--run-id", "q2", "--judge", "sol", "--confirm", sha]) == 6


def test_free_judge_not_in_scope(root, fakes, capsys):
    sha = full(root, "q3", ONE)
    assert run.main(["judge", "--run-id", "q3", "--judge", "gemini", "--confirm", sha]) == 2
    assert "not in Phase 4 scope" in capsys.readouterr().err


def test_judge_requires_judge_flag(root, fakes):
    assert run.main(["judge", "--run-id", "q4", "--confirm", "x"]) == 2


def test_dry_run_grade_and_report_refused(root, fakes):
    assert run.main(["grade", "--run-id", "dryrun-abc"]) == 2
    assert run.main(["report", "--run-id", "dryrun-abc"]) == 2


# ---------------------------------------------------------------- pacing

def test_pacing_stops_and_resumes(root, fakes, monkeypatch, capsys, fake_clock):
    claude, _ = fakes
    monkeypatch.setattr(pacing, "now", fake_clock.now)
    repin(root, cost__window_budget__tokens_per_backend=1600)
    sha = est(root, "p1", ONE)
    capsys.readouterr()
    argv = ["generate", "--run-id", "p1", "--confirm", sha, *ONE]
    assert run.main(argv) == 75
    out = capsys.readouterr().out
    assert out.startswith("paced: anthropic reached 1600 tokens in the 5-hour window starting ")
    assert "rerun after" in out and "to resume from cache" in out
    assert len(claude.calls) == 2
    st = records.read_json(root / "runs" / "p1" / "pacing.json")
    assert st["anthropic"]["tokens"] == 1600
    # Same window: still paced, no new call.
    assert run.main(argv) == 75
    assert len(claude.calls) == 2
    fake_clock.advance(5 * 3600 + 1)
    assert run.main(argv) in (0, 75)
    # Cached calls were skipped: the first two keys are not repeated.
    keys = [r["key"] for r in pipeline.read_calls(root, "p1")]
    assert len(keys) == len(set(keys))
    assert len(claude.calls) > 2
    assert len(claude.calls) == len(keys)


def test_dry_run_is_not_paced(root, fakes):
    claude, _ = fakes
    repin(root, cost__window_budget__tokens_per_backend=1)
    sha = est(root, "dryrun-xyz", [])
    assert run.main(["generate", "--run-id", "dryrun-xyz", "--confirm", sha]) == 0
    assert len(claude.calls) == 9
    assert not (root / "runs" / "dryrun-xyz" / "pacing.json").exists()


# ---------------------------------------------------------------- canaries

def test_claude_canary_shape_and_overhead(root, fakes, capsys):
    assert run.main(["generate", "--canary"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert set(r) == {"backend", "sent_chars", "sent_tokens_chars4", "reported_input_tokens", "output_tokens",
                      "overhead", "raw_usage", "model_resolved"}
    assert r["backend"] == "anthropic" and r["reported_input_tokens"] == 700 and r["output_tokens"] == 100
    sent = len(gen.CANARY_SYSTEM) + len(gen.CANARY_USER)
    assert r["sent_chars"] == sent
    assert r["overhead"] == round(700 - sent / 4)
    assert [p for p in (root / "runs").glob("*") if p.name != ".gitkeep"] == []


def test_judge_canary_overhead_arithmetic(root, fakes, capsys):
    assert run.main(["judge", "--judge-canary"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["backend"] == "agents-inc-codex" and r["reported_total_tokens"] == 12345
    sent = len(jd.CANARY_PROMPT)
    assert r["sent_chars"] == sent and r["output_chars"] == 2
    assert r["overhead"] == 12345 - round(sent / 4) - round(2 / 4)
    assert r["model_resolved"] == "gpt-6.1-sol" and r["codex_home"] == "isolated"
    assert len(r["raw_stderr_tail"]) <= 2000


def test_judge_canary_colon_form_and_missing_count(root, fakes, capsys):
    _, sol = fakes
    sol.stderr = 'tokens used: 777\nagents-inc run: record {"model": "sol", "slug": "gpt-6.1-sol"}\n'
    assert run.main(["judge", "--judge-canary"]) == 0
    assert json.loads(capsys.readouterr().out)["reported_total_tokens"] == 777
    sol.stderr = 'agents-inc run: record {"model": "sol", "slug": "gpt-6.1-sol"}\n'
    assert run.main(["preflight", "--judge-canary"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["overhead"] is None and r["reported_total_tokens"] is None and "note" in r


def test_canary_out_file_and_runs_refusal(root, fakes, tmp_path, capsys):
    out = tmp_path / "out" / "c.json"
    assert run.main(["generate", "--canary", "--canary-out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["backend"] == "anthropic"
    assert run.main(["generate", "--canary", "--canary-out", str(root / "runs" / "x.json")]) == 2
    assert not (root / "runs" / "x.json").exists()


def test_judge_argv_uses_isolated_shim(root, fakes):
    _, sol = fakes
    run.main(["judge", "--judge-canary"])
    a = sol.calls[0]["argv"]
    assert a[0] == "/fake/python3.14" and a[1].endswith("bench/agents_inc_isolated.py")
    assert a[2:6] == ["--model", "sol", "--effort", "medium"]
    assert "run" not in a and "--no-tools" not in a
    assert "sgb-judge-" in a[a.index("--cwd") + 1]


def test_judge_slug_equal_passes(root, fakes):
    sha = full(root, "q4", ONE)
    assert run.main(["judge", "--run-id", "q4", "--judge", "sol", "--confirm", sha]) == 0


def test_missing_record_line_is_policy_violation(root, fakes):
    _, sol = fakes
    sol.stderr = "tokens used: 5\n"
    sha = full(root, "q5", ONE)
    assert run.main(["judge", "--run-id", "q5", "--judge", "sol", "--confirm", sha]) == 6


def test_fallback_median_is_per_dataset(root, monkeypatch):
    g = pipeline.Generator.__new__(pipeline.Generator)
    g.root = root
    itemsl = [
        {"item_id": "a/1", "dataset": "a", "source_words": 1000},
        {"item_id": "a/2", "dataset": "a", "source_words": 2000},
        {"item_id": "b/1", "dataset": "b", "source_words": 1000},
        {"item_id": "c/1", "dataset": "c", "source_words": 1000},
    ]
    words = {"a/1": 100, "a/2": 400, "b/1": 500}  # a ratios .1,.2 -> med .15 ; b .5 ; c has none

    def skill(it):
        ok = it["item_id"] in words
        return {"item_id": it["item_id"], "method": "skill", "status": "generated" if ok else "failed_generation",
                "words": words.get(it["item_id"], 0)}

    seen = {}
    g.skill = skill
    g.plain = lambda it, arm, n, nsrc: seen.setdefault(it["item_id"], (n, nsrc)) and {}
    g.baseline = lambda it, m, n, nsrc, stop: {}
    monkeypatch.setattr(pipeline.baselines, "load_stopwords", lambda p: set())
    monkeypatch.setattr(pipeline.est, "projected_n", lambda i: 300)
    items = [dict(i) for i in itemsl]
    # force a/2 failed so a's fallback uses a/1 ratio only, b/1 fine
    words.pop("a/2")
    g.run(items)
    assert seen["a/2"] == (round(2000 * 0.1), "fallback_median_ratio")
    assert seen["c/1"] == (300, "fallback_median_ratio")  # no successes in c: projection (300/1000 * 1000)
    assert seen["b/1"] == (500, "skill_sample")


def _bullets_fr022(root, rid):
    res = records.read_json(root / "runs" / rid / "results" / "hotpotqa.json")
    return next(v for v in res["verdicts"] if v["control"] == "plain_bullets")


def test_fr022_flag_follows_holm_not_verdict_label(root, fakes, monkeypatch):
    from bench import score
    sha = est(root, "f1", ONE)
    assert run.main(["all", "--run-id", "f1", "--confirm", sha, *ONE]) == 0
    v = _bullets_fr022(root, "f1")
    assert v["fr022_sentence"] is True  # zero difference: skill not ahead
    # skill significantly ahead on facts (Holm p < alpha): sentence off, even if the label is not the top one
    monkeypatch.setattr(score, "holm", lambda ps: [0.0] * len(ps))
    assert run.main(["grade", "--run-id", "f1"]) == 0
    assert run.main(["report", "--run-id", "f1"]) == 0
    v = _bullets_fr022(root, "f1")
    assert v["fr022_sentence"] is False
    assert "any gain here may come from list format" not in (root / "runs" / "f1" / "REPORT.md").read_text(encoding="utf-8")
