# Handoff to the eval-running session

This corpus was selected and frozen **blind** to structured-gist behavior
(see `README.md`). Nothing below was implemented or run in this session —
this document only describes the mechanical integration surface so the
next session can decide the architecture itself, rather than inheriting
one this corpus-building session invented quietly.

## What the next session should consider running

The full related suite, against these 42 frozen cases, the same way it
already runs against `../pressure-tests/` and `../regression/`:

- `skim` / `standard` / `deep` structured-gist renderings
- semantic fact retention
- relation retention
- critical-loss diagnostics
- recoverability / task answerability
- source-support checks (hallucination / unsupported-claim detection)
- SPR (Semantic Preservation Recall), where applicable
- compression (reported as cost, per `../README.md`'s existing convention
  — never rewarded, never turned into a density composite)
- structural conformance (`../../tests/lint_outline.py`)
- wording fidelity (`../scoring/wording_fidelity.py`, if merged from PR
  #18 by the time this runs)
- corrected retained-unit findability (`../scoring/findability.py`, if
  merged from PR #18 by the time this runs)

**Report QMSum, Qasper, and HotpotQA as three separate profiles.** Do not
pool them into one combined "external validation" number — see
`README.md`'s "Intended roles" table. HotpotQA in particular carries
`pressure_only: true` in every `provenance.json`/`selection.json`/
`MANIFEST.json` record specifically so a careless script doesn't fold it
into a headline average by accident.

## Which metrics cannot yet consume dataset-native annotations directly

This corpus deliberately kept `external_gold.json` in each dataset's own
native shape (see `README.md`'s "Common external case schema") rather
than translating it into this suite's `gold.json` fact/relation/weight
ontology. That means:

- **Scoring code expecting `gold.json`'s shape** (`facts: [...]` with
  `id`/`category`/`weight`/`precision_sensitive`, `relations: [...]` with
  `fact_ids`, `questions: [...]` with `fact_ids`) — e.g.
  `../scoring/combine.py`'s `score_semantic`, `../scoring/spr.py` — will
  **not** run against `external_gold.json` unmodified. An adapter needs
  to be written (and is explicitly out of scope for this session) that
  derives facts/relations from each dataset's native evidence:
  - QMSum: each `native_evidence[i].turns` is a transcript span; there is
    no existing fact/relation decomposition of it. An adapter would need
    to either treat each resolved span as one atomic "fact" (weight
    scheme undefined — this corpus does not invent one), or hand-derive
    finer-grained facts from it (which reintroduces this project's own
    ontology onto external data, the exact thing this session avoided).
  - Qasper: `native_evidence` is already paragraph-granular, closer to a
    "relation-free" fact list, but has no notion of `category` or
    `weight` and no cross-fact `relations`.
  - HotpotQA: `native_evidence` (2 supporting-fact sentences across 2
    paragraphs) maps naturally to two facts plus one implied relation
    (the bridge), but the relation `type` (causal / temporal / etc.) has
    no native annotation to draw from — HotpotQA doesn't label *why* the
    two facts connect, only *that* they must be composed.
- **`recoverability`** (can the gold questions be answered from the
  output) transfers directly — every case already has exactly one
  `question_or_query` + `reference_answer` pair, no adapter needed.
- **`source support` / hallucination checks** transfer directly — they
  only need `source.md` and the rendered output, not `gold.json`'s
  ontology.
- **`wording_fidelity` / `findability`** (PR #18, if merged) — both
  operate on rendered output vs. `source.md` text, not on `gold.json`'s
  fact schema, so they should transfer directly; verify this assumption
  once that scoring code is available on `main`, since this session
  branched from `main` specifically to avoid depending on PR #18's
  implementation details before they land.
- **`structural conformance`** (the linter) operates purely on rendered
  output syntax and needs no gold schema at all.

## Practical notes

- `provenance_ref` in every `external_gold.json` points at the sibling
  `provenance.json` — use it for attribution if any case content is ever
  quoted in a published report.
- Re-fetching upstream data (`scripts/fetch_sources.py`) is optional for
  running the eval suite — the frozen `cases/` directories are
  self-contained. Only re-run it if you need to re-verify selection
  determinism (`scripts/test_corpus.py`'s cache-gated tests) or extend the
  corpus later.
- `scripts/verify_corpus.py` should be run (and should pass) before and
  after any future modification to this corpus, the same way this session
  ran it before finalizing.
