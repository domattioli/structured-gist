#!/usr/bin/env python3
"""
Eval B: findability -- measurement only. Tests structured-gist's practical
thesis ("hierarchical structure makes the important information easier to
locate"), NOT its compression. See ../FINDABILITY_FINDINGS.md for the full
write-up, including two documented failure modes found and fixed before
this corpus's numbers were finalized:

1. The literal per-question minimal baseline the PR brief specifies is
   mathematically degenerate -- see `naive_per_question_baseline_tokens`
   and FINDABILITY_FINDINGS.md "Failure mode 1".
2. The case-level ALL-GOLD-CONTENT baseline that replaced it (still built
   below, as `build_case_baseline`, and still kept as a diagnostic) still
   let compression leak into the comparison: it holds every gold fact/
   relation for the case regardless of whether a given rendering actually
   retained it, while the gist side naturally only has what survived. A
   ~284-token "holds everything" baseline compared against a ~36-token
   skim gist is not a compression-controlled comparison -- deletion is
   still affecting the denominator. See FINDABILITY_FINDINGS.md "Failure
   mode 2" and "The fix: the retained-unit baseline" below.

Deliberately named "Evidence Access Cost", not "reading speed" or "human
findability" -- this is a deterministic proxy, not a timed-reader study.

THE HEADLINE METRIC (`unit_rank_*` below) compares the same SET of
semantic units -- exactly those this specific rendering retained and that
align deterministically on both sides -- in two different ORDERS: their
original position in `source.md`, and their position in the rendering.
Same cards, different shuffle. A unit the gist deleted never appears in
either ordering, so compression cannot earn credit or blame here; only
organization can. The older token-based, case-level-baseline metric
(`build_case_baseline` / `score_question_view` / `finalize_view`) is kept
only as a diagnostic -- see the module-level docstrings on those functions
and FINDABILITY_FINDINGS.md for why it is no longer the causal claim.

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
    FINDABILITY_FINDINGS.md "Failure mode 1"); NOT used for this module's
    actual scoring."""
    merged = merge_spans(required_spans)
    tokens: List[str] = []
    for s in merged:
        tokens.extend(source_tokens[s.start:s.end])
    return tokens


# ---------------------------------------------------------------------------
# Gold-unit <-> source.md alignment (shared: feeds both the retained-unit
# ranking below AND the diagnostic case-level token baseline)
# ---------------------------------------------------------------------------

def all_unit_ids(gold: dict) -> List[Tuple[str, str]]:
    """Every (kind, unit id) this case's gold defines, facts then
    relations, in gold-list order. Order here is never load-bearing for
    scoring (both source-side and gist-side rankings sort explicitly on
    span position, never on this list's order) -- it only fixes iteration
    order for reproducible diagnostics."""
    ids = [("fact", f["id"]) for f in gold.get("facts", [])]
    ids += [("relation", r["id"]) for r in gold.get("relations", [])]
    return ids


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


@dataclass
class SourceAlignment:
    unit_span: Dict[str, Span]     # unit id -> its token span in source.md
    unaligned_unit_ids: List[str]  # gold source_quote not found in source.md (integrity issue)
    ambiguous_unit_ids: List[str]  # source_quote occurs >1 time in source.md (first occurrence used)


def align_units_to_source(gold: dict, source_tokens: List[str]) -> SourceAlignment:
    """Locate every gold fact/relation's `source_quote` in `source.md`,
    independent of any rendering or judge verdict -- a case-level, tier/
    level-independent fact. First-occurrence, exact-token-sequence match
    only (see text_norm.find_start); no fuzzy matching, ever."""
    unaligned: List[str] = []
    ambiguous: List[str] = []
    unit_span: Dict[str, Span] = {}
    quotes = {uid: f["source_quote"] for f in gold.get("facts", []) for uid in [f["id"]]}
    quotes.update({uid: r["source_quote"] for r in gold.get("relations", []) for uid in [r["id"]]})
    for _kind, uid in all_unit_ids(gold):
        qtok = tokenize(quotes[uid])
        start = find_start(qtok, source_tokens)
        if start is None:
            unaligned.append(uid)
            continue
        if _count_occurrences(qtok, source_tokens) > 1:
            ambiguous.append(uid)
        unit_span[uid] = Span(start, start + len(qtok))
    return SourceAlignment(unit_span=unit_span, unaligned_unit_ids=unaligned, ambiguous_unit_ids=ambiguous)


# ---------------------------------------------------------------------------
# DIAGNOSTIC ONLY: case-level, all-gold-content token baseline.
#
# This is Failure-mode-2's construction (see module docstring): it holds
# EVERY gold fact/relation for the case, regardless of whether a specific
# rendering actually retained it. That made it a genuine improvement over
# the (also diagnostic) naive per-question baseline, but it does NOT
# control for compression against a rendering that dropped most of that
# content -- a short skim gist is still compared against a baseline sized
# to the FULL case, not to what skim itself retained. Kept here, clearly
# labeled, because the raw token positions/spans it produces are still
# useful *diagnostics* (see FINDABILITY_FINDINGS.md) -- it is no longer the
# headline causal claim about organization. That role now belongs to
# `score_question_unit_rank` below.
# ---------------------------------------------------------------------------

@dataclass
class CaseBaseline:
    tokens: List[str]
    unit_pos: Dict[str, Span]          # unit id -> position within `tokens`
    unaligned_unit_ids: List[str]      # gold source_quote not found in source.md (integrity issue)
    merged_span_count: int
    ambiguous_unit_ids: List[str]      # source_quote occurs >1 time in source.md (first occurrence used)


def build_case_baseline(gold: dict, source_tokens: List[str]) -> CaseBaseline:
    """DIAGNOSTIC ONLY (see module/section docstrings above) -- not the
    headline metric. Case-level content-matched baseline: ALL of this
    case's gold facts + relations (not just one question's, and not just
    what a given rendering retained), located by source_quote, deduplicated
    by span overlap, kept in source order."""
    alignment = align_units_to_source(gold, source_tokens)
    merged = merge_spans(list(alignment.unit_span.values()))

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

    unit_pos = {uid: locate_in_baseline(span) for uid, span in alignment.unit_span.items()}

    return CaseBaseline(
        tokens=baseline_tokens,
        unit_pos=unit_pos,
        unaligned_unit_ids=alignment.unaligned_unit_ids,
        merged_span_count=len(merged),
        ambiguous_unit_ids=alignment.ambiguous_unit_ids,
    )


# ---------------------------------------------------------------------------
# Gist-side evidence location (shared by both the headline metric and the
# diagnostic one)
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


def resolve_kind(uid: str) -> str:
    return "relation" if uid.startswith("r") else "fact"


def _verdict_bucket(judged_level: dict, kind: str) -> dict:
    return judged_level.get("relations" if kind == "relation" else "facts", {})


def locate_all_gist_positions(gold: dict, judged_level: dict, rendering_tokens: List[str]) -> Dict[str, Span]:
    """Locate every gold unit's judge-recorded evidence in one specific
    rendering's token stream, regardless of verdict status -- callers
    filter by status separately. Returns only units whose evidence is
    present and aligns exactly."""
    gist_pos: Dict[str, Span] = {}
    for kind, uid in all_unit_ids(gold):
        verdict = _verdict_bucket(judged_level, kind).get(uid, {})
        ev = verdict.get("evidence", "")
        if not ev.strip():
            continue
        span = locate_evidence_in_rendering(ev, rendering_tokens)
        if span is not None:
            gist_pos[uid] = span
    return gist_pos


# ---------------------------------------------------------------------------
# THE FIX: the retained-unit baseline.
#
# Build the strict retained-and-alignable set R for one (case, tier,
# level): a gold unit belongs to R only if (a) its verdict status in THIS
# rendering is exactly "retained" (or, for the separate exploratory view,
# "retained" or "partial"), (b) its source_quote aligns deterministically
# in source.md, and (c) the judge's evidence for it aligns deterministically
# in THIS rendering. No partial units in the strict view; no fuzzy
# matching; no model calls. A unit failing any check is EXCLUDED from R --
# it then cannot appear on either side of the comparison, so deletion
# cannot earn credit. See FINDABILITY_FINDINGS.md "The fix: the
# retained-unit baseline".
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RetainedUnit:
    uid: str
    kind: str
    source_span: Span
    gist_span: Span


def build_retained_units(
    gold: dict,
    judged_level: dict,
    source_alignment: SourceAlignment,
    gist_pos: Dict[str, Span],
    allowed_statuses: Dict[str, set],
) -> Tuple[Dict[str, RetainedUnit], Dict[str, List[str]]]:
    """Returns (retained, excluded). `retained` maps unit id -> RetainedUnit
    for every unit in R. `excluded` maps every OTHER gold unit id to the
    list of reasons it failed to qualify (status, source alignment,
    rendering alignment -- any/all may apply). Every gold unit for this
    case appears in exactly one of the two dicts -- nothing is silently
    dropped."""
    retained: Dict[str, RetainedUnit] = {}
    excluded: Dict[str, List[str]] = {}
    for kind, uid in all_unit_ids(gold):
        reasons: List[str] = []
        verdict = _verdict_bucket(judged_level, kind).get(uid, {})
        status = verdict.get("status", "omitted" if kind == "fact" else "lost")
        if status not in allowed_statuses[kind]:
            reasons.append(f"status={status}")
        if uid not in source_alignment.unit_span:
            reasons.append("unaligned_in_source")
        if uid not in gist_pos:
            reasons.append("unaligned_in_rendering")
        if reasons:
            excluded[uid] = reasons
            continue
        retained[uid] = RetainedUnit(
            uid=uid,
            kind=kind,
            source_span=source_alignment.unit_span[uid],
            gist_span=gist_pos[uid],
        )
    return retained, excluded


def rank_units(retained: Dict[str, RetainedUnit], side: str) -> Dict[str, int]:
    """1-indexed rank of each retained unit's position on `side` ('source'
    or 'gist'): the first unit in reading order is rank 1, the Nth (last)
    of N units is rank N. Deterministic tie-break -- source side sorts by
    (source_start, source_end, unit_id); gist side sorts by (gist_start,
    gist_end, unit_id) -- so two units that align to the same span (e.g. a
    fact and a relation whose source_quote spans overlap, see "Duplicate /
    relation overlap handling" in FINDABILITY_FINDINGS.md) are ordered by
    unit id, never by incidental JSON/dict iteration order. A fact and a
    relation sharing a span are NEVER collapsed into one unit here -- each
    keeps its own rank."""
    assert side in ("source", "gist")

    def key(u: RetainedUnit):
        span = u.source_span if side == "source" else u.gist_span
        return (span.start, span.end, u.uid)

    ordered = sorted(retained.values(), key=key)
    return {u.uid: i + 1 for i, u in enumerate(ordered)}


def assert_identical_retained_sets(
    retained: Dict[str, RetainedUnit], source_ranks: Dict[str, int], gist_ranks: Dict[str, int]
) -> None:
    """Hard invariant: the source-order and gist-order rankings must cover
    EXACTLY the retained set R -- same unit ids on both sides, only their
    order differs. A unit the gist deleted is excluded from `retained`
    entirely (see build_retained_units) and therefore cannot appear in
    either ranking."""
    ids = set(retained)
    assert set(source_ranks) == ids, "source-order ranking must cover exactly the retained set"
    assert set(gist_ranks) == ids, "gist-order ranking must cover exactly the retained set"


def score_question_unit_rank(
    required_ids: List[str],
    retained: Dict[str, RetainedUnit],
    excluded: Dict[str, List[str]],
    source_ranks: Dict[str, int],
    gist_ranks: Dict[str, int],
) -> dict:
    """Headline metric. A question is scorable only if every required unit
    is in R (`retained`) -- never a silently shrunk required set. On
    success:

    - unit-rank Evidence Access Cost: `EAC_source = rank(last required
      unit in source order) / |R|`, `EAC_gist` likewise in gist order.
      `delta_eac = EAC_gist - EAC_source`; negative means the gist makes
      all required evidence available earlier. 1-indexed cumulative
      traversal: the first of 10 retained units -> 0.1, the tenth -> 1.0.
    - locality span (multi-unit questions): `Span_source = (rank(last) -
      rank(first) + 1) / |R|`, likewise in gist order. `delta_span =
      Span_gist - Span_source`; negative means the required units became
      more clustered.

    Both metrics are computed over identical `|R|` and an identical set of
    required-unit ranks on both sides -- only the two orderings differ.
    """
    if not required_ids:
        return {"eligible": False, "reasons": ["no_required_units"]}

    reasons: List[str] = []
    for uid in required_ids:
        if uid not in retained:
            why = ",".join(excluded.get(uid, ["not_in_retained_set"]))
            reasons.append(f"{uid}:{why}")
    if reasons:
        return {"eligible": False, "reasons": reasons}

    n = len(retained)
    if n == 0:
        return {"eligible": False, "reasons": ["empty_retained_set"]}

    s_ranks = [source_ranks[uid] for uid in required_ids]
    g_ranks = [gist_ranks[uid] for uid in required_ids]
    s_last, s_first = max(s_ranks), min(s_ranks)
    g_last, g_first = max(g_ranks), min(g_ranks)

    source_eac = round(s_last / n, 4)
    gist_eac = round(g_last / n, 4)
    source_span = round((s_last - s_first + 1) / n, 4)
    gist_span = round((g_last - g_first + 1) / n, 4)

    return {
        "eligible": True,
        "retained_set_size": n,
        "source_eac": source_eac,
        "gist_eac": gist_eac,
        "delta_eac": round(gist_eac - source_eac, 4),
        "source_locality_span": source_span,
        "gist_locality_span": gist_span,
        "delta_locality_span": round(gist_span - source_span, 4),
    }


# ---------------------------------------------------------------------------
# DIAGNOSTIC ONLY: the old per-question view against the case-level
# all-gold-content token baseline (see the CaseBaseline section above for
# why this is no longer the headline metric).
# ---------------------------------------------------------------------------

def score_question_view(
    required_ids: List[str],
    judged_level: dict,
    baseline: CaseBaseline,
    gist_pos: Dict[str, Span],
    allowed_statuses: Dict[str, set],
) -> dict:
    """DIAGNOSTIC ONLY. One view (strict or exploratory) of one question
    against the case-level all-gold-content baseline. Eligibility: every
    required unit must (a) have a verdict status in `allowed_statuses` for
    its kind, (b) align in the case baseline, and (c) align in this
    specific rendering."""
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
    """DIAGNOSTIC ONLY -- see score_question_view."""
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
            source_alignment = align_units_to_source(gold, source_tokens)
            # Diagnostic-only case-level baseline (see module docstring).
            diag_baseline = build_case_baseline(gold, source_tokens)

            case_result = {
                "test_class": test_class,
                "source_integrity": {
                    "units_total": len(gold.get("facts", [])) + len(gold.get("relations", [])),
                    "units_unaligned_in_source": source_alignment.unaligned_unit_ids,
                    "units_ambiguous_in_source": source_alignment.ambiguous_unit_ids,
                },
                "diagnostic_case_baseline_token_count": len(diag_baseline.tokens),
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
                    gist_pos = locate_all_gist_positions(gold, judged_level, idx.tokens)

                    # THE retained-unit sets for THIS (case, tier, level):
                    # strict (retained only) and exploratory (retained or
                    # partial), each with its own two orderings.
                    retained_strict, excluded_strict = build_retained_units(
                        gold, judged_level, source_alignment, gist_pos, STRICT_STATUSES
                    )
                    retained_explore, excluded_explore = build_retained_units(
                        gold, judged_level, source_alignment, gist_pos, EXPLORATORY_STATUSES
                    )
                    src_ranks_strict = rank_units(retained_strict, "source")
                    gist_ranks_strict = rank_units(retained_strict, "gist")
                    assert_identical_retained_sets(retained_strict, src_ranks_strict, gist_ranks_strict)
                    src_ranks_explore = rank_units(retained_explore, "source")
                    gist_ranks_explore = rank_units(retained_explore, "gist")
                    assert_identical_retained_sets(retained_explore, src_ranks_explore, gist_ranks_explore)

                    question_results = {}
                    for q in gold.get("questions", []):
                        required_ids = q.get("fact_ids", [])

                        unit_rank_strict = score_question_unit_rank(
                            required_ids, retained_strict, excluded_strict, src_ranks_strict, gist_ranks_strict
                        )
                        unit_rank_explore = score_question_unit_rank(
                            required_ids, retained_explore, excluded_explore, src_ranks_explore, gist_ranks_explore
                        )

                        # Diagnostic-only token-based view (see section docstring above).
                        diag_strict_raw = score_question_view(
                            required_ids, judged_level, diag_baseline, gist_pos, STRICT_STATUSES
                        )
                        diag_explore_raw = score_question_view(
                            required_ids, judged_level, diag_baseline, gist_pos, EXPLORATORY_STATUSES
                        )
                        diag_strict = finalize_view(diag_strict_raw, len(diag_baseline.tokens), len(idx.tokens))
                        diag_explore = finalize_view(diag_explore_raw, len(diag_baseline.tokens), len(idx.tokens))

                        diag_structural = (
                            structural_diagnostic(required_ids, gist_pos, idx)
                            if unit_rank_strict.get("eligible")
                            else None
                        )

                        question_results[q["id"]] = {
                            "type": q["type"],
                            "support_unit_count": len(required_ids),
                            "unit_rank": {
                                "strict": unit_rank_strict,
                                "exploratory": unit_rank_explore,
                            },
                            "diagnostic_token_eac": {
                                "strict": diag_strict,
                                "exploratory": diag_explore,
                            },
                            "structural_diagnostic": diag_structural,
                        }

                    case_result[tier][level] = {
                        "status": "scored",
                        "gist_token_count": len(idx.tokens),
                        "retained_set": {
                            "strict": {
                                "size": len(retained_strict),
                                "unit_ids": sorted(retained_strict),
                                "excluded": excluded_strict,
                            },
                            "exploratory": {
                                "size": len(retained_explore),
                                "unit_ids": sorted(retained_explore),
                                "excluded": excluded_explore,
                            },
                        },
                        "questions": question_results,
                    }

            results[case_id] = case_result

    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / "findability.json"
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {out_path}")

    write_report(results)


def _iter_scored_levels(results: dict):
    for case_id, case in sorted(results.items()):
        for tier, levels in case.items():
            if tier in ("test_class", "source_integrity", "diagnostic_case_baseline_token_count"):
                continue
            for level in LEVELS:
                r = levels.get(level)
                if not r or r.get("status") != "scored":
                    continue
                yield case_id, tier, level, r


def write_report(results: dict):
    lines = []
    lines.append("# Findability (Evidence Access Cost): canonical scores (generated, do not hand-edit)\n")
    lines.append(
        "Measurement only -- see `../FINDABILITY_FINDINGS.md` for full methodology. "
        "**Headline metric is unit-rank EAC / locality span**, computed over "
        "the retained-unit set `R` this specific (case, tier, level) rendering "
        "actually retained and could align -- source order vs. gist order over "
        "the identical set `R`, so compression/deletion cannot affect either "
        "number. The older token-normalized, case-level-baseline EAC is "
        "reported separately as a diagnostic only (see "
        "`FINDABILITY_FINDINGS.md` \"Failure mode 2\"). Regenerate with "
        "`python3 scoring/findability.py`.\n"
    )

    header = (
        "| case | tier | level | qtype | support units | |R| | eligible (strict) | "
        "source EAC | gist EAC | delta EAC | source span | gist span | delta span |"
    )
    lines.append(header)
    lines.append("|---" * 13 + "|")
    for case_id, tier, level, r in _iter_scored_levels(results):
        for qid, q in sorted(r["questions"].items()):
            s = q["unit_rank"]["strict"]
            if not s.get("eligible"):
                lines.append(
                    f"| {case_id} | {tier} | {level} | {q['type']} | {q['support_unit_count']} | - | "
                    f"no ({','.join(s.get('reasons', []))}) | - | - | - | - | - | - |"
                )
            else:
                lines.append(
                    f"| {case_id} | {tier} | {level} | {q['type']} | {q['support_unit_count']} | "
                    f"{s['retained_set_size']} | yes | "
                    f"{s['source_eac']} | {s['gist_eac']} | {s['delta_eac']} | "
                    f"{s['source_locality_span']} | {s['gist_locality_span']} | {s['delta_locality_span']} |"
                )
    lines.append("")

    # Aggregate deltas by question type / level / support-count, strict-eligible only.
    def _collect(key_fn):
        buckets: Dict[str, List[float]] = {}
        buckets_span: Dict[str, List[float]] = {}
        for case_id, tier, level, r in _iter_scored_levels(results):
            for qid, q in r["questions"].items():
                s = q["unit_rank"]["strict"]
                if not s.get("eligible"):
                    continue
                k = key_fn(case_id, tier, level, q)
                buckets.setdefault(k, []).append(s["delta_eac"])
                buckets_span.setdefault(k, []).append(s["delta_locality_span"])
        return buckets, buckets_span

    def _avg(xs):
        return round(sum(xs) / len(xs), 4) if xs else None

    lines.append("## Delta EAC / delta locality-span by question type (strict-eligible, unit-rank)\n")
    by_type, by_type_span = _collect(lambda c, t, l, q: q["type"])
    lines.append("| question type | n | avg delta EAC | avg delta locality-span |")
    lines.append("|---|---|---|---|")
    for k in sorted(by_type):
        lines.append(f"| {k} | {len(by_type[k])} | {_avg(by_type[k])} | {_avg(by_type_span[k])} |")
    lines.append("")

    lines.append("## Delta EAC / delta locality-span by granularity level (strict-eligible, unit-rank)\n")
    by_level, by_level_span = _collect(lambda c, t, l, q: l)
    lines.append("| level | n | avg delta EAC | avg delta locality-span |")
    lines.append("|---|---|---|---|")
    for k in LEVELS:
        if k in by_level:
            lines.append(f"| {k} | {len(by_level[k])} | {_avg(by_level[k])} | {_avg(by_level_span[k])} |")
    lines.append("")

    lines.append(
        "## Delta EAC by support-unit count (single vs. multi-support, strict-eligible, unit-rank)\n"
    )
    by_support, by_support_span = _collect(
        lambda c, t, l, q: "single" if q["support_unit_count"] <= 1 else "multi"
    )
    lines.append("| support | n | avg delta EAC | avg delta locality-span |")
    lines.append("|---|---|---|---|")
    for k in ("single", "multi"):
        if k in by_support:
            lines.append(f"| {k} | {len(by_support[k])} | {_avg(by_support[k])} | {_avg(by_support_span[k])} |")
    lines.append("")

    # Eligibility summary
    total_q = 0
    eligible_q = 0
    for case_id, tier, level, r in _iter_scored_levels(results):
        for q in r["questions"].values():
            total_q += 1
            if q["unit_rank"]["strict"].get("eligible"):
                eligible_q += 1
    lines.append(
        f"**Strict eligibility (unit-rank):** {eligible_q}/{total_q} "
        f"(case, tier, level, question) combinations were strict-findability-scorable "
        f"({round(100*eligible_q/total_q, 1) if total_q else 0}%). "
        "See `results/findability.json` for the per-question `reasons` on every ineligible one, "
        "and each rendering's `retained_set.strict.excluded` for why any given unit did not make it into `R`.\n"
    )

    lines.append(
        "## Diagnostic only: token-normalized, case-level-baseline EAC "
        "(no longer the headline metric -- see `FINDABILITY_FINDINGS.md` \"Failure mode 2\")\n"
    )

    def _collect_diag(key_fn):
        buckets: Dict[str, List[float]] = {}
        for case_id, tier, level, r in _iter_scored_levels(results):
            for qid, q in r["questions"].items():
                s = q["diagnostic_token_eac"]["strict"]
                if not s.get("eligible"):
                    continue
                k = key_fn(case_id, tier, level, q)
                buckets.setdefault(k, []).append(s["delta_eac"])
        return buckets

    diag_by_type = _collect_diag(lambda c, t, l, q: q["type"])
    lines.append("| question type | n | avg delta EAC (diagnostic, token-based) |")
    lines.append("|---|---|---|")
    for k in sorted(diag_by_type):
        lines.append(f"| {k} | {len(diag_by_type[k])} | {_avg(diag_by_type[k])} |")
    lines.append("")

    out = RESULTS / "FINDABILITY_SCORES.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
