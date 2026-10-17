"""The pre-registration gate and SC-001 check (tasks T017, T025).

Every test except the live-file ones at the bottom runs in a temporary git
repository under ``tmp_path`` (see prereg_fixture.py). The real repository is
never written to.
"""
from __future__ import annotations

import hashlib
import json
import re

import pytest

from bench import prereg
from tests import prereg_fixture as fx


def _has(problems: list[str], *needles: str) -> bool:
    return any(all(n in p for n in needles) for p in problems)


# --------------------------------------------------------------------------
# Hash
# --------------------------------------------------------------------------

def test_hash_formula(tmp_path):
    root = fx.make_root(tmp_path)
    assert prereg.prereg_sha256(root) == fx.expected_prereg_sha256(root)


def test_hash_ignores_json_formatting_but_not_md_bytes(tmp_path):
    root = fx.make_root(tmp_path)
    before = prereg.prereg_sha256(root)
    obj = json.loads((root / "prereg.json").read_text(encoding="utf-8"))
    (root / "prereg.json").write_text(json.dumps(obj, separators=(",", ":")), encoding="utf-8")
    assert prereg.prereg_sha256(root) == before
    md = root / "PREREGISTRATION.md"
    md.write_bytes(md.read_bytes() + b"\n")
    assert prereg.prereg_sha256(root) != before


def test_hash_formula_by_hand():
    j = {"b": 1, "a": "é"}
    md = b"# x\n"
    want = hashlib.sha256(fx.canonical(j) + md).hexdigest()
    assert prereg.compute_sha256(j, md) == want


def test_committed_hash_reads_head(tmp_path):
    root = fx.make_root(tmp_path)
    committed = prereg.committed_prereg_sha256(root)
    assert committed == prereg.prereg_sha256(root)
    (root / "PREREGISTRATION.md").write_text("changed\n", encoding="utf-8")
    assert prereg.committed_prereg_sha256(root) == committed
    assert prereg.prereg_sha256(root) != committed


def test_default_run_id(tmp_path):
    root = fx.make_root(tmp_path)
    assert prereg.default_run_id(root) == "pr-" + fx.expected_prereg_sha256(root)[:12]


# --------------------------------------------------------------------------
# Gate (exit 3 conditions)
# --------------------------------------------------------------------------

def test_gate_passes_on_clean_committed_prereg(tmp_path):
    root = fx.make_root(tmp_path)
    assert prereg.gate(root) == []


@pytest.mark.parametrize("name", ["prereg.json", "PREREGISTRATION.md"])
def test_gate_refuses_uncommitted_change(tmp_path, name):
    root = fx.make_root(tmp_path)
    p = root / name
    p.write_bytes(p.read_bytes().replace(b"Text.", b"Text!", 1) if name.endswith(".md")
                  else fx.canonical({**json.loads(p.read_text()), "question": "changed?"}))
    assert _has(prereg.gate(root), name, "uncommitted")


@pytest.mark.parametrize("name", ["prereg.json", "PREREGISTRATION.md"])
def test_gate_refuses_staged_change(tmp_path, name):
    root = fx.make_root(tmp_path)
    p = root / name
    p.write_bytes(p.read_bytes() + b"\n")
    fx.git(root, "add", name)
    assert _has(prereg.gate(root), name, "uncommitted")


def test_gate_refuses_never_committed(tmp_path):
    root = fx.make_root(tmp_path, commit_all=False)
    problems = prereg.gate(root)
    assert _has(problems, "prereg.json", "never committed")
    assert _has(problems, "PREREGISTRATION.md", "never committed")


def test_gate_refuses_missing_files(tmp_path):
    root = fx.make_root(tmp_path, with_prereg=False)
    problems = prereg.gate(root)
    assert _has(problems, "prereg.json", "missing")
    assert _has(problems, "PREREGISTRATION.md", "missing")


def test_gate_refuses_placeholder_after_commit(tmp_path):
    root = fx.make_root(tmp_path)
    obj = fx.mutate(fx.make_prereg(root), "master_seed", "TODO")
    fx.write_prereg(root, obj)
    fx.commit(root, "placeholder")
    assert _has(prereg.gate(root), "master_seed", "placeholder")


def test_gate_refuses_manifest_with_other_hash(tmp_path):
    root = fx.make_root(tmp_path)
    fx.write_manifest(root, "r1", "0" * 64)
    assert _has(prereg.gate(root, run_id="r1"), "r1", "manifest")
    fx.write_manifest(root, "r2", prereg.prereg_sha256(root))
    assert prereg.gate(root, run_id="r2") == []
    # No manifest yet: nothing to compare, the gate passes.
    assert prereg.gate(root, run_id="r3") == []


def test_gate_refuses_consistency_problem(tmp_path):
    root = fx.make_root(tmp_path)
    (root / "prompts" / "judge.md").write_bytes(b"edited judge prompt\n")
    assert _has(prereg.gate(root), "judges.judge_prompt_sha256")


# --------------------------------------------------------------------------
# Required keys and placeholders
# --------------------------------------------------------------------------

def test_complete_prereg_has_no_key_or_placeholder_problems(tmp_path):
    root = fx.make_root(tmp_path)
    obj = fx.make_prereg(root)
    assert prereg.required_key_problems(obj) == []
    assert prereg.placeholder_problems(obj) == []


@pytest.mark.parametrize("dotted", [
    "version", "question", "master_seed", "corpus", "corpus.gold_relation_counts", "methods",
    "generator.model", "generator.effort", "generator.prompt_sha256.shared_user",
    "length.tolerance", "textrank.stopwords_sha256", "scores.combine_py_sha256", "win_rule.verdict_labels",
    "bootstrap.resamples", "judges.main.model", "judges.panel", "judges.subset_rule", "judges.judge_prompt_sha256",
    "judges.notice_sha256", "judges.retry_queue.attempt_limit", "agreement.threshold", "secondary.qmsum",
    "report.pooled", "testing_criteria", "slop.addendum_path", "cost.ceiling_paid_tokens",
])
def test_missing_required_key(tmp_path, dotted):
    root = fx.make_root(tmp_path)
    obj = fx.delete(fx.make_prereg(root), dotted)
    assert _has(prereg.required_key_problems(obj), dotted)


def test_panel_entry_needs_model(tmp_path):
    root = fx.make_root(tmp_path)
    obj = fx.delete(fx.make_prereg(root), "judges.panel.0.model")
    assert _has(prereg.required_key_problems(obj), "judges.panel[0]", "model")


def test_testing_criteria_entries_need_pass_threshold_key(tmp_path):
    root = fx.make_root(tmp_path)
    obj = fx.delete(fx.make_prereg(root), "testing_criteria.0.pass_threshold")
    assert _has(prereg.required_key_problems(obj), "testing_criteria[0]", "pass_threshold")


@pytest.mark.parametrize("dotted, value", [
    ("master_seed", "TODO"),
    ("question", "TODO: write the question"),
    ("generator.effort", None),
    ("generator.skill_md_sha256", "..."),
    ("corpus.gold_relation_counts.qmsum", None),
    ("cost.estimate_inputs", "<fill in>"),
])
def test_placeholder_detected(tmp_path, dotted, value):
    root = fx.make_root(tmp_path)
    obj = fx.mutate(fx.make_prereg(root), dotted, value)
    problems = prereg.placeholder_problems(obj)
    shown = re.sub(r"\.(\d+)(?=\.|$)", r"[\1]", dotted)
    assert _has(problems, shown), problems


@pytest.mark.parametrize("dotted", ["agreement.threshold", "testing_criteria.0.pass_threshold"])
def test_null_allowed_where_preregistered(tmp_path, dotted):
    root = fx.make_root(tmp_path)
    obj = fx.mutate(fx.make_prereg(root), dotted, None)
    assert prereg.placeholder_problems(obj) == []


def test_angle_text_inside_a_sentence_is_not_a_placeholder(tmp_path):
    root = fx.make_root(tmp_path)
    obj = fx.mutate(fx.make_prereg(root), "cost.estimate_inputs", "N from EV/evaluation/<ds>/renderings/<case>/standard.md")
    assert prereg.placeholder_problems(obj) == []


# --------------------------------------------------------------------------
# Headings and notice
# --------------------------------------------------------------------------

def test_headings_in_order(tmp_path):
    root = fx.make_root(tmp_path)
    md = (root / "PREREGISTRATION.md").read_text(encoding="utf-8")
    assert prereg.heading_problems(md) == []
    assert [h for _, h in prereg.REQUIRED_HEADINGS] == fx.HEADINGS


def test_heading_missing_or_out_of_order(tmp_path):
    root = fx.make_root(tmp_path)
    md = (root / "PREREGISTRATION.md").read_text(encoding="utf-8")
    assert prereg.heading_problems(md.replace("## 9. Secondary scores\n", "")) != []
    swapped = md.replace("## 5. Main scores", "## 5. TMP").replace("## 6. Win rule", "## 5. Main scores").replace("## 5. TMP", "## 6. Win rule")
    assert prereg.heading_problems(swapped) != []


def test_extract_notice_matches_file(tmp_path):
    root = fx.make_root(tmp_path)
    md = (root / "PREREGISTRATION.md").read_text(encoding="utf-8")
    assert prereg.extract_notice(md).encode("utf-8") == (root / "prompts" / "provider_notice.txt").read_bytes()


def test_extract_notice_rule():
    md = "## 11. Report shape\n\n```text\nnot this\n```\n\n## 12. Outside-provider notice\n\n- n:\n\n    ```text\n    a\n\n    b\n    ```\n\n## 13. Known limits\n"
    assert prereg.extract_notice(md) == "a\n\nb\n"


# --------------------------------------------------------------------------
# Consistency
# --------------------------------------------------------------------------

def _consistency(root):
    return prereg.consistency_problems(
        root,
        json.loads((root / "prereg.json").read_text(encoding="utf-8")),
        (root / "PREREGISTRATION.md").read_text(encoding="utf-8"),
    )


def test_consistency_clean(tmp_path):
    root = fx.make_root(tmp_path)
    assert _consistency(root) == []


def test_notice_block_must_equal_file(tmp_path):
    root = fx.make_root(tmp_path)
    md = root / "PREREGISTRATION.md"
    text = md.read_text(encoding="utf-8").replace("=== END NOTICE ===", "=== END NOTICE === ")
    md.write_text(text, encoding="utf-8")
    assert _has(_consistency(root), "notice")


def test_notice_sha_must_match(tmp_path):
    root = fx.make_root(tmp_path)
    obj = fx.mutate(fx.make_prereg(root), "judges.notice_sha256", "a" * 64)
    fx.write_prereg(root, obj)
    assert _has(_consistency(root), "judges.notice_sha256")


def test_gold_relation_counts_must_match_items(tmp_path):
    root = fx.make_root(tmp_path)
    obj = fx.mutate(fx.make_prereg(root), "corpus.gold_relation_counts.qasper", 6)
    fx.write_prereg(root, obj)
    assert _has(_consistency(root), "corpus.gold_relation_counts")


def test_dataset_counts_must_match(tmp_path):
    root = fx.make_root(tmp_path)
    obj = fx.mutate(fx.make_prereg(root), "corpus.datasets.hotpotqa", 9)
    fx.write_prereg(root, obj)
    assert _has(_consistency(root), "corpus.datasets")


def test_skill_version_must_match(tmp_path):
    root = fx.make_root(tmp_path)
    obj = fx.mutate(fx.make_prereg(root), "generator.skill_version", "0.0.0")
    fx.write_prereg(root, obj)
    assert _has(_consistency(root), "generator.skill_version")


PINNED = [
    "generator.prompt_sha256.shared_user",
    "generator.prompt_sha256.skill_instruction",
    "generator.prompt_sha256.plain_system",
    "generator.prompt_sha256.prose_instruction",
    "generator.prompt_sha256.bullets_instruction",
    "judges.judge_prompt_sha256",
    "generator.skill_md_sha256",
    "generator.render_modes_md_sha256",
    "scores.combine_py_sha256",
    "textrank.stopwords_sha256",
    "corpus.corpus_manifest_sha256",
    "corpus.derived_manifest_sha256",
]


@pytest.mark.parametrize("dotted", PINNED)
def test_every_pinned_hash_is_checked(tmp_path, dotted):
    root = fx.make_root(tmp_path)
    obj = fx.mutate(fx.make_prereg(root), dotted, "f" * 64)
    fx.write_prereg(root, obj)
    assert _has(_consistency(root), dotted)


def test_pinned_hash_map_covers_contract():
    assert sorted(prereg.pinned_hash_keys()) == sorted(PINNED + ["judges.notice_sha256"])


@pytest.mark.parametrize("rel", ["prompts/judge.md", "prompts/shared_user.md", "bench/stopwords.txt", "prompts/provider_notice.txt"])
def test_live_file_edit_breaks_consistency(tmp_path, rel):
    root = fx.make_root(tmp_path)
    p = root / rel
    p.write_bytes(p.read_bytes() + b"x\n")
    assert _consistency(root) != []


def test_stale_hash_in_md_is_reported(tmp_path):
    root = fx.make_root(tmp_path)
    md = root / "PREREGISTRATION.md"
    md.write_text(md.read_text(encoding="utf-8") + "\nOld hash `" + "b" * 64 + "`.\n", encoding="utf-8")
    assert _has(_consistency(root), "b" * 12)


# --------------------------------------------------------------------------
# verify-prereg (SC-001)
# --------------------------------------------------------------------------

def _repo(root):
    return root.parent


def test_verify_passes_with_no_runs(tmp_path):
    root = fx.make_root(tmp_path)
    res = prereg.verify(root)
    assert res.problems == []
    assert res.checked == []


def test_verify_passes_when_prereg_precedes_runs(tmp_path):
    root = fx.make_root(tmp_path)
    rid = prereg.default_run_id(root)
    fx.write_manifest(root, rid, prereg.prereg_sha256(root))
    fx.commit(_repo(root), "run")
    res = prereg.verify(root)
    assert res.problems == []
    assert res.checked == [rid]


def test_verify_ignores_gitkeep_committed_first(tmp_path):
    # make_root commits runs/.gitkeep in the setup commit, before the prereg.
    root = fx.make_root(tmp_path)
    rid = prereg.default_run_id(root)
    fx.write_manifest(root, rid, prereg.prereg_sha256(root))
    fx.commit(_repo(root), "run")
    assert prereg.verify(root).problems == []


def test_verify_fails_when_a_run_file_came_first(tmp_path):
    root = fx.make_root(tmp_path, with_prereg=False)
    (root / "runs" / "early").mkdir()
    (root / "runs" / "early" / "samples.jsonl").write_text("{}\n", encoding="utf-8")
    fx.commit(_repo(root), "early output")
    fx.write_prereg(root, fx.make_prereg(root))
    fx.commit(_repo(root), "pre-registration")
    res = prereg.verify(root, ["early"])
    assert _has(res.problems, "ancestor")


def test_verify_fails_when_run_and_prereg_share_a_commit(tmp_path):
    root = fx.make_root(tmp_path, with_prereg=False)
    fx.write_prereg(root, fx.make_prereg(root))
    rid = prereg.default_run_id(root)
    fx.write_manifest(root, rid, prereg.prereg_sha256(root))
    fx.commit(_repo(root), "prereg and run together")
    assert _has(prereg.verify(root).problems, "ancestor")


def test_verify_fails_on_manifest_without_committed_hash(tmp_path):
    root = fx.make_root(tmp_path)
    fx.write_manifest(root, "named", "1" * 64)
    fx.commit(_repo(root), "run")
    assert _has(prereg.verify(root, ["named"]).problems, "named", "manifest")


def test_verify_fails_on_missing_manifest(tmp_path):
    root = fx.make_root(tmp_path)
    (root / "runs" / "named").mkdir()
    (root / "runs" / "named" / "items.jsonl").write_text("{}\n", encoding="utf-8")
    fx.commit(_repo(root), "run")
    assert _has(prereg.verify(root, ["named"]).problems, "named", "manifest")


def test_verify_checks_staged_runs(tmp_path):
    root = fx.make_root(tmp_path)
    fx.write_manifest(root, "staged", "2" * 64)
    fx.git(_repo(root), "add", "--", "controlled/runs/staged/manifest.json")
    res = prereg.verify(root)
    assert "staged" in res.checked
    assert _has(res.problems, "staged", "manifest")


def test_verify_only_named_runs(tmp_path):
    root = fx.make_root(tmp_path)
    fx.write_manifest(root, "good", prereg.prereg_sha256(root))
    fx.write_manifest(root, "bad", "3" * 64)
    fx.commit(_repo(root), "runs")
    assert prereg.verify(root, ["good"]).problems == []
    assert prereg.verify(root, ["bad"]).problems != []


def test_verify_lists_and_ignores_superseded_runs(tmp_path):
    root = fx.make_root(tmp_path)
    old_sha = prereg.prereg_sha256(root)
    old_dry = "dryrun-" + old_sha[:12]
    fx.write_manifest(root, old_dry, old_sha)
    fx.commit(_repo(root), "dry run v1")
    # Amendment: new version, new hash, new run id.
    md = root / "PREREGISTRATION.md"
    md.write_text(md.read_text(encoding="utf-8") + "\n### Deviations\n\n- 2026-09-27: test amendment.\n", encoding="utf-8")
    fx.commit(_repo(root), "amend pre-registration")
    new_sha = prereg.prereg_sha256(root)
    new_id = "pr-" + new_sha[:12]
    fx.write_manifest(root, new_id, new_sha)
    fx.commit(_repo(root), "run v2")
    res = prereg.verify(root)
    assert res.problems == []
    assert res.superseded == [old_dry]
    assert res.checked == [new_id]


def test_verify_runs_the_gate(tmp_path):
    root = fx.make_root(tmp_path)
    (root / "prereg.json").write_bytes(b"{}\n")
    assert _has(prereg.verify(root).problems, "uncommitted")


def _wildchat_run(root, sha, **extra):
    fx.write_manifest(root, "slop-abc", sha, **extra)
    (root / "runs" / "slop-abc" / "items.jsonl").write_text(
        json.dumps({"item": {"dataset": "wildchat", "item_id": "wildchat/w1"}}) + "\n", encoding="utf-8")


def test_verify_wildchat_needs_committed_addendum(tmp_path):
    root = fx.make_root(tmp_path)
    _wildchat_run(root, prereg.prereg_sha256(root), slop_addendum_sha256=None)
    fx.commit(_repo(root), "slop run")
    assert _has(prereg.verify(root, ["slop-abc"]).problems, "slop")


def test_verify_wildchat_passes_with_matching_addendum(tmp_path):
    root = fx.make_root(tmp_path)
    (root / "slop").mkdir()
    (root / "slop" / "PREREGISTRATION.md").write_text("# Slop addendum v1\n", encoding="utf-8")
    fx.commit(_repo(root), "slop addendum")
    add_sha = fx.sha(root / "slop" / "PREREGISTRATION.md")
    _wildchat_run(root, prereg.prereg_sha256(root), slop_addendum_sha256=add_sha)
    fx.commit(_repo(root), "slop run")
    assert prereg.verify(root, ["slop-abc"]).problems == []


def test_verify_wildchat_fails_with_other_addendum_hash(tmp_path):
    root = fx.make_root(tmp_path)
    (root / "slop").mkdir()
    (root / "slop" / "PREREGISTRATION.md").write_text("# Slop addendum v1\n", encoding="utf-8")
    fx.commit(_repo(root), "slop addendum")
    _wildchat_run(root, prereg.prereg_sha256(root), slop_addendum_sha256="4" * 64)
    fx.commit(_repo(root), "slop run")
    assert _has(prereg.verify(root, ["slop-abc"]).problems, "slop")


def test_real_repo_is_not_touched(tmp_path, paths):
    import subprocess
    before = subprocess.run(["git", "-C", str(paths["REPO"]), "rev-parse", "HEAD"], capture_output=True, text=True).stdout
    fx.make_root(tmp_path)
    after = subprocess.run(["git", "-C", str(paths["REPO"]), "rev-parse", "HEAD"], capture_output=True, text=True).stdout
    assert before == after


# --------------------------------------------------------------------------
# Live files (T025): the real prereg.json and PREREGISTRATION.md
# --------------------------------------------------------------------------
# These read the real files and never write. The git-state part of the gate
# (committed, clean) is not asserted here: the files stay uncommitted until
# the T027 commit gate, which `run.py verify-prereg` checks.

@pytest.fixture(scope="module")
def live(paths):
    cb = paths["CB"]
    return {
        "root": cb,
        "obj": json.loads((cb / "prereg.json").read_text(encoding="utf-8")),
        "md": (cb / "PREREGISTRATION.md").read_text(encoding="utf-8"),
    }


def test_live_required_keys(live):
    assert prereg.required_key_problems(live["obj"]) == []


def test_live_placeholder_free(live):
    assert prereg.placeholder_problems(live["obj"]) == []


def test_live_headings_in_order(live):
    assert prereg.heading_problems(live["md"]) == []


def test_live_consistency(live):
    assert prereg.consistency_problems(live["root"], live["obj"], live["md"]) == []


def test_live_notice_block_is_byte_equal(live):
    notice = (live["root"] / "prompts" / "provider_notice.txt").read_bytes()
    assert prereg.extract_notice(live["md"]).encode("utf-8") == notice
    assert live["obj"]["judges"]["notice_sha256"] == fx.NOTICE_SHA256


def test_live_frozen_values(live):
    obj = live["obj"]
    assert obj["corpus"]["gold_relation_counts"] == fx.RELATION_COUNTS
    assert obj["corpus"]["datasets"] == {"qmsum": 24, "qasper": 10, "hotpotqa": 8}
    assert obj["generator"]["skill_version"] == prereg.skill_version()
    assert obj["secondary"] == {"qmsum": "rouge_l_recall", "qasper": "answer_token_recall",
                                "hotpotqa": "answer_containment", "normalization": "squad_v1"}
    assert obj["win_rule"]["holm_families"] == ["fact_greater", "fact_less"]
    assert obj["win_rule"]["unadjusted"] == ["relation_less"]
    assert obj["judges"]["panel"][0]["daily_cap"] == 200
    assert obj["judges"]["panel"][1]["daily_cap"] == 50
    assert all(c["pass_threshold"] is None for c in obj["testing_criteria"])


def test_live_fr022_sentence_verbatim(live):
    sentence = ("Plain bullets were not significantly worse than the skill on this dataset, so any gain "
                "here may come from list format alone and not from the skill's rules.")
    assert live["obj"]["report"]["fr022_sentence"] == sentence
    assert sentence in " ".join(live["md"].split())


def test_live_hash_formula(live):
    root = live["root"]
    want = hashlib.sha256(fx.canonical(live["obj"]) + (root / "PREREGISTRATION.md").read_bytes()).hexdigest()
    assert prereg.prereg_sha256(root) == want


def test_live_prereg_json_is_canonical(live):
    assert (live["root"] / "prereg.json").read_bytes() == fx.canonical(live["obj"])
