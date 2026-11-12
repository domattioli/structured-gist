"""
Offline tests for the model-effort sweep harness.

No test starts a real model process: every backend call goes through a fake
runner or a fake call function, and every file is written under pytest's
tmp_path (never the real runs/, judged/, or results/ folders).
"""
import inspect
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

SWEEP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SWEEP))

import backends  # noqa: E402
import generate  # noqa: E402
import judge  # noqa: E402
import plot  # noqa: E402
import prompts  # noqa: E402
import score  # noqa: E402

CASE = "cause-chain-reversal"


# ------------------------------------------------------------------ fixtures

@pytest.fixture
def cfg_path(tmp_path):
    """A copy of config.json with absolute paths and a temp codex_home."""
    real = generate.load_config(SWEEP / "config.json")
    real["codex_home"] = str(tmp_path / "codex-home")
    p = tmp_path / "config.json"
    p.write_text(json.dumps(real), encoding="utf-8")
    return p


@pytest.fixture
def cfg(cfg_path):
    return generate.load_config(cfg_path)


@pytest.fixture
def case(cfg):
    return next(c for c in generate.load_cases(cfg) if c["id"] == CASE)


@pytest.fixture
def gold(case):
    return json.loads((case["dir"] / "gold.json").read_text(encoding="utf-8"))


def fake_result(text, exit_code=0, **kw):
    r = {"text": text, "raw_stdout": text, "input_tokens": 10, "output_tokens": 20,
         "cost_usd": 0.001, "duration_s": 0.01, "exit_code": exit_code, "stderr_tail": ""}
    r.update(kw)
    return r


class Recorder:
    def __init__(self, reply):
        self.reply = reply
        self.calls = []

    def __call__(self, backend, model, effort, prompt, cwd, **kw):
        assert not Path(cwd).resolve().is_relative_to(backends.REPO_ROOT)
        assert list(Path(cwd).iterdir()) == []
        self.calls.append({"backend": backend, "model": model, "effort": effort, "prompt": prompt})
        return self.reply(backend, model, effort, prompt) if callable(self.reply) else self.reply


def full_verdict(gold, status="retained", halluc=None):
    return {
        "facts": {f["id"]: {"status": status, "evidence": "q"} for f in gold["facts"]},
        "relations": {r["id"]: {"status": "retained", "evidence": "q"} for r in gold["relations"]},
        "questions": {q["id"]: {"verdict": "correct", "answer_given": "a"} for q in gold["questions"]},
        "hallucinations": halluc or [],
    }


# ------------------------------------------------------------------ config

def test_config_matrix_shape(cfg):
    assert [g["name"] for g in cfg["generators"]] == ["haiku", "sonnet", "opus", "luna", "terra", "sol"]
    assert cfg["efforts"] == ["low", "medium", "high"]
    assert [j["name"] for j in cfg["judges"]] == ["fable", "astra"]
    assert cfg["condition"] == {"caveman": "off"}
    assert cfg["granularity"] == "standard" and cfg["mode"] == "block"
    assert len(generate.load_cases(cfg)) == 10


# ------------------------------------------------------------------ prompts

def test_generation_prompt_contains_skill_and_source():
    p = prompts.generation_prompt("SKILL-BODY-XYZ", "SOURCE-BODY-ABC")
    assert "SKILL-BODY-XYZ" in p and "SOURCE-BODY-ABC" in p
    assert "standard" in p and "block" in p and "```text" in p
    assert p.index("SKILL-BODY-XYZ") < p.index("SOURCE-BODY-ABC")


def test_judge_prompt_is_model_blind_and_source_blind(cfg, case, gold):
    assert list(inspect.signature(prompts.judge_prompt).parameters) == ["gold", "rendering"]
    rendering = "```text\n- Outage\n    ▸ Start\n        ↪ The outage began at 14:02.\n```\n"
    p = prompts.judge_prompt(gold, rendering)
    for g in cfg["generators"]:
        for name in (g["name"], g["model"]):
            assert not re.search(rf"\b{re.escape(name)}\b", p, re.IGNORECASE), name
    for f in gold["facts"]:
        assert f"{f['id']}: {f['text']}" in p
    for q in gold["questions"]:
        assert q["gold_answer"] in p
    source = (case["dir"] / "source.md").read_text(encoding="utf-8")
    assert source.strip() not in p
    assert "The checkout outage started at 14:02" not in p  # gold source_quote stays out
    assert "source_supported" not in p


def test_support_prompt_lists_claims_with_source():
    p = prompts.support_prompt("SRC TEXT", ["claim one", "claim two"])
    assert "SRC TEXT" in p and "1. claim one" in p and "2. claim two" in p
    assert "source_supported" in p


def test_extract_outline():
    reply = "Here you go:\n```text\n- A\n    ▸ B\n```\ntrailing\n```text\n- second\n```"
    assert prompts.extract_outline(reply) == "```text\n- A\n    ▸ B\n```\n"
    assert prompts.extract_outline("  - bare outline\n") == "- bare outline\n"


def test_extract_json():
    assert prompts.extract_json('{"a": 1}') == {"a": 1}
    assert prompts.extract_json('```json\n{"a": [1, 2]}\n```') == {"a": [1, 2]}
    assert prompts.extract_json('Sure.\n[{"claim": "x"}]\nDone.') == [{"claim": "x"}]
    with pytest.raises(ValueError):
        prompts.extract_json("not json at all")
    with pytest.raises(ValueError):
        prompts.extract_json("")


# ------------------------------------------------------------------ backends

class FakeRunner:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout, self.stderr, self.returncode = stdout, stderr, returncode
        self.calls = []

    def __call__(self, argv, **kw):
        self.calls.append((argv, kw))
        return subprocess.CompletedProcess(argv, self.returncode, self.stdout, self.stderr)


def test_claude_argv_and_parse(tmp_path):
    out = json.dumps({"result": "```text\n- A\n```", "is_error": False, "total_cost_usd": 0.02,
                      "usage": {"input_tokens": 1200, "output_tokens": 300}})
    runner = FakeRunner(stdout=out)
    r = backends.call("claude", "claude-opus-5-5", "high", "PROMPT", tmp_path, runner=runner)
    argv, kw = runner.calls[0]
    assert argv[:2] == ["claude", "-p"]
    i = argv.index("--tools")
    assert argv[i + 1] == ""
    assert argv[argv.index("--setting-sources") + 1] == ""
    for flag in ("--strict-mcp-config", "--no-session-persistence"):
        assert flag in argv
    assert argv[argv.index("--effort") + 1] == "high"
    assert kw["input"] == "PROMPT" and kw["cwd"] == str(tmp_path)
    assert r["text"] == "```text\n- A\n```" and r["exit_code"] == 0
    assert (r["input_tokens"], r["output_tokens"], r["cost_usd"]) == (1200, 300, 0.02)
    assert (r["cache_creation_input_tokens"], r["cache_read_input_tokens"]) == (0, 0)


def test_claude_input_tokens_include_cache(tmp_path):
    usage = {"input_tokens": 9, "cache_creation_input_tokens": 4000,
             "cache_read_input_tokens": 12000, "output_tokens": 300}
    out = json.dumps({"result": "x", "is_error": False, "usage": usage})
    r = backends.call("claude", "m", "low", "P", tmp_path, runner=FakeRunner(stdout=out))
    assert r["input_tokens"] == 16009
    assert r["cache_creation_input_tokens"] == 4000 and r["cache_read_input_tokens"] == 12000
    # no usage block at all: unknown stays None, never 0
    out = json.dumps({"result": "x", "is_error": False})
    r = backends.call("claude", "m", "low", "P", tmp_path, runner=FakeRunner(stdout=out))
    assert r["input_tokens"] is None
    assert r["cache_creation_input_tokens"] is None and r["cache_read_input_tokens"] is None


def test_claude_is_error_is_a_failure(tmp_path):
    runner = FakeRunner(stdout=json.dumps({"result": "boom", "is_error": True}))
    r = backends.call("claude", "m", "low", "P", tmp_path, runner=runner)
    assert r["exit_code"] != 0
    r = backends.call("claude", "m", "low", "P", tmp_path, runner=FakeRunner(stdout="not json"))
    assert r["exit_code"] != 0 and r["text"] == "" and r["input_tokens"] is None


def test_codex_refused_without_auth(tmp_path):
    home = tmp_path / "codex-home"
    home.mkdir()
    runner = FakeRunner(stdout="x")
    with pytest.raises(backends.CodexAuthMissing):
        backends.call("codex", "sol", "low", "P", tmp_path, codex_home=str(home), runner=runner)
    assert runner.calls == []


def test_codex_call_env_and_tokens(tmp_path):
    home = tmp_path / "codex-home"
    home.mkdir()
    (home / "auth.json").touch()  # a fake, empty placeholder for the existence check
    work = tmp_path / "work"
    work.mkdir()
    runner = FakeRunner(stdout="REPLY", stderr="stuff\ntokens used\n12,345\n")
    r = backends.call("codex", "terra", "medium", "P", work, codex_home=str(home), runner=runner)
    argv, kw = runner.calls[0]
    assert argv == ["agents-inc", "run", "--model", "terra", "--effort", "medium", "--cwd", str(work)]
    assert kw["env"]["CODEX_HOME"] == str(home)
    assert r["text"] == "REPLY" and r["total_tokens"] == 12345
    assert r["input_tokens"] is None and r["output_tokens"] is None and r["cost_usd"] is None
    r = backends.call("codex", "terra", "medium", "P", work, codex_home=str(home),
                      runner=FakeRunner(stdout="REPLY", stderr="no usage here"))
    assert r["total_tokens"] is None


def test_cwd_inside_repo_refused():
    runner = FakeRunner()
    with pytest.raises(backends.BackendError):
        backends.call("claude", "m", "low", "P", SWEEP, runner=runner)
    assert runner.calls == []


# ------------------------------------------------------------------ generate

def test_generate_dry_run_makes_no_calls(cfg_path, tmp_path, capsys):
    def boom(*a, **k):
        raise AssertionError("dry run must not call a backend")
    rc = generate.main(["--dry-run", "--config", str(cfg_path), "--root", str(tmp_path)], call_fn=boom)
    assert rc == 0
    out = capsys.readouterr().out
    assert "= 180 cells" in out and "no model calls made" in out
    assert not (tmp_path / "runs").exists()


def test_generate_writes_and_resumes(cfg_path, tmp_path):
    rec = Recorder(fake_result("intro\n```text\n- Outage\n    ▸ Start\n        ↪ 14:02.\n```\n"))
    args = ["--config", str(cfg_path), "--root", str(tmp_path), "--only-case", CASE,
            "--only-model", "haiku", "--only-effort", "low"]
    assert generate.main(args, call_fn=rec) == 0
    assert len(rec.calls) == 1
    d = tmp_path / "runs" / CASE / "haiku-low"
    assert (d / "standard.md").read_text(encoding="utf-8").startswith("```text\n- Outage")
    assert "intro" in (d / "raw.txt").read_text(encoding="utf-8")
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    assert meta["exit_code"] == 0 and meta["model"] == "claude-haiku-4-5-20251001"
    assert meta["condition"] == {"caveman": "off"} and len(meta["prompt_sha256"]) == 64
    assert len(meta["skill_sha256"]) == 64 and meta["finished_utc"].endswith("Z")
    assert "cache_read_input_tokens" in meta and "cache_creation_input_tokens" in meta
    assert generate.main(args, call_fn=rec) == 0
    assert len(rec.calls) == 1  # resumed: cell skipped


def test_generate_failure_recorded_and_retried(cfg_path, tmp_path):
    rec = Recorder(fake_result("", exit_code=3, stderr_tail="bad"))
    args = ["--config", str(cfg_path), "--root", str(tmp_path), "--only-case", CASE,
            "--only-model", "sonnet", "--only-effort", "high"]
    assert generate.main(args, call_fn=rec) == 1
    d = tmp_path / "runs" / CASE / "sonnet-high"
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    assert meta["exit_code"] == 3 and meta["stderr_tail"] == "bad"
    assert not (d / "standard.md").exists()
    generate.main(args, call_fn=rec)
    assert len(rec.calls) == 2  # a failed cell is not skipped


def test_generate_limit(cfg_path, tmp_path):
    rec = Recorder(fake_result("```text\n- A\n```"))
    generate.main(["--config", str(cfg_path), "--root", str(tmp_path), "--only-model", "opus",
                   "--limit", "2"], call_fn=rec)
    assert len(rec.calls) == 2


def test_generate_refuses_codex_without_auth(cfg_path, tmp_path):
    rec = Recorder(fake_result("x"))
    rc = generate.main(["--config", str(cfg_path), "--root", str(tmp_path), "--only-model", "sol",
                        "--only-case", CASE], call_fn=rec)
    assert rc == 2 and rec.calls == []


# ------------------------------------------------------------------ judge

def make_run(root, case_id="cause-chain-reversal", cell="haiku-low"):
    d = Path(root) / "runs" / case_id / cell
    d.mkdir(parents=True)
    (d / "standard.md").write_text("```text\n- Outage\n    ▸ Start\n        ↪ 14:02.\n```\n", encoding="utf-8")
    (d / "meta.json").write_text(json.dumps({"exit_code": 0, "output_tokens": 50}), encoding="utf-8")
    return d


def test_judge_two_passes_merge_and_model_blind(cfg_path, tmp_path, gold):
    make_run(tmp_path)

    def reply(backend, model, effort, prompt):
        if prompt.startswith(prompts.JUDGE_INSTRUCTION):
            v = full_verdict(gold, halluc=[{"claim": "the outage lasted forever", "note": "n"}])
            return fake_result("```json\n" + json.dumps(v) + "\n```")
        return fake_result(json.dumps([{"claim": "the outage lasted forever",
                                         "source_supported": False, "quote": ""}]))
    rec = Recorder(reply)
    rc = judge.main(["--config", str(cfg_path), "--root", str(tmp_path), "--only-judge", "fable"], call_fn=rec)
    assert rc == 0 and len(rec.calls) == 2
    for c in rec.calls:
        assert c["model"] == "claude-fable-5-1" and c["effort"] == "medium"
        assert "haiku" not in c["prompt"].lower()
    out = json.loads((tmp_path / "judged" / "fable" / CASE / "haiku-low.json").read_text(encoding="utf-8"))
    assert out["hallucinations"][0]["source_supported"] is False
    assert out["_meta"]["pass2"] == "done"
    judge.main(["--config", str(cfg_path), "--root", str(tmp_path), "--only-judge", "fable"], call_fn=rec)
    assert len(rec.calls) == 2  # resumed


def test_judge_invalid_json_retries_once_then_error_file(cfg_path, tmp_path):
    make_run(tmp_path)
    rec = Recorder(fake_result("I think it is fine."))
    rc = judge.main(["--config", str(cfg_path), "--root", str(tmp_path), "--only-judge", "fable"], call_fn=rec)
    assert rc == 1 and len(rec.calls) == 2
    jdir = tmp_path / "judged" / "fable" / CASE
    assert not (jdir / "haiku-low.json").exists()
    err = json.loads((jdir / "haiku-low.error.json").read_text(encoding="utf-8"))
    assert err["pass"] == 1 and len(err["attempts"]) == 2


def test_judge_rejects_verdict_missing_gold_ids(gold):
    v = full_verdict(gold)
    del v["facts"][gold["facts"][0]["id"]]
    assert judge.validate_verdict(v, gold)
    assert judge.validate_verdict(full_verdict(gold), gold) == []


def test_judge_dry_run(cfg_path, tmp_path, capsys):
    make_run(tmp_path)
    def boom(*a, **k):
        raise AssertionError("dry run must not call a backend")
    assert judge.main(["--dry-run", "--config", str(cfg_path), "--root", str(tmp_path)], call_fn=boom) == 0
    assert "judge items: 2" in capsys.readouterr().out


# ------------------------------------------------------------------ score

MINI_GOLD = {
    "facts": [{"id": "f1", "text": "fact one", "weight": 1}, {"id": "f2", "text": "fact two", "weight": 3}],
    "relations": [{"id": "r1", "text": "rel one"}],
    "questions": [{"id": "q1", "question": "Q?", "gold_answer": "A"}],
}


def mini(f1="retained", r1="retained", q1="correct", halluc=None):
    return {"facts": {"f1": {"status": f1, "evidence": "e1"}, "f2": {"status": "retained", "evidence": "e2"}},
            "relations": {"r1": {"status": r1, "evidence": "er"}},
            "questions": {"q1": {"verdict": q1, "answer_given": "A"}},
            "hallucinations": halluc or []}


def test_resolve_agreement():
    res, dis = score.resolve(MINI_GOLD, mini(), mini(), {})
    assert dis == [] and res["unresolved_count"] == 0
    assert res["task_weighted_fact_retention"] == 1.0


def test_resolve_unresolved_is_mean():
    res, dis = score.resolve(MINI_GOLD, mini(), mini(f1="omitted", q1="wrong"), {})
    assert {d["item_id"] for d in dis} == {"f1", "q1"}
    assert sorted(res["unresolved_items"]) == ["f1", "q1"]
    assert res["task_weighted_fact_retention"] == 0.875  # mean of 1.0 and 0.75
    assert res["recoverability"] == 0.5


def test_resolve_tiebreak():
    res, dis = score.resolve(MINI_GOLD, mini(), mini(f1="omitted", r1="lost"), {"f1": "omitted", "r1": "retained"})
    assert res["unresolved_count"] == 0 and sorted(res["tiebroken_items"]) == ["f1", "r1"]
    assert res["task_weighted_fact_retention"] == 0.75
    assert res["relation_retention"] == 1.0
    with pytest.raises(ValueError):
        score.resolve(MINI_GOLD, mini(), mini(f1="omitted"), {"f1": "maybe"})


def test_resolve_source_supported_disagreement():
    ha = [{"claim": "The sky is green.", "note": "", "source_supported": False}]
    hb = [{"claim": "the sky is green", "note": "", "source_supported": True}]
    res, dis = score.resolve(MINI_GOLD, mini(halluc=ha), mini(halluc=hb), {})
    assert len(dis) == 1 and dis[0]["kind"] == "hallucinations"
    assert res["unsupported_claim_count"] == 0.5 and res["unresolved_count"] == 1
    res, _ = score.resolve(MINI_GOLD, mini(halluc=ha), mini(halluc=hb), {dis[0]["item_id"]: "false"})
    assert res["unsupported_claim_count"] == 1.0 and res["unresolved_count"] == 0


def test_score_build_end_to_end(cfg, tmp_path, gold):
    make_run(tmp_path)
    for j, status in (("fable", "retained"), ("astra", "partial")):
        p = judge.judged_path(tmp_path, j, CASE, "haiku-low")
        p.parent.mkdir(parents=True)
        v = full_verdict(gold, status=status)
        v["_meta"] = {"pass2": "not_needed"}
        p.write_text(json.dumps(v), encoding="utf-8")
    cases = generate.load_cases(cfg)
    sweep = score.build(cfg, cases, tmp_path)
    cell = sweep["resolved"][CASE]["haiku-low"]
    assert cell["unresolved_count"] == len(gold["facts"])
    assert cell["task_weighted_fact_retention"] == 0.75
    assert cell["lint_violations"] is not None and cell["output_tokens"] == 50
    agg = sweep["aggregate"]["resolved"]["haiku"]["low"]
    assert agg["n_cases"] == 1 and agg["task_weighted_fact_retention"]["mean"] == 0.75
    assert sweep["unresolved"]["total"] == len(gold["facts"])
    dis_md = (tmp_path / "results" / "DISAGREEMENTS.md").read_text(encoding="utf-8")
    assert "| case | cell | item id | gold text | fable verdict + evidence | astra verdict + evidence | tiebreak |" in dis_md
    tb = json.loads((tmp_path / "tiebreaks.json").read_text(encoding="utf-8"))
    assert set(tb[CASE]["haiku-low"].values()) == {None}
    assert (tmp_path / "results" / "SWEEP_SCORES.md").exists()
    # operator fills every tiebreak -> nothing unresolved, template kept as-is
    tb[CASE]["haiku-low"] = {k: "retained" for k in tb[CASE]["haiku-low"]}
    (tmp_path / "tiebreaks.json").write_text(json.dumps(tb), encoding="utf-8")
    sweep = score.build(cfg, cases, tmp_path)
    assert sweep["unresolved"]["total"] == 0
    assert sweep["resolved"][CASE]["haiku-low"]["task_weighted_fact_retention"] == 1.0


# ------------------------------------------------------------------ plot

def sample_sweep():
    gens = ["haiku", "sonnet", "opus", "luna", "terra", "sol"]
    efforts = ["low", "medium", "high"]
    agg = {}
    for i, g in enumerate(gens):
        for k, e in enumerate(efforts):
            base = 0.5 + 0.05 * i + 0.03 * k
            m = {}
            for metric, _, _ in plot.METRICS:
                scale = 1 if metric in plot.UNIT_RANGE else 100
                m[metric] = {"mean": round(min(base, 1) * scale, 4), "min": round((base - 0.1) * scale, 4),
                             "max": round(min(base + 0.05, 1) * scale, 4), "n": 9}
            if g == "sol" and e == "medium":
                m["output_tokens"] = {"mean": None, "min": None, "max": None, "n": 0}
            agg.setdefault(g, {})[e] = m
    return {"generators": gens, "efforts": efforts, "judges": ["fable", "astra"], "n_cases": 9,
            "generator_models": {g: g for g in gens}, "aggregate": {"resolved": agg},
            "unresolved": {"total": 3, "disagreements": 5, "tiebroken": 2, "by_cell": {}}}


def test_plot_deterministic_and_valid_xml(tmp_path):
    s = sample_sweep()
    a = plot.write_plots(s, tmp_path / "a")
    b = plot.write_plots(json.loads(json.dumps(s)), tmp_path / "b")
    assert len(a) == 9 and (tmp_path / "a" / "overview.svg").exists()
    assert (tmp_path / "a" / "total_tokens.svg").exists()
    for pa, pb in zip(a, b):
        assert pa.read_bytes() == pb.read_bytes()
        root = ET.parse(pa).getroot()
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        text = pa.read_text(encoding="utf-8")
        assert "prefers-color-scheme: dark" in text and "var(--c5)" in text
        assert "n = 9 cases" in text and "unresolved" in text


def test_plot_handles_empty_sweep(tmp_path):
    s = sample_sweep()
    s["aggregate"] = {"resolved": {}}
    for p in plot.write_plots(s, tmp_path):
        ET.parse(p)


def _fill_rules(svg_text):
    """(tag or '', set of classes) for every CSS rule that sets a non-none fill."""
    style = re.search(r"<style>(.*?)</style>", svg_text, re.DOTALL).group(1)
    rules = []
    for sel, decls in re.findall(r"([^{}]+)\{([^{}]*)\}", style):
        fills = re.findall(r"fill\s*:\s*([^;]+)", decls)
        if not fills or all(f.strip() == "none" for f in fills):
            continue
        for part in sel.split(","):
            part = part.strip()
            m = re.match(r"^([a-zA-Z]*)((?:\.[\w-]+)*)$", part)
            assert m, f"unexpected selector {part!r}"
            rules.append((m.group(1), set(re.findall(r"\.([\w-]+)", m.group(2)))))
    return rules


def test_plot_lines_whiskers_open_never_filled(tmp_path):
    for p in plot.write_plots(sample_sweep(), tmp_path):
        text = p.read_text(encoding="utf-8")
        rules = _fill_rules(text)
        checked = 0
        for el in ET.parse(p).getroot().iter():
            classes = set(el.get("class", "").split())
            if not classes & {"line", "whisker", "open"}:
                continue
            checked += 1
            assert el.get("fill") == "none", (p.name, el.attrib)
            tag = el.tag.split("}")[-1]
            for rtag, rclasses in rules:
                matches = (not rtag or rtag == tag) and rclasses <= classes
                assert not matches, (p.name, el.attrib, rtag, rclasses)
        assert checked > 0
        # markers stay filled
        assert re.search(r"\.mk\.s0\{fill:var\(--c0\)\}", text)


def test_score_deterministic_metrics_cover_unjudged_runs(cfg, tmp_path, gold):
    other = "migration-tristate"
    make_run(tmp_path)  # judged by both judges below
    d = make_run(tmp_path, case_id=other)  # never judged
    (d / "meta.json").write_text(json.dumps({"exit_code": 0, "input_tokens": 100, "output_tokens": 50}),
                                 encoding="utf-8")
    for j in ("fable", "astra"):
        p = judge.judged_path(tmp_path, j, CASE, "haiku-low")
        p.parent.mkdir(parents=True)
        v = full_verdict(gold)
        v["_meta"] = {"pass2": "not_needed"}
        p.write_text(json.dumps(v), encoding="utf-8")
    sweep = score.build(cfg, generate.load_cases(cfg), tmp_path)
    assert set(sweep["deterministic"]) == {CASE, other}
    assert sweep["deterministic"][other]["haiku-low"]["total_tokens"] == 150
    for view in ("fable", "astra", "resolved"):
        agg = sweep["aggregate"][view]["haiku"]["low"]
        assert agg["n_cases"] == 2 and agg["n_judged"] == 1
        for m in ("lint_violations", "reduction_pct", "output_words", "output_tokens"):
            assert agg[m]["n"] == 2, (view, m)
        assert agg["total_tokens"]["n"] == 1  # the judged run's meta has no input_tokens
        assert agg["task_weighted_fact_retention"]["n"] == 1
    md = (tmp_path / "results" / "SWEEP_SCORES.md").read_text(encoding="utf-8")
    assert "(n=2)" in md and "(n=1)" in md


def test_plot_caption_reports_real_n(tmp_path):
    s = sample_sweep()
    text = plot.metric_svg(s, "resolved", "relation_retention", "R", "y")
    assert "n = 9 cases per point" in text
    s["aggregate"]["resolved"]["haiku"]["low"]["relation_retention"]["n"] = 7
    text = plot.metric_svg(s, "resolved", "relation_retention", "R", "y")
    assert "n = 7-9 cases per point" in text and "n = 9 cases per point" not in text
    assert "n = 7-9 cases per point" in plot.overview_svg(s, "resolved")
    s["aggregate"] = {"resolved": {}}
    assert "No scored points yet." in plot.metric_svg(s, "resolved", "relation_retention", "R", "y")

