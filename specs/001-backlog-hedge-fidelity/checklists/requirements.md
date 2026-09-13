# Requirements Quality Checklist: Backlog Sweep — Hedge Fidelity, Benchmark Harness, Backlog Adjudication

**Purpose**: Unit tests for the requirements writing in `spec.md`, `plan.md`, and `tasks.md` — do the artifacts specify this work completely, unambiguously, measurably, and consistently? These items interrogate the documents, not the implementation.
**Created**: 2026-09-09
**Feature**: [spec.md](../spec.md) · [plan.md](../plan.md) · [tasks.md](../tasks.md)
**Reviewer**: independent opus-tier reviewer (fresh context)

---

## Model-Tier Assignment Discipline (tasks.md)

- [ ] CHK001 Does EVERY task row T001–T094 in `tasks.md` carry an explicit `**tier: <tier>**` assignment, with none left blank, inherited, or implied by a phase heading? [Completeness, Tasks §Format]
- [ ] CHK002 Is the tier of every task discoverable solely from the inline `**tier:**` marker on the task row itself, with no reliance on summary tables or other reference sections? [Clarity, Consistency, Tasks §line 36-39]
- [ ] CHK003 Do all inline per-row `**tier:**` markers assign a valid tier (`free-tier`, `luna`, `terra`, `haiku`, `sonnet`, or `opus — decision gate`) to every task T001–T094, with zero blank or missing assignments? [Consistency, Tasks §Format]
- [ ] CHK004 Do all 94 task rows (T001–T094, including 11 lettered subtasks) carry tier assignments that reconcile with a documented distribution, and do the 7 decision gates (`opus — decision gate`) match the inline row counts? [Measurability, Tasks §Format, §CHK-R16]
- [ ] CHK005 Wherever the paid `sonnet` tier is chosen over a free or cheaper tier (`free-tier`, `haiku`, `luna`, `terra`), does a stated one-line justification accompany that specific row? [Completeness, Tasks §Sonnet justifications]
- [ ] CHK006 Are the sonnet justifications for T022 and T036 substantive — naming the property of the task (cross-file consistency, generative authoring, silent-failure risk) that a cheaper tier could not satisfy — rather than restating the task description? [Clarity, Tasks §T022, §T036]
- [ ] CHK007 Are the two sonnet justifications recorded in BOTH the summary block and inline on their task rows, so a reader working row-by-row cannot miss the escalation rationale? [Consistency, Tasks §T022, §T036]
- [ ] CHK008 Is NO implementation task assigned an `opus`/`astra` tier — i.e. is every opus-tiered row (T004, T017, T023a, T027a, T033, T054, T062) explicitly marked as a judgment/decision gate and explicitly disclaimed as "not an implementation task"? [Consistency, Tasks §Notes]
- [ ] CHK009 Is the allowed-tier enumeration in the Format section (`free-tier`, `luna`, `terra`, `haiku`, `sonnet`) consistent with the tier strings actually used, given that the five gates are written as `opus — decision gate` — a value the allowed list excludes? [Conflict, Tasks §Format]
- [ ] CHK010 Are the criteria that distinguish a "decision gate" from an implementation task stated as a rule a future session could apply to a NEW task, rather than being asserted only for the five existing gates? [Gap, Tasks §Notes]
- [ ] CHK011 Do the decision gates specify a recorded output artifact and location for each adjudication (T004 → `redaction-log.md`; T054 → schema description), and is that location stated for T017, T033, and T062 as well? [Completeness, Gap, Tasks §T017, §T033, §T062]
- [ ] CHK012 Is the escalation rule directional and complete — is there a stated criterion for when a task may be tiered UP (free-tier → haiku → sonnet), or are the non-sonnet tier choices unjustified assertions? [Gap, Tasks §Tier Assignment Summary]
- [ ] CHK013 Are the distinctions among `free-tier`, `luna`, and `terra` defined anywhere in the artifacts, so that a reader can tell whether T005 (terra) and T040 (luna) were tiered on a stated basis? [Ambiguity, Gap, Tasks §Format]

## Redaction / PII Gate — Requirements Quality

- [ ] CHK014 Is "personal data" defined with concrete categories (names, phone numbers, institutional identifiers, message metadata), or does FR-010 rely on an undefined term? [Ambiguity, Spec §FR-010]
- [ ] CHK015 Are the criteria for a redaction verdict specified — what makes an excerpt APPROVED vs APPROVED-WITH-EDITS vs DROPPED? [Gap, Tasks §T004]
- [ ] CHK016 Is the identity and authority of the redaction reviewer specified (human operator? model? either?), given that T004 is written as "human/opus-tier review"? [Ambiguity, Tasks §T004]
- [ ] CHK017 Does FR-010's "before being written to any file, issue, comment, fixture, or benchmark input" conflict with T005, which writes pre-review corpus excerpts into `redaction-log.md` (a file) marked `STATUS: pending-review`? Is the log explicitly carved out of FR-010's scope, and is that carve-out stated in the spec rather than only implied by task ordering? [Conflict, Spec §FR-010, Tasks §T005]
- [ ] CHK018 Does the same pre-write concern apply to T042, which stages the full registrar source message into a benchmark case directory "subject to the T004 verdict" — is the ordering (stage-then-review vs review-then-stage) unambiguous? [Conflict, Spec §FR-010, Tasks §T042]
- [ ] CHK019 Is the `pending-review` grep guard's scope (T007 scans only `skills/`) consistent with FR-010's scope (any file), given the redaction log lives under `specs/`? [Consistency, Spec §FR-010, Tasks §T007]
- [ ] CHK020 Are requirements stated for what happens to an excerpt already published to a GitHub issue that later fails review — is there any retraction/rollback requirement? [Gap, Coverage, Exception Flow]
- [ ] CHK021 Is the redaction requirement stated for the DERIVED artifacts as well as the excerpts — the README example (FR-015/FR-017), the gold-set `source_quote` fields (T025), and the hedge lexicon — or only for the excerpts themselves? [Coverage, Gap, Spec §FR-010]
- [ ] CHK022 Is the "drop it and don't create the test case" edge case (spec Edge Cases) expressed as a requirement with a recorded reason, and is the downstream effect on FR-009's three-case count stated rather than left to inference? [Completeness, Spec §Edge Cases, §FR-009]
- [ ] CHK023 Is SC-010's clause "no corpus excerpt anywhere in the delivered work contains personal data" objectively verifiable — is the verification method (T082 "grep the full delivered diff") specified with patterns, or is it an unbounded manual judgment? [Measurability, Spec §SC-010, Tasks §T082]

## Requirement Completeness

- [ ] CHK024 Is the hedge lexicon's content specified — which modal verbs, epistemic adverbs, approximators, and evidential frames — or is T027 authoring an unspecified artifact? [Gap, Plan §D3, Tasks §T027]
- [ ] CHK025 Are the legal values of `modality` and `polarity` on a claim record enumerated anywhere in spec or plan, or does the schema depend entirely on an unresolved decision gate (T054)? [Gap, Spec §FR-018, Tasks §T054]
- [ ] CHK026 Is `source_span` defined as a data shape (character offsets? line range? quoted text?) sufficiently for a schema to be written? [Ambiguity, Spec §FR-018]
- [ ] CHK027 Are requirements stated for how `parent_id` and claim identifiers are generated and made stable across re-renders? [Gap, Spec §FR-018]
- [ ] CHK028 Is "a claim" defined — which outline nodes produce a claim record and which do not (attributes? enumerators? explanations only?) — so "one record per claim" has a determinate meaning? [Ambiguity, Spec §FR-018]
- [ ] CHK029 Are requirements defined for the token-counting method used in the ±5% budget match (which tokenizer, input vs output tokens, per-case or aggregate)? [Gap, Spec §FR-021, Plan §D6]
- [ ] CHK030 Is "correct vs. incorrect R17 firing" defined, i.e. is there a stated ground-truth rule for split precision, or is the 0.98 threshold measured against an undefined label? [Gap, Measurability, Spec §FR-024]
- [ ] CHK031 Is the sampling procedure for "corpus-sampled leaf nodes" specified — population, sample size, selection method — given FR-024 requires recording the sample but not choosing it? [Gap, Spec §FR-024, Tasks §T069]
- [ ] CHK032 Is "SCU-recall" given an explicit definition in the spec, or is its definition deferred entirely to implementation (plan D5 acknowledges the near-tautology risk)? [Gap, Spec §FR-026, Plan §D5]
- [ ] CHK033 Are requirements defined for the `.github/workflows/` CI lane beyond "no model credentials in scope" — trigger events, failure semantics, required-check status? [Gap, Spec §FR-014, Tasks §T040]
- [ ] CHK034 Does any requirement state where the harness obtains renderings for a condition (pre-committed `renderings/*.md` vs generated per run), which determines whether "byte-identical inputs" (SC-002) is even achievable? [Gap, Spec §SC-002]

## Requirement Clarity & Measurability

- [ ] CHK035 Is "markedly worse" / "substantially worse" hedge survival (FR-023, US7 scenario 3) quantified, or is the prediction unfalsifiable as written? [Ambiguity, Measurability, Spec §FR-023]
- [ ] CHK036 Is "implementable from its own text without reference to this spec" (FR-005) given an objective acceptance test, or does it rest on a reviewer's impression? [Measurability, Spec §FR-005]
- [ ] CHK037 Is FR-002's "no false positives and no false negatives across the eight existing benchmark cases" measurable given no labelled expected-violation set for those cases is specified? [Measurability, Spec §FR-002]
- [ ] CHK038 Is the 0.98 precision threshold justified or merely asserted, and is the confidence/sample-size condition under which it may be applied stated? [Gap, Spec §FR-024]
- [ ] CHK039 Is the ρ=0.8 cutoff paired with a stated "near the threshold" band, or is the borderline edge case (spec Edge Cases, T075) triggered by an undefined proximity? [Ambiguity, Spec §Edge Cases, §FR-027]
- [ ] CHK040 Does the spec acknowledge the statistical power limitation of n=8 as a stated caveat on FR-026's conclusion, rather than only as a plan-level note? [Gap, Spec §FR-026, Plan §D5]
- [ ] CHK041 Is "matched within five percent" specified as a relative delta on which quantity, and is the direction/denominator unambiguous? [Clarity, Spec §FR-021]
- [ ] CHK042 Is FR-013's "cache miss on a changed prompt or model" expressed over a fully enumerated key, and does the spec (not just plan D4) commit to that enumeration? [Clarity, Spec §FR-013, Plan §D4]

## Requirement Consistency & Traceability

- [ ] CHK043 Does every task T001–T094 trace to at least one FR or SC, and does every FR-001–FR-030 trace to at least one task? [Traceability, Coverage]
- [ ] CHK044 Are the R16/R17 identifier assignments stated consistently across FR-003a, plan D1, T003, T019, and T080, with no residual "R16" reference to the comma-split rule? [Consistency, Spec §FR-003a]
- [ ] CHK045 Does FR-030's ordering statement agree with the dependency graph in plan.md and the Phase Dependencies in tasks.md, including the US3-after-US2 edge that plan.md derives but FR-030 does not name? [Consistency, Spec §FR-030]
- [ ] CHK046 Is the `severity` concept (plan D2) traceable to a functional requirement, or does it exist only in the plan while FR-024 assumes warn-only is expressible? [Gap, Traceability, Spec §FR-024, Plan §D2]
- [ ] CHK047 Is the "eight existing benchmark cases" baseline stated consistently, given T044 adds a ninth (`registrar-hedge`) before FR-026's correlation over "the eight existing results" is computed? [Conflict, Spec §FR-026, Tasks §T044]
- [ ] CHK048 Does FR-022's exclusion of the judged `caveat_attach_accuracy` from this spec's scope remain consistent with FR-008, which requires the metric to be *defined* — is "defined but not implemented" stated unambiguously in both? [Consistency, Spec §FR-008, §FR-022]
- [ ] CHK049 Is the Scope Statement's exclusion list (JSONL-primary IR, pptx, unconditional comma-split) reflected as explicit MUST-NOT requirements (FR-020, FR-024, FR-029) with no residual ambiguity about what "deferred" obliges? [Consistency, Spec §Scope Statement]

## Edge Case & Exception Coverage

- [ ] CHK050 Are requirements defined for the case where the judged lane is invoked with no cache entry and no model access — is "reports unavailable" a stated requirement (FR-014 does not say it; only the Edge Cases section does)? [Coverage, Gap, Spec §Edge Cases, §FR-014]
- [ ] CHK051 Are requirements stated for R16 conflicting with R1/R2 on the same line — is additivity a requirement or only an edge-case narrative? [Coverage, Spec §Edge Cases, Tasks §T014]
- [ ] CHK052 Are requirements defined for the T016 regression sweep showing a delta — beyond routing to a decision gate, is either resolution branch's required outcome specified? [Gap, Tasks §T016, §T017]
- [ ] CHK053 Is the failure path defined for FR-025's hard gate — what is required if promotion is attempted while a prerequisite has not landed (detection mechanism, not just prohibition)? [Coverage, Gap, Spec §FR-025]
- [ ] CHK054 Are requirements defined for a GitHub bookkeeping action failing (no write access, issue already closed, comment rejected), given assumptions state write access is merely assumed? [Coverage, Gap, Spec §Assumptions]
- [ ] CHK055 Are requirements defined for the case where the registrar full source message is unreachable (assumption 2 fails), which would block FR-017, FR-015, and US5 entirely? [Coverage, Assumption, Spec §Assumptions]

## Dependencies & Assumptions

- [ ] CHK056 Is each stated assumption paired with a stated consequence if it proves false, or are the six assumptions recorded without contingency? [Gap, Spec §Assumptions]
- [ ] CHK057 Is the "zero runtime dependencies" constraint expressed as a checkable requirement covering the new `render/` module and its stdlib-only schema validation (T053)? [Measurability, Plan §Constitution Check P1, Tasks §T053]
- [ ] CHK058 Are the external dependencies (GitHub issue write access, model access for the judged lane, the local conversation corpus) each documented as a prerequisite with an owner? [Dependency, Spec §Assumptions]

## Resolution Status (post-analyze remediation, 2026-09-09)

The analyze pass raised 45 findings; the artifacts were then amended. Items below are recorded as resolved and need only confirmation, not re-investigation:

- [x] CHK-R01 Redaction ordering conflict (CHK017/018) — resolved: spec FR-010 now mandates extract → review → write; FR-010a carves out an out-of-tree staging buffer; tasks T005 (extract to scratchpad) now precedes T004 (review), and T042 may write only APPROVED / APPROVED-WITH-EDITS text.
- [x] CHK-R02 Redaction verdicts + authority (CHK015/016) — resolved: spec FR-010b defines APPROVED / APPROVED-WITH-EDITS / DROPPED and names the supervising operator session as the authority.
- [x] CHK-R03 "Personal data" undefined (CHK014/023) — resolved: spec FR-010c enumerates the categories any SC-010 scan must cover.
- [x] CHK-R04 Unfalsifiable hedge prediction (CHK035) — resolved: spec FR-023 pins a 0.15 absolute-gap threshold; SC-007 tests against it.
- [x] CHK-R05 Eight-vs-nine case baseline (CHK047) — resolved: spec FR-026 requires a frozen pre-step-3 snapshot at n=8; task T073 cites it.
- [x] CHK-R06 SCU-recall undefined (CHK032) — resolved: spec FR-026a defines it and requires the definition be recorded with the result.
- [x] CHK-R07 `claim` / `source_span` / `parent_id` undefined (CHK026/027/028) — resolved: spec FR-018a defines claim-producing node families, the offset-plus-quote span shape, and parent-id stability.
- [x] CHK-R08 modality/polarity vocabulary (CHK025) — resolved: spec FR-018b requires enumeration in the schema before implementation; task T054 now precedes T051 and T051 lost its parallel marker.
- [x] CHK-R09 Split-precision label and sampling (CHK030/031/038) — resolved: spec FR-024a defines the correctness label, FR-024b the sampling procedure and the underpowered-sample deferral.
- [x] CHK-R10 Token-matching method (CHK029/041) — resolved: spec FR-021 pins output tokens, one recorded tokenizer, per-case comparison.
- [x] CHK-R11 FR-025 gate unenforced (CHK053) — resolved: task T070 now refuses to flip severity unless the step-3 issue, `provenance.json`, and the step-7 record all exist.
- [x] CHK-R12 Pre-review guard scope (CHK019) — resolved: task T007 scans the whole working tree, not only `skills/`.
- [x] CHK-R13 Tier ladder undefined (CHK012/013) — resolved: tasks.md carries an Execution tier ladder plus a single escalation predicate.
- [x] CHK-R14 Tier recorded in three places (CHK002/003) — resolved: summary table and trailing note deleted; the inline row marker is authoritative.
- [x] CHK-R15 Tier vocabulary contradiction (CHK009) — resolved: the Format section now separates execution tiers from `opus — decision gate` rows.
- [x] CHK-R16 Over-provisioned tiers — resolved: 24 mechanical rows demoted to free-tier, both sonnet rows demoted to haiku (their justifications were contradicted by plan D3/D4), T060 promoted to haiku. T069 correctly assigned free-tier (never should have been haiku — FR-024a's "single free-tier labeller" fixes its tier at the requirement level). Final distribution: 66 free-tier, 11 haiku, 1 terra, 7 opus decision gates; zero sonnet, zero opus on implementation rows.
- [x] CHK-R17 Judged-lane unavailability (CHK050) and R16 additivity (CHK051) — resolved: promoted from Edge Cases into FR-014 and FR-001 respectively.
- [x] CHK-R18 SC-002 reproducibility premise (CHK034) — resolved: SC-002 now states renderings are committed inputs, never generated per scored run.
- [x] CHK-R19 Assumptions without consequences (CHK055/056) — resolved: spec Assumptions section gained an explicit consequences paragraph.
- [x] CHK-R20 Decision gates without an output artifact (CHK011) — resolved: T017, T023a, T027a, T033, T054, T062 each record to `specs/001-backlog-hedge-fidelity/decisions.md`.

Items NOT resolved, carried forward as live checklist work: CHK036 (FR-005 "implementable cold" now has an objective check — task T023a dispatches a fresh-context agent to confirm the drafted issue is buildable cold before filing — but the verdict is still a single reviewer's judgment call, not eliminated), CHK024 (hedge-lexicon membership is authored by T027 and now cites sources per FR-007a/T027, but the taxonomy's completeness remains the largest unspecified input), CHK054 (GitHub bookkeeping failure paths — resolved as of this pass: spec clarification #2 pins retry-once-then-halt-and-report, applied to tasks T020, T024, T077, T079).

CHK052 (T016 delta-branch outcomes beyond routing to a gate) is now resolved: task T017a requires fixing R16 and re-running the T016 sweep to zero deltas when T017 rules over-firing (spec clarification #9), and the US1 checkpoint states it is not satisfied until that passes.

## Notes

- Check items off as completed: `[x]`
- `[Gap]` = the requirement appears absent; `[Ambiguity]` = present but not pinned down; `[Conflict]` = two artifacts disagree.
- Items CHK001–CHK013 are the mandatory tier-governance block and must be cleared before any task is dispatched.
- CHK017 / CHK018 (pre-review corpus writes) and CHK047 (eight-vs-nine case baseline) are the two hardest findings in this pass; both are artifact-level conflicts, not implementation defects.
