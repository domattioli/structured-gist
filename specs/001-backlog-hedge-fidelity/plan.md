# Implementation Plan: Backlog Sweep — Hedge Fidelity, Benchmark Harness, Backlog Adjudication

**Branch**: `001-backlog-hedge-fidelity` | **Date**: 2026-09-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backlog-hedge-fidelity/spec.md` (fable-reviewed)

## Summary

Eleven adjudicated backlog steps carried out against `domattioli/structured-gist`. The work divides into four kinds: one linter rule (step 1), four GitHub bookkeeping actions (steps 2, 3, 10, 11), a benchmark-infrastructure rebuild plus the measurements it enables (steps 4, 7, 8, 9), and two artifacts that consume that infrastructure (steps 5, 6). The technical spine is the benchmark harness: it is the only new subsystem, and steps 5, 7, 8, and 9 are all consumers of its output. Everything else is either a small predicate over the existing linter or a derived view over the existing outline tree.

The plan adds no runtime dependency to the skill. All new code lands under the existing `skills/structured-gist/` tree, in `tests/` (linter), `benchmarks/semantic-compression/` (harness, scoring, metrics), and a new `render/` module for the claim-list target.

## Technical Context

**Language/Version**: Python 3 (stdlib only for anything the skill needs at use time); bash for entry points
**Primary Dependencies**: none at runtime. Test/dev only: pytest (already in use). No new binary dependency — this is what disqualifies step 11's pptx target.
**Storage**: files on disk. Benchmark cases are per-case directories holding `gold.json`, `source.md`, `renderings/{skim,standard,deep}.md`, `judged/<tier>.json`. Judged cache is a content-addressed directory of JSON blobs.
**Testing**: `python3 -m pytest skills/structured-gist/tests/test_lint.py` plus `bash skills/structured-gist/tests/smoke.sh`. New: two separate entry scripts — `bash .../benchmarks/semantic-compression/run_deterministic.sh` (CI-safe, no model calls) and `bash .../benchmarks/semantic-compression/run_judged.sh` (manual-only; no CI workflow file references it) — rather than one script with a lane flag.
**Target Platform**: developer workstation and GitHub Actions (Linux)
**Project Type**: single project — a documentation/linting skill with an evaluation harness
**Performance Goals**: deterministic lane completes fast enough to run on every change; judged lane issues zero model calls when inputs are unchanged.
**Constraints**: zero runtime dependencies; no model cost in CI; no personal data anywhere in the repo or in any issue comment.
**Scale/Scope**: 8 benchmark cases today (3 regression, 5 pressure-test); +3 cases from step 3; ~15 existing lint rules; ~40 fixtures.

## Constitution Check

*GATE: passed before Phase 0; re-checked after Phase 1.*

| Principle | Status | Note |
|---|---|---|
| P1 zero runtime deps | PASS | Harness and claim-list target are stdlib. Step 11 is closed precisely because it would violate this. |
| P2 falsifiable claims | PASS | Every step carries a numeric gate or an explicit recorded decision: FN/FP=0 (step 1), ≥0.98 precision (step 8), ρ vs 0.8 (step 9), ±5% budget (step 7). Steps 10 and 11 are closures with stated reasoning rather than built work. |
| P3 no self-graded evidence | PASS | Judged verdicts stay in `judged/*.json` produced by a separately-recorded judge; `combine.py` performs arithmetic only. The new hedge-survival metric is deterministic, avoiding the judge entirely. |
| P4 deterministic checks free | PASS | FR-014 splits the lanes; CI runs only the deterministic lane. |
| P5 structure is the invariant | PASS | Step 1 extends the ladder; step 6 is an explicitly derived view, and the primary-IR alternative is deferred rather than adopted. |
| P6 no personal data | PASS | FR-010 gates steps 2, 3, and 5. The second step-3 test case is conditional on clearing review. |

No violations. Complexity Tracking table below is therefore empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-backlog-hedge-fidelity/
├── spec.md              # fable-reviewed specification
├── plan.md              # this file
├── tasks.md             # produced by the tasks phase
└── checklists/          # produced by the checklist phase
```

### Source Code (repository root)

```text
skills/structured-gist/
├── tests/
│   ├── lint_outline.py                  # step 1: new depth-indent rule; step 8: comma-split rule + severity tier
│   ├── test_lint.py                     # step 1 + step 8 test methods
│   ├── smoke.sh                         # step 1 + step 8 rule-id assertions
│   └── fixtures/
│       ├── good_r16_depth_indent.md     # step 1 (R16 allocated in D1)
│       ├── bad_r16_depth_indent.md      # step 1
│       ├── good_r17_comma_split.md      # step 8
│       └── bad_r17_comma_split.md       # step 8
├── render/
│   ├── __init__.py                      # step 6
│   ├── claim_list.py                    # step 6: outline tree -> claim records (JSON Lines)
│   ├── claim_list.schema.json           # step 6: published schema (JSON Schema for one record)
│   └── README.md                        # step 6: derived-view note + deferred primary-IR design
└── benchmarks/semantic-compression/
    ├── run_deterministic.sh             # step 4: shell entry point, deterministic lane only, CI-safe
    ├── run_judged.sh                    # step 4: shell entry point, judged lane only, manual-invocation only; no CI workflow references it
    ├── run.py                           # step 4: python entry point over the same suite definition, selects the lane the caller invoked it for
    ├── suite.json                        # step 4: case roster + lane membership
    ├── provenance.json                   # step 4: model identifier + prompt hash per run
    ├── .cache/judged/<sha256>.json       # step 4: content-addressed judged cache
    ├── scoring/
    │   ├── deterministic.py              # existing
    │   ├── combine.py                    # step 9: conditional SCU-recall column
    │   └── hedge_survival.py             # step 3/7: deterministic source-aware hedge diff
    ├── regression/ , pressure-tests/     # existing 8 cases; +3 cases from step 3
    └── results/                          # combined.json, deterministic.json, SCORES.md
README.md                                 # step 5: generated before/after example
```

**Test placement note**: tests for the claim-list target live in `skills/structured-gist/tests/test_claim_list.py`, alongside the existing `test_lint.py`, rather than under `render/`. This is deliberate — the repository's convention is a single `tests/` directory, and splitting it would leave the pytest invocation covering only part of the suite.

**Structure Decision**: Everything stays inside the existing `skills/structured-gist/` tree. The only new directory is `render/`, added because the claim-list target is a render target and does not belong under `tests/`. The harness keeps its existing `benchmarks/semantic-compression/` home and its existing per-case layout; step 4 adds entry points, provenance, lane definition, and a cache around what already exists rather than replacing the scoring modules.

## Phase 0 — Research and decisions

These are the questions the spec leaves to implementation, each resolved here so no task starts on an unknown.

### D1 — Depth-indent rule predicate (step 1)

`parse_line` already returns `(depth, family, text)` with `depth = leading_spaces // unit`, where `unit` is the GCD of all leading indents in the outline. The rule is therefore expressible entirely on already-computed depth: for any node whose family is an enumerator (`uroman`, `ualpha`, `lroman`, `lalpha`) or an explanation (`arrow`), the nearest preceding node at a lower-or-equal depth that is an attribute (`attr`) must be at strictly lower depth. A sibling-of-attribute at equal depth is the violation. This is a predicate over the existing parse output; it does not touch the indent computation.

**Interaction with R1 and R2**: R1 already constrains which families are legal at which depth, and R2 forbids skipped rungs. Neither catches the flush case, because a child rendered at its parent's depth is a legal family at a legal depth. The new rule is additive and must not suppress R1 or R2 findings on the same line (spec edge case).

**Rule identifier**: both issue #6 and issue #9 propose "R16". Allocation decision: the depth-indent rule takes **R16** (issue #6, built first), the comma-split rule takes **R17** (issue #9, built last). Recorded in FR-003a. Both issues get a comment noting the allocation.

### D2 — Severity tiers (step 8)

The linter has no warn tier today; all of R1–R15 are hard violations. Step 8's "stays warn-only" outcome therefore requires a severity concept to exist. Decision: add a `severity` field to the violation record with values `error` and `warn`, defaulting to `error` so every existing rule is unchanged in behavior; the exit code counts only `error` violations. R17 lands as `warn` and is promoted to `error` only on the measurement. This is the minimum change that makes both step-8 branches expressible and leaves R1–R15 byte-identical in outcome. The observable is that every rule other than R17 keeps `severity='error'` and the linter's exit code is unchanged across the existing fixture corpus.

### D3 — Hedge-survival measurement (steps 3 and 7)

Deterministic and source-aware means: a hedge lexicon (modal verbs, epistemic adverbs, approximators, evidential frames) is matched against the `source_quote` already carried by each gold fact, and against the rendered outline text. Survival is the fraction of source-side hedge occurrences bound to a retained fact that also appear in the rendering. The existing `source_quote` field is what makes this source-aware without a judge, and is why the metric can ship before the harness rebuild (FR-007).

`attaches_to` is what separates survival from correctness: a hedge that survives but migrates to a different claim counts as surviving under `hedge_survival_rate` and as a failure under the judged `caveat_attach_accuracy`. Only the deterministic metric is required by this spec (FR-022); the judged one is defined in the step-3 issue and tracked there.

### D4 — Cache key (step 4)

The judged cache key is a SHA-256 over the tuple that fully determines a judged verdict: case identifier, rendering level, rendering content, gold content, prompt content, and model identifier. Changing any one misses the cache, which is what makes FR-013's "a changed prompt or model is visible" hold. `provenance.json` records the model identifier and prompt hash in cleartext alongside results so a run is reproducible without reading the cache.

### D5 — SCU-recall and the step-9 risk

`combine.py` today reports `weighted_retention`, `unweighted_retention`, `relation_retention`, `recoverability`, `unsupported_claim_count`, and conformance counts. There is no SCU-recall column. SCU-recall as normally defined is close to `unweighted_retention` over the gold fact list, so the step-9 correlation may be high for a near-tautological reason. Decision: compute SCU-recall explicitly from the gold facts and record, alongside ρ, how SCU-recall was defined — so that a high ρ closing issue #1 is closed on a stated definition rather than an accidental one. With 8 cases the coefficient is low-powered; the recorded output must state n=8. Because step 3 adds a ninth case to the suite before this step runs, the correlation must be computed over a frozen snapshot of the pre-step-3 `combined.json`, not over whatever the suite holds at the time (spec FR-026). SCU-recall's definition is now pinned in the spec at FR-026a rather than left here.

### D6 — Token-budget matching (step 7)

Matching within ±5% is achieved by tuning the granularity/instruction of each condition until measured output token counts converge, then recording both counts. FR-021 pins the quantity (output tokens), the comparison basis (per case), and the requirement that one recorded tokenizer be applied identically to both conditions. If they cannot be brought within tolerance, FR-021 says the comparison is not reported as a result. The prediction (FR-023) is written into the experiment record before any run is executed; ordering here is a review point, not a convention.

### D7 — Redaction (steps 2, 3, 5)

The corpus session is a large local transcript outside the repo. Nothing is copied from it into the repo, an issue, or a comment until a redaction review has run over the specific excerpt. Extraction and review happen in an out-of-tree staging buffer (spec FR-010a) — an excerpt is never written to a tracked path in order to be reviewed — and the review yields APPROVED / APPROVED-WITH-EDITS / DROPPED per FR-010b. Step 5 additionally requires reading the full source message rather than the truncated window, which increases exposure and therefore makes the review mandatory rather than advisory. The phone/Kiran case is included only if it clears review; if it does not, step 3 ships two test cases and records why the third was dropped.

## Phase 1 — Design

### Data shapes

- **Violation record** gains `severity` (`error` | `warn`), default `error`.
- **Gold fact entry** gains category `epistemic` with weight 3, and an optional `attaches_to` naming the fact id the qualifier modifies. Applied per-case, since gold files are per-case.
- **Claim record**: `{claim, modality, polarity, source_span, parent_id}`, one per claim, validated against `claim_list.schema.json`.
- **Run record**: results plus `{model_id, prompt_sha256, suite_sha256, timestamp}`.

### Contracts

- `run_deterministic.sh` exits nonzero on a deterministic regression and issues no model calls; it is the only entry point any CI workflow may reference. `run_judged.sh` requires explicit invocation and is never referenced by any CI workflow file — the manual-only property is structural (two scripts), not a flag or env-var on one script.
- `run.py` exposes the same suite over the same `suite.json` to both scripts, so CI and a developer see identical case rosters.
- `claim_list.py` takes an outline tree and returns records; it never re-parses prose independently of the outline, which is what keeps it a derived view (FR-020).

### Ordering and dependencies

```
1 (lint rule)      independent
2 (#9 comment)     independent
3 (new issue)      needs 2's counterexample redacted
4 (harness)        independent of 1-3, but 3 defines the metric it will host
D3 metric impl     needs 3's definition; ships before 7
5 (README example) needs 4
6 (claim list)     independent
7 (comparison)     needs 4 and the metric
8 (promotion)      needs 3, 4, 7
9 (correlation)    needs existing results only
10 (#8 closure)    needs 3 filed
11 (#3 closure)    independent
```

Steps 1, 2, 6, 9, and 11 can proceed in parallel with the harness build. Steps 5, 7, and 8 are strictly serialized behind it.

### Verification strategy

Each step's acceptance is the spec's own success criterion, checked by a mechanism that already exists where possible: pytest and smoke.sh for steps 1 and 8; a second identical suite run for step 4 (SC-002); schema validation over the fixture corpus for step 6; a regeneration diff for step 5; and recorded numbers for steps 7, 8, and 9. Bookkeeping steps (2, 3, 10, 11) are verified by reading the resulting issue state.

## Complexity Tracking

No constitution violations; table intentionally empty.
