#!/usr/bin/env python3
"""Measure whether outline tree structure carries gold semantic linkage.

Design decisions (the plan's formerly open implementation details):

* Scope is the 11 ``standard`` renderings from the eight finalized cases.
  Case names are allowlisted so unrelated or unjudged cases cannot leak in.
* Rendered block outlines are reparsed because normalized judge paths omit
  marker family.  The parser uses the grammar's four-space indentation,
  recognizes ``-``/``▸``/roman/letter/``↪`` markers, and joins same-indent
  continuation lines with one space.  Its normalized labels therefore match
  the node-path convention documented in the investigation plan.
* Tree distance is edge distance through the lowest common ancestor:
  ``len(a) + len(b) - 2 * len(LCA(a, b))``.  A multi-node endpoint uses the
  minimum over all path combinations: if any node carrying the fact is near
  the other fact, the rendering has made that linkage structurally available.
* Proximity uses every unordered pair of endpoints in each gold relation.
  Missing/omitted/not-locatable endpoints make only their affected pairs
  unscorable.  Relation-endpoint paths are used rather than global fact paths,
  preserving the independent location judgments made for that relation.
* The null draws the same number of distinct pairs, without replacement, from
  all locatable fact pairs in that rendering.  There are 1,000 permutations,
  with a stable content-derived seed: enough resolution for a diagnostic while
  keeping the stdlib-only scorer fast and exactly reproducible.
* Effect size is relative proximity advantage,
  ``(null_mean - real_mean) / null_mean``.  It is unitless across differently
  sized trees and directly reads as the fractional distance reduction versus
  random pairs; positive values mean gold-linked facts are closer.  The null
  percentile is descriptive only, never promoted to a corpus-wide p-value.
* Order applies separately to each consecutive gold pair only when both facts
  can be represented by ordinal-enumerator siblings under the same parent.
  A pair passes when its rendered sibling indices increase.  A 3+ fact chain's
  partial credit is the mean of its eligible adjacent-pair pass indicators
  (e.g. two correct of three = 2/3).  Multi-node endpoints receive the best
  eligible path pairing, matching the proximity availability rule.
* Case rollup is the median rendering effect.  Median limits one tier's unusual
  topology from dominating; the across-case distribution remains about eight
  independent points and is reported descriptively, with no pooled p-value.

This script performs deterministic local arithmetic only: no model, network,
or API is called.  It writes structural_linkage.json and
STRUCTURAL_LINKAGE.md beside this file.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
import re
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LEVEL = "standard"
PERMUTATIONS = 1_000
CASE_NAMES = {
    "cause-chain-reversal",
    "migration-tristate",
    "synthetic-scale-verylarge",
    "negation-and-true-peers",
    "real-hook-discovery",
    "causality-heavy-explain",
    "real-benchmark-archaeology",
    "near-identical-numbers",
}
TEST_CLASSES = ("pressure-tests", "regression")

ROMAN_RE = re.compile(r"^(?P<marker>[IVXLCDMivxlcdm]+)\.\s+(?P<label>.+)$")
LETTER_RE = re.compile(r"^(?P<marker>[A-Za-z]+)\.\s+(?P<label>.+)$")
MARKED_RE = re.compile(r"^(?P<marker>-|▸|↪)\s+(?P<label>.+)$")


@dataclass(frozen=True)
class Node:
    path: tuple[str, ...]
    marker_family: str
    sibling_index: int


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def marker_and_label(text: str) -> tuple[str, str] | None:
    """Return semantic marker family and marker-stripped label."""
    match = MARKED_RE.match(text)
    if match:
        marker = match.group("marker")
        family = {"-": "concept", "▸": "attribute", "↪": "explanation"}[marker]
        return family, match.group("label")
    match = ROMAN_RE.match(text)
    if match:
        return "ordinal", match.group("label")
    match = LETTER_RE.match(text)
    if match:
        return "nominal", match.group("label")
    return None


def parse_outline(path: Path) -> dict[tuple[str, ...], list[Node]]:
    """Parse a fenced block outline into normalized paths and marker metadata."""
    raw_nodes: list[dict] = []
    current: dict | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.strip().startswith("```") or not raw_line.strip():
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        text = raw_line.strip()
        parsed = marker_and_label(text)
        if parsed:
            family, label = parsed
            current = {
                "depth": indent // 4,
                "family": family,
                "label": label,
                "marker": text.split(maxsplit=1)[0],
            }
            raw_nodes.append(current)
        elif current is not None and indent >= current["depth"] * 4:
            # R11 says continuation indentation equals the marker line.  One
            # finalized rendering instead uses a deeper hanging indent; it is
            # still unambiguously unmarked continuation text, so normalize it
            # without mutating the read-only rendering.
            current["label"] += " " + text
        else:
            raise ValueError(f"Unparseable outline line in {path}: {raw_line!r}")

    stack: list[dict] = []
    sibling_counts: dict[tuple[str, ...], int] = {}
    enumerator_families: dict[tuple[str, ...], str] = {}
    indexed: dict[tuple[str, ...], list[Node]] = {}
    for raw in raw_nodes:
        depth = raw["depth"]
        if depth > len(stack):
            raise ValueError(f"Skipped depth in {path}: {raw['label']!r}")
        stack = stack[:depth]
        parent = tuple(item["label"] for item in stack)
        sibling_index = sibling_counts.get(parent, 0)
        sibling_counts[parent] = sibling_index + 1
        family = raw["family"]
        if family in {"ordinal", "nominal"}:
            # A single C./D. (or c./d.) is lexically both a letter and a
            # Roman numeral.  The grammar makes each sibling set one family,
            # whose canonical first marker disambiguates it: I./i. is ordinal
            # and A./a. is nominal.  Carry that family across later siblings.
            marker = raw["marker"][:-1]
            if parent not in enumerator_families:
                if marker in {"A", "a"}:
                    enumerator_families[parent] = "nominal"
                elif marker in {"I", "i"}:
                    enumerator_families[parent] = "ordinal"
                else:
                    enumerator_families[parent] = family
            family = enumerator_families[parent]
        normalized_path = parent + (raw["label"],)
        node = Node(normalized_path, family, sibling_index)
        indexed.setdefault(normalized_path, []).append(node)
        stack.append(raw)
    return indexed


def outcome_paths(outcome: dict | None) -> list[tuple[str, ...]]:
    if not outcome:
        return []
    if "located" in outcome:
        located = outcome["located"]
        # Two finalized judged files use [[path]] for located instead of the
        # documented [path].  Treat that read-only shape as one path; unlike
        # multi_node it does not claim that evidence spans multiple nodes.
        if located and isinstance(located[0], list):
            if len(located) != 1:
                raise ValueError(f"Ambiguous located outcome: {outcome!r}")
            located = located[0]
        return [normalize_judged_path(located)]
    if "multi_node" in outcome:
        return [normalize_judged_path(path) for path in outcome["multi_node"]]
    return []


def normalize_judged_path(path: list[str]) -> tuple[str, ...]:
    """Defensively strip residual markers from finalized judged paths."""
    normalized = []
    for label in path:
        parsed = marker_and_label(label)
        normalized.append(parsed[1] if parsed else label)
    return tuple(normalized)


def resolve_nodes(
    path: tuple[str, ...], nodes: dict[tuple[str, ...], list[Node]]
) -> list[Node]:
    """Resolve exact path, or a unique suffix when an ancestor label drifted."""
    if path in nodes:
        return nodes[path]
    # Finalized synthetic-scale paths say "Mobile app release train" where
    # the rendering says "Mobile release train".  Longest unique suffix
    # preserves descendant identity without fuzzy prose matching.
    for suffix_length in range(len(path) - 1, 0, -1):
        suffix = path[-suffix_length:]
        matches = [node for key, values in nodes.items() if key[-suffix_length:] == suffix
                   for node in values]
        if len(matches) == 1:
            return matches
        if len(matches) > 1:
            return []
    return []


def tree_distance(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    lca = 0
    for a, b in zip(left, right):
        if a != b:
            break
        lca += 1
    return len(left) + len(right) - 2 * lca


def minimum_distance(left: dict | None, right: dict | None) -> int | None:
    distances = [
        tree_distance(a, b)
        for a in outcome_paths(left)
        for b in outcome_paths(right)
    ]
    return min(distances) if distances else None


def all_relation_pairs(fact_ids: list[str]) -> Iterable[tuple[str, str]]:
    return itertools.combinations(fact_ids, 2)


def nearest_ordinal_ancestor(
    node: Node, nodes: dict[tuple[str, ...], list[Node]]
) -> Node | None:
    """Walk self-then-ancestors for the nearest node whose marker family is ordinal."""
    if node.marker_family == "ordinal":
        return node
    for depth in range(len(node.path) - 1, 0, -1):
        for candidate in nodes.get(node.path[:depth], []):
            if candidate.marker_family == "ordinal":
                return candidate
    return None


def pair_order_score(
    left: dict | None,
    right: dict | None,
    nodes: dict[tuple[str, ...], list[Node]],
) -> int | None:
    eligible: list[int] = []
    for left_path in outcome_paths(left):
        for right_path in outcome_paths(right):
            for left_node in resolve_nodes(left_path, nodes):
                for right_node in resolve_nodes(right_path, nodes):
                    left_ordinal = nearest_ordinal_ancestor(left_node, nodes)
                    right_ordinal = nearest_ordinal_ancestor(right_node, nodes)
                    if (
                        left_ordinal is not None
                        and right_ordinal is not None
                        and left_ordinal.path[:-1] == right_ordinal.path[:-1]
                        and left_ordinal.sibling_index != right_ordinal.sibling_index
                    ):
                        eligible.append(
                            int(left_ordinal.sibling_index < right_ordinal.sibling_index)
                        )
    return max(eligible) if eligible else None


def stable_rng(case_id: str, tier: str) -> random.Random:
    digest = hashlib.sha256(f"{case_id}:{tier}:{LEVEL}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def score_rendering(case_dir: Path, tier: str, gold: dict, judged: dict) -> dict:
    rendering_path = case_dir / "renderings" / tier / f"{LEVEL}.md"
    nodes = parse_outline(rendering_path)
    node_paths = judged[LEVEL]["node_paths"]
    relation_paths = node_paths["relations"]
    fact_paths = node_paths["facts"]

    relation_rows = []
    real_distances: list[int] = []
    for relation in gold["relations"]:
        relation_id = relation["id"]
        endpoints = relation_paths[relation_id]
        pair_rows = []
        for left_id, right_id in all_relation_pairs(relation["fact_ids"]):
            distance = minimum_distance(endpoints.get(left_id), endpoints.get(right_id))
            pair_rows.append({"fact_ids": [left_id, right_id], "distance": distance})
            if distance is not None:
                real_distances.append(distance)

        order_pairs = []
        if relation["ordered"]:
            for left_id, right_id in zip(relation["fact_ids"], relation["fact_ids"][1:]):
                score = pair_order_score(endpoints.get(left_id), endpoints.get(right_id), nodes)
                order_pairs.append({"fact_ids": [left_id, right_id], "score": score})
        eligible_scores = [row["score"] for row in order_pairs if row["score"] is not None]
        relation_rows.append(
            {
                "id": relation_id,
                "type": relation["type"],
                "ordered": relation["ordered"],
                "proximity_pairs": pair_rows,
                "mean_distance": round(statistics.mean(
                    row["distance"] for row in pair_rows if row["distance"] is not None
                ), 6) if any(row["distance"] is not None for row in pair_rows) else None,
                "order_pairs": order_pairs,
                "order_score": round(statistics.mean(eligible_scores), 6) if eligible_scores else None,
            }
        )

    candidate_pairs = []
    for left_id, right_id in itertools.combinations(sorted(fact_paths), 2):
        distance = minimum_distance(fact_paths[left_id], fact_paths[right_id])
        if distance is not None:
            candidate_pairs.append((left_id, right_id, distance))

    real_mean = statistics.mean(real_distances) if real_distances else None
    null_means: list[float] = []
    if real_distances and len(candidate_pairs) >= len(real_distances):
        rng = stable_rng(case_dir.name, tier)
        for _ in range(PERMUTATIONS):
            draw = rng.sample(candidate_pairs, len(real_distances))
            null_means.append(statistics.mean(item[2] for item in draw))
    null_mean = statistics.mean(null_means) if null_means else None
    effect = ((null_mean - real_mean) / null_mean) if null_mean else None
    percentile = (
        sum(value >= real_mean for value in null_means) / len(null_means)
        if null_means and real_mean is not None else None
    )
    order_scores = [row["order_score"] for row in relation_rows if row["order_score"] is not None]
    return {
        "rendering": str(rendering_path.relative_to(ROOT)),
        "relation_count": len(relation_rows),
        "scorable_proximity_pair_count": len(real_distances),
        "candidate_null_pair_count": len(candidate_pairs),
        "real_mean_distance": round(real_mean, 6) if real_mean is not None else None,
        "null_mean_distance": round(null_mean, 6) if null_mean is not None else None,
        "proximity_advantage": round(effect, 6) if effect is not None else None,
        "null_percentile_closer": round(percentile, 6) if percentile is not None else None,
        "order_relation_count": len(order_scores),
        "mean_order_score": round(statistics.mean(order_scores), 6) if order_scores else None,
        "relations": relation_rows,
    }


def discover_cases() -> list[Path]:
    found = []
    for test_class in TEST_CLASSES:
        for case_dir in (ROOT / test_class).iterdir():
            if case_dir.is_dir() and case_dir.name in CASE_NAMES:
                found.append(case_dir)
    names = {path.name for path in found}
    if names != CASE_NAMES:
        raise RuntimeError(f"Case discovery mismatch: missing={sorted(CASE_NAMES - names)}")
    return sorted(found, key=lambda path: path.name)


def build_report() -> dict:
    cases = {}
    for case_dir in discover_cases():
        gold = load_json(case_dir / "gold.json")
        missing_ordered = [r["id"] for r in gold["relations"] if "ordered" not in r]
        if missing_ordered:
            raise ValueError(f"{case_dir.name} relations lack ordered: {missing_ordered}")
        renderings = {}
        for judged_path in sorted((case_dir / "judged").glob("*.json")):
            tier = judged_path.stem
            judged = load_json(judged_path)
            if LEVEL not in judged:
                continue
            renderings[tier] = score_rendering(case_dir, tier, gold, judged)
        effects = [r["proximity_advantage"] for r in renderings.values()
                   if r["proximity_advantage"] is not None]
        cases[case_dir.name] = {
            "test_class": case_dir.parent.name,
            "rendering_count": len(renderings),
            "case_effect_median": round(statistics.median(effects), 6) if effects else None,
            "renderings": renderings,
        }

    case_effects = [case["case_effect_median"] for case in cases.values()
                    if case["case_effect_median"] is not None]
    if len(case_effects) != len(CASE_NAMES):
        raise RuntimeError(f"Expected 8 scorable case effects, got {len(case_effects)}")
    return {
        "design": {
            "level": LEVEL,
            "permutations_per_rendering": PERMUTATIONS,
            "tree_distance": "edge count via LCA",
            "multi_node_aggregation": "minimum path-combination distance",
            "effect_size": "(null_mean_distance - real_mean_distance) / null_mean_distance",
            "order_partial_credit": "mean pass rate across eligible consecutive ordinal-sibling pairs",
            "case_rollup": "median rendering proximity advantage",
            "independent_case_count": len(case_effects),
            "corpus_wide_p_value": None,
        },
        "cases": cases,
        "across_case_distribution": {
            "n": len(case_effects),
            "values": sorted(case_effects),
            "min": round(min(case_effects), 6),
            "q1": round(statistics.quantiles(case_effects, n=4, method="inclusive")[0], 6),
            "median": round(statistics.median(case_effects), 6),
            "mean": round(statistics.mean(case_effects), 6),
            "q3": round(statistics.quantiles(case_effects, n=4, method="inclusive")[2], 6),
            "max": round(max(case_effects), 6),
        },
        "limitations": [
            "Effective independent n is about eight cases, not the relation-instance count.",
            "Shared endpoints within a rendering remain dependent.",
            "Corpus grammar non-conformance can confound a null result.",
            "Topic-based source sections can make proximity restate topical grouping.",
        ],
    }


def fmt(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_markdown(report: dict, path: Path) -> None:
    design = report["design"]
    lines = [
        "# Structural-linkage diagnostic (generated)",
        "",
        "Regenerate with `python3 scoring/structural_linkage.py` from the semantic-compression directory.",
        "Positive proximity advantage means gold-linked facts are closer than random fact pairs.",
        "",
        "## Method decisions",
        "",
        f"- Tree distance: {design['tree_distance']}; for paths `a` and `b`, "
        "`len(a) + len(b) - 2 * len(LCA(a, b))`.",
        f"- Multi-node facts: {design['multi_node_aggregation']}; this asks whether any node "
        "carrying the fact makes the linkage structurally available.",
        f"- Permutation baseline: {design['permutations_per_rendering']:,} deterministic draws per "
        "rendering, each sampling the real pair count without replacement from that rendering's "
        "locatable fact pairs. This gives stable diagnostic resolution while remaining fast.",
        f"- Effect size: `{design['effect_size']}`. Positive values are the fractional distance "
        "reduction versus random pairs; null percentiles are descriptive only.",
        f"- Order partial credit: {design['order_partial_credit']}. Only consecutive pairs whose "
        "endpoints resolve to ordinal-enumerator siblings under one parent are eligible.",
        f"- Case rollup: {design['case_rollup']}; the median limits one tier's topology from "
        "dominating. Effective independent n is about eight cases, so no corpus-wide p-value is computed.",
        "",
        "## Rendering results",
        "",
        "| case | tier | real mean distance | null mean distance | proximity advantage | null percentile | order relations | mean order score |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for case_id, case in report["cases"].items():
        for tier, rendering in case["renderings"].items():
            lines.append(
                f"| {case_id} | {tier} | {fmt(rendering['real_mean_distance'])} | "
                f"{fmt(rendering['null_mean_distance'])} | {fmt(rendering['proximity_advantage'])} | "
                f"{fmt(rendering['null_percentile_closer'])} | {rendering['order_relation_count']} | "
                f"{fmt(rendering['mean_order_score'])} |"
            )
    lines.extend([
        "",
        "## Case rollup",
        "",
        "Case effect = median rendering proximity advantage. No corpus-wide p-value is computed.",
        "",
        "| case | renderings | case effect |",
        "|---|---:|---:|",
    ])
    for case_id, case in report["cases"].items():
        lines.append(f"| {case_id} | {case['rendering_count']} | {fmt(case['case_effect_median'])} |")
    dist = report["across_case_distribution"]
    lines.extend([
        "",
        "## Across-case distribution",
        "",
        f"n={dist['n']}; min={fmt(dist['min'])}; Q1={fmt(dist['q1'])}; "
        f"median={fmt(dist['median'])}; mean={fmt(dist['mean'])}; "
        f"Q3={fmt(dist['q3'])}; max={fmt(dist['max'])}.",
        "",
        "Limitations: shared endpoints remain dependent; grammar non-conformance can confound a null result; topic-oriented source sections can make proximity reflect topical grouping.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    report = build_report()
    json_path = HERE / "structural_linkage.json"
    md_path = HERE / "STRUCTURAL_LINKAGE.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
