# KG mode (experimental) — full specification

Pointer target from `SKILL.md` `## KG mode (experimental)`. Spec of record:
`specs/023-nested-notes-kg-benchmark/` (contracts/kg-schema.md is the frozen
schema contract; this file is the skill-local reference).

Fence policy in this file: ` ```text ` fences contain ONLY lint-clean outlines
(the test suite lints every one); JSON and shell examples use their own tags.

## What it is

An alternative, explicitly-invoked generation path for structured-gist outlines:

1. **Extract** — the model captures source content as a typed knowledge graph
   (a JSON file, schema `nested-notes-kg/v1`) instead of writing the outline
   directly.
2. **Validate** — `scripts/kg.py` rejects malformed graphs with named
   `KG-REJECT ERR_*` errors (never a broken outline).
3. **Render** — `scripts/kg_render.py` deterministically traverses the graph
   into a block-mode outline that passes the conformance linter with zero
   violations, byte-identically on every run.

The direct-prompt mode remains the default; KG mode is additive and opt-in.
Its promise: structural rules are enforced *before* rendering (prevention,
not post-hoc linting), and granularity levels are mechanical prunes of one
graph rather than fresh judgment calls.

## Node and edge types

Node types map 1:1 to the role ladder: `concept` (root only, ≤3 words),
`attribute` (`▸`, ≤4 words), `ordered-part` / `unordered-part` (enumerators,
≤6 words, `rank` required on ordered), `explanation` (`↪`, uncapped prose).

Edge types: `has-attribute` (never from an attribute — R8), `composed-of`
(parts; a part may have sub-parts only where they render at depth 2),
`explains` (≤1 non-leaf explanation per parent, rendered first — R4). Roots
are parentless concepts; there is no grouping edge.

Word budgets are uniform per role — deliberately tighter than linter R7 at
some depths, so a valid graph can never render into a budget violation.

## Canonical example

The contract's 14-node example graph renders byte-for-byte to the
`## Worked example` block in SKILL.md — the two are kept equal by test.

```json
{"schema": "nested-notes-kg/v1", "source_id": "...",
 "nodes": [{"id": "c1", "type": "concept", "text": "Agentic harness"}, "..."],
 "edges": [{"type": "has-attribute", "from": "c1", "to": "a1"}, "..."]}
```

Full graph: `specs/023-nested-notes-kg-benchmark/contracts/kg-schema.md` and
`tests/fixtures/kg/canonical.json`.

## Validation errors

Two layers, one fixed first-error-wins order (contract `## Validation order`):

- **Structural (kg.py, stages 1–6)**: schema/id/reference defects, node-field
  defects (type, empty text, word budget, stray leading marker, delimiter
  tail, rank), edge-type defects (attribute-under-attribute, edges targeting
  concepts, endpoint mismatches), tree defects (multiple parents, cycles, no
  root, orphans), role-composition defects (mixed ordered/unordered parts,
  attribute+part children on one node, multiple summary explanations,
  duplicate ranks).
- **Render-level (kg_render.py, stage 7)**: arrow-rarity across all three
  granularity levels, part-nesting depth, and render overflow (a line that
  cannot fit the 64-char budget, including wrap points that would start a
  continuation line with a marker-lookalike token).

Rejection format: `KG-REJECT <ERR_NAME> node=<id|-> edge=<idx|-> : <detail>`
on stderr, exit 2. `INTERNAL_LINT_FAILURE` is a bug sentinel — every
user-reachable cause has a named error, so it should never fire on valid
input.

## Rendering guarantees

- Same graph in → byte-identical outline out, at every granularity level.
- Every rendered outline passes `tests/lint_outline.py` with zero violations
  (the renderer self-lints and refuses to emit otherwise).
- `skim` ⊆ `standard` ⊆ `deep` — prunes of one graph, word-count monotone.
  A pruned node's entire subtree goes with it; nothing is reparented.
- Block mode only in v0.4.0 (fenced ` ```text `). The glyph-free responsive
  presentation cannot be deterministically linted, so a responsive flag is
  deferred rather than shipped unverifiable.

## CLI

```bash
python3 skills/structured-gist/scripts/kg_render.py <graph.json> --validate-only
python3 skills/structured-gist/scripts/kg_render.py <graph.json> --level skim|standard|deep [--out <file>]
```

## Benchmark evidence

The mode ships benchmark-gated: `benchmarks/compare_corpus.py` scores both
modes over a 20-source corpus on retention / brevity / robustness
(formulas + limitations: `benchmarks/scoring.md`; committed evidence:
`benchmarks/reports/comparison-v0.4.0.md`). The headline verdict uses the
conformance-excluded composite, because KG conformance is 1.0 by
construction. Promotion to default is a separate operator decision.
