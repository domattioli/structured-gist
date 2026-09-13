#!/usr/bin/env python3
"""
Qasper selection: builds the eligibility pool from the official dev-v0.3
split (public gold annotations), then picks 10 cases deterministically.

Inputs are read only from the local cache populated by fetch_sources.py
(--dataset qasper). No network. No structured-gist output is read,
generated, or referenced anywhere in this module.

Candidate = one (paper, question) pair, using each question's first
annotator answer (`qas[i]['answers'][0]`) as the primary human answer --
first-in-file-order, not hand-picked, and the same choice every rerun of
this script makes against the same pinned dev-v0.3.json.

Eligibility (a candidate must have all of):
  - the primary answer is not `unanswerable`
  - the primary answer has extractive_spans, a free_form_answer, or a
    yes_no value (i.e. an actual human answer exists)
  - the primary answer has a non-empty `evidence` list
  - at least one evidence entry is textual (not `FLOAT SELECTED ...`,
    which points at a figure/table image this corpus does not carry) and
    resolves by exact (whitespace-normalized) match to a paragraph in the
    paper's `full_text`
  - every *textual* evidence entry resolves this way -- one that doesn't
    match any paragraph is treated as a malformed annotation and the
    whole candidate is rejected, not silently dropped

Evidence cardinality = number of distinct resolved paragraph locations
(deduplicated by flattened paragraph index), not the raw evidence-string
count. Evidence distance (multi-evidence candidates only) = the flattened
paragraph-index spread between the closest and farthest resolved
locations, bucketed mechanically: nearby <=2, moderate 3-10, wide >10.

Composition: 7 multi-evidence + 3 single-evidence (fixed by the task
brief). The 7 multi-evidence slots are spread across the three distance
buckets by corpus_lib.scarcity_first_allocate with a per-bucket cap of
ceil(7/3)=3 (scarcest bucket claims its own candidates first, up to the
cap; without the cap, scarcity-first degenerates to handing the entire
quota to whichever single bucket is scarcest, which defeats the point of
covering multiple distances). Within each bucket/pool, candidates are
ordered by corpus_lib.selection_sort_key("qasper", candidate_id) and the
first N are taken.

Run: python3 select_qasper.py --cache-dir <path> --out qasper/selection.json
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from corpus_lib import canonical_json_bytes, scarcity_first_allocate, selection_sort_key, word_count  # noqa: E402

MULTI_QUOTA = 7
SINGLE_QUOTA = 3
DISTANCE_BUCKETS = {"nearby": (0, 2), "moderate": (3, 10), "wide": (11, float("inf"))}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _distance_bucket(distance: int) -> str:
    for name, (lo, hi) in DISTANCE_BUCKETS.items():
        if lo <= distance <= hi:
            return name
    raise AssertionError(distance)


def _flatten_paragraphs(full_text: list[dict]) -> list[dict]:
    flat = []
    gidx = 0
    for sidx, section in enumerate(full_text):
        for pidx, para in enumerate(section.get("paragraphs", [])):
            flat.append(
                {
                    "global_idx": gidx,
                    "section_idx": sidx,
                    "para_idx": pidx,
                    "section_name": section.get("section_name") or "",
                    "text": para,
                    "norm": _norm(para),
                }
            )
            gidx += 1
    return flat


def _answer_text(answer: dict) -> tuple[str, str]:
    """Returns (answer_type, rendered_text)."""
    if answer.get("extractive_spans"):
        return "extractive", " | ".join(answer["extractive_spans"])
    if (answer.get("free_form_answer") or "").strip():
        return "free_form", answer["free_form_answer"].strip()
    if answer.get("yes_no") is not None:
        return "yes_no", "Yes" if answer["yes_no"] else "No"
    return "none", ""


def build_pool(cache_dir: Path) -> tuple[list[dict], dict]:
    data = json.loads((cache_dir / "qasper" / "qasper-dev-v0.3.json").read_text("utf-8"))
    rejects = defaultdict(int)
    pool = []
    n_questions = 0

    for arxiv_id, paper in data.items():
        flat = _flatten_paragraphs(paper.get("full_text", []))
        by_norm = defaultdict(list)
        for p in flat:
            by_norm[p["norm"]].append(p)

        for qa in paper.get("qas", []):
            n_questions += 1
            question_id = qa["question_id"]
            answers = qa.get("answers") or []
            if not answers:
                rejects["no_answers"] += 1
                continue
            primary = answers[0]["answer"]

            if primary.get("unanswerable"):
                rejects["unanswerable"] += 1
                continue

            answer_type, answer_text = _answer_text(primary)
            if answer_type == "none":
                rejects["empty_answer"] += 1
                continue

            evidence = primary.get("evidence") or []
            if not evidence:
                rejects["empty_evidence"] += 1
                continue

            resolved = []
            float_evidence = []
            unresolved = False
            for ev in evidence:
                if ev.strip().startswith("FLOAT SELECTED"):
                    float_evidence.append(ev)
                    continue
                matches = by_norm.get(_norm(ev))
                if not matches:
                    unresolved = True
                    break
                resolved.append(matches[0])
            if unresolved:
                rejects["evidence_location_unresolved"] += 1
                continue

            distinct = {}
            for r in resolved:
                distinct[r["global_idx"]] = r
            locations = sorted(distinct.values(), key=lambda r: r["global_idx"])

            if not locations:
                rejects["float_only_evidence"] += 1
                continue

            cardinality = "single" if len(locations) == 1 else "multi"
            distance = locations[-1]["global_idx"] - locations[0]["global_idx"] if len(locations) > 1 else 0
            candidate_id = f"{arxiv_id}:{question_id}"
            source_word_count = sum(word_count(p["text"]) for p in flat) + word_count(paper.get("abstract", ""))

            pool.append(
                {
                    "arxiv_id": arxiv_id,
                    "paper_title": paper.get("title", ""),
                    "question_id": question_id,
                    "candidate_id": candidate_id,
                    "sort_key": selection_sort_key("qasper", candidate_id),
                    "question": qa["question"],
                    "answer_type": answer_type,
                    "answer_text": answer_text,
                    "n_annotators": len(answers),
                    "nlp_background": qa.get("nlp_background", ""),
                    "topic_background": qa.get("topic_background", ""),
                    "evidence_raw": evidence,
                    "float_evidence": float_evidence,
                    "resolved_locations": [
                        {
                            "global_idx": r["global_idx"],
                            "section_idx": r["section_idx"],
                            "para_idx": r["para_idx"],
                            "section_name": r["section_name"],
                        }
                        for r in locations
                    ],
                    "cardinality": cardinality,
                    "n_evidence_locations": len(locations),
                    "evidence_distance": distance,
                    "distance_bucket": _distance_bucket(distance) if cardinality == "multi" else "n/a",
                    "source_word_count": source_word_count,
                    "n_paragraphs": len(flat),
                }
            )

    stats = {
        "n_papers": len(data),
        "n_questions_seen": n_questions,
        "rejections": dict(rejects),
        "eligible_pool_size": len(pool),
        "eligible_cardinality": {
            "single": sum(1 for c in pool if c["cardinality"] == "single"),
            "multi": sum(1 for c in pool if c["cardinality"] == "multi"),
        },
        "eligible_distance_buckets": {
            b: sum(1 for c in pool if c["distance_bucket"] == b) for b in DISTANCE_BUCKETS
        },
    }
    return pool, stats


def select(pool: list[dict], stats: dict) -> dict:
    multi_pool = [c for c in pool if c["cardinality"] == "multi"]
    single_pool = [c for c in pool if c["cardinality"] == "single"]

    availability = {b: sum(1 for c in multi_pool if c["distance_bucket"] == b) for b in DISTANCE_BUCKETS}
    # per-bucket cap = ceil(quota / n_buckets): without a cap, scarcity-first
    # degenerates to "hand everything to the single scarcest bucket" once
    # that bucket alone can cover the whole quota. The cap is what actually
    # forces the "cover different evidence distances" requirement; scarcity
    # ordering still governs who gets first claim within that cap.
    cap = math.ceil(MULTI_QUOTA / len(DISTANCE_BUCKETS))
    bucket_quota = scarcity_first_allocate(availability, MULTI_QUOTA, per_key_cap=cap)

    selected = []
    bucket_trace = {}
    for bucket in DISTANCE_BUCKETS:
        bucket_pool = sorted(
            (c for c in multi_pool if c["distance_bucket"] == bucket), key=lambda c: c["sort_key"]
        )
        n = bucket_quota[bucket]
        picked = bucket_pool[:n]
        selected.extend(picked)
        bucket_trace[bucket] = {
            "quota": n,
            "available": len(bucket_pool),
            "picked_ids": [c["candidate_id"] for c in picked],
        }

    single_sorted = sorted(single_pool, key=lambda c: c["sort_key"])
    picked_single = single_sorted[:SINGLE_QUOTA]
    selected.extend(picked_single)

    selected.sort(key=lambda c: c["sort_key"])

    wcs = sorted(c["source_word_count"] for c in selected)
    n = len(wcs)
    quantile = lambda q: wcs[min(n - 1, int(q * (n - 1)))]  # noqa: E731

    return {
        "dataset": "qasper",
        "eligibility_stats": stats,
        "multi_quota": MULTI_QUOTA,
        "single_quota": SINGLE_QUOTA,
        "distance_bucket_definition": {k: list(v) for k, v in DISTANCE_BUCKETS.items()},
        "distance_bucket_trace": bucket_trace,
        "single_trace": {
            "quota": SINGLE_QUOTA,
            "available": len(single_sorted),
            "picked_ids": [c["candidate_id"] for c in picked_single],
        },
        "selected_count": len(selected),
        "cardinality_totals": {
            "single": sum(1 for c in selected if c["cardinality"] == "single"),
            "multi": sum(1 for c in selected if c["cardinality"] == "multi"),
        },
        "distance_bucket_totals": {
            b: sum(1 for c in selected if c["distance_bucket"] == b) for b in DISTANCE_BUCKETS
        },
        "source_word_count_distribution": {
            "min": wcs[0] if wcs else None,
            "p25": quantile(0.25) if wcs else None,
            "median": quantile(0.5) if wcs else None,
            "p75": quantile(0.75) if wcs else None,
            "max": wcs[-1] if wcs else None,
        },
        "selected_candidates": selected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    pool, stats = build_pool(args.cache_dir)
    result = select(pool, stats)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical_json_bytes(result))

    print(f"[qasper] eligible pool: {stats['eligible_pool_size']} (of {stats['n_questions_seen']} questions)")
    print(f"[qasper] rejections: {stats['rejections']}")
    print(f"[qasper] selected: {result['selected_count']} "
          f"(single={result['cardinality_totals']['single']}, multi={result['cardinality_totals']['multi']})")
    print(f"[qasper] distance buckets: {result['distance_bucket_totals']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
