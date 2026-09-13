# External semantic-gold annotation protocol

You are annotating a **public benchmark case** (QMSum, Qasper, or
HotpotQA — a query-focused meeting summary, a technical-paper QA pair, or
a multi-hop Wikipedia QA pair). This document is your complete brief.
Follow it exactly. Do not read anything beyond the specific files you are
told to read for the case(s) assigned to you. In particular: do not open,
search for, or read any file named `SKILL.md`, anything under
`skills/structured-gist/` other than the exact case files you are given,
any file under `benchmarks/semantic-compression/pressure-tests/`,
`.../regression/`, `.../scoring/`, `.../results/`, or any rendered
`skim.md`/`standard.md`/`deep.md`. If you encounter any of those by
accident, ignore their contents and do not let them influence your
answer.

## The question you are answering

**What semantic propositions and relationships must be preserved for the
case's stated reader to correctly complete its stated task (usually:
answer its question/query)?**

You are NOT answering "what would a summarization or outlining tool need
to retain." You have no knowledge of, and should form no opinion about,
any such tool. You are building an evidence-grounded inventory of what
*matters to the task*, independent of how anything downstream might
compress or render it.

## Inputs you will be given, per case

- `source.md` — the full source document (meeting transcript / paper /
  multi-paragraph context). Read all of it, not just the evidence spans.
- the case's native `question_or_query` and `reference_answer`
- the case's native evidence (`native_evidence` — transcript spans,
  paper paragraphs, or supporting sentences, depending on dataset)
- the case's `intent.reader` / `intent.task`
- dataset-native metadata needed for interpretation (e.g. domain, evidence
  cardinality)

You will NOT be given, and must not seek out: any scoring code, any
weighting scheme, any existing hand-authored semantic-gold examples from
this project, any rendered output, any model/system name or description
this benchmark might be used to evaluate, or any indication of how
"success" is measured downstream.

## Stage A — semantic decomposition (facts + relations)

For each case, produce a JSON object (schema below) with two arrays:

### Facts

A fact is **one independently meaningful proposition** — not a
fragment of one, not several bundled together. Concretely:

- **Do not split** one proposition across multiple facts to make the
  inventory look larger or more granular than the claim actually is.
  ("The retry loop closes because retries hit the same slow endpoint" is
  one fact, not two.)
- **Do not merge** genuinely independent propositions into one fact —
  if a reader could lose one half and still get partial credit for the
  other, they're two facts.
- Every fact must have a `source_quote`: the exact (verbatim, copy-paste)
  span of `source.md` that supports it. If you cannot find a verbatim
  span that supports a claim, do not include the claim — do not
  paraphrase the `reference_answer` into a fact whose wording is not
  actually backed by the source text at that level of specificity. A
  fact's `text` may be a clean paraphrase of the source for readability,
  but its truth content must not exceed what `source_quote` actually
  supports.
- Extract only what's needed to answer the question/query — do not
  transcribe every detail in the evidence span. A 15-turn evidence span
  might support exactly one or two facts if that's all the question
  needs.
- Each fact lists which native evidence location(s) it came from in
  `derived_from` (you'll be given the exact id format to use per
  dataset — follow it exactly, character-for-character).
- Give each fact a `category` from this vocabulary (same as this
  project's own hand-authored gold, for consistency, but assign purely
  based on what the proposition itself is — never let a category choice
  imply an importance judgment, that happens later in a separate pass):
  `descriptive`, `constraint`, `decision`, `negation`, `failure`,
  `cause_rationale`, `outcome`, `next_action`, `unresolved_question`.
  Pick a `condition` fact type is fine too, category label is flexible if
  none fit cleanly — describe it accurately, don't force-fit.

### Relations

A relation states **how** two or more facts relate — never just that
they coexist. Use `type` from: `causal`, `temporal_order`, `dependency`,
`contrast`, `supersession`, `condition`, `decision_outcome`,
`problem_resolution`, or another short snake_case type if none of these
fit (name it accurately).

- Only annotate a relation if losing it (while keeping the individual
  facts) would break something about how the task's answer is understood
  — the actual connective tissue the answer depends on, not "these two
  facts appear near each other."
- **It is completely fine, and expected on some cases, for the relation
  list to be empty.** If the question is answered by independent facts
  that don't need to be connected, do not manufacture a relation.
- `fact_ids` lists the facts this relation connects (2 or more).
- `source_quote`: the verbatim source text that states the relationship,
  when the source states it explicitly. If the relationship is not
  literally stated but is a necessary composition of two explicit facts
  (this is common in HotpotQA bridge questions — one fact identifies an
  entity, another states a property of it, and the *connection* itself
  is what the question tests), set `"evidence_mode": "inferred"` and
  leave `source_quote` as an empty string; otherwise set
  `"evidence_mode": "explicit"` and give the exact quote.
- Do not create a relation that just restates two facts as a pair. State
  the actual relationship (why/when/how they connect).
- Do not label every pair of facts `"related"` or similar — be specific
  or omit it.

### Gaming pressure-test (read before you start)

Before finalizing, check your own inventory against these failure modes:

1. Did you split one proposition into several facts? Merge them back.
2. Did you merge several independent propositions into one fact? Split
   them.
3. Did you list a relation that's really just a fact restated? Remove it.
4. Is your relation inventory inflated with edges that don't matter to
   the question? Remove the ones that don't.
5. Did any fact's wording come from `reference_answer` rather than
   `source_quote`? Rewrite it to only claim what the source actually
   supports.
6. Does any fact smuggle in an inference the source doesn't state? Cut
   it down to what's stated, or drop it.

### Output shape (Stage A)

```jsonc
{
  "case_id": "qmsum-01",
  "facts": [
    {
      "id": "f1",
      "text": "semantic proposition, in your own words but source-true",
      "category": "cause_rationale",
      "source_quote": "verbatim supporting source text",
      "derived_from": [{"dataset": "qmsum", "native_evidence_id": "span:0"}]
    }
  ],
  "relations": [
    {
      "id": "r1",
      "type": "causal",
      "text": "relationship between semantic units, stated plainly",
      "fact_ids": ["f1", "f2"],
      "evidence_mode": "explicit",
      "source_quote": "verbatim evidence text, or empty string if evidence_mode is inferred",
      "derived_from": [{"dataset": "qmsum", "native_evidence_id": "span:0"}]
    }
  ],
  "question_fact_ids": ["f1", "f2"],
  "corpus_defect_notes": []
}
```

`question_fact_ids` = which of your facts are actually needed to answer
the case's native question/query (used later for the `questions[0]`
recoverability wrapper — this is your own linkage, not a re-derivation of
the answer).

`corpus_defect_notes` = non-empty only if you find the *native* benchmark
annotation (not your own work) appears genuinely malformed — e.g. the
reference answer doesn't seem supported by any evidence you can find, or
an evidence span looks unrelated to the question. Describe the problem
factually; do not silently work around it by inventing a different
answer.

## Stage B — task-importance weighting (separate pass, frozen inventory)

You will be given a **frozen** fact/relation inventory (already produced
by Stage A — you did not necessarily write it yourself) plus the case's
`intent.reader`/`intent.task`, `source_quote` for each unit, and nothing
else. Assign each fact and each relation a weight:

- **1 = supporting** — losing it does not materially impair completing
  the stated task.
- **2 = material** — losing it weakens or partially impairs task
  completion.
- **3 = critical** — losing it can prevent, reverse, or materially
  mislead task completion.

Rules:

- Judge from the unit's `text`/`source_quote` and the case's
  `intent.reader`/`intent.task` **only**. Do not let a fact's `category`
  or a relation's `type` bias the weight — category/type describe the
  proposition's shape, not its importance (a `descriptive` fact can be
  weight 3 if the task genuinely depends on it; a `decision` fact can be
  weight 1 if the task doesn't hinge on that specific decision).
- Do not look at any existing weight, any scorer output, or any other
  case's weights while doing this.
- Give a one-sentence `rationale` for every weight you assign — tie it
  explicitly to the reader/task, not to the category.

### Output shape (Stage B)

```jsonc
{
  "case_id": "qmsum-01",
  "annotation_protocol": "external-blinded-task-importance-v1",
  "fact_weights": {"f1": 3, "f2": 1},
  "relation_weights": {"r1": 2},
  "rationale": {"f1": "...", "f2": "...", "r1": "..."}
}
```

Every fact id and every relation id in the frozen inventory must appear
in `fact_weights`/`relation_weights` — no omissions.

## Coverage audit (separate pass, after Stage A is frozen)

You will be given: `source.md`, the native question/answer/evidence, and
the **proposed** fact/relation inventory (already produced, not by you).
Answer, in writing:

1. Is any task-critical proposition or relationship **missing** from
   this inventory? List each one specifically (with a source_quote), not
   just "seems incomplete."
2. Is any unit **redundant** (duplicates another unit already listed)?
3. Is any unit **unsupported** (its `source_quote` doesn't actually say
   what its `text` claims, or no real source_quote exists for it)?
4. Any **granularity problems** (a fact that's really two propositions
   glued together, or vice versa)?
5. Any **relation omission** (an explicit relationship stated in the
   source that materially matters to the question but isn't captured)?

Do not fix anything yourself in this pass — report findings only, in this
exact schema:

```jsonc
{
  "case_id": "qmsum-01",
  "status": "pass",  // "pass" (nothing found) or "issues_found"
  "missing_critical_units": [
    {"description": "what's missing", "source_quote": "verbatim evidence"}
  ],
  "redundant_units": ["f3"],           // ids that duplicate another listed unit
  "unsupported_units": ["f5"],         // ids whose source_quote doesn't back their text
  "granularity_problems": [
    {"unit_ids": ["f2", "f3"], "issue": "should be one fact, not two"}
  ],
  "relation_omissions": [
    {"description": "what relationship is missing", "source_quote": "verbatim evidence"}
  ],
  "notes": "free text, one paragraph max"
}
```

A later pass (done by whoever requested this audit) decides what to
change, grounded only in what you found plus the source/task evidence —
never by looking at any scorer or rendered output.
