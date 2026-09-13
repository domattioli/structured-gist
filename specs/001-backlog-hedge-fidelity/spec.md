# Feature Specification: Backlog Sweep — Hedge Fidelity, Benchmark Harness, Backlog Adjudication

**Feature Branch**: `001-backlog-hedge-fidelity`
**Created**: 2026-09-09
**Status**: Draft
**Input**: An adjudicated 11-step merged build order for the `structured-gist` open backlog (issues #1–#9), synthesized from two independent opus-tier reviews plus a reconciliation pass. The build order is settled; this spec encodes it.

## Clarifications

### Session 2026-09-09

- Q: Who has authority over the hedge-lexicon content (which words/phrases count as a hedge) used by the hedge-survival measure? → A: A free-tier delegate drafts the lexicon, grounded by scouting existing web references on epistemic-hedging taxonomies (linguistics literature on hedge markers, modal verbs, epistemic adverbs, approximators, evidential frames), and the supervising operator reviews/edits the drafted list before it is used to score anything.
- Q: What should happen if a GitHub write action (posting the #9 comment, filing the new issue, closing #8/#3) fails (rate-limit, auth, network)? → A: Retry once, then halt and report the specific failure to the operator — no silent skip, no fabricated success.
- Q: If the second corpus case (the phone/"Kiran" excerpt) is DROPPED by redaction review, does US3 fall back to a replacement candidate, or ship with fewer than three test cases? → A: No fallback — if dropped, the new issue ships with two test cases (registrar, deontic) and records that the third was dropped and why.
- Q: FR-018a distinguishes an attribute node that "carries an assertion" (produces a claim record) from a "bare label" (does not) — what is the actual test? → A: Structural, no model judge: an attribute node counts as an assertion iff its own text contains a verb/predicate, OR it has a non-summary `↪` child, in which case that child's content becomes the record instead of the attribute's own text.
- Q: FR-024a's split-precision labelling — who labels sampled leaves, and what happens on an uncertain leaf? → A: Single free-tier labeller; a third "ambiguous" bucket is allowed, and ambiguous leaves count as incorrect (the rule gets no credit for cases nobody is sure about).
- Q: The judged `caveat_attach_accuracy` measure (FR-008) needs a judge model — which tier, and does it see source + output side-by-side or output only? → A: Sonnet judges (escalated from haiku — attachment judgment is subtler than a mechanical check), seeing the source excerpt and rendered output side-by-side per claim.
- Q: Should the hedge lexicon cite the web references it draws vocabulary from? → A: Yes, per entry or per cluster of entries, including a URL to the source, so a later session can trace any lexicon entry back to where it came from.
- Q: FR-005 requires the new issue be "implementable from its own text without reference to this spec" — who verifies that, and how? → A: A fresh-context agent with no prior exposure to this spec/session reads only the filed issue text and confirms it is buildable cold; if not, the issue is revised before filing, not after.
- Q: If T017's decision gate rules that a US1 regression delta is R16 over-firing (rather than a previously-mis-passing fixture), is fixing R16 in scope for this spec? → A: Yes, in scope — fix R16 and re-run the regression sweep until zero deltas; US1 is not done until it does.
- Q: This repo's CONTRIBUTING.md states "one rule, one PR" and treats a lint-rule change and a docs fix as two PRs, not one — should this backlog's implementation be one PR or split along that convention? → A: One PR for the whole backlog. Operator overrides CONTRIBUTING.md's stated convention for this bounded-backlog effort specifically.
- Q: spec.md declares `Feature Branch: 001-backlog-hedge-fidelity` but no such branch exists — planning artifacts are untracked on `main`. Create the branch now, or treat the header as unused and commit to `main`? → A: Create the branch now; move `.specify/` and `specs/` onto it; implementation and the eventual single PR happen from that branch.
- Q: CONTRIBUTING.md requires a `SKILL.md` version bump + a real-measured `tests/benchmark.md` row for any behavior change — is that in scope for this backlog (US1/US6/US8 all change behavior)? → A: In scope — version bump(s) and benchmark row(s) for US1, US6, and US8 land as part of this backlog's implementation, not deferred.
- Q: FR-014 requires the judged lane be reachable "only by manual invocation," never a CI gate — what is the actual mechanism? → A: Two separate scripts, `run_deterministic.sh` (CI-safe) and `run_judged.sh` (manual-only, never referenced by any CI workflow file), so the property is structurally enforced rather than flag/env-var-gated.
- Q: FR-006's `epistemic` category + `attaches_to` field must apply "consistently across" the per-case gold-set files — migration script, or manual per-file edits? → A: A migration script adds the schema shape to every existing gold.json case file programmatically; new cases are authored with it present from the start.

## Scope Statement *(binding)*

This is a **bounded backlog implementation**, not a new feature built from scratch. Scope is exactly the eleven ordered steps below and nothing else. Each step maps to one user story. Work that is not traceable to one of these eleven steps is out of scope for this spec, including: implementing the JSONL-primary intermediate representation (explicitly deferred), building a pptx render target (explicitly closed), and enforcing the comma-split rule unconditionally (gated behind a measurement).

The eleven steps, in build order:

1. Fix issue #6 — enum/explain children rendered flush with their parent attribute marker; add the missing depth-indent lint rule.
2. Comment on issue #9 with the registrar hedge counterexample; mark error-promotion blocked pending hedge detection.
3. File a new issue establishing a hedge/qualifier fidelity axis (gold-set category, two new metrics, three test cases).
4. Rebuild the benchmark harness (issue #5) with pinned model and prompt hashes, a judged-result cache, and a split CI lane.
5. Add a README before/after worked example driven by the registrar case, generated by the harness.
6. Implement issue #2 option A — a JSONL claim-list render target derived from the outline tree; state option B as a future endgame.
7. Run the issue #4 comparison — structured-gist alone vs. structured-gist plus caveman-lite — at a matched token budget, including hedge survival.
8. Promote the issue #9 comma-split rule from warn-only to enforced, but only if a precision threshold is met.
9. Resolve issue #1 by computing a rank correlation on existing results and either adding a column or closing as duplicate.
10. Close issue #8 as framed; fold its content into the step-3 deontic-modality test case.
11. Close or defer issue #3 (pptx render target) with stated reasoning.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Depth-indent lint rule closes the flush-child gap (Priority: P1)

A skill author writes an outline where enumerator or explanation children sit at the same indentation column as their parent attribute marker. The tree looks nested to the author but carries no depth signal, so the role ladder is not actually expressed. Today the linter accepts this. After this story, the linter rejects it by name.

**Why this priority**: It is the smallest change with the clearest failure mode, it touches only the existing depth calculation, and it is a prerequisite for trusting any outline the later benchmark work produces.

**Independent Test**: Run the linter over the existing fixture corpus and over new good/bad fixtures for the new rule. The rule fires on every bad fixture and on no good fixture.

**Acceptance Scenarios**:

1. **Given** an outline whose enumerator child is indented at the same column as its parent attribute marker, **When** the linter runs, **Then** it reports the new depth-indent violation identifying the offending line.
2. **Given** an outline whose explanation child is indented at the same column as its parent attribute marker, **When** the linter runs, **Then** it reports the same violation.
3. **Given** every existing fixture already in the repository, **When** the linter runs with the new rule enabled, **Then** no previously-passing fixture newly fails and no previously-failing fixture newly passes.
4. **Given** the eight existing semantic-compression benchmark cases, **When** the new rule is evaluated against them, **Then** it produces zero false negatives and zero false positives.

---

### User Story 2 — Issue #9 records why error-promotion is blocked (Priority: P1)

A future reader of issue #9 needs to know that promoting the comma-split rule to an error is not merely unfinished but blocked on a specific missing capability, and needs to see the concrete case that blocks it.

**Why this priority**: It prevents a later session from promoting the rule on incomplete evidence. It costs one comment and unblocks nothing else, so it goes early.

**Independent Test**: Read issue #9. The counterexample and the blocked status are both present and self-contained.

**Acceptance Scenarios**:

1. **Given** the registrar counterexample drawn from the conversation corpus, **When** it is posted to issue #9, **Then** the comment states plainly that error-promotion is blocked pending hedge detection.
2. **Given** the counterexample originates in a conversation corpus, **When** it is prepared for posting, **Then** it has passed an explicit redaction review and contains no personal data.

---

### User Story 3 — A hedge/qualifier fidelity axis exists as a tracked work item (Priority: P1)

The project can currently score whether facts survive compression but cannot score whether the epistemic status of those facts survives. A hedged claim compressed into a bare assertion scores as a perfect retention today. This story files the issue that defines the missing axis.

**Why this priority**: Three later steps depend on the definitions this issue establishes — the metric used in step 7, the gate in step 8, and the worked example in step 5.

**Independent Test**: Read the filed issue. A reader who has never seen this spec can implement the gold-set change, both metrics, and the three test cases from the issue text alone.

**Acceptance Scenarios**:

1. **Given** the new issue, **When** a reader looks for the gold-set change, **Then** it specifies an `epistemic` category weighted equal to the existing `negation` category, and an `attaches_to` field binding a qualifier to the claim it modifies.
2. **Given** the new issue, **When** a reader looks for the metrics, **Then** it defines a deterministic, source-aware hedge-survival measure that needs no model judge and can ship before the harness rebuild, and separately a judged caveat-attachment measure.
3. **Given** the new issue, **When** a reader looks for test cases, **Then** three corpus-sourced cases are named: the registrar case; a second case included only if it survives redaction review; and a deontic-modality case that absorbs the reframed content of issue #8.
4. **Given** any corpus excerpt destined for the issue, **When** it is written down anywhere, **Then** it has passed redaction review first.

---

### User Story 4 — The benchmark harness is reproducible and cheap to run (Priority: P1)

Someone rerunning a benchmark today cannot reproduce a prior number because the model and prompt that produced it were not recorded, and every rerun re-pays for judged evaluation. After this story a rerun is reproducible and the free half of it runs automatically.

**Why this priority**: Steps 5, 7, 8, and 9 all consume harness output. Without it those steps produce numbers nobody can reproduce.

**Independent Test**: Run the suite twice on unchanged inputs. Deterministic results are identical; judged results are served from cache with no new model calls on the second run.

**Acceptance Scenarios**:

1. **Given** a completed run, **When** its results are inspected, **Then** the model identifier and a hash of the prompt content are recorded alongside the numbers.
2. **Given** a run whose inputs are byte-identical to a previous run, **When** the suite is invoked again, **Then** judged results resolve from a content-addressed cache rather than issuing new model calls.
3. **Given** continuous integration, **When** it runs the suite, **Then** only deterministic checks execute and no model cost is incurred; judged checks are reachable only by manual invocation.
4. **Given** a changed prompt or a changed model, **When** the suite runs, **Then** the cache misses and the change is visible in the recorded hashes.

---

### User Story 5 — The README shows a real before/after that motivates the work (Priority: P2)

A reader arriving at the README sees a worked example in which a hedge is preserved on an attribute node while the alternatives it qualifies appear as enumerator children beneath it, demonstrating what the fidelity axis buys.

**Why this priority**: It is the public payoff of steps 1–4 and depends on all of them, but nothing downstream depends on it.

**Independent Test**: Regenerate the example with the harness and diff against the committed README block; they match.

**Acceptance Scenarios**:

1. **Given** the example in the README, **When** its provenance is checked, **Then** it was produced by the harness rather than composed by hand.
2. **Given** the registrar source material, **When** the example is built, **Then** the full source message is examined, not only the truncated corpus window.
3. **Given** the example text, **When** it is committed, **Then** it has passed redaction review.
4. **Given** the rendered example, **When** its structure is read, **Then** the hedge sits on an attribute node and the qualified candidates are enumerator children beneath that node.

---

### User Story 6 — Outlines can be emitted as a machine-readable claim list (Priority: P2)

A consumer that wants claims rather than a rendered outline can obtain one record per claim, carrying the claim text, its modality, its polarity, the span of source it came from, and its parent in the tree.

**Why this priority**: It is the first render target beyond text and enables downstream tooling, but no other step in this backlog depends on it.

**Independent Test**: Render a known outline to the claim list and validate every record against the published schema.

**Acceptance Scenarios**:

1. **Given** an outline tree, **When** the claim-list target renders it, **Then** the output is one record per claim carrying claim text, modality, polarity, source span, and parent identifier.
2. **Given** any produced claim list, **When** it is validated, **Then** every record conforms to a published schema and validation is automated.
3. **Given** the claim list, **When** its relationship to the outline is described, **Then** it is documented as a derived view of the existing tree, not a replacement for it.
4. **Given** the alternative design in which the claim list is the primary internal representation, **When** the documentation is read, **Then** that design is recorded as a stated future endgame and explicitly not built now.

---

### User Story 7 — The caveman-lite comparison is run fairly and its prediction tested (Priority: P2)

The project needs to know whether pairing structured-gist with caveman-lite helps or hurts, measured without the confound of the two conditions spending different token budgets.

**Why this priority**: It answers a standing question and supplies evidence for step 8, but it depends on the harness and the hedge metric first.

**Independent Test**: Inspect both conditions' token counts; they are within the stated tolerance. Inspect the recorded prediction; it was written before the results.

**Acceptance Scenarios**:

1. **Given** the two conditions, **When** their token budgets are compared, **Then** they are matched within five percent, and a naive unmatched comparison is not reported as the result.
2. **Given** the run, **When** its metrics are reported, **Then** hedge survival is among them.
3. **Given** the experiment record, **When** it is read, **Then** the prediction that the paired condition retains hedging markedly worse than structured-gist alone is stated before the outcome, with the reason that compression rules delete hedging language by design.
4. **Given** the results, **When** the write-up concludes, **Then** it explicitly confirms or refutes that prediction rather than leaving it open.

---

### User Story 8 — The comma-split rule is promoted only on evidence (Priority: P3)

The comma-split rule proposed in issue #9 is not yet in the linter, and the linter today has no warn severity — every rule is a hard violation. Step 8's two outcomes both presuppose a warn-only rule exists: it becomes enforced only if it is precise enough on real material; otherwise it lands and stays warn-only indefinitely, and that outcome is recorded as a decision, not a failure.

**Why this priority**: It is the last gate in the chain and depends on steps 3, 4, and 7 having landed.

**Independent Test**: Compute split precision on corpus-sampled leaf nodes and compare against the threshold; the resulting rule severity matches the measured value.

**Acceptance Scenarios**:

1. **Given** measured split precision of at least 0.98 on corpus-sampled leaves, **When** the decision is applied, **Then** the rule is promoted to enforced.
2. **Given** measured split precision below 0.98, **When** the decision is applied, **Then** the rule remains warn-only with no expiry date attached, and the measurement is recorded.
3. **Given** steps 3, 4, or 7 not yet landed, **When** promotion is considered, **Then** it does not proceed.

---

### User Story 9 — Issue #1 is settled by a correlation, not an opinion (Priority: P3)

Whether the existing weighted-retention score already captures what an SCU-recall column would add is decided by measuring the rank correlation between them on results that already exist.

**Why this priority**: Cheap, self-contained, and needs only existing benchmark output.

**Independent Test**: The computed correlation coefficient is recorded, and the action taken matches the branch that value selects.

**Acceptance Scenarios**:

1. **Given** the eight existing benchmark results, **When** the rank correlation between SCU-recall and weighted retention is computed, **Then** the coefficient is recorded with the data it was computed from.
2. **Given** a coefficient below 0.8, **When** the branch is taken, **Then** an SCU-recall column is added to the scoring combiner.
3. **Given** a coefficient at or above 0.8, **When** the branch is taken, **Then** issue #1 is closed as duplicative of the existing scorer, citing the coefficient.

---

### User Story 10 — Issue #8 is reframed rather than left ambiguous (Priority: P3)

Issue #8 as written proposes migrating the skill definition into the skill's own format. That framing is closed; the part of it worth keeping becomes a test case.

**Why this priority**: Bookkeeping that removes a misleading open item.

**Independent Test**: Issue #8 is closed with stated reasoning, and the deontic-modality test case named in step 3 exists.

**Acceptance Scenarios**:

1. **Given** issue #8, **When** it is closed, **Then** the closure states that the original framing is being retired and names where its useful content went.
2. **Given** the step-3 issue, **When** it is read, **Then** the deontic-modality test case is present and traceable back to issue #8.

---

### User Story 11 — Issue #3 is deferred with reasons on the record (Priority: P3)

The pptx render target is not built. The reasoning is written down so the decision does not have to be rediscovered.

**Why this priority**: Bookkeeping; nothing depends on it.

**Independent Test**: Issue #3 is closed or deferred and the closing text contains all three stated reasons and the reopening condition.

**Acceptance Scenarios**:

1. **Given** issue #3, **When** it is closed or deferred, **Then** the reasoning names that a ladder-to-slide mapping is lossy, that no falsifiable success metric exists for it, and that it would add a binary dependency to a dependency-free skill.
2. **Given** the closure, **When** a future reader considers reviving it, **Then** the stated condition for reopening is demonstrated demand.

### Edge Cases

- What happens when a corpus excerpt cannot be redacted without destroying the property it illustrates? It is dropped and the affected test case is not created; the second step-3 test case is conditional on exactly this.
- What happens when the harness is asked for a judged result and no cache entry exists in a context where model calls are unavailable? The judged lane reports unavailable rather than substituting a deterministic proxy.
- What happens when the new depth-indent rule conflicts with an existing rule on the same line? Both findings are reported; the new rule does not suppress or subsume an existing one.
- What happens when the step-9 correlation lands near the threshold — that is, 0.75 <= rho < 0.85? The branch is still decided by the recorded coefficient against the 0.8 cutoff, and the closing text explicitly notes the reading was borderline at n=8.
- What happens when the two conditions in step 7 cannot be brought within the token tolerance? The comparison is not reported as a result; the mismatch is recorded instead.
- What happens when a GitHub write (the #9 comment, the new-issue filing, closing #8 or #3) fails? It is retried once; if the retry also fails, the affected step halts and reports the specific failure rather than being silently skipped or reported as done.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The linter MUST report a violation when an enumerator or explanation node is not indented deeper than its parent attribute node, using the existing per-line depth determination as the basis for the check. The new rule MUST be additive: it MUST NOT suppress, subsume, or reorder findings from any existing rule reported on the same line.
- **FR-002**: Introducing the new rule MUST NOT change the lint outcome of any existing fixture or of any rendering in the eight existing semantic-compression benchmark cases, except where a changed outcome is adjudicated and recorded as a previously-missed genuine violation. This is the measurable form of the build order's zero-false-positive, zero-false-negative requirement: no labelled expected-violation set exists for those cases, so the delta against current behavior is the observable. If a delta is instead adjudicated as the new rule over-firing, fixing the rule so the regression sweep shows zero deltas is in scope for this spec; User Story 1 is not complete until it does.
- **FR-003**: The new rule MUST ship with both a passing and a failing fixture following the repository's existing fixture-naming convention, and MUST be covered by the existing test invocation.
- **FR-003a**: Rule identifiers MUST be unique. Both the depth-indent rule (step 1) and the comma-split rule (step 8) have been proposed as "R16" in separate issues; the delivered work MUST assign each a distinct identifier and record which issue owns which.
- **FR-004**: A comment MUST be posted to issue #9 presenting the registrar hedge counterexample and declaring error-promotion blocked pending hedge detection.
- **FR-005**: A new issue MUST be filed defining the hedge/qualifier fidelity axis, and MUST be implementable from its own text without reference to this spec. Before filing, a fresh-context agent with no prior exposure to this spec or session MUST read only the drafted issue text and confirm it is buildable cold; if it is not, the issue MUST be revised and re-checked before filing, not after.
- **FR-006**: The new issue MUST specify a gold-set `epistemic` category carrying the same weight as the existing `negation` category (weight 3), and an `attaches_to` field binding a qualifier to the claim it modifies. Gold sets are per-case files, so the change MUST be specified once and applied consistently across cases rather than to a single shared file. Application to the existing eight case files MUST be performed by a migration script, not by hand-editing each file, so the added shape is structurally identical across every case; the new cases from step 3 are authored with the fields present from the start.
- **FR-007**: The new issue MUST define a hedge-survival measure that is deterministic, source-aware, requires no model judge, and is shippable ahead of the harness rebuild.
- **FR-007a**: The hedge lexicon underlying the hedge-survival measure MUST be drafted by scouting existing published references on epistemic-hedging taxonomies (e.g. linguistics literature on hedge markers, modal verbs, epistemic adverbs, approximators, evidential frames) rather than invented from scratch, and MUST be reviewed and edited by the supervising operator before it is used to score any case. The lexicon file MUST record which entries came from which reference and which were added or removed by operator review. Each cited reference MUST include a URL, recorded per entry or per cluster of entries sharing a source, so any lexicon entry is traceable back to where it came from.
- **FR-008**: The new issue MUST define a separate caveat-attachment measure that is model-judged. Judging MUST be performed at sonnet tier (escalated from the harness's default haiku/free-tier — attachment correctness is judgment work, not a mechanical check), with the judge shown the source excerpt and the rendered output side-by-side per claim, never the output alone.
- **FR-009**: The new issue MUST name three test cases: the registrar case; a second corpus case included only if it clears redaction review; and a deontic-modality case carrying the reframed content of issue #8.
- **FR-009a**: If the second corpus case is DROPPED by redaction review, no replacement candidate is sought. The new issue proceeds with two test cases and MUST record that a third was attempted and dropped, and why.
- **FR-010**: Every corpus-derived excerpt MUST pass an explicit redaction review before being written to any file, issue, comment, fixture, or benchmark input tracked by the repository. This applies to steps 2, 3, and 5 without exception. The review is ordered strictly **extract → review → write**: an excerpt MUST NOT be written to a repository-tracked path in order to be reviewed.
- **FR-010a**: Extraction and review MUST happen in a staging buffer outside the repository working tree (the session scratchpad). The staging buffer is the single carve-out from FR-010 and MUST NOT be committed, MUST NOT live under `skills/` or `specs/`, and MUST be discarded once verdicts are recorded. Only the verdict record — excerpt identifier, verdict, and approved text where the verdict permits — is written into the repository.
- **FR-010b**: The review MUST yield exactly one of three verdicts per excerpt: APPROVED (usable verbatim), APPROVED-WITH-EDITS (usable only in the recorded redacted form), or DROPPED (not usable anywhere). A DROPPED excerpt MUST NOT appear in any repository file, issue, or comment, in whole or paraphrased. The reviewing authority is the supervising operator session; the review MUST NOT be delegated to an implementation-tier agent.
- **FR-010c**: Personal data, for the purpose of FR-010, means: personal names, usernames and handles, email addresses, phone numbers, postal addresses, account, student, patient or record identifiers, URLs and file paths containing any of the foregoing, employer or institution names identifying an individual, and dates specific enough to identify an individual in context. Any repository-wide scan asserting SC-010 MUST cover this enumerated set.
- **FR-011**: The benchmark harness MUST be invocable both as a shell entry point and as a Python entry point over the same suite definition.
- **FR-012**: Each harness run MUST record the identity of the model used and a hash of the prompt used, alongside its results.
- **FR-013**: Judged results MUST be cached and addressed by the content that produced them, so that an unchanged input resolves without a new model call and a changed input misses.
- **FR-014**: The harness MUST separate a deterministic lane from a judged lane. The deterministic lane MUST be runnable in continuous integration at no model cost; the judged lane MUST require manual invocation and MUST NOT run as a CI gate. When a judged result is requested, no cache entry exists, and model calls are unavailable, the harness MUST report the result as unavailable and MUST NOT substitute a deterministic proxy. The two lanes MUST be implemented as two separate entry-point scripts (`run_deterministic.sh`, `run_judged.sh`); no CI workflow file MUST reference `run_judged.sh`, so the manual-only property is structural rather than flag- or env-var-gated.
- **FR-015**: The README MUST contain a before/after example built from the registrar case, in which the hedge is carried on an attribute node and the qualified candidates appear as enumerator children beneath it.
- **FR-016**: The README example MUST be generated by the harness and MUST be regenerable; a hand-typed example does not satisfy this requirement.
- **FR-017**: The README example MUST be derived from the complete source message, not from the truncated corpus window alone.
- **FR-018**: A claim-list render target MUST emit JSON Lines — one JSON object per line, one line per claim — each containing the claim text, its modality, its polarity, the source span it came from, and its parent identifier.
- **FR-018a**: A claim, for this target, is a node that asserts something: explanation nodes (the prose leaves) and enumerator nodes always produce a record; attribute nodes produce a record only when they carry an assertion rather than a bare label; concept nodes never produce a record. The assertion-vs-bare-label test MUST be structural and require no model judge: an attribute node's own text is an assertion iff it contains a verb/predicate; if the attribute instead has a non-summary `↪` child, that child's content is the record emitted in the attribute's place, not the attribute's own text; an attribute node satisfying neither condition produces no record. `source_span` MUST be a character-offset pair into the source document, paired with the quoted text at that span so a record remains checkable if the source is re-indexed. `parent_id` MUST identify the emitting node's parent in the outline tree and MUST be stable across re-renders of an unchanged outline.
- **FR-018b**: The legal values of `modality` and `polarity` MUST be enumerated in the published schema before the renderer is implemented; the renderer MUST reject a value outside the enumeration rather than emitting it.
- **FR-019**: The claim-list output MUST be validated against a published schema, and that validation MUST be automated.
- **FR-020**: The claim-list target MUST be implemented as a derived view of the existing outline tree; the design in which the claim list is the primary internal representation MUST be documented as a future endgame and MUST NOT be implemented under this spec.
- **FR-021**: The comparison of structured-gist alone against structured-gist paired with caveman-lite MUST hold the token budget of the two conditions within five percent of each other. Token budget means output tokens of the rendered result, counted by a single recorded tokenizer applied identically to both conditions, compared per case rather than only in aggregate; the tokenizer identity MUST be recorded with the result.
- **FR-022**: That comparison MUST report the hedge-survival measure among its metrics. This presupposes the deterministic hedge-survival measure defined under step 3 is implemented before step 7 runs; implementing the judged caveat-attachment measure is NOT required by this spec (it is defined in the step-3 issue and tracked there).
- **FR-023**: The comparison MUST record, before results are known, a numerically falsifiable prediction with its stated reason, and MUST conclude by confirming or refuting it against that number. The prediction is: the paired condition's `hedge_survival_rate` is at least 0.15 lower in absolute terms than structured-gist alone, measured on the same cases at the matched token budget. The stated reason is that caveman's compression rules delete hedging language by design. A measured gap below 0.15, or a gap in the opposite direction, REFUTES the prediction and MUST be recorded as such.
- **FR-024**: The comma-split rule MUST be promoted from warn-only to enforced only when its split precision on corpus-sampled leaf nodes is at least 0.98; otherwise it MUST remain warn-only with no expiry. The measurement MUST be recorded together with the sample size and the set of leaves sampled.
- **FR-024a**: A rule firing counts as correct when the flagged leaf does in fact contain three or more coordinate list items that the role ladder would express as sibling enumerator nodes, and incorrect otherwise — including commas inside quotations, inline code, parentheticals, and appositives. The labelling criterion MUST be written down before any leaf is labelled, and each labelled leaf MUST record its label and the reason. A single free-tier labeller labels each sampled leaf; a third "ambiguous" bucket is permitted for leaves the labeller cannot confidently classify, and an ambiguous leaf MUST be counted as incorrect in the split-precision computation.
- **FR-024b**: The sample MUST be drawn from explanation leaves across the whole benchmark corpus, selected by a recorded deterministic procedure (for example, a seeded random draw over all leaves the rule fires on), with the population, the seed, and the sample size recorded. The sample MUST be large enough that the observed precision distinguishes 0.98 from 0.95; if it is not, the promotion decision MUST be deferred rather than taken on an underpowered sample.
- **FR-025**: Promotion MUST NOT proceed before the step-3 issue, the harness rebuild, and the paired comparison have landed.
- **FR-026**: The Spearman rank correlation between SCU-recall and weighted retention MUST be computed and recorded. It MUST be computed over a frozen snapshot of the eight benchmark cases that exist before any new case is added by step 3, so that adding a ninth case does not silently change the baseline. The recorded output MUST state n=8, name the snapshot it used, and note that a correlation at n=8 is low-powered.
- **FR-026a**: SCU-recall, for the purpose of FR-026, is the unweighted fraction of gold facts recorded as retained (partial counting as one half), computed from the same per-case gold fact lists the existing scorer uses. Because this is close by construction to the existing unweighted-retention dimension, the recorded output MUST state the definition used, so a high correlation is interpreted against a stated definition rather than an accidental one.
- **FR-027**: If that correlation is below 0.8 (the build order's "~0.8", pinned here so the branch is decidable), an SCU-recall column MUST be added to the scoring combiner; otherwise issue #1 MUST be closed as duplicative of the existing scorer, citing the measured value.
- **FR-028**: Issue #8 MUST be closed as originally framed, with its closure naming where its useful content was folded.
- **FR-029**: Issue #3 MUST be closed or deferred with reasoning that names the lossy ladder-to-slide remapping, the absence of a falsifiable success metric, and the added binary dependency to a dependency-free skill, and MUST state demonstrated demand as the condition for reopening.
- **FR-030**: The eleven steps MUST be executed in the stated order where a dependency exists; specifically the harness precedes the README example, the paired comparison, and the promotion decision, the step-3 issue precedes the paired comparison and the promotion decision, and the step-2 redaction verdict precedes the step-3 issue. No other ordering edge is implied: steps 1, 6, 9, and 11 have no predecessors.
- **FR-030a**: The implementation MUST land as a single pull request covering the whole backlog. This is an explicit operator override of this repository's own CONTRIBUTING.md convention ("one rule, one PR") for this bounded-backlog effort specifically; it does not change that convention for any other work.
- **FR-030b**: The implementation MUST bump `skills/structured-gist/SKILL.md`'s `version:` frontmatter and add a corresponding row to `skills/structured-gist/tests/benchmark.md` with a real measured number, for each of User Stories 1, 6, and 8 (each changes linter or render behavior), per this repository's own CONTRIBUTING.md convention. This is in addition to, not instead of, the harness-level recording required by FR-012.

### Key Entities

- **Depth-indent rule**: A linter rule asserting that a child node's indentation is strictly greater than its parent attribute node's, expressed over the existing depth determination.
- **Epistemic category**: A gold-set fact category for hedges and qualifiers, weighted as a peer of the negation category.
- **`attaches_to` binding**: A field on a gold-set entry naming the claim a qualifier modifies, so a surviving hedge attached to the wrong claim is distinguishable from a correctly attached one.
- **Hedge-survival measure**: A deterministic, source-aware comparison of qualifiers present in the source against qualifiers present in the rendered output.
- **Caveat-attachment measure**: A judged measure of whether a surviving qualifier remained bound to the claim it originally modified.
- **Benchmark run record**: The results of one suite invocation together with the model identity and prompt hash that produced them.
- **Judged-result cache**: A content-addressed store mapping a judged input to its recorded verdict.
- **Claim record**: One claim rendered as claim text, modality, polarity, source span, and parent identifier.
- **Split precision**: The proportion of comma-split rule firings on corpus-sampled leaves that are correct.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The depth-indent rule reports zero false positives and zero false negatives across the eight existing benchmark cases, and no existing fixture changes outcome.
- **SC-002**: Rerunning the full suite on unchanged inputs issues zero new judged model calls and reproduces every deterministic number exactly. This holds because renderings are committed inputs checked into each case directory, not generated per run; the harness MUST NOT generate renderings as part of a scored run.
- **SC-003**: Continuous integration runs the deterministic lane at zero model cost on every change.
- **SC-004**: The README example can be regenerated by a reader from the harness and matches the committed text.
- **SC-005**: Every claim-list record produced from the fixture corpus validates against the published schema, with zero validation failures.
- **SC-006**: The two conditions in the paired comparison differ in token budget by no more than five percent.
- **SC-007**: The stated hedge-survival prediction is recorded with its 0.15 absolute-gap threshold before results are known, and afterward is marked confirmed or refuted by comparing the measured gap against that threshold.
- **SC-008**: The comma-split severity in effect after this work matches the branch selected by the measured split precision against the 0.98 threshold.
- **SC-009**: The SCU-recall correlation coefficient is recorded and the action taken on issue #1 matches the branch that value selects.
- **SC-010**: Issues #1, #3, #6, #8, and #9 each reach a recorded terminal state — closed, resolved, or explicitly deferred with reasons — and no corpus excerpt anywhere in the delivered work contains personal data.

## Assumptions

- The eleven-step build order is already adjudicated; this spec encodes it and does not revisit its reasoning.
- The registrar counterexample and any second corpus case exist in the referenced conversation corpus and are reachable in full, not only as truncated windows.
- The existing eight semantic-compression benchmark cases and their weighted-retention results are usable as-is as input to steps 1, 7, and 9.
- Model access for the judged lane exists for manual invocation but is not available to continuous integration.
- The linter has no comma-split rule and no warn/error severity tier today (rules R1–R15, R3 removed, all hard violations). Step 8's "warn-only" outcome therefore requires the rule to land with a warn severity; this spec treats that as part of step 8, not a new step.
- The skill remains dependency-free at runtime; harness and test tooling may use additional packages only where they are not required to use the skill itself.
- Steps 2, 3, 10, and 11 are GitHub bookkeeping actions on the `domattioli/structured-gist` repository and require write access to its issues.
- Implementation of this spec is supervised by the operating session; this document and its siblings are planning artifacts only.

**Consequences if an assumption fails.** If the full registrar source message is not reachable, FR-015 through FR-017 and all of US5 are void and step 5 is deferred rather than approximated from the truncated window. If judged model access is unavailable even manually, US7 cannot be completed and steps 7 and 8 defer. If an excerpt is DROPPED in review, the test case it would have supported is not created and the omission is recorded. If the existing eight benchmark results prove unusable, steps 1, 7, and 9 defer rather than proceeding on substituted data.
