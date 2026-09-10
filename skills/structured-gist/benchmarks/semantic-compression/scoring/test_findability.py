#!/usr/bin/env python3
"""
Hand-calculable deterministic tests for scoring/findability.py. No network,
no model calls, no randomness. Every expected numeric value is derived by
hand in the test's own comment.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from findability import (  # noqa: E402
    STRICT_STATUSES,
    CaseBaseline,
    Span,
    build_case_baseline,
    build_rendering_index,
    finalize_view,
    merge_spans,
    naive_per_question_baseline_tokens,
    score_question_view,
    split_evidence_fragments,
)
from text_norm import tokenize  # noqa: E402


def _fence(*lines: str) -> str:
    return "```text\n" + "\n".join(lines) + "\n```\n"


def _gold(facts, relations=None, questions=None):
    return {"facts": facts, "relations": relations or [], "questions": questions or []}


def _fact(fid, quote):
    return {"id": fid, "source_quote": quote}


def _judged_level(fact_status_evidence, rel_status_evidence=None):
    return {
        "facts": {fid: {"status": st, "evidence": ev} for fid, (st, ev) in fact_status_evidence.items()},
        "relations": {rid: {"status": st, "evidence": ev} for rid, (st, ev) in (rel_status_evidence or {}).items()},
    }


# ---------------------------------------------------------------------------
# merge_spans
# ---------------------------------------------------------------------------

def test_merge_spans_dedupes_overlap():
    spans = [Span(0, 5), Span(3, 8), Span(20, 25)]
    merged = merge_spans(spans)
    assert merged == [Span(0, 8), Span(20, 25)]


def test_merge_spans_empty_input():
    assert merge_spans([]) == []


# ---------------------------------------------------------------------------
# Case-level baseline: single support span
# ---------------------------------------------------------------------------

def test_single_support_span_baseline_and_eac():
    source = "zero alpha beta gamma delta"
    gold = _gold([_fact("f1", "alpha beta gamma")])
    baseline = build_case_baseline(gold, tokenize(source))
    assert baseline.tokens == ["alpha", "beta", "gamma"]
    assert baseline.unit_pos["f1"] == Span(0, 3)

    rendering = _fence("- alpha beta gamma")
    idx = build_rendering_index(rendering)
    gist_pos = {"f1": Span(0, 3)}
    judged = _judged_level({"f1": ("retained", "alpha beta gamma")})

    raw = score_question_view(["f1"], judged, baseline, gist_pos, STRICT_STATUSES)
    view = finalize_view(raw, len(baseline.tokens), len(idx.tokens))
    assert view["eligible"] is True
    assert view["baseline_eac"] == 1.0
    assert view["gist_eac"] == 1.0
    assert view["delta_eac"] == 0.0


# ---------------------------------------------------------------------------
# Case-level baseline: multiple, non-adjacent support spans; baseline
# preserves source order even when gold lists facts out of order.
# ---------------------------------------------------------------------------

def _three_fact_case():
    # f_A first in source, f_B second, f_C third -- listed in gold OUT OF
    # source order (C, A, B) to test that the baseline still comes out in
    # SOURCE order, not gold-list order.
    source = "alpha alpha2 bravo bravo2 charlie charlie2"
    gold = _gold([
        _fact("f_C", "charlie charlie2"),
        _fact("f_A", "alpha alpha2"),
        _fact("f_B", "bravo bravo2"),
    ])
    return source, gold


def test_baseline_preserves_source_order_regardless_of_gold_list_order():
    source, gold = _three_fact_case()
    baseline = build_case_baseline(gold, tokenize(source))
    assert baseline.tokens == ["alpha", "alpha2", "bravo", "bravo2", "charlie", "charlie2"]
    assert baseline.unit_pos["f_A"] == Span(0, 2)
    assert baseline.unit_pos["f_B"] == Span(2, 4)
    assert baseline.unit_pos["f_C"] == Span(4, 6)


def test_evidence_reordered_closer_to_start_improves_gist_eac():
    # Question needs f_B and f_C, NOT f_A. In source order, f_B and f_C are
    # the LAST two of three units (f_A is first) -- the baseline (which
    # preserves source order) must therefore traverse almost the whole
    # thing: baseline_last_end = 6 (end of f_C, which is baseline-last),
    # baseline total = 6 -> EAC_baseline = 1.0.
    source, gold = _three_fact_case()
    baseline = build_case_baseline(gold, tokenize(source))
    judged = _judged_level({
        "f_A": ("retained", "alpha alpha2"),
        "f_B": ("retained", "bravo bravo2"),
        "f_C": ("retained", "charlie charlie2"),
    })

    raw = score_question_view(["f_B", "f_C"], judged, baseline, baseline.unit_pos, STRICT_STATUSES)
    view = finalize_view(raw, len(baseline.tokens), len(baseline.tokens))
    assert view["baseline_eac"] == 1.0
    assert view["baseline_evidence_span"] == round((6 - 2) / 6, 4)

    # The gist puts the two REQUIRED units first and pushes the unrelated
    # one (f_A) last: gist_tokens = bravo bravo2 charlie charlie2 alpha
    # alpha2. Now the last required token (end of f_C) is at position 4 of
    # 6 -> EAC_gist = 4/6 = 0.6667, an IMPROVEMENT (delta < 0).
    rendering = _fence("- bravo bravo2", "- charlie charlie2", "- alpha alpha2")
    idx = build_rendering_index(rendering)
    gist_pos = {"f_B": Span(0, 2), "f_C": Span(2, 4), "f_A": Span(4, 6)}

    raw2 = score_question_view(["f_B", "f_C"], judged, baseline, gist_pos, STRICT_STATUSES)
    view2 = finalize_view(raw2, len(baseline.tokens), len(idx.tokens))
    assert view2["gist_eac"] == round(4 / 6, 4)
    assert view2["delta_eac"] < 0  # negative = better, per module convention


def test_evidence_moved_farther_apart_regresses_gist_eac():
    # Same three units, but source order now has f_B and f_C ADJACENT
    # (positions 0-1, 2-3) with f_A after them (4-5) -- baseline for a
    # question needing f_B+f_C: last_end=4, total=6 -> EAC_baseline=0.6667.
    source = "bravo bravo2 charlie charlie2 alpha alpha2"
    gold = _gold([_fact("f_B", "bravo bravo2"), _fact("f_C", "charlie charlie2"), _fact("f_A", "alpha alpha2")])
    baseline = build_case_baseline(gold, tokenize(source))
    judged = _judged_level({
        "f_A": ("retained", "alpha alpha2"),
        "f_B": ("retained", "bravo bravo2"),
        "f_C": ("retained", "charlie charlie2"),
    })
    raw = score_question_view(["f_B", "f_C"], judged, baseline, baseline.unit_pos, STRICT_STATUSES)
    view = finalize_view(raw, len(baseline.tokens), len(baseline.tokens))
    assert view["baseline_eac"] == round(4 / 6, 4)

    # The gist WEDGES the unrelated f_A between the two required units:
    # bravo bravo2 [alpha alpha2] charlie charlie2. Now the last required
    # token (end of f_C) sits at the very end -> EAC_gist = 1.0, a
    # regression (delta > 0) even though nothing was omitted or mutated.
    rendering = _fence("- bravo bravo2", "- alpha alpha2", "- charlie charlie2")
    idx = build_rendering_index(rendering)
    gist_pos = {"f_B": Span(0, 2), "f_A": Span(2, 4), "f_C": Span(4, 6)}
    raw2 = score_question_view(["f_B", "f_C"], judged, baseline, gist_pos, STRICT_STATUSES)
    view2 = finalize_view(raw2, len(baseline.tokens), len(idx.tokens))
    assert view2["gist_eac"] == 1.0
    assert view2["delta_eac"] > 0
    assert view2["delta_evidence_span"] > 0


# ---------------------------------------------------------------------------
# Overlapping spans (fact + relation quotes overlapping, as in the real
# corpus -- see README.md pressure-check "relation source_quote overlapping
# its component fact quotes")
# ---------------------------------------------------------------------------

def test_overlapping_fact_and_relation_spans_are_deduped_in_baseline():
    source = "the migration dropped the index causing slow queries today"
    gold = _gold(
        facts=[_fact("f1", "dropped the index")],
        relations=[{"id": "r1", "source_quote": "the migration dropped the index causing slow queries"}],
    )
    baseline = build_case_baseline(gold, tokenize(source))
    # r1's span fully contains f1's span -> one merged span, not two
    # separately-counted, double-included ranges.
    assert baseline.merged_span_count == 1
    assert len(baseline.tokens) == len(tokenize("the migration dropped the index causing slow queries"))
    # f1 sits at its correct offset WITHIN the merged (r1-sized) span.
    f1_span = baseline.unit_pos["f1"]
    assert baseline.tokens[f1_span.start:f1_span.end] == ["dropped", "the", "index"]


# ---------------------------------------------------------------------------
# Duplicated source phrase -- first-occurrence convention
# ---------------------------------------------------------------------------

def test_duplicated_source_phrase_uses_first_occurrence_and_is_flagged_ambiguous():
    source = "alpha beta alpha beta gamma"
    gold = _gold([_fact("f1", "alpha beta")])
    baseline = build_case_baseline(gold, tokenize(source))
    assert baseline.unit_pos["f1"] == Span(0, 2)  # first occurrence, not the second at (2,4)
    assert baseline.ambiguous_unit_ids == ["f1"]


# ---------------------------------------------------------------------------
# Omitted / unalignable support units make a question ineligible
# ---------------------------------------------------------------------------

def test_omitted_support_unit_makes_question_ineligible():
    source = "alpha beta gamma"
    gold = _gold([_fact("f1", "alpha beta gamma")])
    baseline = build_case_baseline(gold, tokenize(source))
    judged = _judged_level({"f1": ("omitted", "")})
    raw = score_question_view(["f1"], judged, baseline, {}, STRICT_STATUSES)
    assert raw["eligible"] is False
    assert any("status=omitted" in r for r in raw["reasons"])


def test_unalignable_evidence_makes_question_ineligible_even_when_retained():
    # Status says retained, but the evidence text does not appear anywhere
    # in the gist's token stream -- must fail closed, not guess.
    source = "alpha beta gamma"
    gold = _gold([_fact("f1", "alpha beta gamma")])
    baseline = build_case_baseline(gold, tokenize(source))
    judged = _judged_level({"f1": ("retained", "totally different wording")})
    gist_pos = {}  # locate_evidence_in_rendering would have failed to find it
    raw = score_question_view(["f1"], judged, baseline, gist_pos, STRICT_STATUSES)
    assert raw["eligible"] is False
    assert any("unaligned_in_rendering" in r for r in raw["reasons"])
    assert not any("status=" in r for r in raw["reasons"])  # status WAS fine


# ---------------------------------------------------------------------------
# split_evidence_fragments -- judge-authored multi-part evidence strings
# ---------------------------------------------------------------------------

def test_split_evidence_fragments_handles_ellipsis_slash_and_marker_prefix():
    assert split_evidence_fragments("walk, validate, symlink ... verify each new link") == [
        "walk, validate, symlink",
        "verify each new link",
    ]
    assert split_evidence_fragments("auth-service: reverted / notifications: scheduled") == [
        "auth-service: reverted",
        "notifications: scheduled",
    ]
    assert split_evidence_fragments("IV. retry adds load") == ["retry adds load"]


# ---------------------------------------------------------------------------
# No division by zero
# ---------------------------------------------------------------------------

def test_empty_source_baseline_has_no_tokens_and_no_crash():
    gold = _gold([_fact("f1", "alpha beta")])
    baseline = build_case_baseline(gold, [])
    assert baseline.tokens == []
    assert baseline.unaligned_unit_ids == ["f1"]

    judged = _judged_level({"f1": ("retained", "alpha beta")})
    raw = score_question_view(["f1"], judged, baseline, {"f1": Span(0, 2)}, STRICT_STATUSES)
    assert raw["eligible"] is False  # f1 is in unaligned_unit_ids


def test_empty_gist_representation_is_ineligible_not_a_crash():
    source = "alpha beta"
    gold = _gold([_fact("f1", "alpha beta")])
    baseline = build_case_baseline(gold, tokenize(source))
    judged = _judged_level({"f1": ("retained", "alpha beta")})
    raw = score_question_view(["f1"], judged, baseline, {"f1": Span(0, 2)}, STRICT_STATUSES)
    view = finalize_view(raw, len(baseline.tokens), 0)  # gist_total == 0
    assert view["eligible"] is False


def test_no_required_units_case_does_not_crash():
    baseline = CaseBaseline(tokens=[], unit_pos={}, unaligned_unit_ids=[], merged_span_count=0, ambiguous_unit_ids=[])
    raw = score_question_view([], {}, baseline, {}, STRICT_STATUSES)
    view = finalize_view(raw, 0, 0)
    assert view["eligible"] is False


# ---------------------------------------------------------------------------
# The literal per-question minimal baseline (PR brief's 5-step construction,
# NOT what this module actually scores with) is mathematically degenerate:
# since it contains ONLY the required evidence and nothing else, traversal
# to the last required token is unconditionally the ENTIRE baseline, for
# any nonempty set of required spans. This is why scoring uses a case-level
# baseline instead -- see FINDABILITY_FINDINGS.md.
# ---------------------------------------------------------------------------

def test_naive_per_question_baseline_is_always_fully_traversed():
    source_tokens = tokenize("alpha beta gamma delta epsilon zeta eta theta")
    for required in (
        [Span(0, 2)],                    # single support span
        [Span(0, 2), Span(5, 7)],        # two non-adjacent spans
        [Span(3, 4), Span(0, 2), Span(6, 8)],  # three, out of order
    ):
        baseline_tokens = naive_per_question_baseline_tokens(required, source_tokens)
        # By construction the baseline contains ONLY required content, so
        # the last required unit's end is unconditionally the full length
        # -- EAC and EvidenceSpan against this baseline are both exactly
        # 1.0 no matter what the actual spans are.
        total = len(baseline_tokens)
        merged = merge_spans(required)
        last_end_in_baseline = sum(s.length for s in merged)  # the last merged span ends exactly at `total`
        assert last_end_in_baseline == total
        eac = last_end_in_baseline / total
        span = (last_end_in_baseline - 0) / total
        assert eac == 1.0
        assert span == 1.0
