#!/usr/bin/env python3
"""
Deterministic check: in block-mode outline files, do hedged claims keep their hedge?
Reuses _merge_continuations from fidelity_check.py.
"""

import sys
import re
import json
import argparse
from pathlib import Path

# Add tests dir to sys.path to import fidelity_check
tests_dir = Path(__file__).parent.parent.parent.parent / "skills" / "structured-gist" / "tests"
sys.path.insert(0, str(tests_dir))

from fidelity_check import _merge_continuations


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check if hedged claims in outline files keep their hedge."
    )
    parser.add_argument(
        "--claim-regex",
        required=True,
        help="Regex to match claim nodes (case-insensitive)",
    )
    parser.add_argument(
        "--hedges",
        required=True,
        help="Comma-separated list of hedge words (case-insensitive whole-word match)",
    )
    parser.add_argument("files", nargs="+", help="Outline files to check")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON list of dicts",
    )
    return parser.parse_args()


def get_node_indent(line):
    """Return indent level (spaces before content)."""
    return len(line) - len(line.lstrip(" "))


def is_hook_node(stripped):
    """True if node opens with ↪."""
    return stripped.startswith("↪ ")


def check_file(filepath, claim_regex_str, hedge_words):
    """
    Check a single file. Return dict with keys:
      - verdict: NO_CLAIM | HEDGED | PARTIAL | STRIPPED
      - path: filepath
      - claims: count of claim nodes found
      - attached: count of claim nodes with attached hedge
      - hedges_found: list of unique hedges seen
      - where: list of (claim_idx, where_attached) tuples where attached
      - claim_texts: list of matched claim node texts
    """
    try:
        with open(filepath, encoding="utf-8") as fh:
            text = fh.read()
    except Exception as e:
        return {
            "verdict": "ERROR",
            "path": str(filepath),
            "error": str(e),
        }

    lines = _merge_continuations(text.splitlines())

    # Compile regex and hedge patterns
    claim_re = re.compile(claim_regex_str, re.IGNORECASE)
    hedge_patterns = [
        re.compile(rf"\b{re.escape(w)}\b", re.IGNORECASE) for w in hedge_words
    ]

    # Find claim nodes
    claim_indices = []
    claim_texts = []
    for i, line in enumerate(lines):
        if claim_re.search(line):
            claim_indices.append(i)
            claim_texts.append(line)

    if not claim_indices:
        return {
            "verdict": "NO_CLAIM",
            "path": str(filepath),
            "claims": 0,
            "attached": 0,
            "hedges_found": [],
            "where": [],
            "claim_texts": [],
        }

    # Check each claim node for hedge attachment
    attached_count = 0
    where_attached = []
    hedges_found = set()

    for claim_idx in claim_indices:
        claim_line = lines[claim_idx]
        claim_indent = get_node_indent(claim_line)
        claim_stripped = claim_line.lstrip(" ")

        # Check 1: hedge in claim node itself
        hedge_locations = []
        for hedge_word in hedge_words:
            hedge_pattern = re.compile(rf"\b{re.escape(hedge_word)}\b", re.IGNORECASE)
            if hedge_pattern.search(claim_line):
                hedge_locations.append("self")
                hedges_found.add(hedge_word)
                break

        # Check 2: hedge in parent node (nearest preceding with smaller indent)
        if not hedge_locations:
            for i in range(claim_idx - 1, -1, -1):
                parent_line = lines[i]
                parent_indent = get_node_indent(parent_line)
                if parent_indent < claim_indent:
                    for hedge_word in hedge_words:
                        hedge_pattern = re.compile(
                            rf"\b{re.escape(hedge_word)}\b", re.IGNORECASE
                        )
                        if hedge_pattern.search(parent_line):
                            hedge_locations.append("parent")
                            hedges_found.add(hedge_word)
                            break
                    break

        # Check 3: hedge in child ↪ node (deeper indent, ↪ marker, before sibling)
        if not hedge_locations:
            for i in range(claim_idx + 1, len(lines)):
                child_line = lines[i]
                child_indent = get_node_indent(child_line)

                # Stop if we hit a sibling or ancestor
                if child_indent <= claim_indent:
                    break

                child_stripped = child_line.lstrip(" ")
                if is_hook_node(child_stripped):
                    for hedge_word in hedge_words:
                        hedge_pattern = re.compile(
                            rf"\b{re.escape(hedge_word)}\b", re.IGNORECASE
                        )
                        if hedge_pattern.search(child_line):
                            hedge_locations.append("child")
                            hedges_found.add(hedge_word)
                            break
                    if hedge_locations:
                        break

        if hedge_locations:
            attached_count += 1
            where_attached.append((claim_idx, hedge_locations[0]))

    verdict = "NO_CLAIM" if not claim_indices else (
        "HEDGED" if attached_count == len(claim_indices) else (
            "PARTIAL" if attached_count > 0 else "STRIPPED"
        )
    )

    return {
        "verdict": verdict,
        "path": str(filepath),
        "claims": len(claim_indices),
        "attached": attached_count,
        "hedges_found": sorted(hedges_found),
        "where": where_attached,
        "claim_texts": claim_texts,
    }


def main():
    args = parse_args()

    hedge_words = [w.strip() for w in args.hedges.split(",") if w.strip()]
    results = []
    total_claims = 0
    total_attached = 0

    for filepath in args.files:
        result = check_file(filepath, args.claim_regex, hedge_words)
        results.append(result)
        if result["verdict"] != "NO_CLAIM" and result["verdict"] != "ERROR":
            total_claims += result["claims"]
            total_attached += result["attached"]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            verdict = result["verdict"]
            path = result["path"]
            claims = result.get("claims", 0)
            attached = result.get("attached", 0)
            hedges = result.get("hedges_found", [])
            where = result.get("where", [])

            where_str = ", ".join(
                [f"{idx}:{loc}" for idx, loc in where]
            ) if where else ""
            hedges_str = "[" + ", ".join(hedges) + "]" if hedges else "[]"

            print(
                f"{verdict:12} {path:50} claims={claims} attached={attached}  "
                f"hedges_found={hedges_str}  where={where_str}"
            )

        print(
            f"{'TOTAL':12} claims={total_claims} attached={total_attached}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
