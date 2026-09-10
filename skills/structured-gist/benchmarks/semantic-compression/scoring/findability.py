#!/usr/bin/env python3
"""
Eval B: findability -- measurement only. Tests structured-gist's practical
thesis ("hierarchical structure makes the important information easier to
locate"), NOT its compression. See ../FINDABILITY_FINDINGS.md for the full
write-up, including a documented failure mode found and fixed before this
corpus's numbers were finalized (the literal per-question minimal baseline
the PR brief specifies is mathematically degenerate -- see "Baseline
construction" below and FINDABILITY_FINDINGS.md "Why the baseline is
case-level, not per-question").

Deliberately named "Evidence Access Cost", not "reading speed" or "human
findability" -- this is a deterministic proxy, not a timed-reader study.

Critical design requirement (from the PR brief): do NOT compare position in
full source directly against position in a much-shorter gist -- that mostly
measures deletion. This module instead builds a CONTENT-MATCHED baseline:
the same answer-supporting evidence (this case's gold facts/relations,
located via their source_quote spans, deduplicated and reassembled in
original source order) with structured-gist's hierarchy removed, so both
sides of every comparison hold the same underlying evidence content.

Alignment is entirely deterministic: exact normalized-token containment via
text_norm.py (no embeddings, no fuzzy/edit-distance matching, no model).
Where alignment fails, this reports the question as `not_findability_
scorable` with a specific reason -- it never falls back to approximate
matching and never rewards a rendering for evidence that was omitted or
whose provenance could not be confirmed.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = ROOT / "results"
TEST_CLASSES = ["regression", "pressure-tests"]
LEVELS = ["skim", "standard", "deep"]

sys.path.insert(0, str(HERE))
from outline_nodes import Node, extract_nodes, strip_marker_prefix  # noqa: E402
from text_norm import find_start, tokenize  # noqa: E402

STRICT_STATUSES = {"fact": {"retained"}, "relation": {"retained"}}
EXPLORATORY_STATUSES = {"fact": {"retained", "partial"}, "relation": {"retained", "partial"}}

_FRAGMENT_SPLIT = re.compile(r"\s*\.\.\.\s*|\s+/\s+")


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Span utilities
# ---------------------------------------------------------------------------

@dataclass
class Span:
    start: int
    end: int  # exclusive

    @property
    def length(self) -> int:
        return self.end - self.start


def merge_spans(spans: List[Span]) -> List[Span]:
    """Standard interval merge: sort by start, merge any two spans that
    touch or overlap (next.start <= current.end). Deterministic, stable
    for ties (Python sort is stable; ties broken by original list order,
    which callers pass in unit-id order for reproducibility)."""
    if not spans:
        return []
    ordered = sorted(spans, key=lambda s: s.start)
    merged = [Span(ordered[0].start, ordered[0].end)]
    for s in ordered[1:]:
        last = merged[-1]
        if s.start <= last.end:
            last.end = max(last.end, s.end)
        else:
            merged.append(Span(s.start, s.end))
    return merged


def naive_per_question_baseline_tokens(required_spans: List[Span], source_tokens: List[str]) -> List[str]:
    """The PR brief's literal 5-step per-question baseline: resolve support
    unit spans, dedupe overlaps, keep source order, concatenate -- nothing
    else. Kept ONLY as a diagnostic proving this construction is
    mathematically degenerate for EAC/EvidenceSpan (see
    test_naive_baseline_is_always_fully_traversed and
    FINDABILITY_FINDINGS.md); NOT used for this module's actual scoring,
    which uses a case-level baseline instead (build_case_baseline below)."""
    merged = merge_spans(required_spans)
    tokens: List[str] = []
    for s in merged:
        tokens.extend(source_tokens[s.start:s.end])
    return tokens


# ---------------------------------------------------------------------------
# Case-level content-matched baseline
# ---------------------------------------------------------------------------

@dataclass
class CaseBaseline:
    tokens: List[str]
    unit_pos: Dict[str, Span]          # unit id -> position within `tokens`
    unaligned_unit_ids: List[str]      # gold source_quote not found in source.md (integrity issue)
    merged_span_count: int
    ambiguous_unit_ids: List[str]      # source_quote occurs >1 time in source.md (first occurrence used)


def _count_occurrences(needle: List[str], haystack: List[str]) -> int:
    if not needle:
        return 0
    sep = "\x01"
    hay = sep + sep.join(haystack) + sep
    n = sep + sep.join(needle) + sep
    count, i = 0, 0
    while True:
        i = hay.find(n, i)
        if i == -1:
            break
        count += 1
        i += 1
    return count


def build_case_baseline(gold: dict, source_tokens: List[str]) -> CaseBaseline:
    """Case-level content-matched baseline: ALL of this case's gold facts +
    relations (not just one question's), located by source_quote,
    deduplicated by span overlap, kept in source order. See
    FINDABILITY_FINDINGS.md "Why the baseline is case-level" for why this
    is a deliberate, documented adaptation of the PR brief's literal
    per-question construction (which is mathematically degenerate)."""
    units = [("fact", f["id"], f["source_quote"]) for f in gold.get("facts", [])]
    units += [("relation", r["id"], r["source_quote"]) for r in gold.get("relations", [])]

    unaligned: List[str] = []
    ambiguous: List[str] = []
    unit_src_span: Dict[str, Span] = {}
    for _kind, uid, quote in units:
        qtok = tokenize(quote)
        start = find_start(qtok, source_tokens)
        if start is None:
            unaligned.append(uid)
            continue
        if _count_occurrences(qtok, source_tokens) > 1:
            ambiguous.append(uid)
        unit_src_span[uid] = Span(start, start + len(qtok))

    merged = merge_spans(list(unit_src_span.values()))

    # cumulative baseline-start offset for each merged span, in source order
    baseline_tokens: List[str] = []
    merged_baseline_start: List[int] = []
    for m in merged:
        merged_baseline_start.append(len(baseline_tokens))
        baseline_tokens.extend(source_tokens[m.start:m.end])

    def locate_in_baseline(span: Span) -> Span:
        for m, b_start in zip(merged, merged_baseline_start):
            if m.start <= span.start and span.end <= m.end:
                offset = span.start - m.start
                return Span(b_start + offset, b_start + offset + span.length)
        raise AssertionError("unit span not contained in any merged span -- merge_spans invariant violated")

    unit_pos = {uid: locate_in_baseline(span) for uid, span in unit_src_span.items()}

    return CaseBaseline(
        tokens=baseline_tokens,
        unit_pos=unit_pos,
        unaligned_unit_ids=unaligned,
        merged_span_count=len(merged),
        ambiguous_unit_ids=ambiguous,
    )


# ---------------------------------------------------------------------------
# Gist-side evidence location
# ---------------------------------------------------------------------------

@dataclass
class RenderingIndex:
    nodes: List[Node]
    tokens: List[str]              # every scorable node's tokens, concatenated in reading order
    node_token_range: List[Span]   # per node index -> its [start,end) in `tokens`


def build_rendering_index(text: str) -> RenderingIndex:
    nodes = extract_nodes(text)
    tokens: List[str] = []
    ranges: List[Span] = []
    for n in nodes:
        node_tokens = tokenize(n.text)
        ranges.append(Span(len(tokens), len(tokens) + len(node_tokens)))
        tokens.extend(node_tokens)
    return RenderingIndex(nodes=nodes, tokens=tokens, node_token_range=ranges)


def split_evidence_fragments(evidence: str) -> List[str]:
    """Judge-recorded `evidence` strings sometimes join multiple
    non-contiguous rendering locations with "..." or " / " (observed
    directly in judged/*.json -- e.g. "walk, validate, symlink ... verify
    each new link", "auth-service: ... vs notifications-service: ..."). Each
    resulting fragment may also echo its own node's marker glyph as quoted
    text (e.g. "IV. retry adds load") even though extract_nodes() never
    includes the marker in a real node's `.text` -- stripped here the same
    way a real node would have it stripped."""
    parts = [p.strip() for p in _FRAGMENT_SPLIT.split(evidence) if p.strip()]
    return [strip_marker_prefix(p) for p in parts]


def locate_evidence_in_rendering(evidence: str, rendering_tokens: List[str]) -> Optional[Span]:
    """Locate a judge's evidence text within a rendering's token stream.
    Returns the span from the start of its first fragment to the end of
    its last, or None if ANY fragment fails to align -- never a partial/
    best-effort span (see module docstring: fail closed, don't guess)."""
    fragments = split_evidence_fragments(evidence)
    if not fragments:
        return None
    starts, ends = [], []
    for frag in fragments:
        ftok = tokenize(frag)
        s = find_start(ftok, rendering_tokens)
        if s is None:
            return None
        starts.append(s)
        ends.append(s + len(ftok))
    return Span(min(starts), max(ends))


# ---------------------------------------------------------------------------
# Per-question scoring
# ---------------------------------------------------------------------------

def resolve_kind(uid: str) -> str:
    return "relation" if uid.startswith("r") else "fact"


def _verdict_bucket(judged_level: dict, kind: str) -> dict:
    return judged_level.get("relations" if kind == "relation" else "facts", {})


def score_question_view(
    required_ids: List[str],
    judged_level: dict,
    baseline: CaseBaseline,
    gist_pos: Dict[str, Span],
    allowed_statuses: Dict[str, set],
) -> dict:
    """One view (strict or exploratory) of one question against one
    rendering. Eligibility: every required unit must (a) have a verdict
    status in `allowed_statuses` for its kind, (b) align in the case
    baseline, and (c) align in this specific rendering."""
    if not required_ids:
        return {"eligible": False, "reasons": ["no_required_units"]}

    reasons = []
    for uid in required_ids:
        kind = resolve_kind(uid)
        verdict = _verdict_bucket(judged_level, kind).get(uid, {})
        status = verdict.get("status", "omitted" if kind == "fact" else "lost")
        if status not in allowed_statuses[kind]:
            reasons.append(f"{uid}:status={status}")
        if uid in baseline.unaligned_unit_ids or uid not in baseline.unit_pos:
            reasons.append(f"{uid}:unaligned_in_baseline")
        if uid not in gist_pos:
            reasons.append(f"{uid}:unaligned_in_rendering")

    if reasons:
        return {"eligible": False, "reasons": reasons}

    b_spans = [baseline.unit_pos[uid] for uid in required_ids]
    g_spans = [gist_pos[uid] for uid in required_ids]

    b_last_end = max(s.end for s in b_spans)
    b_first_start = min(s.start for s in b_spans)
    g_last_end = max(s.end for s in g_spans)
    g_first_start = min(s.start for s in g_spans)

    return {
        "eligible": True,
        "baseline_first_start": b_first_start,
        "baseline_last_end": b_last_end,
        "gist_first_start": g_first_start,
        "gist_last_end": g_last_end,
    }


def finalize_view(raw: dict, baseline_total: int, gist_total: int) -> dict:
    if not raw["eligible"] or not baseline_total or not gist_total:
        out = {"eligible": raw["eligible"]}
        if not raw["eligible"]:
            out["reasons"] = raw["reasons"]
        else:
            out["reasons"] = ["empty_representation"]
            out["eligible"] = False
        return out

    b_eac = round(raw["baseline_last_end"] / baseline_total, 4)
    g_eac = round(raw["gist_last_end"] / gist_total, 4)
    b_span = round((raw["baseline_last_end"] - raw["baseline_first_start"]) / baseline_total, 4)
    g_span = round((raw["gist_last_end"] - raw["gist_first_start"]) / gist_total, 4)
    return {
        "eligible": True,
        "baseline_eac": b_eac,
        "gist_eac": g_eac,
        "delta_eac": round(g_eac - b_eac, 4),
        "baseline_evidence_span": b_span,
        "gist_evidence_span": g_span,
        "delta_evidence_span": round(g_span - b_span, 4),
    }


def structural_diagnostic(required_ids: List[str], gist_pos: Dict[str, Span], idx: RenderingIndex) -> Optional[dict]:
    """Optional diagnostic (never a score): which output node holds each
    support unit's evidence, the depth of their lowest common ancestor,
    and how many other nodes sit between the first and last one in
    reading order. Only meaningful for multi-support questions."""
    if len(required_ids) < 2:
        return None

    def node_at_token(pos: int) -> Optional[int]:
        for i, r in enumerate(idx.node_token_range):
            if r.start <= pos < r.end:
                return i
        return None

    node_indices = []
    for uid in required_ids:
        n = node_at_token(gist_pos[uid].start)
        if n is None:
            return None
        node_indices.append(n)

    def ancestors(n: int) -> List[int]:
        chain = [n]
        while idx.nodes[chain[-1]].parent is not None:
            chain.append(idx.nodes[chain[-1]].parent)
        return chain

    chains = [ancestors(n) for n in node_indices]
    common = set(chains[0])
    for c in chains[1:]:
        common &= set(c)
    lca = next((n for n in chains[0] if n in common), None)
    lca_depth = idx.nodes[lca].depth if lca is not None else None

    lo, hi = min(node_indices), max(node_indices)
    intervening = max(0, hi - lo - 1)

    return {
        "support_node_indices": node_indices,
        "lca_node_index": lca,
        "lca_depth": lca_depth,
        "intervening_node_count": intervening,
    }


# ---------------------------------------------------------------------------
# Corpus driver
# ---------------------------------------------------------------------------

def main():
    results = {}

    for test_class in TEST_CLASSES:
        class_dir = ROOT / test_class
        if not class_dir.exists():
            continue
        for case_dir in sorted(class_dir.iterdir()):
            if not case_dir.is_dir():
                continue
            case_id = case_dir.name
            gold_path = case_dir / "gold.json"
            source_path = case_dir / "source.md"
            judged_dir = case_dir / "judged"
            if not gold_path.exists() or not source_path.exists() or not judged_dir.exists():
                continue

            gold = load_json(gold_path)
            source_tokens = tokenize(read(source_path))
            baseline = build_case_baseline(gold, source_tokens)

            case_result = {
                "test_class": test_class,
                "baseline_token_count": len(baseline.tokens),
                "baseline_integrity": {
                    "units_total": len(gold.get("facts", [])) + len(gold.get("relations", [])),
                    "units_unaligned_in_source": baseline.unaligned_unit_ids,
                    "units_ambiguous_in_source": baseline.ambiguous_unit_ids,
                    "merged_span_count": baseline.merged_span_count,
                },
            }

            for judged_path in sorted(judged_dir.glob("*.json")):
                tier = judged_path.stem
                judged = load_json(judged_path)
                case_result[tier] = {}
                for level in LEVELS:
                    if level not in judged:
                        continue
                    rpath = case_dir / "renderings" / tier / f"{level}.md"
                    if not rpath.exists():
                        case_result[tier][level] = {"status": "missing"}
                        continue
                    idx = build_rendering_index(read(rpath))
                    judged_level = judged[level]

                    # Locate every gold unit's evidence in THIS rendering once.
                    gist_pos: Dict[str, Span] = {}
                    for kind, bucket_key in (("fact", "facts"), ("relation", "relations")):
                        for uid, verdict in judged_level.get(bucket_key, {}).items():
                            ev = verdict.get("evidence", "")
                            if not ev.strip():
                                continue
                            span = locate_evidence_in_rendering(ev, idx.tokens)
                            if span is not None:
                                gist_pos[uid] = span

                    question_results = {}
                    for q in gold.get("questions", []):
                        required_ids = q.get("fact_ids", [])
                        strict_raw = score_question_view(
                            required_ids, judged_level, baseline, gist_pos, STRICT_STATUSES
                        )
                        explore_raw = score_question_view(
                            required_ids, judged_level, baseline, gist_pos, EXPLORATORY_STATUSES
                        )
                        strict = finalize_view(strict_raw, len(baseline.tokens), len(idx.tokens))
                        explore = finalize_view(explore_raw, len(baseline.tokens), len(idx.tokens))
                        diag = (
                            structural_diagnostic(required_ids, gist_pos, idx)
                            if strict.get("eligible")
                            else None
                        )
                        question_results[q["id"]] = {
                            "type": q["type"],
                            "support_unit_count": len(required_ids),
                            "strict": strict,
                            "exploratory": explore,
                            "structural_diagnostic": diag,
                        }

                    case_result[tier][level] = {
                        "status": "scored",
                        "gist_token_count": len(idx.tokens),
                        "questions": question_results,
                    }

            results[case_id] = case_result

    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / "findability.json"
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {out_path}")

    write_report(results)


def write_report(results: dict):
    lines = []
    lines.append("# Findability (Evidence Access Cost): canonical scores (generated, do not hand-edit)\n")
    lines.append(
        "Measurement only -- see `../FINDABILITY_FINDINGS.md` for what this "
        "found and why the baseline is case-level. Regenerate with "
        "`python3 scoring/findability.py`.\n"
    )

    header = (
        "| case | tier | level | qtype | support units | eligible (strict) | "
        "baseline EAC | gist EAC | delta EAC | baseline span | gist span | delta span |"
    )
    lines.append(header)
    lines.append("|---" * 12 + "|")
    for case_id, case in sorted(results.items()):
        for tier, levels in case.items():
            if tier in ("test_class", "baseline_token_count", "baseline_integrity"):
                continue
            for level in LEVELS:
                r = levels.get(level)
                if not r or r.get("status") != "scored":
                    continue
                for qid, q in sorted(r["questions"].items()):
                    s = q["strict"]
                    if not s.get("eligible"):
                        lines.append(
                            f"| {case_id} | {tier} | {level} | {q['type']} | {q['support_unit_count']} | "
                            f"no ({','.join(s.get('reasons', []))}) | - | - | - | - | - | - |"
                        )
                    else:
                        lines.append(
                            f"| {case_id} | {tier} | {level} | {q['type']} | {q['support_unit_count']} | yes | "
                            f"{s['baseline_eac']} | {s['gist_eac']} | {s['delta_eac']} | "
                            f"{s['baseline_evidence_span']} | {s['gist_evidence_span']} | {s['delta_evidence_span']} |"
                        )
    lines.append("")

    # Aggregate deltas by question type and by level, strict-eligible only.
    def _collect(key_fn):
        buckets: Dict[str, List[float]] = {}
        buckets_span: Dict[str, List[float]] = {}
        for case_id, case in results.items():
            for tier, levels in case.items():
                if tier in ("test_class", "baseline_token_count", "baseline_integrity"):
                    continue
                for level in LEVELS:
                    r = levels.get(level)
                    if not r or r.get("status") != "scored":
                        continue
                    for qid, q in r["questions"].items():
                        s = q["strict"]
                        if not s.get("eligible"):
                            continue
                        k = key_fn(case_id, tier, level, q)
                        buckets.setdefault(k, []).append(s["delta_eac"])
                        buckets_span.setdefault(k, []).append(s["delta_evidence_span"])
        return buckets, buckets_span

    def _avg(xs):
        return round(sum(xs) / len(xs), 4) if xs else None

    lines.append("## Delta EAC / delta evidence-span by question type (strict-eligible only)\n")
    by_type, by_type_span = _collect(lambda c, t, l, q: q["type"])
    lines.append("| question type | n | avg delta EAC | avg delta evidence-span |")
    lines.append("|---|---|---|---|")
    for k in sorted(by_type):
        lines.append(f"| {k} | {len(by_type[k])} | {_avg(by_type[k])} | {_avg(by_type_span[k])} |")
    lines.append("")

    lines.append("## Delta EAC / delta evidence-span by granularity level (strict-eligible only)\n")
    by_level, by_level_span = _collect(lambda c, t, l, q: l)
    lines.append("| level | n | avg delta EAC | avg delta evidence-span |")
    lines.append("|---|---|---|---|")
    for k in LEVELS:
        if k in by_level:
            lines.append(f"| {k} | {len(by_level[k])} | {_avg(by_level[k])} | {_avg(by_level_span[k])} |")
    lines.append("")

    lines.append("## Delta EAC by support-unit count (single vs. multi-support, strict-eligible only)\n")
    by_support, by_support_span = _collect(
        lambda c, t, l, q: "single" if q["support_unit_count"] <= 1 else "multi"
    )
    lines.append("| support | n | avg delta EAC | avg delta evidence-span |")
    lines.append("|---|---|---|---|")
    for k in ("single", "multi"):
        if k in by_support:
            lines.append(f"| {k} | {len(by_support[k])} | {_avg(by_support[k])} | {_avg(by_support_span[k])} |")
    lines.append("")

    # Eligibility summary
    total_q = 0
    eligible_q = 0
    for case in results.values():
        for tier, levels in case.items():
            if tier in ("test_class", "baseline_token_count", "baseline_integrity"):
                continue
            for level in LEVELS:
                r = levels.get(level)
                if not r or r.get("status") != "scored":
                    continue
                for q in r["questions"].values():
                    total_q += 1
                    if q["strict"].get("eligible"):
                        eligible_q += 1
    lines.append(
        f"**Strict eligibility:** {eligible_q}/{total_q} "
        f"(case, tier, level, question) combinations were strict-findability-scorable "
        f"({round(100*eligible_q/total_q, 1) if total_q else 0}%). "
        "See `results/findability.json` for the per-question `reasons` on every ineligible one.\n"
    )

    out = RESULTS / "FINDABILITY_SCORES.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
