#!/usr/bin/env python3
"""
HotpotQA selection: builds the eligibility pool from the official
distractor dev split, then picks 8 cases deterministically. This is
explicitly a `pressure_only` set (see MANIFEST.json / README.md), not part
of the headline external-validation average.

Inputs are read only from the local cache populated by fetch_sources.py
(--dataset hotpotqa). No network. No structured-gist output is read,
generated, or referenced anywhere in this module.

Every row in the distractor dev split is already `level == "hard"` (the
whole split is hard-level by construction -- there is nothing to filter
there). The remaining eligibility work:

  - `type == "bridge"`: comparison-type questions ("were X and Y the same
    nationality?") can be answerable fact-by-fact without genuinely
    chaining one fact into the next; bridge questions are the genuinely
    compositional ones and are abundant in this split (5918 of 7405), so
    this corpus requires bridge and does not fall back to comparison.
  - a non-empty `answer`
  - at least 2 supporting facts, spanning at least 2 distinct paragraph
    titles (a same-paragraph pair would not be a real multi-location
    pressure test)
  - every supporting fact resolves exactly: its title exists in `context`
    and its sentence index is in range for that paragraph
  - the full 10-paragraph distractor context is present (>=8 paragraphs,
    guards against a truncated/malformed row -- the intact distractor set
    is what keeps this a retrieval pressure test rather than a
    evidence-only toy)

Selection: the eligible pool is single (no domain/type strata beyond the
bridge/hard filter already applied), so the 8 cases are simply the first 8
by corpus_lib.selection_sort_key("hotpotqa", candidate_id) ascending --
the same no-cherry-picking rule used for the other two datasets.

Run: python3 select_hotpotqa.py --cache-dir <path> --out hotpotqa/selection.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from corpus_lib import canonical_json_bytes, selection_sort_key, word_count  # noqa: E402

QUOTA = 8
MIN_CONTEXT_PARAGRAPHS = 8


def build_pool(cache_dir: Path) -> tuple[list[dict], dict]:
    path = cache_dir / "hotpotqa" / "distractor_validation.jsonl"
    rejects = defaultdict(int)
    pool = []
    n_seen = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            n_seen += 1
            row = json.loads(line)

            if row.get("type") != "bridge":
                rejects["not_bridge_type"] += 1
                continue
            answer = (row.get("answer") or "").strip()
            if not answer:
                rejects["empty_answer"] += 1
                continue

            sf = row.get("supporting_facts") or {}
            sf_titles = sf.get("title") or []
            sf_sent_ids = sf.get("sent_id") or []
            if len(sf_titles) != len(sf_sent_ids) or len(sf_titles) < 2:
                rejects["fewer_than_2_supporting_facts"] += 1
                continue

            ctx = row.get("context") or {}
            ctx_titles = ctx.get("title") or []
            ctx_sentences = ctx.get("sentences") or []
            if len(ctx_titles) < MIN_CONTEXT_PARAGRAPHS:
                rejects["insufficient_distractor_context"] += 1
                continue
            title_to_sentences = dict(zip(ctx_titles, ctx_sentences))

            resolved = []
            malformed = False
            for title, sent_id in zip(sf_titles, sf_sent_ids):
                sentences = title_to_sentences.get(title)
                if sentences is None or not (0 <= sent_id < len(sentences)):
                    malformed = True
                    break
                resolved.append({"title": title, "sent_id": sent_id, "text": sentences[sent_id]})
            if malformed:
                rejects["supporting_fact_unresolved"] += 1
                continue

            distinct_titles = sorted({r["title"] for r in resolved})
            if len(distinct_titles) < 2:
                rejects["supporting_facts_single_location"] += 1
                continue

            candidate_id = row["id"]
            source_word_count = sum(
                word_count(s) for sentences in ctx_sentences for s in sentences
            )

            pool.append(
                {
                    "hotpot_id": candidate_id,
                    "candidate_id": candidate_id,
                    "sort_key": selection_sort_key("hotpotqa", candidate_id),
                    "question": row["question"],
                    "answer": answer,
                    "type": row["type"],
                    "level": row["level"],
                    "supporting_facts": resolved,
                    "n_supporting_facts": len(resolved),
                    "n_distinct_titles": len(distinct_titles),
                    "distinct_titles": distinct_titles,
                    "context_titles": ctx_titles,
                    "context_sentences": ctx_sentences,
                    "n_context_paragraphs": len(ctx_titles),
                    "source_word_count": source_word_count,
                }
            )

    stats = {
        "n_rows_seen": n_seen,
        "rejections": dict(rejects),
        "eligible_pool_size": len(pool),
    }
    return pool, stats


def select(pool: list[dict], stats: dict) -> dict:
    ordered = sorted(pool, key=lambda c: c["sort_key"])
    selected = ordered[:QUOTA]

    wcs = sorted(c["source_word_count"] for c in selected)
    sfs = sorted(c["n_supporting_facts"] for c in selected)
    n = len(wcs)
    quantile = lambda vals, q: vals[min(len(vals) - 1, int(q * (len(vals) - 1)))]  # noqa: E731

    return {
        "dataset": "hotpotqa",
        "pressure_only": True,
        "eligibility_stats": stats,
        "quota": QUOTA,
        "selected_count": len(selected),
        "supporting_fact_count_distribution": {
            "min": sfs[0] if sfs else None,
            "median": quantile(sfs, 0.5) if sfs else None,
            "max": sfs[-1] if sfs else None,
        },
        "source_word_count_distribution": {
            "min": wcs[0] if wcs else None,
            "median": quantile(wcs, 0.5) if wcs else None,
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

    print(f"[hotpotqa] eligible pool: {stats['eligible_pool_size']} (of {stats['n_rows_seen']} rows)")
    print(f"[hotpotqa] rejections: {stats['rejections']}")
    print(f"[hotpotqa] selected: {result['selected_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
