# Adjudication protocol (calibration cases only)

Used only for the 7 calibration cases, where two independent annotators
(A and B) each produced a Stage-A decomposition of the same case. For
every other case, a single Stage-A pass is frozen directly (see
`ANNOTATION_PROTOCOL.md`) — this document does not apply to those; see
`FINDINGS.md` for the reliability result that justified not double-passing
every case.

You are the adjudicator. You will be given: `source.md`, the case's
native `question_or_query`/`reference_answer`/`intent`/`native_evidence`,
and both annotators' Stage-A output (`annotator_a.json`,
`annotator_b.json`). You will NOT be given `SKILL.md`, any rendered
output, any scoring code, or `calibration_comparison.json` (the
quantitative overlap numbers) — adjudicate from the actual proposition
content, not from a similarity score.

## Rules

1. **Union only when independently supported and task-relevant.** A fact
   that appears (in substance, not necessarily identical wording) in both
   A and B's output is included once. A fact that appears in only one
   annotator's output is included **only if** you independently confirm
   it is source-supported (its `source_quote` genuinely appears in
   `source.md` and supports its `text`) and task-relevant (needed to
   answer the native question/query per the case's `intent`) — not
   merely because one annotator happened to include it.
2. **Merge obvious duplicates.** If A and B extracted essentially the
   same proposition with different wording or a different `id`, keep one
   version (prefer the one whose `text` is more precisely tied to its
   `source_quote`), and record both original ids in a `merged_from` list
   on the surviving fact for traceability.
3. **Reject unsupported or merely-descriptive extras that don't serve the
   task.** If a fact from only one annotator is technically
   source-supported but not needed for the question/query, leave it out
   — this corpus is built to the same "extract only what's needed" rule
   both annotators were given.
4. Apply the same three rules to relations, plus: a relation only
   survives if the facts it connects both survived adjudication (renumber
   `fact_ids` to the adjudicated fact ids).
5. **Preserve disagreements in metadata.** Every adjudicated fact and
   relation gets an `adjudication` object:
   ```jsonc
   "adjudication": {
     "agreement": "both" | "a_only" | "b_only" | "merged",
     "source_annotator_ids": ["a:f3"]   // or ["a:f3", "b:f2"] if merged
   }
   ```
6. If the two annotators' inventories are so different that a good-faith
   union/merge isn't possible (e.g. they identified essentially different
   task-relevant propositions, not just different granularity), do not
   force an adjudication — instead, set `"adjudication_status":
   "irreconcilable"` at the top level, explain why in one paragraph, and
   stop. This is a reliability finding to report, not a case to paper
   over.
7. Run the Stage-A "gaming pressure-test" checklist (in
   `ANNOTATION_PROTOCOL.md`) once more against your adjudicated output
   before finalizing.

## Output

The adjudicated result becomes that case's frozen `derived_gold.json`
directly (same schema as ANNOTATION_PROTOCOL.md's Stage-A output shape,
plus each fact/relation's `adjudication` object, plus a top-level
`"adjudication_status": "reconciled"` or `"irreconcilable"`).
