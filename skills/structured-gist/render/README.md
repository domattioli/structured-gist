# Render Targets for structured-gist

This directory contains render targets that consume an outline tree (as parsed by `lint_outline.py`) and emit structured output in different formats.

## Claim List (JSONL)

**Module**: `claim_list.py`

**Purpose**: Emit one JSON record per claim extracted from an outline tree, carrying the claim text, its epistemic/deontic modality, its polarity (affirmative/negative), the source span it came from, and its parent node identifier.

**Usage**:

```python
from render.claim_list import render_claim_list

outline_text = """
- Topic
    ↪ This is a claim
    I. First enumerator
    II. Second enumerator
    ▸ Attribute with verb
    ↪ Child explanation
"""

jsonl_output = render_claim_list(outline_text)
```

**Output Format**: JSON Lines (JSONL) — one JSON object per line. Each record contains:

```json
{
  "claim": "text of the claim",
  "modality": "assertion|epistemic_hedge|deontic_hedge",
  "polarity": "affirmative|negative",
  "source_span": {
    "start": 123,
    "end": 156,
    "text": "quoted text from source"
  },
  "parent_id": "node_0_1"
}
```

**Structural Rules** (FR-018a):

- **Explanation nodes** (`↪` family, `arrow`): ALWAYS emit a record from their own text.
- **Enumerator nodes** (`I.`, `A.`, `i.`, `a.` families): ALWAYS emit a record from their own text.
- **Attribute nodes** (`▸` family): Emit ONLY if:
  - The attribute's own text contains a verb/predicate (structural test: contains auxiliary verbs like "is/are/has/have", common verbs, words ending in -ed/-ing, etc.), OR
  - The attribute has a non-summary `↪` child. In this case, the child's content is emitted as the claim, not the attribute's own text. A child is "non-summary" if it is not a near-verbatim restatement (>80% word overlap indicates summary).
- **Concept nodes** (`-` family, `dash`): NEVER emit a record, regardless of their text.

**Derived View** (FR-020):

The claim-list target is a **derived view** of the existing outline tree — it reuses the parser from `lint_outline.py` rather than implementing its own independent prose parser. This ensures consistency: any change to outline parsing automatically propagates to claim-list output.

The alternative design, in which the claim list becomes the **primary internal representation** (replacing the outline tree as the canonical form), is documented here as a stated **future endgame**, explicitly not built under the current scope. A claim-list-first architecture would require:
- Restructuring the entire pipeline to generate claim records at parse time
- Rewriting the linter to operate over claim records instead of outline nodes
- Redefining all existing render targets (text, markdown) to project from claims rather than from trees
- Updating the benchmark harness and all test infrastructure

This future design is architecturally sound and may be revisited, but it is deferred to allow the current feature (claim-list as a derived view) to ship independently.

**Schema Validation**: Every emitted record is validated against `claim_list.schema.json` before output. Invalid records raise a `ValueError` rather than emitting bad data.

**Schema** (`claim_list.schema.json`):

Defines required fields, types, and legal enum values for both `modality` and `polarity`. See the schema file for full details.

## Design Notes

- **No external dependencies**: The skill remains dependency-free at runtime. The render target uses only Python 3 stdlib.
- **Incremental addition**: New render targets can be added to this directory without modifying the core linter or pipeline.
- **Stability**: Parent IDs are stable across re-renders of unchanged outlines, enabling reliable linking and referencing of claims.

## Testing

Run claim-list-specific tests:
```bash
python3 -m pytest skills/structured-gist/render/test_claim_list.py -v
```

Fixture sweep (SC-005):
```bash
bash skills/structured-gist/tests/smoke.sh
# Test 44: T055: claim-list sweep validates all records (SC-005)
```
