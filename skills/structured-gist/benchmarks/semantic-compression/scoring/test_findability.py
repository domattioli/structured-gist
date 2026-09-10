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
    EXPLORATORY_STATUSES,
    STRICT_STATUSES,
    CaseBaseline,
    RetainedUnit,
    Span,
    SourceAlignment,
    align_units_to_source,
    assert_identical_retained_sets,
    build_case_baseline,
    build_rendering_index,
    build_retained_units,
    finalize_view,
    locate_all_gist_positions,
    merge_spans,
    naive_per_question_baseline_tokens,
    rank_units,
    score_question_unit_rank,
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


# ---------------------------------------------------------------------------
# THE FIX: unit-rank Evidence Access Cost over the retained-unit set R.
#
# R is exactly the units this specific (case, tier, level) rendering
# retained AND could align on both sides -- never all of a case's gold
# content. Both orderings (source, gist) are permutations of the SAME set
# R; only their order differs. See findability.py's `build_retained_units`,
# `rank_units`, `score_question_unit_rank` and FINDABILITY_FINDINGS.md "The
# fix: the retained-unit baseline".
# ---------------------------------------------------------------------------

def _ru(uid, kind, s_start, s_end, g_start, g_end):
    return RetainedUnit(uid=uid, kind=kind, source_span=Span(s_start, s_end), gist_span=Span(g_start, g_end))


def test_identical_retained_set_on_both_sides():
    retained = {
        "f1": _ru("f1", "fact", 0, 1, 4, 5),
        "f2": _ru("f2", "fact", 1, 2, 0, 1),
        "f3": _ru("f3", "fact", 2, 3, 2, 3),
    }
    source_ranks = rank_units(retained, "source")
    gist_ranks = rank_units(retained, "gist")
    assert set(source_ranks) == set(retained) == set(gist_ranks)
    assert_identical_retained_sets(retained, source_ranks, gist_ranks)  # must not raise


def test_assert_identical_retained_sets_catches_a_real_mismatch():
    retained = {"f1": _ru("f1", "fact", 0, 1, 0, 1)}
    good = {"f1": 1}
    bad = {"f1": 1, "f2": 2}  # an extra id that is NOT in the retained set
    assert_identical_retained_sets(retained, good, good)  # sanity: no raise
    try:
        assert_identical_retained_sets(retained, bad, good)
        assert False, "expected AssertionError for a ranking that does not match the retained set"
    except AssertionError:
        pass


def test_deleted_unit_absent_from_both_orderings():
    # f2 is NOT retained (status is "omitted") -- it must not appear in
    # build_retained_units' output, and therefore cannot appear in either
    # ranking, regardless of whether it happens to align on one side.
    gold = _gold([_fact("f1", "alpha beta"), _fact("f2", "gamma delta")])
    source_tokens = tokenize("alpha beta gamma delta")
    alignment = align_units_to_source(gold, source_tokens)
    judged = _judged_level({"f1": ("retained", "alpha beta"), "f2": ("omitted", "")})
    gist_pos = {"f1": Span(0, 2), "f2": Span(2, 4)}  # f2 WOULD align if it were eligible
    retained, excluded = build_retained_units(gold, judged, alignment, gist_pos, STRICT_STATUSES)
    assert set(retained) == {"f1"}
    assert "status=omitted" in excluded["f2"]
    source_ranks = rank_units(retained, "source")
    gist_ranks = rank_units(retained, "gist")
    assert "f2" not in source_ranks
    assert "f2" not in gist_ranks


def test_single_required_unit_moved_earlier_in_gist_improves_eac():
    # Source order: fA(1), fB(2), fC(3) of 3 -- EAC_source for fB = 2/3.
    # Gist order moves fB to the FRONT: fB(1), fA(2), fC(3) -- EAC_gist for
    # fB = 1/3. Moved earlier -> negative delta (improvement).
    retained = {
        "fA": _ru("fA", "fact", 0, 1, 1, 2),
        "fB": _ru("fB", "fact", 1, 2, 0, 1),
        "fC": _ru("fC", "fact", 2, 3, 2, 3),
    }
    source_ranks = rank_units(retained, "source")
    gist_ranks = rank_units(retained, "gist")
    view = score_question_unit_rank(["fB"], retained, {}, source_ranks, gist_ranks)
    assert view["eligible"] is True
    assert view["source_eac"] == round(2 / 3, 4)
    assert view["gist_eac"] == round(1 / 3, 4)
    assert view["delta_eac"] < 0


def test_single_required_unit_moved_later_in_gist_regresses_eac():
    # Source order: fA(1), fB(2), fC(3) -- EAC_source for fB = 2/3. Gist
    # order moves fB to the BACK: fA(1), fC(2), fB(3) -- EAC_gist for fB =
    # 3/3 = 1.0. Moved later -> positive delta (regression).
    retained = {
        "fA": _ru("fA", "fact", 0, 1, 0, 1),
        "fB": _ru("fB", "fact", 1, 2, 2, 3),
        "fC": _ru("fC", "fact", 2, 3, 1, 2),
    }
    source_ranks = rank_units(retained, "source")
    gist_ranks = rank_units(retained, "gist")
    view = score_question_unit_rank(["fB"], retained, {}, source_ranks, gist_ranks)
    assert view["source_eac"] == round(2 / 3, 4)
    assert view["gist_eac"] == 1.0
    assert view["delta_eac"] > 0


def test_two_required_units_clustered_closer_in_gist_improves_locality_span():
    # 4 retained units. Source order fA,fB,fC,fD (ranks 1..4). Required
    # fA+fD are the FIRST and LAST in source -> Span_source = (4-1+1)/4 = 1.0
    # (maximally spread). Gist clusters them adjacent at the end:
    # fB,fC,fA,fD -> fA=3, fD=4 -> Span_gist = (4-3+1)/4 = 0.5.
    retained = {
        "fA": _ru("fA", "fact", 0, 1, 2, 3),
        "fB": _ru("fB", "fact", 1, 2, 0, 1),
        "fC": _ru("fC", "fact", 2, 3, 1, 2),
        "fD": _ru("fD", "fact", 3, 4, 3, 4),
    }
    source_ranks = rank_units(retained, "source")
    gist_ranks = rank_units(retained, "gist")
    view = score_question_unit_rank(["fA", "fD"], retained, {}, source_ranks, gist_ranks)
    assert view["source_locality_span"] == 1.0
    assert view["gist_locality_span"] == 0.5
    assert view["delta_locality_span"] < 0


def test_two_required_units_spread_farther_in_gist_regresses_locality_span():
    # Required fA+fB are ADJACENT in source (ranks 1,2 of 4) -> Span_source
    # = (2-1+1)/4 = 0.5. Gist interposes fC and fD between them: fA,fC,fD,fB
    # -> fA=1, fB=4 -> Span_gist = (4-1+1)/4 = 1.0.
    retained = {
        "fA": _ru("fA", "fact", 0, 1, 0, 1),
        "fB": _ru("fB", "fact", 1, 2, 3, 4),
        "fC": _ru("fC", "fact", 2, 3, 1, 2),
        "fD": _ru("fD", "fact", 3, 4, 2, 3),
    }
    source_ranks = rank_units(retained, "source")
    gist_ranks = rank_units(retained, "gist")
    view = score_question_unit_rank(["fA", "fB"], retained, {}, source_ranks, gist_ranks)
    assert view["source_locality_span"] == 0.5
    assert view["gist_locality_span"] == 1.0
    assert view["delta_locality_span"] > 0


def test_ties_at_same_source_position_break_by_unit_id():
    # f1 and f2 align to the IDENTICAL source span -- must not depend on
    # dict/JSON insertion order. Sorted by (start, end, uid): f0 < f1 < f2 < f3.
    retained = {
        "f2": _ru("f2", "fact", 2, 4, 20, 21),
        "f0": _ru("f0", "fact", 0, 1, 30, 31),
        "f3": _ru("f3", "fact", 5, 6, 40, 41),
        "f1": _ru("f1", "fact", 2, 4, 10, 11),  # same source span as f2
    }
    source_ranks = rank_units(retained, "source")
    assert source_ranks == {"f0": 1, "f1": 2, "f2": 3, "f3": 4}


def test_ties_at_same_gist_position_break_by_unit_id():
    retained = {
        "f2": _ru("f2", "fact", 20, 21, 2, 4),
        "f0": _ru("f0", "fact", 30, 31, 0, 1),
        "f3": _ru("f3", "fact", 40, 41, 5, 6),
        "f1": _ru("f1", "fact", 10, 11, 2, 4),  # same gist span as f2
    }
    gist_ranks = rank_units(retained, "gist")
    assert gist_ranks == {"f0": 1, "f1": 2, "f2": 3, "f3": 4}


def test_relation_and_fact_sharing_source_span_remain_separate_units():
    # A fact and a relation whose source_quote spans fully overlap (common
    # in this corpus -- see FINDABILITY_FINDINGS.md "Duplicate / relation
    # overlap handling") are NEVER collapsed into one unit for this metric:
    # each keeps its own rank, tie-broken by unit id ("f1" < "r1").
    gold = _gold(
        facts=[_fact("f1", "dropped the index")],
        relations=[{"id": "r1", "source_quote": "dropped the index"}],
    )
    source_tokens = tokenize("the migration dropped the index today")
    alignment = align_units_to_source(gold, source_tokens)
    assert alignment.unit_span["f1"] == alignment.unit_span["r1"]  # identical span, NOT merged into one unit
    judged = _judged_level(
        {"f1": ("retained", "dropped the index")},
        {"r1": ("retained", "dropped the index")},
    )
    gist_pos = {"f1": Span(0, 3), "r1": Span(0, 3)}
    retained, excluded = build_retained_units(gold, judged, alignment, gist_pos, STRICT_STATUSES)
    assert set(retained) == {"f1", "r1"}
    source_ranks = rank_units(retained, "source")
    assert source_ranks == {"f1": 1, "r1": 2}  # "f1" < "r1" -- deterministic, not incidental


def test_omitted_required_unit_makes_unit_rank_question_ineligible():
    retained = {}
    excluded = {"f1": ["status=omitted", "unaligned_in_rendering"]}
    view = score_question_unit_rank(["f1"], retained, excluded, {}, {})
    assert view["eligible"] is False
    assert any("status=omitted" in r for r in view["reasons"])


def test_partial_required_unit_makes_strict_view_ineligible_but_not_exploratory():
    source = "alpha beta gamma delta"
    gold = _gold([_fact("f1", "alpha beta"), _fact("f2", "gamma delta")])
    source_tokens = tokenize(source)
    alignment = align_units_to_source(gold, source_tokens)
    judged = _judged_level({"f1": ("retained", "alpha beta"), "f2": ("partial", "gamma delta")})
    rendering = _fence("- alpha beta", "- gamma delta")
    idx = build_rendering_index(rendering)
    gist_pos = locate_all_gist_positions(gold, judged, idx.tokens)

    retained_strict, excluded_strict = build_retained_units(gold, judged, alignment, gist_pos, STRICT_STATUSES)
    assert set(retained_strict) == {"f1"}
    assert excluded_strict["f2"] == ["status=partial"]
    strict_ranks_s = rank_units(retained_strict, "source")
    strict_ranks_g = rank_units(retained_strict, "gist")
    strict_view = score_question_unit_rank(["f2"], retained_strict, excluded_strict, strict_ranks_s, strict_ranks_g)
    assert strict_view["eligible"] is False
    assert any("status=partial" in r for r in strict_view["reasons"])

    retained_explore, excluded_explore = build_retained_units(gold, judged, alignment, gist_pos, EXPLORATORY_STATUSES)
    assert set(retained_explore) == {"f1", "f2"}
    explore_ranks_s = rank_units(retained_explore, "source")
    explore_ranks_g = rank_units(retained_explore, "gist")
    explore_view = score_question_unit_rank(
        ["f2"], retained_explore, excluded_explore, explore_ranks_s, explore_ranks_g
    )
    assert explore_view["eligible"] is True


def test_zero_retained_units_is_ineligible_not_a_crash():
    retained = {}
    excluded = {"f1": ["unaligned_in_source"]}
    view = score_question_unit_rank(["f1"], retained, excluded, {}, {})
    assert view["eligible"] is False


def test_one_retained_unit_has_eac_and_span_of_one():
    retained = {"f1": _ru("f1", "fact", 0, 1, 5, 6)}
    source_ranks = rank_units(retained, "source")
    gist_ranks = rank_units(retained, "gist")
    view = score_question_unit_rank(["f1"], retained, {}, source_ranks, gist_ranks)
    assert view["eligible"] is True
    assert view["retained_set_size"] == 1
    assert view["source_eac"] == 1.0
    assert view["gist_eac"] == 1.0
    assert view["source_locality_span"] == 1.0
    assert view["gist_locality_span"] == 1.0
    assert view["delta_eac"] == 0.0


def test_rank_normalization_first_and_last_of_ten():
    # 1-indexed cumulative traversal: first of 10 retained units -> 0.1,
    # tenth (last) of 10 -> 1.0.
    retained = {f"u{i}": _ru(f"u{i}", "fact", i, i + 1, i, i + 1) for i in range(10)}
    source_ranks = rank_units(retained, "source")
    first_view = score_question_unit_rank(["u0"], retained, {}, source_ranks, source_ranks)
    last_view = score_question_unit_rank(["u9"], retained, {}, source_ranks, source_ranks)
    assert first_view["source_eac"] == 0.1
    assert last_view["source_eac"] == 1.0


def test_deterministic_ordering_regardless_of_dict_insertion_order():
    units = [
        _ru("f3", "fact", 3, 4, 3, 4),
        _ru("f1", "fact", 1, 2, 1, 2),
        _ru("f2", "fact", 2, 3, 2, 3),
        _ru("f0", "fact", 0, 1, 0, 1),
    ]
    retained_order_a = {u.uid: u for u in units}
    retained_order_b = {u.uid: u for u in reversed(units)}
    assert rank_units(retained_order_a, "source") == rank_units(retained_order_b, "source")
    assert rank_units(retained_order_a, "gist") == rank_units(retained_order_b, "gist")
