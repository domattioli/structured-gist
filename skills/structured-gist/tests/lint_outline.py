#!/usr/bin/env python3
"""
Deterministic conformance linter for structured-gist outline format.
Pure Python 3 stdlib, no external dependencies, no randomness, no network.
"""

import sys
import re
from typing import List, Tuple, Optional
from math import gcd
from functools import reduce


# Type: violation = (lineno: int, rule_id: str, message: str)
Violation = Tuple[int, str, str]


_RESPONSIVE_ITEM = re.compile(r'^(\s*)-\s+(.*)$')


def _looks_like_ladder_marker(s: str) -> bool:
    """
    True if `s` (already stripped of a GFM '- ' list-item prefix) itself
    starts with a NON-dash ladder glyph — attribute (`▸`), hook (`↪`/`→`),
    or an ordinal/nominal enumerator (`I.`/`A.`/`i.`/`a.`). This is the
    `responsive`-mode detection signal (SKILL.md `## Render modes`): only
    `responsive` syntax ever puts a marker glyph directly after a GFM `- `
    bullet — `inline` mode emits the bare glyph with no leading dash, so a
    plain inline outline never matches and stays inline (conservative
    detection, per SKILL.md `responsive` mode spec).
    """
    if s.startswith('▸ ') or s.startswith('↪ ') or s.startswith('→ '):
        return True
    if re.match(r'^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+', s):
        return True
    if re.match(r'^[A-Z]\.\s+', s):
        return True
    if re.match(r'^(i|ii|iii|iv|v|vi|vii|viii|ix|x)\.\s+', s):
        return True
    if re.match(r'^[a-z]\.\s+', s):
        return True
    return False


def extract_outline_from_text(text: str) -> Tuple[List[str], bool]:
    """
    Extract outline lines from text.
    - If text contains triple-backtick fences, extract lines INSIDE the first fence block.
    - Otherwise, detect `responsive` mode (a genuine GFM list, 2-space-per-rung
      indent, ladder glyph inside each item's content — SKILL.md `## Render
      modes`) vs. plain `inline` lines, and use all non-empty lines either way.
    Returns (lines, is_block_mode) where lines have leading/trailing whitespace
    preserved (rewritten to their block-equivalent form when the source was
    `responsive`, so R1-R10 validate identically) and is_block_mode is True
    only when the lines came from a fenced block (block render mode — the
    surface R11 line-wrap rule applies to; `inline` AND `responsive` modes
    wrap themselves — GitHub markdown / the chat renderer respectively — per
    SKILL.md `## Spacing` + `## Render modes`, so R11 does not apply to
    either).
    """
    lines = text.split('\n')
    in_fence = False
    outline_lines = []
    fence_pattern = re.compile(r'^```')

    for line in lines:
        if fence_pattern.match(line):
            if not in_fence:
                in_fence = True
            else:
                break # end of fence block
        elif in_fence and line.strip():
            outline_lines.append(line)
        elif not in_fence and not in_fence and line.strip():
            # No fence found yet and line is non-empty; will accumulate if no fence appears
            pass

    # If we found a fence, return what we extracted (block mode).
    if outline_lines:
        return outline_lines, True

    # No fence: either `inline` (raw ladder glyphs, no list wrapper) or
    # `responsive` (real GFM list items, marker glyph inside each item's
    # content). Detect responsive by scanning for a '- ' list item whose
    # content itself starts with a non-dash ladder glyph — a shape `inline`
    # mode never produces (see `_looks_like_ladder_marker`).
    raw_lines = [line for line in lines if line.strip()]
    is_responsive = False
    for line in raw_lines:
        m = _RESPONSIVE_ITEM.match(line)
        if m and _looks_like_ladder_marker(m.group(2)):
            is_responsive = True
            break

    if not is_responsive:
        return raw_lines, False

    # Rewrite each responsive GFM list-item line into its block-equivalent
    # form: depth = (list-item's own leading spaces) // 2 (GFM-standard
    # rung for a '- ' bullet), then re-indent at 4 spaces/rung (this
    # linter's internal unit) and drop the list bullet — re-adding a bare
    # '- ' only for a depth-0 concept, whose content has no glyph of its
    # own (the list bullet AND the concept marker are both '-'). Every
    # deeper item's content already starts with its own ladder glyph, so
    # it needs only the re-indent.
    rewritten = []
    for line in raw_lines:
        m = _RESPONSIVE_ITEM.match(line)
        if not m:
            rewritten.append(line)
            continue
        indent_str, content = m.group(1), m.group(2)
        depth = len(indent_str) // 2
        if _looks_like_ladder_marker(content):
            rewritten.append(' ' * (depth * 4) + content)
        else:
            rewritten.append(' ' * (depth * 4) + '- ' + content)
    return rewritten, False


def parse_line(line: str, unit: int = 2) -> Tuple[int, str, str]:
    """
    Parse a single outline line.
    Returns (depth, family, text) where:
    - depth = (count of leading spaces) // unit
    - family = marker type ('dash', 'arrow', 'attr', 'uroman', 'ualpha', 'lroman', 'lalpha', 'unknown')
    - text = content after the marker (stripped of marker and surrounding **)
    """
    # Count leading spaces
    stripped = line.lstrip(' ')
    leading_spaces = len(line) - len(stripped)
    depth = leading_spaces // unit

    # Now parse the family and text from the stripped line
    s = stripped

    if not s:
        return depth, 'unknown', ''

    # Test order matters: roman before single-letter alpha

    # Check for hook arrow (↪ primary) or plain arrow (→ legacy-tolerated)
    if s.startswith('↪ '):
        text = s[2:].strip()
        return depth, 'arrow', text
    if s.startswith('→ '):
        text = s[2:].strip()
        return depth, 'arrow', text

    # Check for attribute marker (▸ - U+25B8)
    if s.startswith('▸ '):
        text = s[2:].strip()
        return depth, 'attr', text

    # Check for uppercase roman numeral (I, II, III, ..., X)
    uroman_match = re.match(r'^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+', s)
    if uroman_match:
        text = s[len(uroman_match.group(0)):].strip()
        return depth, 'uroman', text

    # Check for single uppercase letter (A-Z) followed by period and space (but not roman)
    if re.match(r'^[A-Z]\.\s+', s):
        match = re.match(r'^[A-Z]\.\s+', s)
        text = s[len(match.group(0)):].strip()
        return depth, 'ualpha', text

    # Check for lowercase roman numeral (i, ii, iii, ..., x)
    lroman_match = re.match(r'^(i|ii|iii|iv|v|vi|vii|viii|ix|x)\.\s+', s)
    if lroman_match:
        text = s[len(lroman_match.group(0)):].strip()
        return depth, 'lroman', text

    # Check for single lowercase letter (a-z) followed by period and space
    if re.match(r'^[a-z]\.\s+', s):
        match = re.match(r'^[a-z]\.\s+', s)
        text = s[len(match.group(0)):].strip()
        return depth, 'lalpha', text

    # Check for dash
    if s.startswith('- '):
        text = s[2:].strip()
        # Strip surrounding ** if present
        if text.startswith('**') and text.endswith('**'):
            text = text[2:-2]
        return depth, 'dash', text

    # Check for bullet (•)
    if s.startswith('• '):
        text = s[2:].strip()
        return depth, 'bullet', text

    return depth, 'unknown', s


def count_words(text: str) -> int:
    """Count whitespace-separated words in text, after stripping ** if present."""
    if text.startswith('**') and text.endswith('**'):
        text = text[2:-2]
    return len(text.split()) if text.strip() else 0


_STRAY_LEADING_MARKER = re.compile(r'^(•|→|↪|▸|-)\s')


def r9_delimiter_violation(text: str) -> Optional[str]:
    """
    Return a short reason string if `text` appends >2 words after a delimiter
    (spaced dash, colon, semicolon, arrow) or inside a parenthetical, else None.
    Inline code spans are stripped first. Caller must skip arrow-family nodes.
    """
    # strip inline code spans so file:line / code delimiters don't count
    t = re.sub(r'`[^`]*`', '', text)
    # strip HTML entities (&amp; &#x27; &gt;) — their trailing ';' is not a prose
    # semicolon and must not trip the delimiter scan ()
    t = re.sub(r'&#?\w+;', ' ', t)
    # strip surrounding bold if present
    if t.startswith('**') and t.endswith('**'):
        t = t[2:-2]
    # 1) parentheticals: >2 words inside any (...) group
    for m in re.finditer(r'\(([^)]*)\)', t):
        if len(m.group(1).split()) > 2:
            return f"parenthetical with {len(m.group(1).split())} words (>2) — nest as a child"
    # remove parentheticals before the delimiter scan
    t2 = re.sub(r'\([^)]*\)', '', t)
    # 2) delimiters: first occurrence of spaced dash / colon / semicolon / arrow
    # space-flanked dash forms: ' - ', ' – ', ' — '
    delim_re = re.compile(r'\s[-–—]\s|:|;|→')
    m = delim_re.search(t2)
    if m:
        tail = t2[m.end():]
        n = len(tail.split())
        if n > 2:
            d = m.group(0).strip() or '-'
            return f"'{d}' followed by {n} words (>2) — nest the tail as a child"
    return None


def lint_text(text: str) -> List[Violation]:
    """
    Lint an outline text and return list of violations.
    """
    outline_lines, is_block_mode = extract_outline_from_text(text)
    if not outline_lines:
        return []

    # Step 1: Merge continuation lines into marker lines.
    # A continuation line is one whose parse_line returns family='unknown'.
    # We build merged_lines by keeping only marker-bearing lines.
    # Continuation lines are either dropped or appended to the preceding marker line's text.
    # raw_line_info tracks each PHYSICAL line (marker or continuation) against
    # the merged_lines index it folds into, plus its owning marker's indent —
    # R11 (block-mode line wrap) needs physical-line width + indent, which the
    # merge step below discards.
    merged_lines = []
    raw_line_info = [] # (merged_lineno, raw_line, is_continuation, marker_indent)
    owning_indent = None
    for line in outline_lines:
        # Check if this line has a marker by parsing with unit=2 (temporary)
        _, family, _ = parse_line(line, unit=2)
        if family != 'unknown':
            # This is a marker line; add it
            merged_lines.append(line)
            owning_indent = len(line) - len(line.lstrip(' '))
            raw_line_info.append((len(merged_lines), line, False, owning_indent))
        else:
            # This is a continuation line (markerless)
            if merged_lines:
                # Append stripped text to the previous marker line's text
                # (We'll re-parse the whole thing below with the correct unit)
                merged_lines[-1] = merged_lines[-1] + ' ' + line.strip()
                raw_line_info.append((len(merged_lines), line, True, owning_indent))
            # else: continuation is first line, keep it for potential error flagging below

    # Step 2: Compute indent unit from marker-bearing lines ONLY
    # This prevents continuation lines from polluting the GCD
    leading_spaces_list = []
    for line in merged_lines:
        stripped = line.lstrip(' ')
        leading_spaces = len(line) - len(stripped)
        if leading_spaces > 0:
            leading_spaces_list.append(leading_spaces)

    if leading_spaces_list:
        unit = reduce(gcd, leading_spaces_list)
    else:
        unit = 2 # fallback if no indented lines

    # Step 3: Parse all lines (merged_lines only) and apply rules
    parsed = []
    for i, line in enumerate(merged_lines):
        depth, family, text = parse_line(line, unit=unit)
        parsed.append((i + 1, depth, family, text, line)) # lineno is 1-indexed within merged

    violations: List[Violation] = []

    # Pre-compute parent info for each line
    parent_info = {} # lineno -> (parent_depth, parent_family)
    for i, (lineno, depth, _family, _text, _) in enumerate(parsed):
        if depth == 0:
            parent_info[lineno] = (None, None)
        else:
            # Find the nearest ancestor with depth < current depth
            parent_depth = None
            parent_family = None
            for j in range(i - 1, -1, -1):
                prev_lineno, prev_depth, prev_family, _, _ = parsed[j]
                if prev_depth < depth:
                    parent_depth = prev_depth
                    parent_family = prev_family
                    break
            parent_info[lineno] = (parent_depth, parent_family)

    # R1: ladder-by-depth (NEW: bullet invalid at all depths, arrow valid at any depth, attr valid at depth>=1)
    for lineno, depth, family, _text, _line in parsed:
        valid_families = set()
        if depth == 0:
            valid_families = {'dash'}
        elif depth == 1:
            valid_families = {'uroman', 'ualpha', 'arrow', 'attr'}
        elif depth >= 2:
            valid_families = {'lroman', 'lalpha', 'arrow', 'attr'}

        if family == 'bullet':
            violations.append((lineno, 'R1', "bullet (•) invalid at any depth"))
        elif family not in valid_families:
            violations.append((lineno, 'R1', f"invalid family '{family}' at depth {depth}"))

    # R2: no skipped rungs
    for i, (lineno, depth, _family, _text, _line) in enumerate(parsed):
        if i > 0:
            prev_lineno, prev_depth, prev_family, _, _ = parsed[i - 1]
            if depth > prev_depth + 1:
                violations.append((lineno, 'R2', f"skipped rung (depth {depth} after depth {prev_depth})"))

    # R3: REMOVED (block-only means no ** on tops needed)

    # R4 (REVISED): non-leaf arrow must be first child of its parent
    # A leaf arrow (no children) is valid anywhere.
    # A non-leaf arrow (has children) MUST be the first child of its parent.
    for i, (lineno, depth, family, _text, _line) in enumerate(parsed):
        if family == 'arrow':
            # Check if this arrow has children (next line with greater depth)
            has_children = False
            if i + 1 < len(parsed):
                next_lineno, next_depth, next_family, _, _ = parsed[i + 1]
                if next_depth > depth:
                    has_children = True

            # If non-leaf, check that it's the first child of its parent
            if has_children:
                # Find parent (nearest prior line at depth < current depth)
                parent_lineno = None
                parent_depth = None
                for j in range(i - 1, -1, -1):
                    prev_lineno, prev_depth, prev_family, _, _ = parsed[j]
                    if prev_depth < depth:
                        parent_lineno = prev_lineno
                        parent_depth = prev_depth
                        break

                # Find siblings at same depth with same parent appearing before this arrow
                has_earlier_sibling = False
                for j in range(i):
                    sib_lineno, sib_depth, sib_family, _, _ = parsed[j]
                    if sib_depth == depth:
                        # Check if this sibling has the same parent
                        # Find parent of this sibling
                        sib_parent_lineno = None
                        for k in range(j - 1, -1, -1):
                            prev_lineno, prev_depth, prev_family, _, _ = parsed[k]
                            if prev_depth < sib_depth:
                                sib_parent_lineno = prev_lineno
                                break
                        # If same parent, this is an earlier sibling
                        if sib_parent_lineno == parent_lineno:
                            has_earlier_sibling = True
                            break

                if has_earlier_sibling:
                    violations.append((lineno, 'R4', "non-leaf arrow must be first child of its parent"))

    # R5: arrow rarity (bullets gone; count depth-1 NON-arrow enumerator nodes)
    i = 0
    while i < len(parsed):
        lineno, depth, family, text, line = parsed[i]
        if depth == 0 and family == 'dash':
            # This is the start of a block; count arrows and depth-1 NON-arrow enumerators
            block_start = i
            block_end = i + 1
            while block_end < len(parsed):
                next_lineno, next_depth, next_family, _, _ = parsed[block_end]
                if next_depth == 0:
                    break # new top-level block
                block_end += 1

            # Count arrows at any depth, and non-arrow enumerators at depth 1
            arrow_count = 0
            depth1_non_arrow_count = 0
            for j in range(block_start + 1, block_end):
                _, jdepth, jfamily, _, _ = parsed[j]
                if jfamily == 'arrow':
                    arrow_count += 1
                elif jdepth == 1 and jfamily != 'arrow':
                    depth1_non_arrow_count += 1

            if arrow_count > depth1_non_arrow_count:
                for j in range(block_start + 1, block_end):
                    _, jdepth, jfamily, jtext, _ = parsed[j]
                    if jfamily == 'arrow':
                        violations.append((parsed[j][0], 'R5', f"too many arrows ({arrow_count}) vs depth-1 non-arrow nodes ({depth1_non_arrow_count}) in block"))
                        break # Report once per block

            i = block_end
        else:
            i += 1

    # R6: sibling family consistency (non-arrow only)
    # Group lines by parent
    sibling_groups = {} # (parent_depth, parent_lineno) -> [(lineno, family, text, is_arrow), ...]
    for i, (lineno, depth, family, text, _line) in enumerate(parsed):
        if depth == 0:
            continue

        # Find parent
        parent_lineno = None
        parent_depth = None
        for j in range(i - 1, -1, -1):
            prev_lineno, prev_depth, prev_family, _, _ = parsed[j]
            if prev_depth < depth:
                parent_lineno = prev_lineno
                parent_depth = prev_depth
                break

        key = (parent_depth, parent_lineno)
        if key not in sibling_groups:
            sibling_groups[key] = []
        sibling_groups[key].append((lineno, family, text, family == 'arrow'))

    # Check consistency within each sibling group
    for _key, siblings in sibling_groups.items():
        non_arrow_families = set(f for _, f, _, is_arrow in siblings if not is_arrow)
        if len(non_arrow_families) > 1:
            # Violation: mixed families among non-arrow siblings
            for lineno, _family, _text, is_arrow in siblings:
                if not is_arrow:
                    violations.append((lineno, 'R6', f"mixed sibling families: {non_arrow_families}"))

    # R7: word caps (REVISED: add attr cap ≤4 words; cap all depth>=2 enumerators)
    for lineno, depth, family, text, _line in parsed:
        if family == 'arrow':
            continue # arrows exempt

        word_count = count_words(text)
        max_words = None

        if depth == 0 and family == 'dash':
            max_words = 3
        elif depth == 1 and family in ('attr', 'bullet'):
            # attr at any depth has 4-word cap; bullet (legacy, but here for completeness) has 5
            if family == 'attr':
                max_words = 4
            else:
                max_words = 5
        elif depth >= 2 and family == 'attr':
            max_words = 4
        elif depth >= 2 and family in ('uroman', 'ualpha', 'lroman', 'lalpha'):
            max_words = 6

        if max_words is not None and word_count > max_words:
            violations.append((lineno, 'R7', f"text too wordy ({word_count} words, max {max_words})"))

    # R8: attr cannot nest directly under attr
    for lineno, depth, family, _text, _line in parsed:
        if family == 'attr':
            # Find parent (nearest prior line at depth < current depth)
            parent_family = None
            for i, (parsed_lineno, _parsed_depth, _parsed_family, _, _) in enumerate(parsed):
                if parsed_lineno == lineno:
                    # Found self, now look backward for parent
                    for j in range(i - 1, -1, -1):
                        prev_lineno, prev_depth, prev_family, _, _ = parsed[j]
                        if prev_depth < depth:
                            parent_family = prev_family
                            break
                    break

            if parent_family == 'attr':
                violations.append((lineno, 'R8', "attribute cannot nest directly under attribute; interpose a hook or enumerator"))

    # R9: delimiter-split — a structural (non-arrow) node that appends >2 words
    # after a spaced dash / colon / semicolon / arrow, or inside a parenthetical,
    # should split the tail into a nested child. Arrow (↪) leaves are exempt.
    for lineno, _depth, family, text, _line in parsed:
        if family == 'arrow':
            continue
        reason = r9_delimiter_violation(text)
        if reason is not None:
            violations.append((lineno, 'R9', reason))

    # R10: double-marker — a non-arrow node whose text BEGINS with a stray
    # marker glyph (• → ↪ ▸ or a leading '- ') is two markers wearing one
    # line: the terminal double-bullet defect (e.g. '- • target').
    # Arrow families (↪/→) are the one legitimate leading-glyph case and are
    # exempt; a mid-text 'X → Y' causality idiom does not start the text, so
    # it never fires here (preserves the single-arrow interaction note).
    for lineno, _depth, family, text, _line in parsed:
        if family in ('arrow', 'unknown'):
            continue
        if _STRAY_LEADING_MARKER.match(text):
            violations.append((lineno, 'R10', f"double marker: node text begins with stray glyph '{text[0]}'"))

    # R11: block-mode line wrap — narrow-viewport soft-wrap defect (user
    # screenshot, 2026-07-22). Block mode (fenced) only; inline mode is
    # GitHub-rendered markdown and wraps itself (SKILL.md `## Spacing`).
    # (i) any physical line >64 chars is flagged (phone-portrait monospace
    # budget); (ii) a hand-wrapped continuation line's leading whitespace
    # must be IDENTICAL to its owning marker line's indent — no hanging
    # indent, no marker glyph (user spec, verbatim).
    if is_block_mode:
        _MAX_LINE_WIDTH = 64
        for merged_lineno, raw_line, is_continuation, marker_indent in raw_line_info:
            if len(raw_line) > _MAX_LINE_WIDTH:
                violations.append((merged_lineno, 'R11', f"line exceeds {_MAX_LINE_WIDTH} chars ({len(raw_line)})"))
            if is_continuation:
                cont_indent = len(raw_line) - len(raw_line.lstrip(' '))
                if cont_indent != marker_indent:
                    violations.append((merged_lineno, 'R11', f"continuation indent ({cont_indent}) != node indent ({marker_indent})"))

    # R12: connective-clause check — a node's text must NOT contain a subordinate
    # "because", "since", or "so that" clause that joins two independent facts.
    # Exception: short quoted fragments (like '"failed because the cache was cold"').
    for lineno, _depth, family, text, _line in parsed:
        if family == 'arrow':
            continue # arrows exempt

        # Strip surrounding ** if present
        t = text
        if t.startswith('**') and t.endswith('**'):
            t = t[2:-2]

        # Find connective words NOT inside quotes
        # Strategy: remove all quoted spans, then check for connective words
        t_no_quotes = re.sub(r'"[^"]*"', ' ', t)
        t_no_quotes = re.sub(r"'[^']*'", ' ', t_no_quotes)

        # Check for connective words: "because", "since", "so that"
        # These should be word-bounded to avoid matching inside longer words
        if re.search(r'\bbecause\b|\bsince\b|\bso that\b', t_no_quotes, re.IGNORECASE):
            violations.append((lineno, 'R12', "text contains a subordinate clause ('because', 'since', 'so that') joining independent facts — nest the consequent as a child"))

    # R13: concept-attribute duplication check — a concept (dash-family node) must
    # NOT duplicate an attribute (▸-child) heading. Concepts CAN duplicate other
    # concepts or enumerators.
    for i, (lineno, depth, family, text, _line) in enumerate(parsed):
        if depth != 0 or family != 'dash':
            continue # only check top-level concepts

        # Get the concept text (strip ** if present)
        concept_text = text
        if concept_text.startswith('**') and concept_text.endswith('**'):
            concept_text = concept_text[2:-2]

        # Find all immediate ▸ (attribute) children of this concept
        concept_end = i + 1
        while concept_end < len(parsed):
            next_lineno, next_depth, next_family, _, _ = parsed[concept_end]
            if next_depth == 0:
                break # new top-level concept
            concept_end += 1

        # Check all attributes at depth 1 within this concept
        for j in range(i + 1, concept_end):
            child_lineno, child_depth, child_family, child_text, _ = parsed[j]
            if child_depth == 1 and child_family == 'attr':
                # Get attribute text (strip ** if present)
                attr_text = child_text
                if attr_text.startswith('**') and attr_text.endswith('**'):
                    attr_text = attr_text[2:-2]

                # Check if concept text matches attribute text
                if concept_text == attr_text:
                    violations.append((child_lineno, 'R13', f"attribute text duplicates its parent concept text ('{concept_text}') — this is a flattening defect"))

    # R14: interrogative attribute check — an attribute (▸ node) must NOT be
    # interrogative (must not start with interrogative words like "What", "Why",
    # "How", "When", "Where", "Which", "Who").
    interrogatives = r'\b(What|Why|How|When|Where|Which|Who)\b'
    for lineno, _depth, family, text, _line in parsed:
        if family != 'attr':
            continue # only check attributes

        # Get attribute text (strip ** if present)
        attr_text = text
        if attr_text.startswith('**') and attr_text.endswith('**'):
            attr_text = attr_text[2:-2]

        # Check if text starts with an interrogative word
        if re.match(interrogatives, attr_text):
            violations.append((lineno, 'R14', f"attribute '{attr_text}' is interrogative (starts with a question word) — use a descriptive property name instead"))

    # R15: concept count-word prefix check — a concept (dash-family node) must NOT
    # start with a number or count-word (e.g., "Three findings", "5 decisions",
    # "One open question"). Count-words include: One, Two, Three, ..., Nine, Ten,
    # Multiple, Several, Few, Many, Some, etc.
    count_words_set = {
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
        'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen',
        'eighteen', 'nineteen', 'twenty',
        'multiple', 'several', 'few', 'many', 'some', 'various', 'numerous', 'countless'
    }
    for lineno, depth, family, text, _line in parsed:
        if depth != 0 or family != 'dash':
            continue # only check top-level concepts

        # Get concept text (strip ** if present)
        concept_text = text
        if concept_text.startswith('**') and concept_text.endswith('**'):
            concept_text = concept_text[2:-2]

        # Check if text starts with a digit or count-word
        # First, check for leading digit
        if re.match(r'^\d+', concept_text):
            violations.append((lineno, 'R15', f"concept '{concept_text}' starts with a number — remove the count and keep only the noun"))

        # Next, check for leading count-word (case-insensitive, word-bounded)
        first_word = concept_text.split()[0].lower() if concept_text.split() else ''
        if first_word in count_words_set:
            violations.append((lineno, 'R15', f"concept '{concept_text}' starts with a count-word ('{first_word}') — remove the count and keep only the noun"))

    return violations


def lint_file(path: str) -> List[Violation]:
    """Lint a file and return list of violations."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        return lint_text(text)
    except Exception as e:
        return [(0, 'IO', f"failed to read file: {e}")]


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        # Read from stdin
        text = sys.stdin.read()
        violations = lint_text(text)
        for lineno, rule, msg in sorted(violations, key=lambda x: x[0]):
            print(f" line {lineno} [{rule}]: {msg}")
        print(f"structured-gist-lint: {'PASS' if not violations else 'FAIL'} ({len(violations)} violations)")
        sys.exit(0 if not violations else 1)

    # Lint files
    all_violations = {}
    for filepath in sys.argv[1:]:
        violations = lint_file(filepath)
        all_violations[filepath] = violations
        for lineno, rule, msg in sorted(violations, key=lambda x: x[0]):
            print(f" line {lineno} [{rule}]: {msg}")
        status = 'PASS' if not violations else 'FAIL'
        print(f"structured-gist-lint {filepath}: {status} ({len(violations)} violations)")

    # Exit with success only if all files are clean
    has_violations = any(all_violations.values())
    sys.exit(1 if has_violations else 0)


if __name__ == '__main__':
    main()
