#!/usr/bin/env python3
"""
Deterministic pytest tests for scoring/combine.py's arithmetic, focused on
the semantic-sufficiency formalization: `semantic_sufficiency` must be the
exact same number as the historical `weighted_retention` (an alias, not an
independently computed metric), and the new case-level `intent` /
per-fact `weight_reason` schema fields must not be consumed by any
arithmetic -- they exist only to make an already-computed weight
interpretable.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from combine import score_semantic  # noqa: E402


def _gold(facts, relations=None, questions=None, extra=None):
    g = {"facts": facts, "relations": relations or [], "questions": questions or []}
    if extra:
        g.update(extra)
    return g


def _verdict(fact_status, rel_status=None, q_verdict=None, hallucinations=None):
    return {
        "facts": {fid: {"status": st} for fid, st in fact_status.items()},
        "relations": {rid: {"status": st} for rid, st in (rel_status or {}).items()},
        "questions": {qid: {"verdict": v} for qid, v in (q_verdict or {}).items()},
        "hallucinations": hallucinations or [],
    }


# A fixture with hand-calculable weights: f1 weight 3 retained (3.0),
# f2 weight 1 partial (0.5), f3 weight 2 omitted (0.0).
# total_weight = 6, weighted_units = 3.5 -> 3.5/6 = 0.583333... -> 0.5833
FACTS = [
    {"id": "f1", "text": "a", "category": "decision", "weight": 3},
    {"id": "f2", "text": "b", "category": "descriptive", "weight": 1},
    {"id": "f3", "text": "c", "category": "outcome", "weight": 2},
]
RELATIONS = [
    {"id": "r1", "type": "causal", "text": "a->b", "fact_ids": ["f1", "f2"]},
    {"id": "r2", "type": "causal", "text": "b->c", "fact_ids": ["f2", "f3"]},
]
QUESTIONS = [{"id": "q1", "question": "?", "gold_answer": "a", "fact_ids": ["f1"]}]


def test_semantic_sufficiency_matches_hand_calculation():
    gold = _gold(FACTS, RELATIONS, QUESTIONS)
    verdict = _verdict(
        {"f1": "retained", "f2": "partial", "f3": "omitted"},
        {"r1": "retained", "r2": "lost"},
        {"q1": "correct"},
    )
    result = score_semantic(gold, verdict)
    assert result["semantic_sufficiency"] == 0.5833
    assert result["unweighted_retention"] == round((1.0 + 0.5 + 0.0) / 3, 4)
    assert result["relation_retention"] == 0.5
    assert result["recoverability"] == 1.0


def test_weighted_retention_is_an_exact_alias_of_semantic_sufficiency():
    gold = _gold(FACTS, RELATIONS, QUESTIONS)
    for fact_status in (
        {"f1": "retained", "f2": "retained", "f3": "retained"},
        {"f1": "omitted", "f2": "omitted", "f3": "omitted"},
        {"f1": "mutated", "f2": "partial", "f3": "retained"},
    ):
        verdict = _verdict(fact_status)
        result = score_semantic(gold, verdict)
        assert result["weighted_retention"] == result["semantic_sufficiency"]


def test_mutated_scores_as_zero_like_omitted():
    gold = _gold(FACTS)
    mutated = score_semantic(gold, _verdict({"f1": "mutated", "f2": "omitted", "f3": "omitted"}))
    omitted = score_semantic(gold, _verdict({"f1": "omitted", "f2": "omitted", "f3": "omitted"}))
    assert mutated["semantic_sufficiency"] == omitted["semantic_sufficiency"]


def test_missing_fact_status_defaults_to_omitted():
    gold = _gold(FACTS)
    result = score_semantic(gold, _verdict({}))
    assert result["semantic_sufficiency"] == 0.0


def test_intent_and_weight_reason_do_not_affect_arithmetic():
    """
    intent (case-level) and weight_reason (per-fact) are audit metadata,
    consumed by README/SCORES.md presentation, never by scoring arithmetic.
    """
    plain_gold = _gold(FACTS, RELATIONS, QUESTIONS)
    annotated_facts = [dict(f) for f in FACTS]
    annotated_facts[0]["weight_reason"] = "this is the corrected conclusion the case tests"
    annotated_gold = _gold(
        annotated_facts,
        RELATIONS,
        QUESTIONS,
        extra={"intent": {"reader": "someone", "task": "something"}},
    )

    verdict = _verdict(
        {"f1": "retained", "f2": "partial", "f3": "omitted"},
        {"r1": "retained", "r2": "lost"},
        {"q1": "correct"},
    )
    assert score_semantic(plain_gold, verdict) == score_semantic(annotated_gold, verdict)


def test_missing_intent_and_weight_reason_handled_deliberately():
    """gold.json without `intent` or any `weight_reason` must still score cleanly."""
    gold = _gold(FACTS)  # no "intent" key, no fact carries "weight_reason"
    result = score_semantic(gold, _verdict({"f1": "retained", "f2": "retained", "f3": "retained"}))
    assert result["semantic_sufficiency"] == 1.0


def test_no_facts_does_not_divide_by_zero():
    gold = _gold([])
    result = score_semantic(gold, _verdict({}))
    assert result["semantic_sufficiency"] == 0.0
    assert result["unweighted_retention"] is None


def test_unsupported_claim_correction_unaffected_by_this_change():
    gold = _gold(FACTS)
    verdict = _verdict(
        {"f1": "retained", "f2": "retained", "f3": "retained"},
        hallucinations=[
            {"claim": "verbatim source text gold didn't extract", "source_supported": True},
            {"claim": "actually invented", "source_supported": False},
        ],
    )
    result = score_semantic(gold, verdict)
    assert result["unsupported_claim_count"] == 1
    assert result["flagged_vs_gold_count"] == 2


def test_score_semantic_is_deterministic():
    gold = _gold(FACTS, RELATIONS, QUESTIONS)
    verdict = _verdict(
        {"f1": "retained", "f2": "partial", "f3": "omitted"},
        {"r1": "retained", "r2": "lost"},
        {"q1": "correct"},
    )
    assert score_semantic(gold, verdict) == score_semantic(gold, verdict)
