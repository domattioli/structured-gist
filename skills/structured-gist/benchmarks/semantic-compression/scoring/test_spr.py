#!/usr/bin/env python3
"""
Deterministic pytest tests for scoring/spr.py's arithmetic: the hand-calculable
example from the PR brief (facts: weight-3 retained + weight-1 partial;
relations: weight-3 lost + weight-2 retained -> SPR = 5.5/9 = 0.6111), plus
edge cases (empty facts/relations, no division by zero, critical-loss
counting, and -- the one property this module cannot ever be allowed to
regress -- that a fact's legacy `weight` in gold.json can NEVER leak into
score_spr()'s arithmetic, only the blinded weight can.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from spr import score_spr, compare_weights, spearman_rho, _round_half_up  # noqa: E402


def _gold(facts, relations=None):
    return {"facts": facts, "relations": relations or []}


def _verdict(fact_status, rel_status=None):
    return {
        "facts": {fid: {"status": st} for fid, st in fact_status.items()},
        "relations": {rid: {"status": st} for rid, st in (rel_status or {}).items()},
    }


def _blind(case_id, fact_weights, relation_weights):
    return {
        "case_id": case_id,
        "annotation_protocol": "blinded-task-importance-v1",
        "fact_weights": fact_weights,
        "relation_weights": relation_weights,
    }


# The brief's hand-calculable example:
# facts:     weight 3 retained -> 3.0   |  weight 1 partial -> 0.5
# relations: weight 3 lost     -> 0.0   |  weight 2 retained -> 2.0
# total preserved = 3.0 + 0.5 + 0.0 + 2.0 = 5.5
# total possible  = 3 + 1 + 3 + 2 = 9
# SPR = 5.5 / 9 = 0.6111...
HAND_FACTS = [{"id": "f1", "weight": 1}, {"id": "f2", "weight": 1}]  # legacy weights irrelevant, see test below
HAND_RELATIONS = [{"id": "r1"}, {"id": "r2"}]


def test_hand_calculable_example_from_brief():
    gold = _gold(HAND_FACTS, HAND_RELATIONS)
    verdict = _verdict({"f1": "retained", "f2": "partial"}, {"r1": "lost", "r2": "retained"})
    blind = _blind("hand-calc", {"f1": 3, "f2": 1}, {"r1": 3, "r2": 2})
    result = score_spr(gold, verdict, blind)
    assert result["blinded_task_weighted_fact_recall"] == round((3 * 1.0 + 1 * 0.5) / 4, 4)
    assert result["blinded_task_weighted_fact_recall"] == 0.875
    assert result["task_weighted_relation_recall"] == round((3 * 0.0 + 2 * 1.0) / 5, 4)
    assert result["task_weighted_relation_recall"] == 0.4
    assert result["semantic_preservation_recall"] == round(5.5 / 9, 4)
    assert result["semantic_preservation_recall"] == 0.6111


def test_partial_scores_as_half():
    gold = _gold([{"id": "f1", "weight": 2}])
    verdict = _verdict({"f1": "partial"})
    blind = _blind("c", {"f1": 2}, {})
    result = score_spr(gold, verdict, blind)
    assert result["blinded_task_weighted_fact_recall"] == 0.5


def test_omitted_and_mutated_and_lost_score_as_zero():
    gold = _gold([{"id": "f1", "weight": 3}, {"id": "f2", "weight": 3}], [{"id": "r1"}])
    verdict = _verdict({"f1": "omitted", "f2": "mutated"}, {"r1": "lost"})
    blind = _blind("c", {"f1": 3, "f2": 3}, {"r1": 3})
    result = score_spr(gold, verdict, blind)
    assert result["blinded_task_weighted_fact_recall"] == 0.0
    assert result["task_weighted_relation_recall"] == 0.0
    assert result["semantic_preservation_recall"] == 0.0


def test_empty_facts_is_not_applicable_not_zero():
    gold = _gold([], [{"id": "r1"}])
    verdict = _verdict({}, {"r1": "retained"})
    blind = _blind("c", {}, {"r1": 2})
    result = score_spr(gold, verdict, blind)
    assert result["blinded_task_weighted_fact_recall"] is None
    assert result["task_weighted_relation_recall"] == 1.0
    # SPR still computable from relations alone -- facts contribute 0 weight,
    # not a fabricated 0 score
    assert result["semantic_preservation_recall"] == 1.0


def test_empty_relations_is_not_applicable_not_zero():
    gold = _gold([{"id": "f1", "weight": 2}], [])
    verdict = _verdict({"f1": "retained"}, {})
    blind = _blind("c", {"f1": 2}, {})
    result = score_spr(gold, verdict, blind)
    assert result["task_weighted_relation_recall"] is None
    assert result["blinded_task_weighted_fact_recall"] == 1.0
    assert result["semantic_preservation_recall"] == 1.0


def test_empty_facts_and_relations_never_divides_by_zero():
    gold = _gold([], [])
    verdict = _verdict({}, {})
    blind = _blind("c", {}, {})
    result = score_spr(gold, verdict, blind)
    assert result["blinded_task_weighted_fact_recall"] is None
    assert result["task_weighted_relation_recall"] is None
    assert result["semantic_preservation_recall"] is None


def test_legacy_gold_weight_never_leaks_into_spr_arithmetic():
    """The one property this module cannot regress: score_spr() must ignore
    gold.json's legacy `weight` field entirely and use ONLY the blinded
    weight. Two golds that differ only in legacy `weight` must score
    identically once the blinded weight is held fixed."""
    gold_a = _gold([{"id": "f1", "weight": 1}, {"id": "f2", "weight": 1}])
    gold_b = _gold([{"id": "f1", "weight": 3}, {"id": "f2", "weight": 3}])  # legacy weights flipped
    verdict = _verdict({"f1": "retained", "f2": "omitted"})
    blind = _blind("c", {"f1": 3, "f2": 1}, {})  # blinded weights held fixed, differ from BOTH legacy sets
    result_a = score_spr(gold_a, verdict, blind)
    result_b = score_spr(gold_b, verdict, blind)
    assert result_a == result_b
    # and the number reflects the BLINDED weights (3, 1), not either legacy set
    assert result_a["blinded_task_weighted_fact_recall"] == round(3 * 1.0 / 4, 4)


def test_missing_blind_weight_for_a_gold_id_is_a_hard_error():
    """Annotation coverage is a precondition, not a runtime fallback -- a
    case with an unannotated fact must fail loudly (KeyError), never
    silently default to some weight and produce a quietly-wrong score."""
    gold = _gold([{"id": "f1", "weight": 1}, {"id": "f2", "weight": 1}])
    verdict = _verdict({"f1": "retained", "f2": "retained"})
    blind = _blind("c", {"f1": 2}, {})  # f2 missing from blind annotation
    try:
        score_spr(gold, verdict, blind)
        assert False, "expected KeyError for unannotated fact id"
    except KeyError:
        pass


def test_critical_loss_counts_only_blind_weight_3_units():
    gold = _gold(
        [{"id": "f1", "weight": 1}, {"id": "f2", "weight": 1}, {"id": "f3", "weight": 1}],
        [{"id": "r1"}, {"id": "r2"}],
    )
    # blind weights: f1=3 (critical, omitted), f2=3 (critical, partial),
    # f3=1 (not critical, omitted -- must not count), r1=3 (critical, lost),
    # r2=1 (not critical, lost -- must not count)
    verdict = _verdict(
        {"f1": "omitted", "f2": "partial", "f3": "omitted"},
        {"r1": "lost", "r2": "lost"},
    )
    blind = _blind("c", {"f1": 3, "f2": 3, "f3": 1}, {"r1": 3, "r2": 1})
    result = score_spr(gold, verdict, blind)
    assert result["critical_units_total"] == 3  # f1, f2, r1
    assert result["critical_units_lost"] == 2  # f1 (omitted), r1 (lost)
    assert result["critical_units_partial"] == 1  # f2


def test_critical_loss_counts_zero_when_all_critical_units_retained():
    gold = _gold([{"id": "f1", "weight": 1}])
    verdict = _verdict({"f1": "retained"})
    blind = _blind("c", {"f1": 3}, {})
    result = score_spr(gold, verdict, blind)
    assert result["critical_units_total"] == 1
    assert result["critical_units_lost"] == 0
    assert result["critical_units_partial"] == 0


def test_score_spr_is_deterministic():
    gold = _gold(HAND_FACTS, HAND_RELATIONS)
    verdict = _verdict({"f1": "retained", "f2": "partial"}, {"r1": "lost", "r2": "retained"})
    blind = _blind("hand-calc", {"f1": 3, "f2": 1}, {"r1": 3, "r2": 2})
    assert score_spr(gold, verdict, blind) == score_spr(gold, verdict, blind)


def test_missing_fact_status_defaults_to_omitted():
    gold = _gold([{"id": "f1", "weight": 1}])
    verdict = _verdict({})
    blind = _blind("c", {"f1": 3}, {})
    result = score_spr(gold, verdict, blind)
    assert result["blinded_task_weighted_fact_recall"] == 0.0


def test_missing_relation_status_defaults_to_lost():
    gold = _gold([], [{"id": "r1"}])
    verdict = _verdict({}, {})
    blind = _blind("c", {}, {"r1": 3})
    result = score_spr(gold, verdict, blind)
    assert result["task_weighted_relation_recall"] == 0.0


# --- compare_weights() / spearman_rho() ---

def test_compare_weights_exact_agreement_uses_round_half_up_on_legacy_scale():
    # legacy 2.5 rounds up to 3 -- matches a blind weight of 3 exactly
    facts = [{"id": "f1", "weight": 2.5}, {"id": "f2", "weight": 1}]
    blind_weights = {"f1": 3, "f2": 1}
    result = compare_weights(facts, blind_weights)
    assert result["exact_agreement_rate"] == 1.0
    assert result["mean_abs_diff_legacy_scale"] == 0.25  # |2.5-3| + |1-1| over 2 = 0.25


def test_compare_weights_disagreement_is_captured():
    facts = [{"id": "f1", "weight": 1}, {"id": "f2", "weight": 3}]
    blind_weights = {"f1": 3, "f2": 1}
    result = compare_weights(facts, blind_weights)
    assert result["exact_agreement_rate"] == 0.0
    assert result["mean_abs_diff_legacy_scale"] == 2.0
    assert len(result["largest_disagreements"]) == 2


def test_compare_weights_handles_empty_facts():
    result = compare_weights([], {})
    assert result["n_facts"] == 0
    assert result["exact_agreement_rate"] is None
    assert result["spearman_rho"] is None


def test_round_half_up():
    assert _round_half_up(2.5) == 3
    assert _round_half_up(1.5) == 2
    assert _round_half_up(1.0) == 1
    assert _round_half_up(2.4) == 2


def test_spearman_rho_perfect_agreement():
    assert spearman_rho([1, 2, 3], [1, 2, 3]) == 1.0


def test_spearman_rho_perfect_disagreement():
    assert spearman_rho([1, 2, 3], [3, 2, 1]) == -1.0


def test_spearman_rho_undefined_when_one_side_constant():
    assert spearman_rho([1, 1, 1], [1, 2, 3]) is None


def test_spearman_rho_undefined_below_two_points():
    assert spearman_rho([1], [1]) is None


def test_deterministic_regeneration_of_real_corpus():
    """Re-running spr.py's main() against the committed judged/gold/blind_weights
    files must reproduce results/spr.json byte-for-byte -- no model call, no
    randomness, pure arithmetic over already-committed inputs."""
    import json
    import subprocess

    here = Path(__file__).parent
    root = here.parent
    before = (root / "results" / "spr.json").read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(here / "spr.py")], cwd=str(root), check=True, capture_output=True)
    after = (root / "results" / "spr.json").read_text(encoding="utf-8")
    assert json.loads(before) == json.loads(after)
