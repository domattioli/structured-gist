# External-validation corpus

A frozen, 42-case corpus drawn from three independently-annotated public
datasets (QMSum, Qasper, HotpotQA), built to let a *later* session run
this suite's full evaluation pipeline against cases whose questions,
answers, and evidence were **not** authored by this project and were
**not** selected by looking at how structured-gist performs on them.

**Cases were selected and frozen without generating or inspecting
structured-gist outputs.** No `/structured-gist` render, no model call, no
skim/standard/deep output, and no scoring script from
`../scoring/` ran against any candidate at any point during selection.
Every script here (`scripts/select_*.py`, `scripts/build_cases.py`)
reads only public-dataset metadata: source text, dataset split, domain,
the dataset's own question/query, its own answer, and its own
evidence/support annotations. See "Selection blindness" below for exactly
what that guarantees and doesn't.

This directory sits alongside, and does not modify, `../pressure-tests/`,
`../regression/`, `../scoring/`, `../results/`, `../RESULTS.md`,
`../SPR_FINDINGS.md`, or `../README.md`. It also does not touch
`SKILL.md` or the linter. Nothing in `../scoring/` was copied or modified
to build this corpus.

## Why these three datasets

- **QMSum** (`qmsum/`, 24 cases, **primary external validation set**) —
  externally annotated, query-focused meeting summarization with explicit
  `relevant_text_span` evidence. This is the closest public analogue to
  structured-gist's actual use case: someone asks a specific question
  about a long, messy transcript and needs the answer without re-reading
  everything, and the dataset's own annotators (not this project) marked
  exactly which turns of the transcript the answer depends on.
- **Qasper** (`qasper/`, 10 cases, **external evidence/relation pressure
  set**) — independently annotated evidence retrieval over long technical
  papers, with human answers and paragraph-level supporting evidence.
  Harder than QMSum in one specific way: evidence is spread across a
  structured document with headings and citations rather than a flat
  conversational transcript, and a meaningful fraction of its eligible
  pool requires *multiple* separated evidence locations per answer.
- **HotpotQA** (`hotpotqa/`, 8 cases, **multi-hop pressure set only** —
  `pressure_only: true` in every selection/manifest record) — deliberately
  artificial (short Wikipedia paragraphs, crowdsourced questions), but the
  strongest available public source of *sentence-level* supporting-fact
  annotations that require composing two separate paragraphs to answer.
  It exists to answer one narrow question: can structured compression
  preserve two pieces of evidence that must be connected to answer a
  question, not "is this representative of realistic recap/explain
  input." It is not pooled into a headline "external validation average"
  with QMSum or Qasper — see "Intended roles" below.

## Why these counts

- **24 QMSum** — enough breadth (3 domains x 8, roughly half single- and
  half multi-span) to test replication of this suite's existing findings
  against fully external annotations, without turning this repo into a
  benchmark warehouse the way, e.g., raw QMSum/Qasper/HotpotQA train
  splits would.
- **10 Qasper** — a targeted hard-evidence set, not a second broad
  validation corpus; composition is fixed at 7 multi-evidence + 3
  single-evidence controls (see `qasper/selection.json`).
- **8 HotpotQA** — a small sentinel pressure set. It answers one question
  (multi-hop evidence composition survives compression, yes/no) and does
  not need to be large to do that.

## Selection blindness

What "selected blind to structured-gist behavior" means concretely here:

- Every eligibility rule (non-empty answer, resolvable evidence span,
  evidence cardinality, bridge vs. comparison type, distractor-context
  size, etc.) is evaluated purely against the upstream dataset's own
  fields — see each `scripts/select_*.py` module docstring for the exact
  rule set per dataset.
- Every tie among eligible candidates is broken by
  `sha256(dataset_name + upstream_case_id)`
  (`scripts/corpus_lib.py::selection_sort_key`), never by hand-picking
  "the interesting one." Re-running `select_qmsum.py` / `select_qasper.py`
  / `select_hotpotqa.py` against the same pinned upstream data reproduces
  the exact same 42 case IDs byte-for-byte (verified in
  `scripts/test_corpus.py`, and re-verifiable by hand — see below).
- Zero manual exclusions were used. `scripts/select_*.py`'s rejection
  counters (see "Eligibility pool and rejections" below) are the only
  candidates that were dropped, and every rejection reason is objective
  and mechanical (empty field, unresolvable span, wrong annotation type),
  never "this looks hard for structured-gist."
- What this does **not** guarantee: that these particular public datasets
  are themselves free of any property that happens to correlate with how
  well an unrelated system compresses them. Blindness here means *this
  project's own selection process* introduced no such correlation, not
  that the datasets were reviewed for it.

## Intended roles (do not pool these into one score)

| dataset | role | counts toward a combined "external validation" average? |
|---|---|---|
| QMSum | primary external validation | yes |
| Qasper | external evidence/relation pressure | reported separately, not pooled with QMSum |
| HotpotQA | multi-hop pressure only (`pressure_only: true`) | no |

A future eval session should report QMSum, Qasper, and HotpotQA results
as three separate profiles, the same way `../README.md` already keeps
`regression/` and `pressure-tests/` results separate rather than
averaging them into one number.

## Directory layout

```
external-validation/
  README.md                 -- this file
  HANDOFF.md                -- mechanical integration surface for the next eval session
  MANIFEST.json             -- one row per frozen case, sorted deterministically (generated)
  .gitignore                -- ignores .raw-cache/ (fetched upstream data, never committed)
  qmsum/
    selection.json          -- eligibility pool stats + strata + exact selection trace (generated)
    cases/<case-id>/{source.md, external_gold.json, provenance.json}
  qasper/                   -- same shape
  hotpotqa/                 -- same shape
  scripts/
    corpus_lib.py            -- shared hashing/ordering/serialization helpers
    fetch_sources.py         -- network: caches canonical upstream data + raw_manifest.json per dataset
    select_qmsum.py          -- offline (given cache): eligibility + stratified deterministic selection
    select_qasper.py         -- offline (given cache): eligibility + stratified deterministic selection
    select_hotpotqa.py       -- offline (given cache): eligibility + deterministic selection
    build_cases.py           -- offline (given cache + selection.json): writes case files + MANIFEST.json
    verify_corpus.py         -- fully offline: validates the committed corpus, no cache needed
    test_corpus.py           -- pytest suite (offline unit tests + integration tests against the committed corpus)
```

`case_id` numbering (`qmsum-01`..`qmsum-24`, `qasper-01`..`qasper-10`,
`hotpotqa-01`..`hotpotqa-08`) is positional over each `select_*.py`'s own
deterministic output order — not a ranking of anything.

## Reproducing the corpus

```
# 1. network step -- populates external-validation/.raw-cache/ (gitignored)
python3 scripts/fetch_sources.py --dataset all --cache-dir .raw-cache

# 2. offline -- recomputes eligibility pools + selection.json (should be byte-identical to committed)
python3 scripts/select_qmsum.py   --cache-dir .raw-cache --out qmsum/selection.json
python3 scripts/select_qasper.py  --cache-dir .raw-cache --out qasper/selection.json
python3 scripts/select_hotpotqa.py --cache-dir .raw-cache --out hotpotqa/selection.json

# 3. offline (given cache + selection.json) -- rebuilds case files + MANIFEST.json
python3 scripts/build_cases.py --dataset all --cache-dir .raw-cache --base-dir .

# 4. fully offline -- validates the committed corpus, no cache required
python3 scripts/verify_corpus.py --base-dir .
```

Steps 2-4 were run against the exact pinned upstream revisions recorded
in `provenance.json`/`raw_manifest.json`; re-running them (with a fresh
`fetch_sources.py` pull of the same pinned commit/version) is how a
skeptical reviewer confirms "selection rerun chooses different cases"
does *not* happen. `scripts/test_corpus.py` automates this check when
`.raw-cache/` is present locally (it's skipped, not failed, when absent —
see `HAS_CACHE` in that file) and always runs the fully-offline checks.

## Licensing and provenance

| dataset | license | source | pinned revision |
|---|---|---|---|
| QMSum | MIT | `github.com/Yale-LILY/QMSum` | commit `83d7768c1f2b4dfeb091385d3dc7e239b8e5bb7e` |
| Qasper | CC BY 4.0 | official AllenAI S3 tarball (`qasper-train-dev-v0.3.tgz`) | version `v0.3` |
| HotpotQA | CC BY-SA 4.0 | `hotpotqa.github.io` (canonical); `huggingface.co/datasets/hotpotqa/hotpot_qa` (mirror actually used) | HF repo sha `1908d6afbbead072334abe2965f91bd2709910ab` |

All three were verified against the canonical source at build time, not
assumed:

- QMSum's `LICENSE` file was fetched directly from the pinned commit and
  confirmed to read "MIT License" (`scripts/fetch_sources.py::fetch_qmsum`).
- Qasper's CC BY 4.0 license was confirmed against the dataset's own
  Hugging Face card (`cardData.license: cc-by-4.0`) and homepage
  (`allenai.org/data/qasper`); the code baseline repo
  (`allenai/qasper-led-baseline`) is separately Apache-2.0, which is the
  *code's* license, not the *dataset's* — the two were not conflated.
- HotpotQA's CC BY-SA 4.0 was confirmed against `hotpotqa.github.io`'s own
  license statement.

**One documented deviation:** HotpotQA's canonical host,
`curtis.ml.cmu.edu`, did not respond from this build environment (TCP
connect timeout, not an HTTP-level error or a license/access issue) at
retrieval time. `fetch_sources.py` fell back to the `hotpotqa` GitHub
organization's own official Hugging Face mirror
(`huggingface.co/datasets/hotpotqa/hotpot_qa`), published by the same
team, pinned to that repo's commit sha, with identical schema and
content — only the transport differs. This is recorded in
`hotpotqa/cases/*/provenance.json`'s `deviations` field and in
`.raw-cache/hotpotqa/raw_manifest.json`'s `deviation_note` (the latter is
not committed since it lives under the gitignored cache, but is
regenerated identically by `fetch_sources.py`). Every `provenance.json` in
this corpus carries a `source_sha256`, `transformed_case_sha256`,
`upstream_revision`, `license`, `retrieval_date`, and `deviations` list —
see "Common external case schema" below for the exact case-file shape.

## Eligibility pools and rejections

### QMSum

Eligibility pool: **244** specific-query candidates (across the official
`test` split of all three domains), from an initial 281 specific queries
plus 37 general (whole-meeting) queries seen — general queries are never
eligible by design (see task brief: "do not use general whole-meeting
queries as the main validation cases"). **Zero** candidates were rejected
as malformed; every specific query in these test splits already had a
non-empty answer and cleanly in-bounds `relevant_text_span`.

| domain | eligible | eligible single | eligible multi |
|---|---|---|---|
| Academic | 49 | 49 | 0 |
| Committee | 66 | 59 | 7 |
| Product | 129 | 98 | 31 |

Academic's official test split has **zero** multi-span specific queries
(multi-span queries do exist in Academic's train/val splits, confirmed
during grounding, but this corpus uses `test` uniformly across domains
for the "held-out" framing rather than switching splits per domain to
manufacture a cleaner ratio). Given that constraint, the domain quota
(8/8/8, fixed) and the corpus-wide single/multi target (12/12) are
reconciled by `select_qmsum.py`'s scarcity-first allocator: domains are
processed in ascending order of available multi-span candidates
(Academic 0, Committee 7, Product 31), each claims
`min(remaining_multi_target, available, domain_quota)` multi-span slots,
and the rest of its 8-slot quota is filled with single-span candidates.
This is not a hand-picked split — see `scripts/select_qmsum.py`'s
docstring for the exact rule — and it happens to land exactly on 12/12:

| domain | multi taken | single taken |
|---|---|---|
| Academic | 0 | 8 |
| Committee | 7 | 1 |
| Product | 5 | 3 |
| **total** | **12** | **12** |

Source word-count distribution (full meeting, not just gold spans) over
the 24 retained cases: min 4,624 / p25 7,279 / median 13,945 / p75 14,631
/ max 19,894.

### Qasper

Eligibility pool: **788** of 1,005 questions in the public `dev-v0.3`
split (281 papers). Rejections:

| reason | count |
|---|---|
| `unanswerable` (dataset marks no answer exists) | 95 |
| `empty_evidence` (no evidence list at all) | 27 |
| `float_only_evidence` (evidence is exclusively a figure/table caption, not reconstructable from text) | 60 |
| `evidence_location_unresolved` (a textual evidence string didn't exact-match any paragraph in `full_text`) | 35 |

Eligible cardinality: 581 single-evidence, 207 multi-evidence. Eligible
multi-evidence candidates by (mechanically computed) paragraph-distance
bucket: nearby (<=2 paragraphs apart) 78, moderate (3-10) 90, wide (>10)
39. Composition is fixed at 7 multi + 3 single; the 7 multi-evidence slots
are spread across the three distance buckets by the same scarcity-first
allocator, capped at `ceil(7/3)=3` per bucket so the scarcest bucket
(wide, 39 available) can't simply absorb the entire quota:

| distance bucket | available | taken |
|---|---|---|
| nearby | 78 | 3 |
| moderate | 90 | 1 |
| wide | 39 | 3 |

Source word-count distribution (full paper text) over the 10 retained
cases: min 1,948 / p25 2,756 / median 3,482 / p75 3,759 / max 4,402.

### HotpotQA (`pressure_only: true`)

Eligibility pool: **5,899** of 7,405 rows in the official `distractor`
dev split (which is entirely `level: hard` by dataset construction — no
filtering needed there). Rejections:

| reason | count |
|---|---|
| `not_bridge_type` (comparison-type question, excluded — see below) | 1,487 |
| `insufficient_distractor_context` (fewer than 8 of the expected 10 context paragraphs present) | 18 |
| `supporting_fact_unresolved` (a supporting-fact sentence index didn't resolve) | 1 |

Comparison-type questions ("were X and Y the same nationality?") are
excluded outright rather than down-weighted, because bridge questions —
which require using one fact to identify the entity the next fact is
about — are the genuinely compositional type this pressure set exists to
test, and bridge questions are abundant (5,918 of 7,405 rows) so nothing
was lost by not falling back to comparison. All 8 selected cases have
exactly 2 supporting facts across exactly 2 distinct paragraphs (the
modal shape in this split). Source word-count distribution (all 10
distractor paragraphs) over the 8 retained cases: min 522 / median 843 /
max 1,504.

## Selection algorithm (all three datasets)

1. Build the eligibility pool directly from the pinned upstream data —
   never from anything this project generated.
2. Compute `sha256(dataset_name + upstream_case_id)` for every eligible
   candidate (`corpus_lib.selection_sort_key`).
3. Where a stratum/quota exists (QMSum's domain x cardinality, Qasper's
   cardinality x distance-bucket), allocate slots to strata via
   `corpus_lib.scarcity_first_allocate` — the stratum with fewest
   available candidates is filled first (up to any documented cap), so no
   stratum is starved by a more abundant one.
4. Within each stratum (or the whole pool, for HotpotQA), take the first
   N candidates in ascending sort-key order.
5. Every one of these steps is implemented in `scripts/select_*.py` and
   reproduced byte-for-byte by `scripts/test_corpus.py` when the raw
   cache is present.

## Common external case schema

Every case has three files. `external_gold.json` deliberately does
**not** use this suite's own `gold.json` semantic-unit schema (facts,
relations, weights) — that schema is this project's own ontology, and
forcing these three independently-annotated datasets into it before ever
testing against them would defeat the point of an *external* validation
corpus. A later eval-adaptation session may derive a fact/relation view
if it needs one (see `HANDOFF.md`); this session only preserves what the
datasets natively provide, losslessly.

```jsonc
{
  "case_id": "qmsum-01",
  "dataset": "qmsum",              // or "qasper" / "hotpotqa"
  "intent": { "reader": "...", "task": "..." },   // fixed per-dataset framing template, not per-case hand authoring
  "question_or_query": "...",
  "reference_answer": "...",
  "native_evidence": [ /* dataset-native evidence, losslessly preserved -- shape differs per dataset */ ],
  "native_metadata": { /* dataset-native fields: domain, cardinality, evidence distance, answer type, etc. */ },
  "provenance_ref": "provenance.json"
}
```

`provenance.json` carries, per case: `dataset`, `upstream_case_id`,
`upstream_document_id`, `upstream_question_id`, `upstream_split`,
`upstream_source_repository`, `upstream_revision`, `license`,
`license_source`, `retrieval_date`, `source_sha256`,
`transformed_case_sha256`, `transformation_script_version`, and
`deviations` (a list, empty only if nothing deviated from the plain
upstream record — every QMSum case documents the native-ID join, every
Qasper case documents the float-evidence caveat, every HotpotQA case
documents the host-fallback deviation).

## Corpus integrity checks

`scripts/verify_corpus.py` is fully offline (no network, no cache
required) and fails loudly if:

- a dataset's case count differs from 24 / 10 / 8
- any `upstream_case_id` is duplicated within a dataset
- a case is missing `source.md`, `external_gold.json`, or
  `provenance.json`, or `source.md`/`reference_answer` is empty
- `provenance.json` is missing a required field, or has no `license`
- a recomputed `transformed_case_sha256` (hash of the committed
  `source.md` + `external_gold.json` bytes) doesn't match the recorded
  one
- a freshly recomputed `MANIFEST.json` differs from the committed one
- a QMSum case has no relevant span, or its single/multi label disagrees
  with its evidence count
- a Qasper case has no resolved evidence location
- a HotpotQA case has fewer than 2 supporting facts, spans fewer than 2
  distinct paragraphs, or is missing `pressure_only: true`

`scripts/test_corpus.py` (pytest) wraps `verify_corpus.py` as one
integration test, adds direct assertions on the stratum counts and
distributions documented above, and unit-tests every eligibility/ordering
primitive (span resolution, answer typing, distance bucketing,
scarcity-first allocation, deterministic JSON serialization) with
synthetic inputs — no network dependency anywhere in this file.

## Verification performed this session

- `SKILL.md`: no diff (confirmed via `git status`; this session never
  opened it).
- Existing benchmark cases/renderings/judgments/scores
  (`../pressure-tests/`, `../regression/`, `../results/`,
  `../scoring/blind_weights/`): no diff.
- `../scoring/*.py`: no diff; nothing from PR #18 (which was still open
  at the time this branch was cut from `origin/main`, and is
  independently reviewable from it) was copied in.
- Full existing repo test suite
  (`pytest skills/structured-gist/benchmarks/semantic-compression/
  skills/structured-gist/tests/`): 89 passed before this work, 120 passed
  after (89 existing + 31 new, all in `scripts/test_corpus.py`) — no
  existing test was changed or removed.
- Corpus rebuild determinism: re-running `select_*.py` against the pinned
  upstream cache reproduced `selection.json` byte-for-byte for all three
  datasets; re-running `build_cases.py` reproduced every case file
  byte-for-byte; `verify_corpus.py` passes; a deliberate corruption of one
  case file was caught by `verify_corpus.py` and cleanly reverted.
