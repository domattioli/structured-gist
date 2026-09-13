#!/usr/bin/env python3
"""
QMSum selection: builds the eligibility pool from the official test split
of all three domains (Academic/Committee/Product), then picks 24 cases
deterministically.

Inputs are read only from the local cache populated by fetch_sources.py
(--dataset qmsum). No network. No structured-gist output is read,
generated, or referenced anywhere in this module.

Candidate = one (meeting, specific_query) pair. QMSum's published jsonl
splits carry no per-meeting ID field, so each meeting's real upstream ID
(an ICSI/AMI/committee-corpus identifier such as "Bed006" or "ES2002a") is
recovered by exact content match against data/<domain>/all/<id>.json,
which QMSum does publish with native filenames.

Eligibility (a candidate must have all of):
  - drawn from specific_query_list, never general_query_list
  - non-empty reference answer
  - non-empty relevant_text_span
  - every span is a valid, in-bounds [start, end] pair over
    meeting_transcripts (start/end parse as int, 0 <= start <= end < len)
  - the meeting's native ID resolves via the content-hash join above

Stratification:
  - domain quota: 8 Academic / 8 Committee / 8 Product (fixed, per the
    task brief's "closest feasible balance" instruction -- Academic's
    published test split has zero multi-span specific queries, so an
    even per-domain single/multi split is not available; see below)
  - single/multi quota: allocated by a deterministic scarcity-first rule,
    not by hand-picking a number that happens to hit 12/12. Domains are
    processed in ascending order of *available* multi-span candidates
    (ties broken alphabetically); each domain is given
    min(remaining_multi_target, available_in_domain, domain_quota)
    multi-span slots, and the rest of its quota is filled with
    single-span candidates. remaining_multi_target starts at 12 (this
    corpus's stated target for the corpus-wide multi/single split).
  - within a domain's single-pool and multi-pool separately, candidates
    are ordered by corpus_lib.selection_sort_key("qmsum", candidate_id)
    (ascending hex) and the first N are taken -- this is the "no manual
    cherry-picking" rule the task brief requires.

Run: python3 select_qmsum.py --cache-dir <path> --out qmsum/selection.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from corpus_lib import canonical_json_bytes, selection_sort_key, sha256_hex, word_count  # noqa: E402

DOMAINS = ["Academic", "Committee", "Product"]
DOMAIN_QUOTA = 8
GLOBAL_MULTI_TARGET = 12


def _load_all_meetings_index(cache_dir: Path, domain: str) -> dict[str, str]:
    """hash(meeting_transcripts) -> native meeting id, for one domain."""
    index = {}
    d = cache_dir / "qmsum" / "data" / domain / "all"
    for fp in sorted(d.glob("*.json")):
        obj = json.loads(fp.read_text("utf-8"))
        key = sha256_hex(canonical_json_bytes(obj["meeting_transcripts"]))
        index[key] = fp.stem
    return index


def _resolve_span(span: list, n_turns: int) -> tuple[int, int] | None:
    if not isinstance(span, list) or len(span) != 2:
        return None
    try:
        start, end = int(span[0]), int(span[1])
    except (TypeError, ValueError):
        return None
    if start < 0 or end < 0 or start > end or end >= n_turns:
        return None
    return start, end


def build_pool(cache_dir: Path) -> tuple[list[dict], dict]:
    rejects = defaultdict(int)
    general_query_count = 0
    pool = []

    for domain in DOMAINS:
        native_index = _load_all_meetings_index(cache_dir, domain)
        test_path = cache_dir / "qmsum" / "jsonl" / domain / "test.jsonl"
        lines = [l for l in test_path.read_text("utf-8").splitlines() if l.strip()]

        for line_idx, line in enumerate(lines):
            meeting = json.loads(line)
            transcripts = meeting["meeting_transcripts"]
            n_turns = len(transcripts)
            mkey = sha256_hex(canonical_json_bytes(transcripts))
            native_id = native_index.get(mkey)
            if native_id is None:
                rejects["meeting_native_id_unresolved"] += 1
                continue

            general_query_count += len(meeting.get("general_query_list", []))
            source_word_count = sum(word_count(t["content"]) for t in transcripts)

            for qidx, q in enumerate(meeting.get("specific_query_list", [])):
                query = (q.get("query") or "").strip()
                answer = (q.get("answer") or "").strip()
                spans_raw = q.get("relevant_text_span") or []

                if not query:
                    rejects["empty_query"] += 1
                    continue
                if not answer:
                    rejects["empty_answer"] += 1
                    continue
                if not spans_raw:
                    rejects["empty_relevant_span"] += 1
                    continue

                resolved_spans = []
                malformed = False
                for span in spans_raw:
                    r = _resolve_span(span, n_turns)
                    if r is None:
                        malformed = True
                        break
                    resolved_spans.append(r)
                if malformed:
                    rejects["malformed_or_out_of_bounds_span"] += 1
                    continue

                candidate_id = f"{domain}:{native_id}:sq{qidx}"
                pool.append(
                    {
                        "domain": domain,
                        "native_meeting_id": native_id,
                        "test_line_index": line_idx,
                        "query_index": qidx,
                        "candidate_id": candidate_id,
                        "sort_key": selection_sort_key("qmsum", candidate_id),
                        "query": query,
                        "answer": answer,
                        "relevant_text_span": spans_raw,
                        "resolved_spans": resolved_spans,
                        "cardinality": "single" if len(resolved_spans) == 1 else "multi",
                        "n_spans": len(resolved_spans),
                        "source_word_count": source_word_count,
                        "n_turns": n_turns,
                    }
                )

    stats = {
        "rejections": dict(rejects),
        "general_queries_seen": general_query_count,
        "eligible_pool_size": len(pool),
        "eligible_by_domain": {
            d: sum(1 for c in pool if c["domain"] == d) for d in DOMAINS
        },
        "eligible_cardinality_by_domain": {
            d: {
                "single": sum(1 for c in pool if c["domain"] == d and c["cardinality"] == "single"),
                "multi": sum(1 for c in pool if c["domain"] == d and c["cardinality"] == "multi"),
            }
            for d in DOMAINS
        },
    }
    return pool, stats


def select(pool: list[dict], stats: dict) -> dict:
    by_domain = defaultdict(list)
    for c in pool:
        by_domain[c["domain"]].append(c)

    avail_multi = {
        d: sum(1 for c in by_domain[d] if c["cardinality"] == "multi") for d in DOMAINS
    }
    # scarcity-first: fewest available multi candidates processed first,
    # ties broken alphabetically by domain name.
    domain_order = sorted(DOMAINS, key=lambda d: (avail_multi[d], d))

    remaining_multi_target = GLOBAL_MULTI_TARGET
    multi_quota = {}
    for d in domain_order:
        take = min(remaining_multi_target, avail_multi[d], DOMAIN_QUOTA)
        multi_quota[d] = take
        remaining_multi_target -= take

    selected = []
    selection_trace = {}
    for d in DOMAINS:
        multi_pool = sorted(
            (c for c in by_domain[d] if c["cardinality"] == "multi"),
            key=lambda c: c["sort_key"],
        )
        single_pool = sorted(
            (c for c in by_domain[d] if c["cardinality"] == "single"),
            key=lambda c: c["sort_key"],
        )
        n_multi = multi_quota[d]
        n_single = DOMAIN_QUOTA - n_multi
        picked_multi = multi_pool[:n_multi]
        picked_single = single_pool[:n_single]
        selected.extend(picked_multi)
        selected.extend(picked_single)
        selection_trace[d] = {
            "multi_quota": n_multi,
            "single_quota": n_single,
            "multi_available": len(multi_pool),
            "single_available": len(single_pool),
            "picked_multi_ids": [c["candidate_id"] for c in picked_multi],
            "picked_single_ids": [c["candidate_id"] for c in picked_single],
        }

    selected.sort(key=lambda c: (c["domain"], c["sort_key"]))

    wcs = sorted(c["source_word_count"] for c in selected)
    n = len(wcs)
    quantile = lambda q: wcs[min(n - 1, int(q * (n - 1)))]  # noqa: E731

    result = {
        "dataset": "qmsum",
        "eligibility_stats": stats,
        "domain_quota": DOMAIN_QUOTA,
        "global_multi_target": GLOBAL_MULTI_TARGET,
        "scarcity_domain_order": domain_order,
        "availability": {"multi": avail_multi},
        "selection_trace": selection_trace,
        "selected_count": len(selected),
        "cardinality_totals": {
            "single": sum(1 for c in selected if c["cardinality"] == "single"),
            "multi": sum(1 for c in selected if c["cardinality"] == "multi"),
        },
        "domain_totals": {d: sum(1 for c in selected if c["domain"] == d) for d in DOMAINS},
        "source_word_count_distribution": {
            "min": wcs[0] if wcs else None,
            "p25": quantile(0.25) if wcs else None,
            "median": quantile(0.5) if wcs else None,
            "p75": quantile(0.75) if wcs else None,
            "max": wcs[-1] if wcs else None,
        },
        "selected_candidates": selected,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    pool, stats = build_pool(args.cache_dir)
    result = select(pool, stats)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical_json_bytes(result))

    print(f"[qmsum] eligible pool: {stats['eligible_pool_size']}")
    print(f"[qmsum] rejections: {stats['rejections']}")
    print(f"[qmsum] selected: {result['selected_count']} "
          f"(single={result['cardinality_totals']['single']}, "
          f"multi={result['cardinality_totals']['multi']})")
    print(f"[qmsum] domain totals: {result['domain_totals']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
