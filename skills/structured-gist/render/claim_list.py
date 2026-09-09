#!/usr/bin/env python3
"""
Claim-list render target for structured-gist outline trees.

Implements FR-018, FR-018a, FR-018b, FR-019, FR-020:
- Emits JSONL (one claim record per line)
- Each record: claim, modality, polarity, source_span, parent_id
- Validates against published schema
- Derived view of the existing outline tree (reuses lint_outline parser)

No external dependencies beyond Python 3 stdlib.
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from io import StringIO

# Add parent directory to path for lint_outline import
sys.path.insert(0, str(Path(__file__).parent.parent / 'tests'))

from lint_outline import parse_line, extract_outline_from_text, lint_text


# Load and cache the schema
def _load_schema() -> Dict[str, Any]:
    """Load the claim_list schema from the adjacent JSON file."""
    schema_path = Path(__file__).parent / 'claim_list.schema.json'
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


_SCHEMA = _load_schema()


def _has_verb_predicate(text: str) -> bool:
    """
    Heuristic: determine if text contains a verb/predicate.

    Returns True if text contains:
    - Common auxiliary/modal verbs (is, are, was, were, has, have, had, do, does, did,
      can, could, will, would, should, must, may, might, shall)
    - Common verbs (be, have, do, go, get, make, take, know, give, come, use, find, tell,
      work, call, try, ask, need, feel, become, leave, put, mean, seem, help, talk, turn,
      start, show, hear, play, run, move, like, live, believe, hold, bring, begin, let,
      provide, contain, validate, check, require, allow, enable, disable, perform,
      support, expect, represent, implement, define, create, generate, produce, process,
      handle, manage, control, maintain, update, remove, add, delete, modify, retrieve,
      store, load, save, open, close, read, write, execute, return, throw, catch, pass,
      fail, succeed, etc.)
    - Words ending in -ed (past tense forms)
    - Words ending in -ing (gerund/progressive forms)

    Does NOT count bare noun phrases like "Configuration" or "Name".
    """
    if not text or not text.strip():
        return False

    # Strip surrounding ** if present (from bold markdown)
    cleaned = text.strip()
    if cleaned.startswith('**') and cleaned.endswith('**'):
        cleaned = cleaned[2:-2].strip()

    if not cleaned:
        return False

    # Common auxiliary and modal verbs
    auxiliaries = {
        'is', 'are', 'was', 'were', 'been', 'be',
        'has', 'have', 'had',
        'does', 'do', 'did',
        'can', 'could', 'will', 'would', 'should', 'must', 'may', 'might', 'shall',
    }

    # Common content verbs (infinitive forms)
    verbs = {
        'go', 'get', 'make', 'take', 'know', 'give', 'come', 'use', 'find', 'tell',
        'work', 'call', 'try', 'ask', 'need', 'feel', 'become', 'leave', 'put', 'mean',
        'seem', 'help', 'talk', 'turn', 'start', 'show', 'hear', 'play', 'run', 'move',
        'like', 'live', 'believe', 'hold', 'bring', 'begin', 'let', 'provide', 'contain',
        'validate', 'check', 'require', 'allow', 'enable', 'disable', 'perform', 'support',
        'expect', 'represent', 'implement', 'define', 'create', 'generate', 'produce',
        'process', 'handle', 'manage', 'control', 'maintain', 'update', 'remove', 'add',
        'delete', 'modify', 'retrieve', 'store', 'load', 'save', 'open', 'close',
        'read', 'write', 'execute', 'return', 'throw', 'catch', 'pass', 'fail', 'succeed',
        'resolve', 'render', 'emit', 'consume', 'accept', 'reject', 'parse', 'compute',
        'apply', 'enforce', 'collect', 'gather', 'extract', 'combine', 'merge', 'split',
        'build', 'develop', 'ship', 'test', 'verify', 'validate', 'inspect', 'audit',
        'cover', 'fix', 'resolve', 'discover', 'investigate', 'determine', 'calculate',
        'measure', 'record', 'track', 'flag', 'warn', 'report', 'document', 'explain',
        'describe', 'analyze', 'examine', 'review', 'check', 'assess', 'evaluate',
    }

    # Split text into words
    words = cleaned.split()

    for word in words:
        # Remove punctuation for comparison
        word_stripped = word.rstrip('.,;:!?\'")').lower()

        # Check for auxiliary verbs
        if word_stripped in auxiliaries:
            return True

        # Check for common verbs (3rd person singular: adds, makes, validates, etc.)
        if word_stripped[:-1] in verbs and word_stripped.endswith('s'):
            return True

        # Check for past tense (-ed)
        if word_stripped.endswith('ed') and len(word_stripped) > 3:
            return True

        # Check for progressive (-ing)
        if word_stripped.endswith('ing') and len(word_stripped) > 4:
            return True

        # Check infinitive forms
        if word_stripped in verbs:
            return True

    return False


def _is_summary(attr_text: str, child_text: str) -> bool:
    """
    Determine if a child's text is a near-verbatim restatement of the attribute.
    A child is "summary" (excluded from emission) if it merely restates the parent
    almost verbatim — use word overlap heuristic.

    Returns True if >80% of words in child are present in attribute.
    """
    if not attr_text or not child_text:
        return False

    # Normalize both texts
    attr_words = set(w.lower().rstrip('.,;:!?') for w in attr_text.split())
    child_words = [w.lower().rstrip('.,;:!?') for w in child_text.split()]

    if not child_words:
        return False

    # Count how many child words appear in attribute
    overlap = sum(1 for w in child_words if w in attr_words)
    overlap_ratio = overlap / len(child_words)

    return overlap_ratio >= 0.8


def _validate_record(record: Dict[str, Any]) -> List[str]:
    """
    Validate a claim record against the schema.
    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Check required keys
    required_keys = {'claim', 'modality', 'polarity', 'source_span', 'parent_id'}
    missing = required_keys - set(record.keys())
    if missing:
        errors.append(f"Missing required keys: {missing}")

    # Check no extra keys
    extra = set(record.keys()) - required_keys
    if extra:
        errors.append(f"Unexpected extra keys: {extra}")

    # Check types and values
    if 'claim' in record:
        if not isinstance(record['claim'], str):
            errors.append(f"'claim' must be string, got {type(record['claim'])}")

    if 'modality' in record:
        if not isinstance(record['modality'], str):
            errors.append(f"'modality' must be string, got {type(record['modality'])}")
        elif record['modality'] not in ['assertion', 'epistemic_hedge', 'deontic_hedge']:
            errors.append(f"'modality' must be one of ['assertion', 'epistemic_hedge', 'deontic_hedge'], got {record['modality']}")

    if 'polarity' in record:
        if not isinstance(record['polarity'], str):
            errors.append(f"'polarity' must be string, got {type(record['polarity'])}")
        elif record['polarity'] not in ['affirmative', 'negative']:
            errors.append(f"'polarity' must be one of ['affirmative', 'negative'], got {record['polarity']}")

    if 'source_span' in record:
        if not isinstance(record['source_span'], dict):
            errors.append(f"'source_span' must be dict, got {type(record['source_span'])}")
        else:
            ss = record['source_span']
            if 'start' not in ss:
                errors.append("'source_span' missing 'start' key")
            elif not isinstance(ss.get('start'), int):
                errors.append(f"'source_span.start' must be int, got {type(ss.get('start'))}")

            if 'end' not in ss:
                errors.append("'source_span' missing 'end' key")
            elif not isinstance(ss.get('end'), int):
                errors.append(f"'source_span.end' must be int, got {type(ss.get('end'))}")

            if 'text' not in ss:
                errors.append("'source_span' missing 'text' key")
            elif not isinstance(ss.get('text'), str):
                errors.append(f"'source_span.text' must be string, got {type(ss.get('text'))}")

    if 'parent_id' in record:
        if not isinstance(record['parent_id'], str):
            errors.append(f"'parent_id' must be string, got {type(record['parent_id'])}")

    return errors


def _build_parent_id(depth: int, line_index: int) -> str:
    """
    Generate a stable parent_id for a node.
    Uses depth and line index to create a stable identifier.
    """
    return f"node_{depth}_{line_index}"


def render_claim_list(outline_text: str) -> str:
    """
    Render an outline tree as a claim-list JSONL.

    Args:
        outline_text: The outline text (any render mode: block, inline, or responsive)

    Returns:
        JSONL output (one JSON object per line, one line per claim)

    Raises:
        ValueError: If any emitted record fails schema validation
    """
    # Extract and parse the outline
    outline_lines, is_block_mode = extract_outline_from_text(outline_text)
    if not outline_lines:
        return ""

    # Parse each line into (depth, family, text)
    parsed = []
    for i, line in enumerate(outline_lines):
        depth, family, text = parse_line(line, unit=2)
        parsed.append((i, depth, family, text, line))

    # Build parent index: map each line to its parent's index
    parent_index = {}
    for i, (line_idx, depth, family, text, line) in enumerate(parsed):
        if depth == 0:
            parent_index[i] = None
        else:
            # Find nearest ancestor with depth < current depth
            parent = None
            for j in range(i - 1, -1, -1):
                _, p_depth, _, _, _ = parsed[j]
                if p_depth < depth:
                    parent = j
                    break
            parent_index[i] = parent

    # Emit claims
    records = []
    output = StringIO()

    for i, (line_idx, depth, family, text, original_line) in enumerate(parsed):
        # Calculate character offset in original text
        # Note: this is a simplified approximation; exact offsets would need more tracking
        char_offset = outline_text.find(text)
        if char_offset < 0:
            char_offset = 0

        # Determine parent_id
        parent_i = parent_index[i]
        if parent_i is not None:
            parent_depth = parsed[parent_i][1]
            parent_family = parsed[parent_i][2]
            parent_id = _build_parent_id(parent_depth, parent_i)
        else:
            parent_id = "root"

        # Decide whether to emit and what to emit
        should_emit = False
        claim_text = None

        if family == 'dash':
            # Concept nodes NEVER emit
            should_emit = False
        elif family == 'arrow':
            # Explanation nodes ALWAYS emit
            should_emit = True
            claim_text = text
        elif family in ('uroman', 'ualpha', 'lroman', 'lalpha'):
            # Enumerator nodes ALWAYS emit
            should_emit = True
            claim_text = text
        elif family == 'attr':
            # Attribute nodes emit only if:
            # 1. Own text contains a verb/predicate, OR
            # 2. Has a non-summary ↪ child

            # Check for verb in own text
            if _has_verb_predicate(text):
                should_emit = True
                claim_text = text
            else:
                # Check for non-summary arrow child
                # A child is the next line at greater depth whose parent is this line
                child_text = None
                for j in range(i + 1, len(parsed)):
                    child_line_idx, child_depth, child_family, child_text_raw, _ = parsed[j]
                    if child_depth <= depth:
                        # No more children
                        break
                    if child_depth == depth + 1 and child_family == 'arrow':
                        # This is a direct child
                        # Check if it's non-summary
                        if not _is_summary(text, child_text_raw):
                            should_emit = True
                            claim_text = child_text_raw
                            break

        # Build and validate record
        if should_emit and claim_text:
            record = {
                'claim': claim_text,
                'modality': 'assertion',  # Default; could be enhanced with hedge detection
                'polarity': 'affirmative',  # Default; could be enhanced with negation detection
                'source_span': {
                    'start': char_offset,
                    'end': char_offset + len(claim_text),
                    'text': claim_text
                },
                'parent_id': parent_id
            }

            # Validate record against schema
            validation_errors = _validate_record(record)
            if validation_errors:
                raise ValueError(f"Schema validation failed for record: {validation_errors}\nRecord: {record}")

            # Emit JSONL line
            output.write(json.dumps(record) + '\n')
            records.append(record)

    return output.getvalue()


if __name__ == '__main__':
    # CLI entry point
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        # Read from stdin
        text = sys.stdin.read()

    try:
        jsonl = render_claim_list(text)
        print(jsonl, end='')
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
