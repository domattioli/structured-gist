---
description: "Task list for feature 001-backlog-hedge-fidelity"
---

# Tasks: Backlog Sweep — Hedge Fidelity, Benchmark Harness, Backlog Adjudication

**Input**: Design documents from `/specs/001-backlog-hedge-fidelity/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories)

**Tests**: Tests ARE requested for this feature — the repo is test-gated (`pytest skills/structured-gist/tests/test_lint.py` + `bash skills/structured-gist/tests/smoke.sh`). Test tasks appear before the implementation they cover.

**Organization**: Tasks are grouped by user story. US1–US11 map 1:1 onto the eleven ordered build steps in `spec.md`.

## Format: `[ID] [P?] [Story] Description — **tier: <tier>**`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story the task belongs to
- **tier**: Which model tier executes the task. Allowed EXECUTION tiers: `free-tier`, `luna`, `terra`, `haiku`, `sonnet`. `opus — decision gate` marks judgment rows only and is NOT an execution tier.
- Every path is repo-relative to `/Users/domattioli/Projects/structured-gist/`.

## Path Conventions

Single project. Skill tree: `skills/structured-gist/`. Linter + fixtures: `skills/structured-gist/tests/`. Harness: `skills/structured-gist/benchmarks/semantic-compression/`. New render target: `skills/structured-gist/render/`.

### Execution tier ladder

Tiers name who executes a task, ordered by capability and cost:

- **free-tier** — OpenRouter free delegates (free Gemini, free Mistral). Use for any task whose output is fully determined by a stated predicate, an existing pattern to copy, or arithmetic: lint-rule predicates, fixture authoring, test-method authoring, schema authoring against enumerated fields, grep/scan, mechanical file and table edits, `gh` CLI issue posting, applying a branch decision another task already recorded.
- **luna** / **terra** — mid-tier paid delegates. Use only when a task needs to hold two or three files consistent at once but involves no open design question.
- **haiku** — use when the task requires repo context beyond the row's own description, or genuine (if small) judgment: converging on a tolerance, labelling ambiguous cases, deciding how to phrase something that must be implementable cold.
- **sonnet** — reserved. Every sonnet row requires a one-line justification naming what is genuinely undecided that haiku could not settle. If plan.md or a decision gate already fixes the design, the task is execution, not design, and does not qualify.
- **opus — decision gate** — NOT an execution tier. Marks a row that adjudicates rather than implements. Such rows produce a recorded verdict, never code.

**Escalation predicate**: escalate one step only when the task's output is not determined by what is already written down. If a prior artifact (spec FR, plan decision, or an upstream decision gate) already fixes the answer, the task is mechanical.

---

Tier assignments are carried inline on each task row, which is authoritative; no summary table is maintained, to avoid the three copies drifting.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the directories and the identifier allocation every later phase names.

- [ ] T001 [P] Create `skills/structured-gist/render/` with an empty `__init__.py` per plan.md Project Structure — **tier: free-tier**
- [ ] T002 [P] Create `skills/structured-gist/benchmarks/semantic-compression/.cache/judged/` with a `.gitignore` that ignores blobs but keeps the directory — **tier: free-tier**
- [ ] T003 Record the FR-003a rule-identifier allocation (depth-indent = **R16** / issue #6; comma-split = **R17** / issue #9) as a comment block at the top of the rule table in `skills/structured-gist/tests/lint_outline.py` — **tier: free-tier**

**Checkpoint**: Directories exist; R16/R17 collision is resolved on the record.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The redaction gate. FR-010 forbids writing ANY corpus-derived excerpt to any file, issue, comment, fixture, or benchmark input before review. This phase blocks US2, US3, and US5 outright.

**⚠️ CRITICAL**: No corpus excerpt may be written anywhere until T004 passes for that excerpt.

- [ ] T005 Extract the registrar counterexample and the conditional second case from the local conversation corpus into the session scratchpad (out-of-repo staging buffer) as candidate excerpts, pre-review, marked `STATUS: pending-review` (FR-010a) — **tier: terra**
- [ ] T004 **DECISION GATE (redaction sign-off)** — human/opus-tier review of each candidate corpus excerpt staged in the T005 scratchpad (registrar case; conditional second case; deontic-modality case) against FR-010; read the staging buffer and write a per-excerpt APPROVED / APPROVED-WITH-EDITS / DROPPED verdict to `specs/001-backlog-hedge-fidelity/redaction-log.md` (FR-010b). Not an implementation task. — **tier: opus — decision gate**
- [ ] T006 [P] Apply the T004 verdicts: rewrite APPROVED-WITH-EDITS excerpts in place and mark DROPPED excerpts with the reason, in `specs/001-backlog-hedge-fidelity/redaction-log.md` — **tier: free-tier**
- [ ] T007 [P] Add a `pending-review` grep guard to `skills/structured-gist/tests/smoke.sh` asserting no file in the repository working tree contains a `STATUS: pending-review` marker (the out-of-repo staging buffer is by definition not in scope) — **tier: free-tier**

**Checkpoint**: Every excerpt destined for a file, issue, or fixture carries a recorded verdict. US2/US3/US5 unblocked for approved excerpts only.

---

## Phase 3: User Story 1 — Depth-indent lint rule closes the flush-child gap (Priority: P1) 🎯 MVP

**Goal**: The linter rejects enumerator/explanation children rendered flush with their parent attribute marker (R16).

**Independent Test**: Run the linter over the existing fixture corpus plus new good/bad R16 fixtures — the rule fires on every bad fixture and on no good fixture (SC-001).

### Tests for User Story 1

> Write these first; confirm they FAIL before T013.

- [ ] T008 [P] [US1] Add fixture `skills/structured-gist/tests/fixtures/bad_r16_depth_indent.md` — an enumerator child at the same depth as its parent `▸` attribute — **tier: free-tier**
- [ ] T009 [P] [US1] Add fixture `skills/structured-gist/tests/fixtures/bad_r16_depth_indent_arrow.md` — an `↪` explanation child flush with its parent attribute (FR-001, scenario 2) — **tier: free-tier**
- [ ] T010 [P] [US1] Add fixture `skills/structured-gist/tests/fixtures/good_r16_depth_indent.md` — the same content correctly nested one rung deeper — **tier: free-tier**
- [ ] T011 [P] [US1] Add `test_bad_r16_depth_indent_caught` and `test_bad_r16_depth_indent_arrow_caught` to `skills/structured-gist/tests/test_lint.py`, asserting the reported rule id is exactly `R16` — **tier: free-tier**
- [ ] T012 [P] [US1] Add `test_good_r16_depth_indent_passes` to `skills/structured-gist/tests/test_lint.py` — **tier: free-tier**

### Implementation for User Story 1

- [ ] T013 [US1] Implement the R16 predicate in `skills/structured-gist/tests/lint_outline.py` per plan.md D1: for any node whose family is an enumerator (`uroman`/`ualpha`/`lroman`/`lalpha`) or `arrow`, the nearest preceding node at lower-or-equal depth that is an `attr` must be at strictly lower depth (FR-001) — **tier: free-tier**
- [ ] T014 [US1] Assert additivity in `skills/structured-gist/tests/lint_outline.py`: R16 appends its finding and never suppresses an R1/R2 finding on the same line (spec Edge Cases) — cover with a mixed-violation fixture assertion in `test_lint.py` — **tier: free-tier**
- [ ] T015 [US1] Add an R16 rule-id assertion to `skills/structured-gist/tests/smoke.sh` matching the existing per-rule assertion pattern — **tier: free-tier**
- [ ] T016 [US1] Regression sweep: run the linter over every file in `skills/structured-gist/tests/fixtures/` and every `renderings/*/{skim,standard,deep}.md` under the eight benchmark cases; record pass/fail before and after R16 and confirm zero deltas (FR-002, SC-001). Write the table to `specs/001-backlog-hedge-fidelity/r16-regression.md` — **tier: free-tier**
- [ ] T017 [US1] **DECISION GATE** — if T016 shows any delta, adjudicate whether the fixture was previously mis-passing or R16 is over-firing, and record the call in `specs/001-backlog-hedge-fidelity/decisions.md`. Not an implementation task. — **tier: opus — decision gate**
- [ ] T017a [US1] If T017 rules the delta is R16 over-firing (not a previously-mis-passing fixture): fix the R16 predicate in `skills/structured-gist/tests/lint_outline.py` and re-run the T016 regression sweep, repeating until zero deltas. US1 is NOT complete until the sweep shows zero deltas (spec clarification #9, FR-002) — **tier: haiku**
- [ ] T017b [US1] Bump `skills/structured-gist/SKILL.md`'s `version:` frontmatter and add a row to `skills/structured-gist/tests/benchmark.md` recording R16's measured false-negative/false-positive count from T016/T017a as the real number (FR-030b) — **tier: free-tier**

**Checkpoint**: US1 fully functional; SC-001 demonstrated; zero regression deltas confirmed (T017a, if triggered); SKILL.md version + benchmark row landed (T017b).

---

## Phase 4: User Story 2 — Issue #9 records why error-promotion is blocked (Priority: P1)

**Goal**: Issue #9 carries the registrar counterexample and a plain statement that error-promotion is blocked pending hedge detection.

**Independent Test**: Read issue #9 — counterexample and blocked status are both present and self-contained.

**Depends on**: T004 (redaction sign-off for the registrar excerpt).

- [ ] T018 [US2] Draft the issue #9 comment body into `specs/001-backlog-hedge-fidelity/artifacts/issue-9-comment.md` using only the T004-APPROVED registrar excerpt, stating error-promotion blocked pending hedge detection (FR-004) — **tier: haiku**
- [ ] T019 [US2] Append the R16/R17 identifier allocation note (FR-003a) to the same comment body — **tier: free-tier**
- [ ] T020 [US2] Post the comment to `domattioli/structured-gist` issue #9 via `gh issue comment 9 --body-file specs/001-backlog-hedge-fidelity/artifacts/issue-9-comment.md`; record the returned comment URL in the artifact file. On failure: retry once; if the retry also fails, halt and report the specific failure to the operator — no silent skip, no fabricated success (spec clarification #2) — **tier: free-tier**

**Checkpoint**: US2 complete; step 8 cannot proceed on incomplete evidence unnoticed.

---

## Phase 5: User Story 3 — A hedge/qualifier fidelity axis exists as a tracked work item (Priority: P1)

**Goal**: A new issue defines the epistemic gold-set category, both metrics, and three test cases — implementable from its own text.

**Independent Test**: A reader who has never seen this spec can implement the gold-set change, both metrics, and the three test cases from the issue text alone.

**Depends on**: T004 (redaction verdict only, not the GitHub round-trip).

- [ ] T021 [P] [US3] Draft the gold-set section into `specs/001-backlog-hedge-fidelity/artifacts/issue-hedge-axis.md`: `epistemic` category at weight 3 (peer of `negation`), plus the `attaches_to` field; state that gold files are per-case so the change is specified once and applied across cases (FR-006) — **tier: haiku**
- [ ] T022 [US3] Author the metric definitions in the same file — a deterministic, source-aware, judge-free `hedge_survival_rate` shippable ahead of the harness rebuild (FR-007), and a separate model-judged `caveat_attach_accuracy` (FR-008) — each specified precisely enough to implement cold. For `caveat_attach_accuracy`, state explicitly that judging runs at **sonnet** tier (escalated from the harness default) with the judge shown the source excerpt and rendered output side-by-side per claim, never the output alone (FR-008, spec clarification #6) — **tier: haiku**
- [ ] T023 [US3] Name the three test cases in the same file (registrar; conditional second case, included only per its T004 verdict; deontic-modality case absorbing issue #8's reframed content) and record the drop reason if the second case was DROPPED (FR-009, spec Edge Cases) — **tier: free-tier**
- [ ] T023a [US3] **DECISION GATE** — dispatch a fresh-context agent with no prior exposure to this spec or session; it reads only `specs/001-backlog-hedge-fidelity/artifacts/issue-hedge-axis.md` and confirms it is implementable cold. If it is not, revise the artifact and re-check before T024 files it — never after (FR-005, spec clarification #8). Record the verdict in `specs/001-backlog-hedge-fidelity/decisions.md`. Not an implementation task. — **tier: opus — decision gate**
- [ ] T024 [US3] File the issue via `gh issue create --repo domattioli/structured-gist --title "Hedge/qualifier fidelity axis" --body-file specs/001-backlog-hedge-fidelity/artifacts/issue-hedge-axis.md`; record the issue number back into the artifact file. Depends on T023a passing. On `gh` failure: retry once; if the retry also fails, halt and report the specific failure — no silent skip (spec clarification #2) — **tier: free-tier**
- [ ] T025 [P] [US3] Author a migration script `skills/structured-gist/benchmarks/semantic-compression/scoring/migrate_gold_schema.py` that programmatically adds the `epistemic` category and optional `attaches_to` field shape to every `gold.json` under `skills/structured-gist/benchmarks/semantic-compression/{regression,pressure-tests}/*/`, populated where a qualifier is present in `source_quote`, then run it once against all eight existing cases so the added shape is structurally identical across every case — NOT manual per-file edits (FR-006, spec clarification #14) — **tier: haiku**
- [ ] T026 [P] [US3] Add a schema/shape check for the `epistemic` + `attaches_to` fields to `skills/structured-gist/tests/smoke.sh` — every `gold.json` parses and every `attaches_to` resolves to a fact id in the same file — **tier: free-tier**

### Deterministic hedge-survival metric (defined by US3, consumed by US7)

- [ ] T027 [P] [US3] Author the hedge lexicon (modal verbs, epistemic adverbs, approximators, evidential frames) as `skills/structured-gist/benchmarks/semantic-compression/scoring/hedge_lexicon.json`, drafted by scouting existing published references on epistemic-hedging taxonomies rather than invented from scratch; cite each entry or cluster of entries with the URL of the reference it came from (FR-007a, spec clarification #1, #7) — **tier: haiku**
- [ ] T027a [US3] **DECISION GATE** — supervising operator reviews and edits the drafted `hedge_lexicon.json` (entries, citations); the lexicon file records which entries came from which reference and which were added/removed by review. The lexicon MUST NOT be used to score any case before this verdict is recorded (FR-007a, spec clarification #1). Not an implementation task. — **tier: opus — decision gate**
- [ ] T028 [US3] Implement `skills/structured-gist/benchmarks/semantic-compression/scoring/hedge_survival.py` per plan.md D3: match the T027a-reviewed lexicon against each gold fact's `source_quote` and against the rendered outline; report survival as the fraction of source-side hedge occurrences bound to a retained fact that also appear in the rendering — **tier: haiku**
- [ ] T029 [P] [US3] Add `skills/structured-gist/benchmarks/semantic-compression/scoring/test_hedge_survival.py` with hand-built source/rendering pairs covering full survival, total loss, and partial survival — **tier: free-tier**
- [ ] T030 [P] [US3] Add a hedge-migration test to the same file: a hedge that survives but attaches to a different claim still scores as surviving under `hedge_survival_rate` (plan.md D3 — separation from the judged metric) — **tier: free-tier**

**Checkpoint**: US3 complete; the metric US7 and US8 depend on exists and is tested.

---

## Phase 6: User Story 4 — The benchmark harness is reproducible and cheap to run (Priority: P1)

**Goal**: Pinned model + prompt hashes, a content-addressed judged cache, and a split deterministic/judged lane.

**Independent Test**: Run the suite twice on unchanged inputs — deterministic results identical, judged results served from cache with zero new model calls (SC-002).

### Tests for User Story 4

- [ ] T031 [P] [US4] Add `skills/structured-gist/benchmarks/semantic-compression/test_cache.py` asserting a byte-identical input hits the cache and a changed prompt or model id misses it (FR-013) — **tier: haiku**
- [ ] T032 [P] [US4] Add a double-run assertion to `skills/structured-gist/tests/smoke.sh`: `run_deterministic.sh` twice produces byte-identical `results/deterministic.json` (SC-002) — **tier: free-tier**

### Implementation for User Story 4

- [ ] T033 [US4] **DECISION GATE** — confirm the D4 cache-key tuple (case id, rendering level, rendering content, gold content, prompt content, model id) is complete, i.e. nothing outside it can change a judged verdict. Adjudication only; record in `specs/001-backlog-hedge-fidelity/decisions.md`. — **tier: opus — decision gate**
- [ ] T034 [P] [US4] Author `skills/structured-gist/benchmarks/semantic-compression/suite.json` with an explicit `{cases, conditions}` top-level shape: `cases` is the case roster with per-case lane membership (`deterministic` | `judged`) covering the eight existing cases; `conditions` is initially empty — **tier: free-tier**
- [ ] T035 [P] [US4] Author `skills/structured-gist/benchmarks/semantic-compression/provenance.json` shape and writer stub: `{model_id, prompt_sha256, suite_sha256, timestamp}` (FR-012) — **tier: free-tier**
- [ ] T036 [US4] Implement `skills/structured-gist/benchmarks/semantic-compression/run.py` — the Python entry point over `suite.json`, lane selection, SHA-256 cache read/write under `.cache/judged/<sha256>.json`, and provenance emission (FR-011–FR-014) — **tier: haiku**
- [ ] T037 [US4] Implement TWO separate shell entry points, `skills/structured-gist/benchmarks/semantic-compression/run_deterministic.sh` and `.../run_judged.sh`, each a thin wrapper delegating to `run.py` over the same `suite.json` and selecting its own lane — NOT a `--lane` flag or env-var on a single script, so the CI-safe/manual-only split is structural (FR-011, FR-014, spec clarification #13) — **tier: free-tier**
- [ ] T038 [US4] Make `run_judged.sh` require explicit invocation and report `unavailable` — never a deterministic proxy — when a judged result is requested with no cache entry and no model access (FR-014, spec Edge Cases) — **tier: free-tier**
- [ ] T039 [US4] Register `hedge_survival.py` as a deterministic-lane metric in `run.py` so US7 can consume it — **tier: free-tier**
- [ ] T040 [US4] Add `.github/workflows/benchmark-deterministic.yml` running `run_deterministic.sh` on every push and PR, with no model credentials in scope (FR-014, SC-003). NOTE: the repo has no `.github/workflows/` directory today — create it — **tier: free-tier**
- [ ] T040a [US4] Add a smoke.sh assertion that no file under `.github/workflows/` contains the string `run_judged.sh`, so the judged lane's CI-exclusion is structurally verified, not just asserted in prose (FR-014, spec clarification #13) — **tier: free-tier**
- [ ] T041 [US4] Verify SC-002 by hand: run `run_deterministic.sh` twice, diff `results/deterministic.json`, and separately confirm `run_judged.sh` serves from cache with zero new model calls when inputs are unchanged; record in `specs/001-backlog-hedge-fidelity/harness-verification.md` — **tier: free-tier**

**Checkpoint**: US4 complete; US5, US7, US8, US9 unblocked.

---

## Phase 7: User Story 5 — The README shows a real before/after (Priority: P2)

**Goal**: A harness-generated, regenerable README example in which the hedge sits on an attribute node and the qualified candidates are enumerator children beneath it.

**Independent Test**: Regenerate the example with the harness and diff against the committed README block; they match (SC-004).

**Depends on**: Phase 2 (T004), Phase 6.

- [ ] T042 [US5] Stage the FULL registrar source message (not the truncated corpus window) as a benchmark case source at `skills/structured-gist/benchmarks/semantic-compression/pressure-tests/registrar-hedge/source.md`; may only write text already carrying an APPROVED or APPROVED-WITH-EDITS verdict from the T004 redaction gate (FR-017, FR-010) — **tier: free-tier**
- [ ] T043 [P] [US5] Author `.../pressure-tests/registrar-hedge/gold.json` including `epistemic` facts and `attaches_to` bindings — **tier: free-tier**
- [ ] T044 [US5] Add the `registrar-hedge` case to `suite.json` on the deterministic lane — **tier: free-tier**
- [ ] T045 [US5] Add a `--emit-readme-example` mode to `run.py` that writes the before/after block to `skills/structured-gist/benchmarks/semantic-compression/results/readme_example.md` (FR-016) — **tier: free-tier**
- [ ] T046 [US5] Generate the example and paste the generated block into `README.md` between explicit `<!-- README-EXAMPLE:START -->` / `<!-- README-EXAMPLE:END -->` markers (FR-015) — **tier: free-tier**
- [ ] T047 [US5] Verify the rendered structure: the hedge is on the `▸` attribute node and the qualified candidates are enumerator children beneath that node (FR-015, US5 scenario 4) — **tier: free-tier**
- [ ] T048 [US5] Add a regeneration-diff check to `skills/structured-gist/tests/smoke.sh` comparing the README marker block against a fresh `--emit-readme-example` output (SC-004) — **tier: free-tier**

**Checkpoint**: US5 complete; the public payoff of steps 1–4 is on the README and is regenerable.

---

## Phase 8: User Story 6 — Outlines can be emitted as a machine-readable claim list (Priority: P2)

**Goal**: A JSONL claim-list render target derived from the outline tree, schema-validated.

**Independent Test**: Render a known outline to the claim list and validate every record against the published schema (SC-005).

**Depends on**: Phase 1 only. Runs in parallel with Phases 4–7.

### Tests for User Story 6

- [ ] T049 [P] [US6] Add `skills/structured-gist/render/test_claim_list.py` asserting one record per claim carrying `claim`, `modality`, `polarity`, `source_span`, `parent_id` (FR-018) — **tier: free-tier**
- [ ] T050 [P] [US6] Add a derived-view test to the same file: `claim_list.py` accepts only a parsed outline tree and never re-parses prose independently (FR-020) — **tier: haiku**
- [ ] T050a [P] [US6] Add a structural assertion-vs-bare-label test to the same file per FR-018a: an attribute node whose own text has no verb/predicate and no non-summary `↪` child emits no record; an attribute node with a verb/predicate in its own text emits a record from its own text; an attribute node with a non-summary `↪` child emits a record from the child's content instead; a concept node never emits a record — **tier: free-tier**

### Implementation for User Story 6

- [ ] T054 [US6] **DECISION GATE** — settle the modality/polarity vocabulary (which values are legal for `modality` and `polarity`), since neither spec nor plan enumerates them. Adjudication only; record in `specs/001-backlog-hedge-fidelity/decisions.md`. — **tier: opus — decision gate**
- [ ] T051 [US6] Author `skills/structured-gist/render/claim_list.schema.json` — the published JSON Schema for a claim record (FR-019); depends on T054 — **tier: free-tier**
- [ ] T052 [US6] Implement `skills/structured-gist/render/claim_list.py`: consume the tree from `lint_outline.parse_line` output, emit one JSONL record per claim (FR-018, FR-020) — **tier: free-tier**
- [ ] T052a [US6] Implement the FR-018a structural assertion-vs-bare-label predicate in `claim_list.py`: an attribute node emits a record iff its own text contains a verb/predicate, OR it has a non-summary `↪` child (in which case that child's content is the emitted record, not the attribute's own text); an attribute node satisfying neither emits nothing; concept nodes never emit — **tier: haiku**
- [ ] T053 [US6] Implement stdlib-only schema validation in `claim_list.py` (no new runtime dependency — plan.md P1) and wire it into the emit path (FR-019) — **tier: haiku**
- [ ] T055 [US6] Run `claim_list.py` over every fixture in `skills/structured-gist/tests/fixtures/` and assert zero validation failures (SC-005); add the sweep to `skills/structured-gist/tests/smoke.sh` — **tier: free-tier**
- [ ] T056 [US6] Document in `skills/structured-gist/render/README.md` that the claim list is a derived view, and record the claim-list-as-primary-IR design as a stated future endgame explicitly not built here (FR-020) — **tier: free-tier**
- [ ] T056a [US6] Bump `skills/structured-gist/SKILL.md`'s `version:` frontmatter and add a row to `skills/structured-gist/tests/benchmark.md` recording the measured SC-005 validation-failure count (zero) from T055 as the real number (FR-030b) — **tier: free-tier**

**Checkpoint**: US6 complete; the first non-text render target ships.

---

## Phase 9: User Story 7 — The caveman-lite comparison is run fairly (Priority: P2)

**Goal**: A token-matched comparison of structured-gist alone vs. structured-gist + caveman-lite, reporting hedge survival, with the prediction recorded before results.

**Independent Test**: Both conditions' token counts are within five percent; the recorded prediction predates the results (SC-006, SC-007).

**Depends on**: Phase 5 (T028), Phase 6.

- [ ] T057 [US7] Write the prediction FIRST into `specs/001-backlog-hedge-fidelity/experiments/caveman-lite.md`: the paired condition retains hedging markedly worse, because compression rules delete hedging language by design. Commit this before any run (FR-023) — **tier: free-tier**
- [ ] T058 [P] [US7] Populate the `conditions` key in `suite.json` with both conditions as `sg-alone` and `sg-plus-caveman-lite` — **tier: free-tier**
- [ ] T059 [US7] Implement token counting per condition in `run.py` and emit both counts plus their percentage delta into `results/combined.json` (FR-021) — **tier: free-tier**
- [ ] T060 [US7] Tune granularity/instruction per condition until measured output token counts converge within ±5%, recording each attempt in the experiment file (plan.md D6) — **tier: haiku**
- [ ] T061 [US7] Run both conditions and record `hedge_survival_rate` per condition alongside the existing retention metrics (FR-022) — **tier: free-tier**
- [ ] T062 [US7] **DECISION GATE** — if the two conditions cannot be brought within the ±5% tolerance, rule that the comparison is NOT reported as a result and only the mismatch is recorded in `specs/001-backlog-hedge-fidelity/decisions.md` (FR-021, spec Edge Cases). Adjudication only. — **tier: opus — decision gate**
- [ ] T063 [US7] Conclude the experiment file by explicitly marking the prediction CONFIRMED or REFUTED against the measured numbers (FR-023, SC-007) — **tier: free-tier**

**Checkpoint**: US7 complete; step 8's evidence exists.

---

## Phase 10: User Story 8 — The comma-split rule is promoted only on evidence (Priority: P3)

**Goal**: R17 lands with a `warn` severity and is promoted to `error` only if split precision on corpus-sampled leaves is ≥ 0.98.

**Independent Test**: Compute split precision on corpus-sampled leaf nodes and compare against the threshold; the resulting rule severity matches the measured value (SC-008).

**Depends on**: Phases 5, 6, 9 (FR-025).

### Tests for User Story 8

- [ ] T064 [P] [US8] Add fixtures `skills/structured-gist/tests/fixtures/good_r17_comma_split.md` and `bad_r17_comma_split.md` — **tier: free-tier**
- [ ] T065 [P] [US8] Add `test_r17_comma_split_warns` to `skills/structured-gist/tests/test_lint.py` asserting the finding carries `severity == 'warn'` and does NOT affect the exit code — **tier: free-tier**
- [ ] T066 [P] [US8] Add `test_existing_rules_default_to_error` to `test_lint.py` asserting every rule other than R17 keeps severity='error' and the linter exit code is unchanged across the existing fixture corpus (plan.md D2) — **tier: free-tier**

### Implementation for User Story 8

- [ ] T067 [US8] Add a `severity` field (`error` | `warn`, default `error`) to the violation record in `skills/structured-gist/tests/lint_outline.py`, and make the exit code count only `error` violations (plan.md D2) — **tier: haiku**
- [ ] T068 [US8] Implement the R17 comma-split rule in `lint_outline.py` at `severity='warn'` — **tier: free-tier**
- [ ] T068a [US8] Draw the split-precision sample per FR-024b: a deterministic seeded random draw of explanation leaves from across the whole benchmark corpus that R17 fires on. Record the population (full fired-on leaf set), the seed, and the sample size in `specs/001-backlog-hedge-fidelity/r17-precision.md`, before any labelling occurs — **tier: free-tier** (fully determined by a stated predicate — a seeded draw — no judgment involved)
- [ ] T069 [US8] Measure split precision: a SINGLE free-tier labeller labels each leaf in the T068a sample correct / incorrect / ambiguous per FR-024a; an ambiguous label counts as incorrect. Record the value in the same `r17-precision.md` file (FR-024, FR-024a, spec clarification #5) — **tier: free-tier**
- [ ] T069a [US8] Power check per FR-024b: confirm the T068a sample size is large enough that the observed precision from T069 distinguishes 0.98 from 0.95. If it is not, record the promotion decision as DEFERRED (not taken) in `r17-precision.md` and skip T070's branch application. Deciding what counts as an adequately powered sample size for this distinction is a judgment call beyond a stated predicate — **tier: haiku**
- [ ] T070 [US8] Unless T069a recorded DEFERRED: apply the branch — if precision ≥ 0.98 flip R17 to `severity='error'`; otherwise leave it `warn` with no expiry date and record the outcome as a decision, not a failure (FR-024, SC-008). Prerequisite: refuse to flip severity unless all three exist — the step-3 issue number, the harness `provenance.json`, and the step-7 experiment record file (FR-025) — **tier: free-tier**
- [ ] T071 [US8] Add an R17 rule-id + severity assertion to `skills/structured-gist/tests/smoke.sh` matching whichever branch T070 took — **tier: free-tier**
- [ ] T071a [US8] Bump `skills/structured-gist/SKILL.md`'s `version:` frontmatter and add a row to `skills/structured-gist/tests/benchmark.md` recording the measured R17 split precision from T069/T070 as the real number, along with the severity branch taken (FR-030b) — **tier: free-tier**

**Checkpoint**: US8 complete; severity in effect matches the measurement.

---

## Phase 11: User Story 9 — Issue #1 is settled by a correlation (Priority: P3)

**Goal**: A rank correlation between SCU-recall and weighted retention over the eight existing results decides whether a column is added or the issue is closed.

**Independent Test**: The coefficient is recorded and the action taken matches the branch it selects (SC-009).

**Depends on**: nothing beyond existing results — can run in parallel from Phase 1.

- [ ] T072 [P] [US9] Compute SCU-recall explicitly from the gold fact lists of the eight cases and record the definition used, in `specs/001-backlog-hedge-fidelity/scu-correlation.md` (plan.md D5) — **tier: free-tier**
- [ ] T073 [US9] Compute the Spearman rank correlation ρ between SCU-recall and `weighted_retention` over a FROZEN snapshot of the pre-step-3 8-case `results/combined.json` (T044 adds a 9th case), stdlib-only; record ρ, the input data, and state `n=8` in the recorded output (FR-026, D5) — **tier: free-tier**
- [ ] T074 [US9] Apply the branch: if ρ < 0.8 add an `scu_recall` column to `skills/structured-gist/benchmarks/semantic-compression/scoring/combine.py` and to the `write_scores_table` header; if ρ ≥ 0.8 close issue #1 as duplicative via `gh issue close 1 --reason completed`, citing the coefficient and the SCU-recall definition (FR-027) — **tier: free-tier**
- [ ] T075 [US9] If ρ lands near 0.8, note the borderline reading explicitly in the closing text or the column commit message (spec Edge Cases) — **tier: free-tier**

**Checkpoint**: US9 complete; issue #1 reaches a terminal state.

---

## Phase 12: User Story 10 — Issue #8 is reframed rather than left ambiguous (Priority: P3)

**Goal**: Issue #8 closed as framed, its useful content named as folded into the step-3 deontic-modality test case.

**Independent Test**: Issue #8 is closed with stated reasoning and the deontic-modality test case named in the US3 issue exists.

**Depends on**: T024.

- [ ] T076 [US10] Draft the closure text into `specs/001-backlog-hedge-fidelity/artifacts/issue-8-closure.md`, retiring the original framing and naming the step-3 issue number as where its content went (FR-028) — **tier: free-tier**
- [ ] T077 [US10] Close via `gh issue close 8 --repo domattioli/structured-gist --reason "not planned" --comment "$(cat ...)"`, then verify the deontic-modality test case is present and traceable back to issue #8 in the US3 issue body (US10 scenario 2). On `gh` failure: retry once; if the retry also fails, halt and report the specific failure — no silent skip (spec clarification #2) — **tier: free-tier**

---

## Phase 13: User Story 11 — Issue #3 is deferred with reasons on the record (Priority: P3)

**Goal**: The pptx target is closed or deferred with all three reasons and the reopening condition on the record.

**Independent Test**: The closing text contains all three reasons and the reopening condition.

**Depends on**: nothing — parallel from Phase 1.

- [ ] T078 [P] [US11] Draft the closure into `specs/001-backlog-hedge-fidelity/artifacts/issue-3-closure.md`, naming the lossy ladder-to-slide remapping, the absence of a falsifiable success metric, the added binary dependency to a dependency-free skill, and demonstrated demand as the reopening condition (FR-029) — **tier: free-tier**
- [ ] T079 [US11] Close issue #3 via `gh issue close 3 --repo domattioli/structured-gist --reason "not planned"` with that body. On `gh` failure: retry once; if the retry also fails, halt and report the specific failure — no silent skip (spec clarification #2) — **tier: free-tier**

---

## Phase 14: Polish & Cross-Cutting Concerns

- [ ] T080 [P] Update `skills/structured-gist/SKILL.md` rule table with R16 and R17, including R17's severity as landed (FR-003a) — **tier: free-tier**
- [ ] T081 [P] Update `skills/structured-gist/benchmarks/semantic-compression/README.md` with the lane split, the cache, and how to invoke each lane — **tier: free-tier**
- [ ] T082 Verify SC-010: confirm issues #1, #3, #6, #8, #9 each reach a recorded terminal state and grep the full delivered diff for personal data one final time — **tier: free-tier**
- [ ] T083 Run the full gate — `python3 -m pytest skills/structured-gist/tests/` and `bash skills/structured-gist/tests/smoke.sh` — and confirm both pass — **tier: free-tier**

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: no dependencies.
- **Phase 2 (Foundational — redaction)**: after Setup. **BLOCKS US2, US3, US5.** Does not block US1, US4, US6, US9, US11.
- **Phase 3 (US1)**: after Setup.
- **Phase 4 (US2)**: after Phase 2.
- **Phase 5 (US3)**: after Phase 2 and Phase 4.
- **Phase 6 (US4)**: after Setup. Independent of US1–US3, though it hosts the US3 metric.
- **Phase 7 (US5)**: after Phase 2 and Phase 6.
- **Phase 8 (US6)**: after Setup only.
- **Phase 9 (US7)**: after Phase 5 (metric) and Phase 6 (harness).
- **Phase 10 (US8)**: after Phases 5, 6, 9 (FR-025 — hard gate).
- **Phase 11 (US9)**: after Setup only.
- **Phase 12 (US10)**: after T024.
- **Phase 13 (US11)**: after Setup only.
- **Phase 14 (Polish)**: after all desired stories.

### Ordering graph (from plan.md)

```
US1  (lint rule)      independent
US2  (#9 comment)     needs redaction gate
US3  (new issue)      needs US2's redacted counterexample
US4  (harness)        independent of US1-US3; hosts US3's metric
US5  (README example) needs US4 + redaction gate
US6  (claim list)     independent
US7  (comparison)     needs US4 + US3's metric
US8  (promotion)      needs US3, US4, US7
US9  (correlation)    needs existing results only
US10 (#8 closure)     needs US3 filed
US11 (#3 closure)     independent
```

### Parallel Opportunities

- **Immediately after Setup**, four tracks run concurrently: US1 (linter), US4 (harness), US6 (claim list), US9 + US11 (bookkeeping).
- Within US1: T008–T012 (fixtures + tests) all `[P]`.
- Within US4: T031/T032 (tests) and T034/T035 (config authoring) all `[P]`.
- Within US6: T049/T050/T051 all `[P]`.
- Within US8: T064/T065/T066 all `[P]`.
- Strictly serial: US5, US7, US8 behind the harness; US3 behind US2 behind the redaction gate.

---

## Parallel Example: User Story 1

```bash
# Fixtures and tests together (all different files):
Task: "Add fixture bad_r16_depth_indent.md"          # T008  free-tier
Task: "Add fixture bad_r16_depth_indent_arrow.md"    # T009  free-tier
Task: "Add fixture good_r16_depth_indent.md"         # T010  haiku
Task: "Add R16 bad-fixture tests to test_lint.py"    # T011  free-tier
Task: "Add R16 good-fixture test to test_lint.py"    # T012  free-tier
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Phase 1 Setup → 2. Phase 3 (US1) → 3. **STOP and VALIDATE**: pytest + smoke pass, SC-001 demonstrated.

### Incremental Delivery

1. Setup → 2. Redaction gate (unblocks the corpus work) → 3. US1 (MVP) → 4. US2 + US3 (definitions) → 5. US4 (harness) → 6. US5, US6, US7 → 7. US8, US9, US10, US11 → 8. Polish.

---

## Notes

- `[P]` tasks touch different files and have no ordering dependency.
- **FR-010 is absolute**: no corpus excerpt is written to any file, issue, comment, fixture, or benchmark input before its T004 verdict.
- **opus/astra never executes implementation.** The seven decision gates (T004, T017, T023a, T027a, T033, T054, T062) are judgment calls with no code output.
- Steps 2, 3, 10, 11 (US2, US3, US10, US11) are `gh` CLI actions on `domattioli/structured-gist`, not code. Every `gh` write in this backlog retries once on failure, then halts and reports the specific failure to the operator — never a silent skip, never a fabricated success (spec clarification #2).
- The repo has no `.github/workflows/` directory today — T040 creates the first one.
- **This backlog ships as ONE pull request** covering all eleven steps (FR-030a) — an explicit, one-time operator override of this repo's own CONTRIBUTING.md "one rule, one PR" convention; do not split by rule or by user story.
- **The judged benchmark lane is two separate scripts**, `run_deterministic.sh` and `run_judged.sh` (T037) — never a `--lane` flag or env-var on one script, and no CI workflow file may reference `run_judged.sh` (T040a).
- Commit after each task or logical group; stop at any checkpoint to validate a story independently.
