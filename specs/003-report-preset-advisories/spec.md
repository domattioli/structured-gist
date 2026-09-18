# Feature Specification: Report preset + interrogative/hedge advisories

**Feature Branch**: `development` (spec directory `003-report-preset-advisories`; speckit helper scripts are run with `SPECIFY_FEATURE=003-report-preset-advisories`)
**Created**: 2026-09-18
**Status**: Draft
**Input**: User description: "Advisory doc-only edits to skills/structured-gist/SKILL.md (~25-40 lines, no linter code change): C1 taxonomy 'answers' extension + interrogatives-are-content-prompts rule; C2 advisory attribute-name lexicon; C3 hedge-preservation prose rule with enforcement deferred; C4 opt-in `/structured-gist report` preset (alias `findings`); C5 softened observed-vs-inferred advisory; M1 preset omission contract; M2 preserve source relation wording. Mandatory 5W1H/IMRaD skeleton rejected. Likely ancillary: version bump, frontmatter description/trigger update, benchmark row, examples/report.md, plugin manifest sync."

## Overview

`structured-gist` gives authors a fixed role ladder (concept → attribute → enumerator → explanation) but almost no guidance on *which* content belongs in which role, and no guidance at all for the most common non-recap document shape: a findings/report write-up. Authors currently guess. Two recurring guesses are wrong in ways the linter cannot see: they read interrogative words ("who/what/where/when/why/how") as if they selected a marker, and they strip or relocate a source's hedge when promoting a claim to a heading.

This feature adds **advisory prose** to the skill document plus **one new opt-in preset**. It changes no linter code and introduces no new required structure. A mandatory 5W1H or IMRaD section skeleton was considered and **rejected** — universal section spines conflict with dependency-driven nesting. Opt-in presets remain the sanctioned mechanism (precedent: the existing summary preset).

## Clarifications

### Session 2026-09-18

- Q1 (version) → **`0.5.0b1`** (minor + beta, PEP 440 string). All version-carrying sites carry exactly `0.5.0b1` (five of them — see FR-018). Anything that parses the version as strict semver must be identified rather than worked around by changing the string.
- Q2 (worked example) → **both**: a short inline skeleton in the skill document plus a thin standalone example file. Because the existing structural-check suite only checks two named example files, the new example must be added to that checked list.
- Q3 (preset-omission contract) → the contract **governs both presets** and sits immediately after the existing summary preset block; the summary preset's shape becomes omit-if-absent.
- Q4 (relation-wording rule) → placed **next to the inline-arrow rule**, with one additional line in the limitations section recording that it is not enforced.
- Q5 (hedge rule home) → a **new sibling section titled "Hedge preservation"** immediately after the existing leaf-preservation section. The leaf-preservation section is NOT renamed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Author a findings write-up with a preset (Priority: P1)

An author has investigation or evaluation results and wants a skimmable outline. They invoke `/structured-gist report` (or `findings`) and get a finding-first shape: each supported finding is its own top concept, with optional named branches for the question asked, the method used, what was observed, what was inferred, and what comes next. Nothing is required; unsupported branches are simply omitted, and multiple findings are allowed as peer concepts.

**Why this priority**: it is the only user-visible new capability; the other changes are guidance that makes this preset produce sound output.

**Independent Test**: invoke the preset on a short investigation source and confirm the output is finding-first, uses only source-supported branches, carries no generic Intro/Background/Conclusion heading, and lints cleanly under the existing rules.

**Acceptance Scenarios**:

1. **Given** a source establishing two independent findings, **When** the report preset is applied, **Then** the outline emits two peer top-level concepts, not one packaging root.
2. **Given** a source with no stated method, **When** the report preset is applied, **Then** no Method branch appears and no placeholder is invented.
3. **Given** the preset output, **When** it is checked against the ladder rules, **Then** enumerators under a `▸` branch use the lowercase family and Method itself is never an ordinal node.

---

### User Story 2 - Pick the right marker without interrogative folklore (Priority: P2)

An author reading the marker taxonomy sees what each role answers, including attribute and explanation, and reads an explicit statement that interrogative words are prompts for *content*, not selectors for a *marker*. They also get an advisory list of attribute names commonly supported by sources, with the traps called out.

**Why this priority**: it prevents the most common misuse of the new preset and of attributes generally, but the skill is usable without it.

**Independent Test**: read the taxonomy and attribute sections cold and answer "does 'why' mean I must use a specific marker?" — the document must answer no in its own text.

**Acceptance Scenarios**:

1. **Given** the revised taxonomy table, **When** a reader looks up attribute or explanation, **Then** each row states the question that role answers about its parent.
2. **Given** the advisory lexicon, **When** a reader looks for a confidence label, **Then** the document states that "whether" names a proposition to resolve and is not a confidence label, and that Scope and Trigger are separate names rather than catch-alls for every "where"/"when".
3. **Given** the advisory lexicon, **When** a source uses its own property names, **Then** the document tells the author to prefer the source's names and states the lexicon is advisory, not linter-enforced.

---

### User Story 3 - Do not lose the source's hedge or its relation wording (Priority: P2)

An author outlining a hedged source keeps the hedge attached to the claim it governs, rather than dropping it or hoisting the claim into an unqualified heading. The same fidelity rule covers relation wording: an association stated in the source is not upgraded to a causal arrow.

**Why this priority**: it is a correctness/fidelity rule with real downstream harm. General enforcement stays deferred, but this feature ships a bounded deterministic check over declared source statements so the rule can fail rather than only be asserted.

**Independent Test**: run the fidelity check over the shipped example and over a hedge-dropped negative fixture — zero violations on the former, at least one on the latter.

**Acceptance Scenarios**:

1. **Given** a hedged source claim, **When** it becomes a node, **Then** the rule requires the hedge to stay in the claim text or in an immediately attached explanation leaf.
2. **Given** a hedge whose scope is ambiguous, **When** the author considers a dedicated certainty branch, **Then** the rule permits that branch only when the hedge's scope is unambiguous.
3. **Given** the deferred enforcement, **When** a reader checks the limitations section, **Then** it states that structural linting alone cannot establish hedge retention or claim attachment, and names the held follow-up.

### Edge Cases

- A source establishes no finding at all → the preset must not manufacture one.
- A single finding with rich detail → still finding-first, no forced sibling padding.
- Skim granularity collapses detail → the hedge rule still applies to whatever survives.
- Method steps are genuinely unordered → the nominal enumerator family applies; Method stays a named branch, never an ordinal node.
- An author wants only a subset of branches → permitted by the shared preset-omission contract; the summary preset must not be read as contradicting it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The marker-taxonomy section MUST state, for the attribute and explanation roles, the question each answers about its parent, in the same form as the existing concept and enumerator rows.
- **FR-002**: The document MUST state that who/what/where/when/why/how/whether are content prompts and do not select a marker, and MUST point the reader back to the existing role criteria instead.
- **FR-003**: The attribute-versus-enumerator section MUST carry an advisory list of attribute names (purpose, mechanism, actor, location, timing, certainty) marked explicitly as optional and not linter-enforced.
- **FR-004**: That advisory MUST keep scope and trigger as distinct names and MUST state that "whether" names a proposition to resolve rather than a degree of confidence.
- **FR-005**: That advisory MUST instruct authors to prefer source-specific names and omit properties the source does not support.
- **FR-006**: A new section dedicated to hedge preservation, placed immediately after the existing leaf-preservation section and leaving that section's title unchanged, MUST require source hedges to stay with the claim they govern — in the claim text or an immediately attached explanation leaf — including in collapsed output.
- **FR-007**: The document MUST forbid turning a qualified source claim into an unqualified heading, and MUST allow a dedicated certainty branch only when the hedge's scope is unambiguous.
- **FR-008**: The limitations section MUST record that acceptance of the hedge rule requires source-versus-output comparison covering both retention and attachment, that structural linting cannot establish either, and that enforcement is deferred to the held follow-up item.
- **FR-009**: The activation section MUST document an opt-in preset invoked as `/structured-gist report` with the alias `findings`, presented as a peer of the existing summary preset.
- **FR-010**: The report preset MUST be finding-first: one top concept per supported finding, multiple findings permitted as peers, with no generic introduction, background, or conclusion headings. It MUST also state that a finding is never invented when the source establishes none.
- **FR-011**: The report preset MUST name its optional branches — question, method, observed, inferred, next — and MUST state that only source-supported branches are included. It MUST also state how parts nest under the method branch: ordered steps take the lowercase ordinal family, unordered components the lowercase nominal family, and the method branch is itself a named attribute, never an ordinal node.
- **FR-012**: The report preset MUST state that granularity and render mode apply unchanged and that the preset introduces no new marker roles.
- **FR-013**: The document MUST carry a shared preset-omission contract stating that presets supply optional branch names rather than required slots. It is placed immediately after the existing summary preset block and governs both presets, so the summary preset's shape is explicitly omit-if-absent.
- **FR-014**: The dependency-nesting section MUST carry a softened advisory: preserve an observation-versus-inference distinction the source makes, using separate branches only when grouping would blur status, without inferring evidential status from wording or manufacturing missing evidence.
- **FR-015**: The document MUST state, alongside the existing inline-arrow rule, that source relation wording is preserved — an association or an uncertain link is not rewritten as a causal arrow, and relation endpoints stay identifiable — with one line in the limitations section recording that this is not machine-enforced.
- **FR-016**: All added text MUST be advisory guidance only: no linter rule is added, renamed, or altered, and no existing required structure becomes optional or vice versa. Sole carve-out, authorized in Clarifications Q3: the summary preset's branch set becomes omit-if-absent. No other loosening is permitted.
- **FR-017**: The change MUST add both a short inline skeleton outline for the report preset in the skill document and a thin standalone example file for it; every illustrative outline added MUST satisfy the existing structural rules, and the new example file MUST be added to the set of example files the structural-check suite verifies.
- **FR-018**: The skill version MUST become exactly `0.5.0b1` at all five version-carrying surfaces — skill frontmatter, plugin manifest, README badge, changelog entry, benchmark row — which MUST agree after the change. If any consumer or check requires a strict three-part semantic version, that incompatibility MUST be reported rather than resolved by altering the chosen version string.
- **FR-019a**: The changelog MUST gain a `v0.5.0b1` entry in its existing per-version format, summarizing the added guidance, the preset, and the explicit absence of any rule-logic change.
- **FR-019**: The skill frontmatter description MUST mention the new preset and its alias. Any trigger phrase added MUST be a qualified form that includes the skill's own lexicon (for example a skill-name-plus-`report` form); the bare words `report` and `findings` MUST NOT be added as standalone triggers, because they occur constantly in ordinary speech.
- **FR-020**: A benchmark row MUST be added for the new version in the same column format and measurement convention as the row immediately above it, recording either a measured metric or an explicit no-measurement entry with rationale. No measurement may be fabricated.
- **FR-021**: Every pre-existing test MUST remain unmodified and MUST still pass; new test cases and new test-only helper modules are permitted additions.
- **FR-022**: The fidelity rules introduced by FR-006, FR-007, and FR-015 MUST be backed by a deterministic, model-free check that runs in the existing test suite. The check MUST first merge wrapped continuation lines back into the node they belong to, so a declared phrase split across a hard wrap is neither missed nor falsely reported. For a declared source statement it MUST report a violation when: (a) any declared field is missing or empty, or the declared hedge occurs inside the declared claim key — a declaration that would make the hedge check pass unconditionally; (b) the declared hedge, matched as a whole word rather than a substring, is absent from both the claim node and its immediately attached explanation leaf; (c) the declared association wording is absent, or the declared endpoints appear joined by a causal arrow in either order.
- **FR-023**: That check MUST be demonstrably capable of failing: one negative fixture per failure mode — hedge dropped, relation upgraded, declaration malformed — MUST exist, and a test MUST assert the check reports a violation on each. Those fixtures MUST additionally be asserted to pass the structural linter, so each proven failure is attributable to the fidelity property alone, and they MUST NOT be named with the prefix the repository already reserves for fixtures that are required to fail the linter.
- **FR-024**: The check MUST NOT modify or re-implement the existing linter; it is a separate test-only helper using the standard library only.
- **FR-025**: The example-listing surfaces that enumerate example files MUST be updated to include the new example: the machine-readable index file, and the skill document's own "more examples" pointer. The README activation section MUST note that opt-in presets exist and name them.
- **FR-027**: Every worked example shipped by this change MUST itself obey the rules the change introduces — it MUST NOT present any branch the declared source does not support, and it MUST NOT render a hedged source claim as an unhedged heading. This MUST be enforced by an exact comparison: the declaration names the branches the source supports, and the check reports a mismatch in either direction against the branches the outline actually carries. **Stated limit:** the declared branch list is author-supplied, so the check detects drift between the declaration and the outline — the failure mode that occurred twice here — but cannot detect a declaration that is itself dishonest. That residual sits at the same trust level as the declared source text and is recorded, not claimed as covered.
- **FR-026**: The plugin-manifest validation path used for the previous release MUST be re-run read-only against the new version string and its result reported verbatim. A rejection MUST be escalated for an operator decision with the version string left unchanged. **SATISFIED 2026-09-18 by an orchestrator-run validation, not by this session:** `claude plugin validate` passed from the repository root and from an unrelated working directory; validating the plugin directory passed with a symlink-not-read warning; a fully dereferenced copy passed with no warnings; and a local marketplace add, install, and `claude plugin details` reported `structured-gist 0.5.0b1`, Skills (1). The test install and marketplace entry were removed afterwards. The PEP 440 version string is therefore accepted by the real plugin loader and no operator decision is outstanding.

### Key Entities

Terminology is fixed here and used consistently throughout this feature's documents.

- **Preset**: a named opt-in invocation that suggests a branch vocabulary and an ordering principle; supplies optional names, never required slots. The two presets are referred to as the **summary preset** and the **report preset** (never "session-summary preset").
- **Advisory**: guidance prose in the skill document that shapes author judgement but is not machine-checked.
- **Hedge**: a source-stated qualification on a claim, such as a modal or an approximator. The term **hedge** is used throughout; "qualification" is not used as a separate concept.
- **Certainty branch**: the optional attribute branch that names degree of confidence. The term **certainty branch** is used throughout; "confidence branch" is not used.
- **Finding**: a claim the source actually establishes; the organizing unit of the report preset.
- **Fidelity check**: the deterministic test-only helper that verifies hedge attachment and relation-wording preservation against declared source statements.

## Success Criteria *(mandatory)*

- **SC-001**: A shipped example demonstrates the preset end to end: it exists, passes the structural check with zero violations, and shows at least two findings whose branch sets differ, proving branches are omitted rather than filled.
- **SC-002**: The statement that interrogative words do not select a marker is present in the marker-taxonomy section and retrievable by a literal text search of the skill document.
- **SC-003**: The fidelity check reports zero violations on the shipped example and at least one violation on each of three negative fixtures — hedge dropped, relation upgraded, declaration malformed — every one of which independently passes the structural linter, so the rule can be failed on the fidelity property alone and not merely asserted.
- **SC-004**: Every fenced outline in the changed skill document, the new example, and every fidelity fixture passes the structural linter **in file mode** with zero violations. File mode is required: the text-mode entry point skips the line-wrap rule, because merging continuation lines discards the physical-line widths that rule needs (`lint_outline.py:308-318`). A text-mode-only check reported these files clean while the file-mode linter reported real line-wrap violations.
- **SC-005**: Insertions into the skill document total 25–45 lines as reported by `git diff --numstat`, excluding the version and description lines, and no rule-enforcement code is added.
- **SC-006**: All pre-existing automated checks that passed before the change still pass after it, with no pre-existing test modified.

**Recorded limitations, not success criteria.** Whether an author's judgement actually improves — that the advisory lexicon leads to better attribute names, or that the observed-versus-inferred advisory is applied correctly on unseen sources — is not mechanically checkable and is recorded in the skill's limitations section rather than claimed as a met requirement. Only the checks above are claimed.

## Assumptions

- The skill document and the linter's rule set do not change behavior; the only executable additions are test-only (a fidelity-check helper, its fixtures, and new test cases).
- The rejected mandatory 5W1H/IMRaD skeleton is a settled decision and is not revisited here.
- General hedge-fidelity enforcement across arbitrary sources stays deferred to the existing held backlog item. This feature ships a bounded deterministic check over declared source statements in the shipped example and fixtures, which is narrower than that deferred work and does not close it.
- The `~25-40 lines` figure quoted in the Input line above is the original dispatch estimate. The budget was widened to 25–45 during planning because two items were added after that estimate: the inline preset skeleton (Clarifications Q2) and a whole new section rather than an appended paragraph (Clarifications Q5). SC-005 is authoritative.
- The summary preset keeps its canonical branch names, but per Clarifications Q3 those branches are omit-if-absent rather than required slots.
- Ancillary bookkeeping (version string, frontmatter trigger text, benchmark row, an example file, plugin metadata) rides along with the documentation change in the same unit of work.
- No downstream consumer repo files are touched by this feature.
