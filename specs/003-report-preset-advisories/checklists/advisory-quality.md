# Checklist: Advisory-guidance quality gate

**Purpose**: Verify the documentation change is advisory-only, internally consistent, and does not silently alter the enforced contract
**Created**: 2026-09-18
**Feature**: [spec.md](../spec.md) · **Plan**: [plan.md](../plan.md) · **Tasks**: [tasks.md](../tasks.md)

## Non-interference with the enforced contract

- [ ] CHK001 `skills/structured-gist/tests/lint_outline.py` is absent from `git diff --stat` (FR-016)
- [ ] CHK002 No rule identifier is added, renamed, or renumbered anywhere in `SKILL.md` (FR-016)
- [ ] CHK003 No added sentence asserts that the linter checks a newly added advisory (FR-003, FR-008, FR-015)
- [ ] CHK004 No existing required structure is made optional except the summary-preset omit-if-absent change explicitly authorized in Clarifications Q3 and carved out in FR-016 (FR-013, FR-016)
- [ ] CHK005 The role ladder and its four roles are unchanged (constitution P5, FR-012)

## Content correctness

- [ ] CHK006 Attribute and explanation rows each state the question that role answers about its parent (FR-001)
- [ ] CHK006a The explanation row's question covers qualifying and consequence leaves, not only why/how (FR-001)
- [ ] CHK007 The interrogative sentence says those words prompt content and do not select a marker (FR-002)
- [ ] CHK008 The lexicon lists all six names and is marked optional and unenforced (FR-003)
- [ ] CHK009 Scope and Trigger are kept distinct, and "whether" is stated to name a proposition, not a confidence level (FR-004)
- [ ] CHK010 Source-specific names are preferred and absent properties are omitted (FR-005)
- [ ] CHK011 The hedge rule requires claim-local retention or an immediately attached explanation, including in collapsed output (FR-006)
- [ ] CHK012 Promotion of a hedged claim to an unhedged heading is forbidden, and a certainty branch is allowed only when scope is unambiguous (FR-007)
- [ ] CHK013 Limitations record that structural linting establishes neither hedge retention nor claim attachment, and that general enforcement is deferred (FR-008)
- [ ] CHK014 Limitations record that relation-wording preservation is unenforced (FR-015)
- [ ] CHK015 The observed-versus-inferred advisory is conditional, not an absolute split requirement (FR-014)

## Preset

- [ ] CHK016 The preset is presented as opt-in, named with both `report` and the `findings` alias (FR-009)
- [ ] CHK017 Finding-first: one concept per supported finding, peers permitted, no generic Intro/Background/Conclusion heading (FR-010)
- [ ] CHK018 The five optional branches are named and stated to be included only when source-supported (FR-011)
- [ ] CHK018a Method nesting is stated: ordered steps lowercase ordinal, unordered components lowercase nominal, Method itself never an ordinal node (FR-011)
- [ ] CHK019 Granularity and render mode are stated to apply unchanged, with no new roles (FR-012)
- [ ] CHK020 The preset-omission contract sits after the summary preset block and names both presets (FR-013)
- [ ] CHK020a The preset block states that a finding is never invented when the source establishes none (FR-010)
- [ ] CHK020b The preset's bold lead line carries the exact label `(v0.5.0b1)` (tasks T004)
- [ ] CHK021 The inline skeleton uses the lowercase enumerator family beneath a `▸`, and `Method` is not an ordinal node (plan D2)

## Examples and coverage

- [ ] CHK022 `examples/report.md` exists, is synthetic, carries a machine-readable fidelity declaration, and contains no personal data or real identifiers (constitution P6, FR-017, FR-022)
- [ ] CHK023 Its two findings use different branch subsets, demonstrating omission (FR-017, tasks T009)
- [ ] CHK024 A test case lints `examples/report.md` and fails if violations appear (FR-017, tasks T012)
- [ ] CHK025 Every fenced block in `SKILL.md` still lints clean, and no fenced block has a physical line over 64 columns including indent (FR-017, SC-004)
- [ ] CHK025a `examples/report.md` and all fidelity fixtures pass the linter in **file mode**, not only text mode (SC-004)
- [ ] CHK025b The example presents no branch its declared source does not support — every branch, not only Inferred — and renders no hedged source claim as an unhedged heading (FR-027)
- [ ] CHK025e Each fixture's outline branches are all supported by that fixture's own declared source, enforced by an exact declared-branch-set comparison rather than a heuristic (FR-027)
- [ ] CHK025f New prose uses only the fixed vocabulary — hedge, certainty branch, summary preset — with no "qualified"/"qualification", "confidence branch" or "session-summary preset" in text added by this change (Key Entities)
- [ ] CHK025c The fidelity check merges wrapped continuation lines before matching, proven by a faithful wrapped case reading clean and a wrapped arrow-upgrade still violating (FR-022)
- [ ] CHK025d Shipped prose carries no drafting-process language (no "softened", no reference to drafts the reader never saw)

## Falsifiability (constitution P2)

- [ ] CHK022a The fidelity check exists as a stdlib-only, test-only helper that does not import or re-implement the linter (FR-022, FR-024)
- [ ] CHK022b It reports zero violations on the shipped example (FR-022, SC-003)
- [ ] CHK022c It reports at least one violation on each of the three negative fixtures — hedge dropped, relation upgraded, declaration malformed — proving it can fail (FR-023, SC-003)
- [ ] CHK022e All three negative fixtures lint clean, so each proven failure is attributable to the fidelity property and not to a structural violation (FR-023, N1)
- [ ] CHK022f The fixtures live in `tests/fixtures/fidelity/` and do not use the `bad_` prefix the repository reserves for fixtures required to fail the linter (FR-023, N1)
- [ ] CHK022g The hedge match is whole-word, not substring, and a declaration whose hedge token sits inside its claim key is itself reported as a violation (FR-022)
- [ ] CHK022h The relation check detects the endpoints joined by a causal arrow in either order (FR-022)
- [ ] CHK022d Every claim in the spec's Success Criteria is backed by a runnable check; unmeasurable judgement claims appear only under "Recorded limitations" (constitution P2)

## Bookkeeping

- [ ] CHK026 Exactly `0.5.0b1` appears at all five version surfaces — frontmatter, plugin manifest, README badge, changelog entry, benchmark row; no `0.4.12` remains outside `specs/**`, the changelog, and the benchmark ledger (FR-018, FR-019a)
- [ ] CHK027 Any strict-semver incompatibility found is reported and escalated, not fixed by altering the version string (FR-018, FR-026, Clarifications Q1)
- [ ] CHK027a The plugin-manifest validation path was exercised against the real loader and its result recorded — closed 2026-09-18 on orchestrator-run evidence, `0.5.0b1` accepted (FR-026)
- [ ] CHK028 The frontmatter description mentions the preset and its alias, stays a single line, and adds only qualified trigger phrases — never bare `report` or `findings` (FR-019)
- [ ] CHK029 A `v0.5.0b1` benchmark row exists with the column count and no-measurement convention of the row above it, and no fabricated measurement (FR-020)
- [ ] CHK029a A `v0.5.0b1` changelog entry exists in the file's existing format, appended without rewriting history (FR-019a)
- [ ] CHK029b `examples/report.md` is listed in the machine-readable index and in the skill document's "more examples" pointer, and the README names both opt-in presets (FR-025)
- [ ] CHK030 `pytest` and `smoke.sh` both pass with no pre-existing test modified (FR-021)

## Scope

- [ ] CHK031 The `SKILL.md` insertion count reported by `git diff --numstat` is 25–45 lines excluding the version and description lines (SC-005)
- [ ] CHK032 No file outside this repository is modified, and no commit, push, PR, or release step was performed. `skills/structured-gist/scripts/validate_plugin.sh` is expected-untracked (operator-directed, outside this feature) and is not a breach
- [ ] CHK033 The render-default mismatch between the repository agent instructions and `SKILL.md` remains untouched (plan, out of scope)
