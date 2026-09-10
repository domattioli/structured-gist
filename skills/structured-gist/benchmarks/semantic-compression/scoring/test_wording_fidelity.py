#!/usr/bin/env python3
"""
Hand-calculable deterministic tests for scoring/wording_fidelity.py (and, by
construction, the text_norm.py / outline_nodes.py it's built on). No network,
no model calls, no randomness -- every expected value here is worked out by
hand in the test's own comment.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wording_fidelity import score_rendering  # noqa: E402


def _fence(*lines: str) -> str:
    return "```text\n" + "\n".join(lines) + "\n```\n"


def test_exact_copied_node_is_verbatim():
    source = "The cat sat on the mat."
    rendering = _fence("- The cat sat on the mat")
    r = score_rendering(rendering, source)
    assert r["total_semantic_nodes"] == 1
    assert r["verbatim_node_count"] == 1
    assert r["verbatim_node_rate"] == 1.0
    assert r["extractive_coverage_min1"] == 1.0
    assert r["extractive_coverage_min2"] == 1.0
    assert r["extractive_coverage_min3"] == 1.0
    assert r["novel_span_count"] == 0


def test_reordered_exact_nodes_each_stay_verbatim():
    # Both nodes are exact source spans, but the OUTPUT presents them in the
    # opposite order from the source ("Then do B" before "First do A").
    # Global reordering must not penalize either node -- each is checked
    # against the WHOLE source, not against a fixed alignment position.
    source = "First do A. Then do B."
    rendering = _fence("- Then do B", "- First do A")
    r = score_rendering(rendering, source)
    assert r["total_semantic_nodes"] == 2
    assert r["verbatim_node_count"] == 2
    assert r["verbatim_node_rate"] == 1.0
    assert r["extractive_coverage_min1"] == 1.0
    assert r["extractive_coverage_min3"] == 1.0
    assert r["novel_span_count"] == 0


def test_punctuation_only_difference_still_counts_as_verbatim():
    # Source has commas and a trailing period the rendering drops; the WORDS
    # are identical. This is exactly what "punctuation normalization only
    # where required to compare the same words" is for.
    source = "The system, once started, cannot stop."
    rendering = _fence("- The system once started cannot stop")
    r = score_rendering(rendering, source)
    assert r["verbatim_node_rate"] == 1.0
    assert r["non_verbatim_node_count"] == 0


def test_genuine_paraphrase_is_not_verbatim_and_has_low_coverage():
    source = "The database connection timed out after thirty seconds."
    rendering = _fence("- Connection dropped due to timeout")
    r = score_rendering(rendering, source)
    assert r["verbatim_node_rate"] == 0.0
    # No genuine 2-word run from this node appears anywhere in source.
    assert r["extractive_coverage_min2"] == 0.0
    assert r["extractive_coverage_min3"] == 0.0


def test_one_novel_word_inside_otherwise_copied_text():
    # "wolf" replaces "fox" -- everything else is a verbatim quote. The one
    # substituted word must surface as its own novel span, not disappear
    # into a high average driven by the surrounding copied text.
    source = "The quick brown fox jumps over the lazy dog."
    rendering = _fence("- The quick brown wolf jumps over the lazy dog")
    r = score_rendering(rendering, source)
    assert r["total_semantic_nodes"] == 1
    assert r["verbatim_node_rate"] == 0.0  # the node as a WHOLE is not one contiguous span
    assert r["novel_span_count"] == 1
    assert r["longest_novel_span_length"] == 1
    assert r["representative_novel_spans"][0]["text"] == "wolf"
    # 8 of the node's 9 tokens sit in one of two genuine multi-word matches
    # ("the quick brown" + "jumps over the lazy dog" = 3 + 5 = 8).
    assert r["extractive_coverage_min2"] == round(8 / 9, 4)


def test_structural_allowlist_excludes_fixed_preset_vocabulary():
    # "Session summary" is the literal session-summary preset header
    # (SKILL.md's own fixed vocabulary, not source wording or model
    # paraphrase) and must not count as a scorable semantic node at all --
    # neither as verbatim nor as a wording-fidelity violation.
    source = "The deploy finished without incident."
    rendering = _fence("- Session summary", "- The deploy finished without incident")
    r = score_rendering(rendering, source)
    assert r["allowlisted_node_count"] == 1
    assert r["allowlisted_nodes"] == ["Session summary"]
    assert r["total_semantic_nodes"] == 1  # allowlisted node excluded from the denominator
    assert r["verbatim_node_rate"] == 1.0


def test_empty_output_has_no_nodes_and_no_crash():
    r = score_rendering("", "The cat sat on the mat.")
    assert r["total_semantic_nodes"] == 0
    assert r["verbatim_node_rate"] is None
    assert r["extractive_coverage_min1"] is None
    assert r["novel_span_count"] == 0
    assert r["non_verbatim_nodes"] == []


def test_empty_source_makes_every_node_non_verbatim_without_crashing():
    rendering = _fence("- The cat sat on the mat")
    r = score_rendering(rendering, "")
    assert r["total_semantic_nodes"] == 1
    assert r["verbatim_node_rate"] == 0.0
    assert r["extractive_coverage_min1"] == 0.0
    assert r["extractive_coverage_min3"] == 0.0
