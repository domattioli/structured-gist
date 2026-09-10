#!/usr/bin/env python3
"""
Simple, deliberately unsophisticated overlap diagnostics between two
independent Stage-A annotators (annotator_a.json / annotator_b.json) for
each calibration case. Per the task brief: "do NOT invent a sophisticated
agreement metric -- we mainly need to know: is the adapter sufficiently
stable that another competent blind annotator produces materially the
same task-relevant inventory?"

No model calls. Pure text/set overlap over the two annotators' own
output files.

Metrics reported per case:
  - fact_count_a / fact_count_b / fact_count_ratio (min/max, 1.0 = equal)
  - native_evidence_id Jaccard: overlap of which native evidence each
    annotator's facts cite, over the union
  - source_quote word-overlap: for each fact in A, its best word-level
    Jaccard match among B's facts (and vice versa), averaged -- a rough
    "did they extract the same underlying propositions" signal, not a
    claim about paraphrase quality
  - relation_count_a / relation_count_b, and whether both annotators
    agree on "any relations at all" (both empty, both non-empty, or
    disagree)

Run: python3 compare_calibration.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

STOPWORDS = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is",
    "are", "was", "were", "be", "been", "that", "this", "it", "as", "by",
    "with", "at", "from", "which", "who", "its", "their", "his", "her",
}


def _words(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {t for t in tokens if t not in STOPWORDS and len(t) > 1}


def _jaccard(a: set, b: set) -> float | None:
    if not a and not b:
        return None
    union = a | b
    if not union:
        return None
    return len(a & b) / len(union)


def _best_match_overlap(facts_a: list[dict], facts_b: list[dict]) -> float | None:
    if not facts_a or not facts_b:
        return None
    word_sets_b = [_words(f.get("source_quote", "")) for f in facts_b]
    scores = []
    for f in facts_a:
        wa = _words(f.get("source_quote", ""))
        best = max((_jaccard(wa, wb) or 0.0) for wb in word_sets_b) if word_sets_b else 0.0
        scores.append(best)
    return sum(scores) / len(scores) if scores else None


def compare_case(case_id: str) -> dict:
    case_dir = HERE / case_id
    a = json.loads((case_dir / "annotator_a.json").read_text("utf-8"))
    b = json.loads((case_dir / "annotator_b.json").read_text("utf-8"))

    facts_a, facts_b = a.get("facts", []), b.get("facts", [])
    rels_a, rels_b = a.get("relations", []), b.get("relations", [])

    evidence_a = {ref["native_evidence_id"] for f in facts_a for ref in f.get("derived_from", [])}
    evidence_b = {ref["native_evidence_id"] for f in facts_b for ref in f.get("derived_from", [])}

    n_a, n_b = len(facts_a), len(facts_b)
    fact_count_ratio = (min(n_a, n_b) / max(n_a, n_b)) if max(n_a, n_b) else None

    overlap_a_to_b = _best_match_overlap(facts_a, facts_b)
    overlap_b_to_a = _best_match_overlap(facts_b, facts_a)

    return {
        "case_id": case_id,
        "fact_count_a": n_a,
        "fact_count_b": n_b,
        "fact_count_ratio": round(fact_count_ratio, 3) if fact_count_ratio is not None else None,
        "native_evidence_id_jaccard": round(j, 3) if (j := _jaccard(evidence_a, evidence_b)) is not None else None,
        "source_quote_overlap_a_to_b": round(overlap_a_to_b, 3) if overlap_a_to_b is not None else None,
        "source_quote_overlap_b_to_a": round(overlap_b_to_a, 3) if overlap_b_to_a is not None else None,
        "relation_count_a": len(rels_a),
        "relation_count_b": len(rels_b),
        "relation_existence_agreement": (len(rels_a) > 0) == (len(rels_b) > 0),
    }


def main() -> int:
    case_ids = sorted(p.name for p in HERE.iterdir() if p.is_dir())
    results = []
    for case_id in case_ids:
        if (HERE / case_id / "annotator_a.json").exists() and (HERE / case_id / "annotator_b.json").exists():
            results.append(compare_case(case_id))

    out = {"cases": results}
    (HERE / "calibration_comparison.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for r in results:
        print(
            f"{r['case_id']}: facts {r['fact_count_a']}/{r['fact_count_b']} "
            f"(ratio {r['fact_count_ratio']}), evidence_jaccard {r['native_evidence_id_jaccard']}, "
            f"quote_overlap a->b {r['source_quote_overlap_a_to_b']} b->a {r['source_quote_overlap_b_to_a']}, "
            f"relations {r['relation_count_a']}/{r['relation_count_b']} "
            f"(agree: {r['relation_existence_agreement']})"
        )
    print(f"\nWrote {HERE / 'calibration_comparison.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
