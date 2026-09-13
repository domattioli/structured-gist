#!/usr/bin/env python3
"""
Eval A: wording fidelity -- measurement only, tests SKILL.md's own claim
("structure only, wording untouched") directly. See
../WORDING_FIDELITY_FINDINGS.md for the full write-up, what was found, and
whether this should become a durable regression guard.

This is a LEXICAL PROVENANCE test, not a semantic-faithfulness test. A
paraphrase can be semantically correct (and would score fine on this
suite's existing retention/recoverability metrics in combine.py) and still
fail this eval -- that is intentional; it is answering a different
question than combine.py does. Nothing here re-judges semantic content,
calls a model, or changes any existing score.

Three deterministic measures, computed over each rendering's semantic
nodes (`scoring/outline_nodes.py`) against its own `source.md`, after
normalization (`scoring/text_norm.py`):

  1. Verbatim node rate (VNR) -- per-node: does the whole node's normalized
     text appear as ONE contiguous span in source? Binary per node.
       VNR = verbatim_nodes / semantic_nodes

  2. Extractive token coverage -- output-wide: tile every semantic node's
     text (concatenated in on-page output order) against source using
     greedy longest-contiguous-match tiling (global reordering allowed --
     a fragment can be found anywhere in source). Reported at three
     minimum-fragment-length thresholds (K=1,2,3) from the SAME tiling
     pass, because K=1 alone is known to inflate coverage on common words
     that coincidentally exist in isolation elsewhere in source (a
     paraphrase like "root cause" can score 100% coverage at K=1 purely
     because "root" and "cause" each separately exist somewhere in
     source, despite never appearing adjacent) -- see
     WORDING_FIDELITY_FINDINGS.md "Pressure check: common-word inflation".
       coverage@K = sum(len(f) for f in fragments if matched and len(f)>=K)
                    / total_output_tokens

  3. Novel phrase diagnostic -- from the SAME tiling: a "novel span" is a
     maximal run of consecutive output tokens with no length>=2 matched
     fragment covering them (i.e. no genuine 2+-word copied phrase reaches
     them -- deliberately the same >=2 threshold as coverage@2, so a
     "novel" word is exactly a word coverage@2 already refused credit
     for). Diagnostic only -- never folded into a score. Every novel span
     is listed individually (not averaged), so one novel word inside an
     otherwise long verbatim sentence cannot disappear inside a good
     average (see README.md pressure-check list).

No stemming, no embeddings, no synonym/fuzzy matching anywhere in this
file -- every containment check in text_norm.py is exact token-sequence
containment after conservative, documented normalization.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # .../semantic-compression
RESULTS = ROOT / "results"
TEST_CLASSES = ["regression", "pressure-tests"]
LEVELS = ["skim", "standard", "deep"]

sys.path.insert(0, str(HERE))
from outline_nodes import Node, extract_nodes  # noqa: E402
from text_norm import (  # noqa: E402
    contains_contiguous,
    longest_contiguous_match_len,
    normalize,
    tokenize,
)

# Fixed-format vocabulary the skill's grammar itself mandates verbatim --
# the `/structured-gist summary` preset's literal section-header words
# (SKILL.md "## Activation", session-summary preset block). This is the
# ONLY vocabulary source treated as skill-introduced rather than
# source-copied or model-paraphrased; it is a closed, narrow, explicit
# list, not a broad stopword set (see README.md "Do not create a broad
# stopword/exception list that can hide paraphrasing"). None of this
# corpus's 8 cases use the summary preset, so this allowlist is expected
# to match 0 nodes here -- reported explicitly rather than silently
# assumed irrelevant. Matching is whole-node, case-insensitive, exact.
STRUCTURAL_ALLOWLIST = frozenset({
    "session summary", "changed", "decisions", "next", "state", "open questions",
})

MIN_FRAG_LENGTHS = (1, 2, 3)
NOVEL_SPAN_THRESHOLD = 2       # a novel span is a gap in coverage@2
NOVEL_SPAN_REPORT_MIN = 3      # "above a small length threshold" for the count/representative list


@dataclass
class Fragment:
    start: int
    end: int      # exclusive
    matched: bool

    @property
    def length(self) -> int:
        return self.end - self.start


def tile_fragments(output_tokens: List[str], source_tokens: List[str]) -> List[Fragment]:
    """Greedy left-to-right longest-contiguous-match tiling of
    output_tokens against source_tokens. See text_norm.longest_contiguous_
    match_len for why binary search over match length is valid. A position
    with no match at all (not even length 1) yields a length-1 unmatched
    fragment; scanning always advances by at least 1 token so this
    terminates in O(n) fragments."""
    n = len(output_tokens)
    fragments: List[Fragment] = []
    i = 0
    while i < n:
        best = longest_contiguous_match_len(output_tokens, i, source_tokens)
        if best > 0:
            fragments.append(Fragment(start=i, end=i + best, matched=True))
            i += best
        else:
            fragments.append(Fragment(start=i, end=i + 1, matched=False))
            i += 1
    return fragments


def extractive_coverage(fragments: List[Fragment], total_tokens: int, min_len: int) -> Optional[float]:
    if total_tokens == 0:
        return None
    covered = sum(f.length for f in fragments if f.matched and f.length >= min_len)
    return round(covered / total_tokens, 4)


def novel_spans(fragments: List[Fragment], output_tokens: List[str], threshold: int = NOVEL_SPAN_THRESHOLD) -> List[dict]:
    """Merge adjacent fragments whose length < threshold (whether or not
    text_norm found a trivial length-1 match) into maximal novel runs."""
    runs: List[dict] = []
    cur_start: Optional[int] = None
    cur_end: Optional[int] = None
    for f in fragments:
        if (f.matched and f.length >= threshold):
            if cur_start is not None:
                runs.append({"start": cur_start, "end": cur_end})
                cur_start = cur_end = None
        else:
            if cur_start is None:
                cur_start = f.start
            cur_end = f.end
    if cur_start is not None:
        runs.append({"start": cur_start, "end": cur_end})

    out = []
    for r in runs:
        span_tokens = output_tokens[r["start"]:r["end"]]
        out.append({
            "start": r["start"],
            "end": r["end"],
            "length": r["end"] - r["start"],
            "text": " ".join(span_tokens),
        })
    return out


def score_node(node: Node, source_tokens: List[str]) -> dict:
    node_norm = normalize(node.text)
    node_tokens = tokenize(node.text)
    is_allowlisted = node_norm.strip().lower() in STRUCTURAL_ALLOWLIST
    verbatim = bool(node_tokens) and contains_contiguous(node_tokens, source_tokens)
    return {
        "index": node.index,
        "depth": node.depth,
        "family": node.family,
        "text": node.text,
        "normalized_text": node_norm,
        "token_count": len(node_tokens),
        "is_allowlisted": is_allowlisted,
        "verbatim": verbatim,
    }


def score_rendering(rendering_text: str, source_text: str) -> dict:
    nodes = extract_nodes(rendering_text)
    source_tokens = tokenize(source_text)

    node_results = [score_node(n, source_tokens) for n in nodes]
    scorable = [n for n in node_results if not n["is_allowlisted"] and n["token_count"] > 0]
    allowlisted = [n for n in node_results if n["is_allowlisted"]]
    empty_nodes = [n for n in node_results if not n["is_allowlisted"] and n["token_count"] == 0]

    verbatim_nodes = [n for n in scorable if n["verbatim"]]
    non_verbatim_nodes = [n for n in scorable if not n["verbatim"]]

    total_semantic_nodes = len(scorable)
    vnr = round(len(verbatim_nodes) / total_semantic_nodes, 4) if total_semantic_nodes else None

    # by-family breakdown (grouped: concept/attribute/enumerator/explanation)
    family_group = {
        "dash": "concept", "attr": "attribute", "arrow": "explanation",
        "uroman": "enumerator", "ualpha": "enumerator",
        "lroman": "enumerator", "lalpha": "enumerator",
    }
    by_role: Dict[str, dict] = {}
    for n in scorable:
        role = family_group.get(n["family"], n["family"])
        b = by_role.setdefault(role, {"total": 0, "verbatim": 0})
        b["total"] += 1
        b["verbatim"] += 1 if n["verbatim"] else 0
    by_role_rates = {
        role: {
            "total": b["total"],
            "verbatim": b["verbatim"],
            "verbatim_node_rate": round(b["verbatim"] / b["total"], 4) if b["total"] else None,
        }
        for role, b in by_role.items()
    }

    output_tokens: List[str] = []
    for n in scorable:
        output_tokens.extend(tokenize(n["text"]))

    fragments = tile_fragments(output_tokens, source_tokens)
    coverage = {
        f"extractive_coverage_min{k}": extractive_coverage(fragments, len(output_tokens), k)
        for k in MIN_FRAG_LENGTHS
    }

    spans = novel_spans(fragments, output_tokens)
    spans_sorted = sorted(spans, key=lambda s: (-s["length"], s["start"]))
    spans_ge_threshold = [s for s in spans_sorted if s["length"] >= NOVEL_SPAN_REPORT_MIN]

    return {
        "status": "scored",
        "total_semantic_nodes": total_semantic_nodes,
        "verbatim_node_count": len(verbatim_nodes),
        "non_verbatim_node_count": len(non_verbatim_nodes),
        "verbatim_node_rate": vnr,
        "allowlisted_node_count": len(allowlisted),
        "allowlisted_nodes": [n["text"] for n in allowlisted],
        "empty_node_count": len(empty_nodes),
        "by_role": by_role_rates,
        "output_token_count": len(output_tokens),
        **coverage,
        "novel_span_count": len(spans_sorted),
        "novel_span_count_ge3": len(spans_ge_threshold),
        "longest_novel_span_length": max((s["length"] for s in spans_sorted), default=0),
        "representative_novel_spans": spans_sorted[:5],
        "non_verbatim_nodes": [
            {"index": n["index"], "family": n["family"], "depth": n["depth"], "text": n["text"]}
            for n in non_verbatim_nodes
        ],
    }


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
            source_path = case_dir / "source.md"
            rendering_root = case_dir / "renderings"
            if not source_path.exists() or not rendering_root.exists():
                continue
            source_text = read(source_path)

            results[case_id] = {"test_class": test_class}
            for tier_dir in sorted(rendering_root.iterdir()):
                if not tier_dir.is_dir():
                    continue
                tier = tier_dir.name
                results[case_id][tier] = {}
                for level in LEVELS:
                    rpath = tier_dir / f"{level}.md"
                    if not rpath.exists():
                        results[case_id][tier][level] = {"status": "missing"}
                        continue
                    results[case_id][tier][level] = score_rendering(read(rpath), source_text)

    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / "wording_fidelity.json"
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {out_path}")

    write_report(results)


def write_report(results: dict):
    lines = []
    lines.append("# Wording fidelity: canonical scores (generated, do not hand-edit)\n")
    lines.append(
        "Measurement only -- see `../WORDING_FIDELITY_FINDINGS.md` for what "
        "this found. Regenerate with `python3 scoring/wording_fidelity.py`.\n"
    )

    header = (
        "| case | tier | level | semantic nodes | verbatim-node rate | "
        "extractive coverage (>=1 / >=2 / >=3) | novel spans (>=3 tok) | longest novel span |"
    )
    lines.append(header)
    lines.append("|---" * 8 + "|")
    for case_id, tiers in sorted(results.items()):
        for tier, levels in tiers.items():
            if tier == "test_class":
                continue
            for level in LEVELS:
                r = levels.get(level)
                if not r or r.get("status") != "scored":
                    continue
                lines.append(
                    f"| {case_id} | {tier} | {level} | {r['total_semantic_nodes']} | "
                    f"{r['verbatim_node_rate']} | "
                    f"{r['extractive_coverage_min1']} / {r['extractive_coverage_min2']} / {r['extractive_coverage_min3']} | "
                    f"{r['novel_span_count_ge3']} | {r['longest_novel_span_length']} |"
                )
    lines.append("")

    lines.append("## Verbatim-node rate by role (concept/attribute/enumerator/explanation), aggregated across all cases\n")
    role_totals: Dict[str, dict] = {}
    for case_id, tiers in results.items():
        for tier, levels in tiers.items():
            if tier == "test_class":
                continue
            for level in LEVELS:
                r = levels.get(level)
                if not r or r.get("status") != "scored":
                    continue
                for role, b in r["by_role"].items():
                    t = role_totals.setdefault(role, {"total": 0, "verbatim": 0})
                    t["total"] += b["total"]
                    t["verbatim"] += b["verbatim"]
    lines.append("| role | nodes | verbatim | verbatim-node rate |")
    lines.append("|---|---|---|---|")
    for role, t in sorted(role_totals.items()):
        rate = round(t["verbatim"] / t["total"], 4) if t["total"] else None
        lines.append(f"| {role} | {t['total']} | {t['verbatim']} | {rate} |")
    lines.append("")

    out = RESULTS / "WORDING_FIDELITY_SCORES.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
