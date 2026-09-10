#!/usr/bin/env python3
"""
Shared outline-node extraction, used by scoring/wording_fidelity.py and
scoring/findability.py.

Reuses `tests/lint_outline.py`'s real extraction (`extract_outline_from_text`)
and marker parsing (`parse_line`) unmodified -- this module does not
reimplement any structural rule. What it adds is the one preprocessing step
those two evals both need that no existing module exposes: turning a
rendering's raw text into an ordered list of *semantic nodes* (marker +
continuation-merged text), each with the marker glyph stripped and any R11
hard-wrap continuation lines rejoined into one string.

`lint_outline.lint_text()` already performs this exact merge internally (a
continuation line -- `parse_line` family == 'unknown' -- gets appended to the
previous marker line's text) but only as a private step on the way to
computing violations; it never returns the merged nodes themselves. This
module runs the identical merge algorithm (same condition, same order) so a
node's `.text` here is byte-for-byte what the real linter validates, not a
second, potentially-diverging reimplementation.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from functools import reduce
from math import gcd
from pathlib import Path
from typing import List

LINTER_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tests"
sys.path.insert(0, str(LINTER_DIR))
import lint_outline  # noqa: E402

# The four marker roles SKILL.md defines (concept/attribute/enumerator/
# explanation) -- see `## Marker taxonomy`. 'bullet' and 'unknown' are
# linter violations, not valid semantic nodes, and are excluded.
MARKER_FAMILIES = {"dash", "attr", "uroman", "ualpha", "lroman", "lalpha", "arrow"}


@dataclass(frozen=True)
class Node:
    index: int      # 0-indexed position among extracted nodes, in on-page reading order
    depth: int
    family: str     # 'dash' | 'attr' | 'uroman' | 'ualpha' | 'lroman' | 'lalpha' | 'arrow'
    text: str       # marker-stripped, continuation-merged, surrounding ** stripped


def extract_nodes(text: str) -> List[Node]:
    """
    Parse one rendering's raw file content into its ordered semantic nodes.
    Empty input (or input with no fence/list content) returns [].
    """
    outline_lines, _is_block = lint_outline.extract_outline_from_text(text)
    if not outline_lines:
        return []

    # Merge continuation lines into their owning marker line -- identical
    # condition to lint_outline.lint_text()'s Step 1.
    merged_lines: List[str] = []
    for line in outline_lines:
        _, family, _ = lint_outline.parse_line(line, unit=2)
        if family != "unknown":
            merged_lines.append(line)
        elif merged_lines:
            merged_lines[-1] = merged_lines[-1] + " " + line.strip()
        # else: a leading continuation line with nothing to attach to yet
        # carries no marker and is not a node -- dropped, same as lint_text.

    if not merged_lines:
        return []

    # Indent unit = GCD of marker-line leading-space counts, identical to
    # lint_outline.lint_text()'s Step 2 (keeps depth values linter-identical).
    leading = [
        len(l) - len(l.lstrip(" ")) for l in merged_lines if len(l) - len(l.lstrip(" ")) > 0
    ]
    unit = reduce(gcd, leading) if leading else 2

    nodes: List[Node] = []
    for line in merged_lines:
        depth, family, txt = lint_outline.parse_line(line, unit=unit)
        if family in MARKER_FAMILIES:
            nodes.append(Node(index=len(nodes), depth=depth, family=family, text=txt))
    return nodes
