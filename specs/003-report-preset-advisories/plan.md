# Implementation Plan: Report preset + interrogative/hedge advisories

**Branch**: `development` (spec dir `003-report-preset-advisories`) | **Date**: 2026-09-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-report-preset-advisories/spec.md`

## Summary

Add 25–45 lines of advisory guidance to `skills/structured-gist/SKILL.md` plus one opt-in preset (`/structured-gist report`, alias `findings`), a thin `examples/report.md`, a deterministic test-only fidelity check with negative fixtures, lint coverage for the new example, discoverability updates, a version bump to `0.5.0b1` across five surfaces, a changelog entry, and a benchmark row. No linter rule is added or changed; `skills/structured-gist/tests/lint_outline.py` is not touched.

## Technical Context

**Language/Version**: Markdown (normative skill doc) + Python 3 (stdlib only) for the added test-only helper and test cases
**Primary Dependencies**: none added (constitution P1)
**Storage**: N/A
**Testing**: `pytest` over `skills/structured-gist/tests/` + `bash skills/structured-gist/tests/smoke.sh`
**Target Platform**: repo-local skill document consumed by Claude Code sessions
**Project Type**: single-repo skill library
**Performance Goals**: N/A (no runtime path changed)
**Constraints**: `SKILL.md` insertions 25–45 lines as counted by `git diff --numstat` (excluding the version and description lines); every fenced outline in `SKILL.md` and in the new example must lint clean under the existing 15 rules
**Scale/Scope**: 8 edit sites in `SKILL.md`, 1 new example, 1 new test-only helper + 3 negative fixtures + 6 new test cases, 5 version surfaces, 1 changelog entry, 1 benchmark row, 3 discoverability surfaces

## Constitution Check

*GATE: passes before and after design.*

| Principle | Status | Note |
|---|---|---|
| P1 zero runtime deps | PASS | no dependency added |
| P2 falsifiable claims | PASS **only because of D5** | The first draft of this plan marked P2 PASS while the hedge rule (C3) and the relation rule (M2) shipped with no check that could fail — that was a rationalization, and P2 says such features are deferred, not built. D5 replaces it with a deterministic fidelity check plus negative fixtures proving the check can fail. The residual judgement-level claims (does the lexicon improve naming?) are demoted to recorded limitations in the spec and are not claimed as requirements. |
| P3 no self-graded evidence | PASS | the example is graded by the existing linter and by a separate check whose failure modes are pinned by negative fixtures, not by prose assertion |
| P4 deterministic checks free | PASS | both the lint case and the fidelity check are stdlib pytest cases; no model call, no network |
| P5 structure is the invariant | PASS | advisory-only; ladder, rule set, and lint contract untouched — the preset supplies branch *names*, not new roles |
| P6 no personal data | PASS | example content must be synthetic; no corpus excerpt |

No violations → Complexity Tracking omitted.

## Design decisions

**D1 — Edit sites (anchors are current `SKILL.md` line numbers, v0.4.12).**

| ID | Site | Change |
|---|---|---|
| C1 | taxonomy table + prose, :58–65 | add what the attribute and explanation rows answer; add the interrogatives-are-content-prompts sentence |
| C2 | attribute-vs-enumerator, :65 | advisory name lexicon (purpose/mechanism/actor/location/timing/certainty), scope and trigger kept separate, "whether" is a proposition not a confidence, prefer source names, advisory not enforced |
| M1 | after the summary preset block, :38 | shared preset-omission contract governing both presets; summary shape becomes omit-if-absent |
| C4 | after M1 | report preset: invocation + alias, finding-first, one concept per supported finding, multiple findings as peers, optional branches question/method/observed/inferred/next, no generic intro/background/conclusion, granularity and render mode unchanged, plus a short fenced skeleton |
| M2 | arrow rule, :79 | preserve source relation wording; do not upgrade an association to a causal arrow; endpoints stay identifiable |
| C5 | nest-by-dependency, :106–107 | softened observed-vs-inferred advisory |
| C3 | new `## Hedge preservation` after `## Leaf preservation`, :137 | hedge stays claim-local or in an immediately attached `↪`; certainty branch only when scope unambiguous; never promote a qualified claim to an unqualified heading |
| L | `## Limitations`, :239 | two lines: hedge-fidelity acceptance needs source-vs-output comparison and is deferred; relation-wording preservation is likewise unenforced |

**D2 — Preset shape.** Branches are `▸` attributes of the finding concept. Enumerators beneath a `▸` sit at depth 2 → lowercase family (`i.`/`a.`), per the existing depth-keyed ladder. `Method` is itself a named branch, never an ordinal node.

**D3 — Version, five surfaces.** `0.5.0b1` verbatim at: `skills/structured-gist/SKILL.md` frontmatter `version:`; `plugins/structured-gist/.claude-plugin/plugin.json` `"version"`; the `README.md` badge (line 5); a new `skills/structured-gist/CHANGELOG.md` entry (the file carries one entry per version, `v0.4.12` at line 3); a new `skills/structured-gist/tests/benchmark.md` row. Nothing in `tests/` parses the version (`smoke.sh:44` only greps that the `version:` key exists; `grep -rn version tests/*.py` returns nothing) — but the Claude Code plugin manifest validator is an external consumer and `0.5.0b1` is a PEP 440 string, not semver. The `v0.4.12` changelog entry records that `claude plugin install` + `claude plugin details` were the verification path for the previous release, so the same read-only path is re-run here (T018) and its output reported. A rejection is escalated; the string is not altered. **Resolved 2026-09-18:** an orchestrator-run validation (operator-directed, outside this feature) exercised the real loader — `claude plugin validate` clean from two working directories, a dereferenced copy clean with no warnings, and a local marketplace install reporting `structured-gist 0.5.0b1`, Skills (1). PEP 440 is accepted; the semver risk this decision recorded is closed. Evidence is the orchestrator's, not this session's.

**D4 — Coverage of new outlines.** Fenced blocks in `SKILL.md` are already linted by `TestNormativeBlocks::test_skill_md_all_blocks_clean` (`tests/test_lint.py:531`), so the inline skeleton is covered automatically. `examples/report.md` is not, so a sibling case is added in the same class, mirroring `test_attribute_example_clean` (`tests/test_lint.py:557`).

**D5 — Fidelity check (constitution P2, replaces the unmeasurable claim).**

The hedge rule and the relation rule must be able to fail. Mechanism, all stdlib, no model:

- `examples/report.md` carries a machine-readable declaration block as an **HTML comment** (not a fence — `_lint_all_blocks` uses the regex ```` ```(?:text)?\n ````, so any extra fence risks perturbing block pairing). Fields, one per line: `source:`, `hedge:`, `claim-key:`, `relation:`, `endpoint-a:`, `endpoint-b:`.
- New test-only helper `skills/structured-gist/tests/fidelity_check.py` exposes `check_fidelity(path) -> list[str]` (empty list = clean) implementing three checks:
  0. **Declaration validity** — report a violation if any declared field is missing or empty, or if the `hedge` token occurs inside the `claim-key` string. Without this, a declaration like `hedge: may` / `claim-key: timeout may spike` makes the hedge check pass unconditionally — a vacuous pass, exactly what P2 forbids.
  1. **Hedge attachment** — locate the outline line whose text contains `claim-key`; report a violation unless the `hedge` token appears as a **whole word** (regex `\b…\b`, case-insensitive) in that same line, or in a following line that is indented deeper and whose marker is `↪`, reached without first passing a line at or above the claim's indent. Whole-word matching is required: a substring match lets `may` be satisfied by `mayor` or `maybe`.
  2. **Relation preservation** — report a violation if the `relation` phrase is absent from every outline line, or if any single line contains the declared endpoints joined by `→` in **either** order (`a → b` or `b → a`) — both are the same association-to-causality upgrade.
- Negative fixtures live in their own directory `tests/fixtures/fidelity/` with names that do not use the `bad_` prefix: `hedge_dropped.md`, `relation_upgraded.md`, `declaration_malformed.md`. **Naming matters:** every existing `tests/fixtures/bad_*.md` means "must FAIL the linter" (the contract `smoke.sh` checks at lines 248–268). These fixtures have the opposite contract — they must **lint clean** and fail only the fidelity check, so the proof is isolated to the property under test.
- Five test cases: the example is fidelity-clean; each of the three fixtures yields ≥1 violation; and all three fixtures lint clean. Without the fixture cases the check could pass vacuously, which is the defect P2 targets.

This is narrower than general hedge-fidelity enforcement (which stays deferred): it validates declared statements in repo-controlled files, not arbitrary sources.

**D6 — Speckit script convention.** The repository's `.specify/scripts/bash/check-prerequisites.sh` rejects the `development` branch (`ERROR: Not on a feature branch. Current branch: development`). `common.sh` honors the `SPECIFY_FEATURE` override, verified:

```
$ SPECIFY_FEATURE=003-report-preset-advisories bash .specify/scripts/bash/check-prerequisites.sh --json
{"FEATURE_DIR":"/Users/domattioli/Projects/structured-gist/specs/003-report-preset-advisories","AVAILABLE_DOCS":[]}
```

Every speckit helper invocation for this feature sets `SPECIFY_FEATURE=003-report-preset-advisories`. No branch rename.

**D7 — Rule count correction.** This plan previously said "16 rules". The true active count is **15**: `lint_outline.py` emits `R1, R2, R4–R16` (15 distinct ids; `R3: REMOVED` at `lint_outline.py:400`, and `R17` appears only in the reserved-identifier comment at `lint_outline.py:376`, never emitted). `SKILL.md:117` ("the same 15 rules"), `README.md:46`, `README.md:268` and `llms.txt:8` all already say 15 and are correct — no correction task is needed for them, only for this plan.

**D8 — `.specify/feature.json`.** The repoint from `001-backlog-hedge-fidelity` to `003-report-preset-advisories` is intentional and **ships with the feature** (it is how downstream speckit commands locate this feature). It is not reverted at the end.

## Project Structure

### Documentation (this feature)

```text
specs/003-report-preset-advisories/
├── spec.md
├── plan.md              # this file
├── tasks.md
└── checklists/
    ├── requirements.md
    └── advisory-quality.md
```

### Source (repository root)

```text
skills/structured-gist/
├── SKILL.md                     # 8 edit sites (D1) + version + description
├── CHANGELOG.md                 # NEW v0.5.0b1 entry
├── examples/report.md           # NEW — worked example + fidelity declaration
└── tests/
    ├── fidelity_check.py        # NEW test-only helper (D5)
    ├── fixtures/fidelity/hedge_dropped.md          # NEW negative fixture
    ├── fixtures/fidelity/relation_upgraded.md      # NEW negative fixture
    ├── fixtures/fidelity/declaration_malformed.md  # NEW negative fixture
    ├── test_lint.py             # NEW cases: lint the example + 5 fidelity cases
    └── benchmark.md             # NEW row for 0.5.0b1
plugins/structured-gist/.claude-plugin/plugin.json  # version bump
README.md                                           # version badge + preset note
llms.txt                                            # example index entry
```

**Structure Decision**: existing layout; no new directories beyond the spec folder.

## Verification strategy

Every task in `tasks.md` names its own success and failure check. Repo-wide gates re-run by the supervisor after implementation:

1. `python3 -m pytest skills/structured-gist/tests/ -q`
2. `bash skills/structured-gist/tests/smoke.sh`
3. `git diff --numstat -- skills/structured-gist/SKILL.md` — insertions 25–45 (version and description lines excluded).
4. `git diff --name-only` — `skills/structured-gist/tests/lint_outline.py` MUST be absent.
5. `git diff -- skills/structured-gist/tests/test_lint.py` — additions only; no pre-existing case modified.

## Out of scope

- Any linter rule change, rename, or renumber.
- General hedge-fidelity enforcement over arbitrary sources (stays deferred to the held backlog item); only the bounded declared-statement check of D5 ships here.
- The render-default mismatch between the repository agent instructions and `SKILL.md` (block vs responsive) — separately tracked.
- Downstream consumer repositories and any push, PR, or release step.
