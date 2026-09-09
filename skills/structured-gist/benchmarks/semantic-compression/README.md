# Semantic-compression eval suite

A small, durable evaluation suite that checks whether structured-gist's
outlines preserve *meaning* (facts, relationships, answerability), not just
whether they conform to the grammar and not just how much shorter they are.
It exists alongside — and does not replace — `../../tests/lint_outline.py`
(structural conformance) and `../../tests/benchmark.md` (word-count
history). Nothing here changes `SKILL.md`, the grammar, or the linter.

Curated from a round-1 exploratory experiment that ran 11 cases across
skim/standard/deep and two model tiers. See `RESULTS.md` for what that
experiment found and why these 8 cases (of the original 11) were kept.

## Two kinds of case, two different questions

**`regression/`** — *did we accidentally degrade a property structured-gist
already intends to provide?* Ordinary, realistic content. A regression
case should score well; a score drop from its recorded baseline (below) is
a real regression to investigate, not an expected outcome.

**`pressure-tests/`** — *can the concept survive an intentionally hostile
case?* Each one provokes one specific, named failure mode. A pressure test
is a diagnostic instrument, not a pass/fail gate on "quality" — its
canonical score **is** the finding. Some of these currently show a real,
known limitation (e.g. relation loss at `standard` in
`causality-heavy-explain`); that is the point of keeping the case, not a
bug to silently fix by deleting the case.

## Cases

| case | class | property / failure mode protected | observed reference baseline |
|---|---|---|---|
| `regression/real-hook-discovery` | regression | semantic retention + relation retention + recoverability + conformance on an ordinary small realistic recap | `standard`/`deep`: wRetention ≥ 0.95, 0 conformance violations, monotone skim<standard<deep |
| `regression/real-benchmark-archaeology` | regression | same, on a richer realistic recap with unresolved questions and named identifiers | `standard`/`deep`: wRetention ≥ 0.88, unsupported_claim_count = 0 |
| `regression/near-identical-numbers` | regression | exact-value fidelity (numbers/paths/versions/SHAs) under compression | `standard`/`deep`: wRetention ≥ 0.95, unsupported_claim_count = 0 |
| `pressure-tests/causality-heavy-explain` | pressure | **relation collapse** — a causal chain flattened to a bare list, losing the links between steps even when the individual facts survive | `standard` relRetention is *known low* (0.56) vs. wRetention 0.80 — regression = relRetention dropping further, or `deep`'s 0.94 dropping |
| `pressure-tests/migration-tristate` | pressure | **lost status distinction** — 5 systems with different, easily-confused migration statuses (done/scheduled/will-not/reverted/in-progress) | `standard`/`deep` (sonnet): wRetention ≥ 0.95, no status collapsed to a generic bucket |
| `pressure-tests/negation-and-true-peers` | pressure | **lost negation + fake hierarchy on true peers** — 4 flat independent workstreams with load-bearing negations | `standard`/`deep`: wRetention ≥ 0.98, relRetention = 1.0, no invented shared parent |
| `pressure-tests/cause-chain-reversal` | pressure | **root-cause reversal / supersession** — an initial diagnosis is later overturned by better evidence; must preserve *which* cause is real | `standard`/`deep` (sonnet): wRetention ≥ 0.97; **haiku tier included** — this is also the sharpest model-sensitivity signal (see below) |
| `pressure-tests/synthetic-scale-verylarge` | pressure | **compression cliff + buried critical exception + structural-conformance collapse at scale** — 1 critical incident buried among many minor ones across 4 independent threads, 1,313 source words | `skim` is *expected* to lose most substance (wRetention 0.25) but must keep the critical item as its own distinct top-level entry, not merged into the minor bucket; **haiku tier's conformance collapses to 43 violations at `deep`** vs. sonnet's 2 — the clearest model-independence breakpoint found |

`wRetention` above is this suite's original name for the number
`results/combined.json` reports under both `weighted_retention` (unchanged)
and `task_weighted_fact_retention` (same value, precise name — see "Semantic
sufficiency vs. task-weighted fact retention" below for why it is *not*
called `semantic_sufficiency`). These baseline numbers are **observed
reference points from the renderings currently committed, not a formal
definition of "sufficient" and not a required threshold** — there is no
universal acceptable-sufficiency cutoff defined anywhere in this suite.
Likewise, `skim < standard < deep` is something this corpus currently
shows, not a semantic requirement; a strong `skim` output is allowed to
outperform a weak `standard` one, and a future case that does so is a
finding, not a bug in the suite.

Full current numbers for every case/tier/level: `results/SCORES.md`
(generated, do not hand-edit) and `results/combined.json` (machine-readable).

### On model tiers

Three pressure tests (`migration-tristate`, `cause-chain-reversal`,
`synthetic-scale-verylarge`) carry both a `sonnet` and a `haiku` rendering.
This is deliberate, not leftover: they are the cases that most clearly
showed the grammar's structural conformance — not its content fidelity —
breaking down first under a weaker model at scale (`RESULTS.md` §4). The
other 5 cases are sonnet-only; that tier is the one to regenerate against
by default.

## Semantic sufficiency vs. task-weighted fact retention

**Semantic sufficiency** is this suite's evaluation *question*, not a
number: *is enough of the meaning that matters to the intended reader/task
preserved by the transformation?* Nothing in this suite computes that
question as one scalar. It is currently assessed through a profile of
independent dimensions, each reported separately and never combined:

- **task-weighted fact retention** (`task_weighted_fact_retention`, below)
- **relation retention** — did the *relationships* between facts survive,
  not just the facts themselves
- **recoverability** — can the gold questions be answered from the output
- **source support** — is every claim in the output actually backed by the
  source (see "Hallucination / unsupported-claim correction" below)
- **structural conformance** — a linter gate, reported alongside, not
  blended in
- **compression cost** — reduction%, reported as a cost, never rewarded

That profile is deliberately not collapsed into a master score, because the
divergences between its dimensions are the findings this suite exists to
surface — see `causality-heavy-explain` at `standard`: task-weighted fact
retention 0.80 next to relation retention 0.5625, i.e. facts mostly survived
while the causal chain between them did not; or `synthetic-scale-verylarge`
at `skim`: retention as low as 0.25 by design, alongside a separate check
that the one critical item still survives as its own entry rather than
merging into the noise bucket. A single scalar would hide exactly those
cases. No "meaning per word" or other blended efficiency composite is
computed anywhere in this suite (see "No density composite" below).

### `task_weighted_fact_retention` — what it actually measures

```
task_weighted_fact_retention = sum(weight_i * retention_i for fact i) / sum(weight_i)
```

where `retention_i` is `1.0` retained, `0.5` partial, `0.0`
omitted/mutated (`scoring/combine.py`'s `STATUS_SCORE`). This is this
suite's original `weighted_retention` calculation — the arithmetic has not
changed. What changed is the name: an earlier revision of this suite called
this number `semantic_sufficiency`, which overstated what it measures. It
is **narrow by design**:

- it measures retained gold *facts*, weighted for importance
- it does **not** itself measure relationship preservation (`relation_retention` does)
- it does **not** itself prove the reader's task was completed (`recoverability` is the closest proxy this suite has, and even that is not a direct usefulness measurement — see below)
- it is not divided by compression, and never will be (see "No density composite")

`scoring/combine.py` emits both `task_weighted_fact_retention` and the
historical `weighted_retention` key with an identical value —
`weighted_retention` is kept only so the baselines already written down in
this file and in `RESULTS.md` still mean what they said. There are not two
independently-computed "how much meaning survived" numbers in this suite,
and `semantic_sufficiency` is no longer emitted as a scored key at all —
"semantic sufficiency" now names the broader question above, not this
scalar, so there is exactly one canonical numeric name
(`task_weighted_fact_retention`, aliased as `weighted_retention`) rather
than three that mean the same thing.

**Recoverability is not the same as usefulness.** It is a useful *proxy* —
can a reader answer the gold questions from the output alone — but this
corpus has not directly measured whether a human reader actually found an
output useful for their stated task. Treat `recoverability` as evidence
toward that, not as a stand-in for it.

## Weight semantics

A fact's `weight` in `gold.json` is meant to capture **the importance of
preserving that fact for the case's stated `intent.reader` and
`intent.task`** — not a universal importance ranking. That is the *intent*
of the weight. It is not yet a validated *property* of the weight:

**The weights currently in this corpus were assigned primarily by a
category-default heuristic** — decision/constraint/negation/failure ≈ 3,
cause_rationale/outcome/next_action ≈ 2.5, unresolved_question ≈ 2,
descriptive ≈ 1 — not derived from each case's `intent.reader`/`intent.task`
individually. `intent` was added to `gold.json` *after* most weights were
already set, to give those weights an explicit referent and make them
interpretable; adding it does not retroactively prove the weights are
task-sensitive. There is at least one clear counterexample already in this
corpus: `regression/near-identical-numbers` declares a task of precise
recall of exact identifiers (versions/paths/SHAs), yet several of its exact
identifier facts (`f2`, `f6`, `f9`, `f12`) are still category-`descriptive`
at weight `1`, while less identifier-specific rationale/outcome facts sit at
weight `2.5`–`3` — defensible as *weighted fact retention*, not yet proven
as *task-weighted* retention for that case's stated task. This PR does not
retroactively reweight the corpus to fix that (see "Next experiment"
below) — mixing a metric-definition correction with new human judgment and
changed benchmark scores in one change would make neither auditable.

The category buckets above remain a reasonable **default** for
hand-authoring a new case, and category never implies every fact in it
must carry the default weight: the same "outcome" category already holds
weight-1 facts (routine, resolved noise in `synthetic-scale-verylarge`)
and weight-3 facts (the corrected root cause in the same case) side by
side. But "this fact's weight differs from its category default" is not
the same claim as "this weight was independently derived from the stated
task" — only the former is currently true of this corpus.

Where a fact's weight is unusual for its category, the fact may carry an
optional `weight_reason` string — a one-line note on **why this weight is
especially consequential for the stated task**, not a claim about how or
when the weight was originally set. It is not consumed by any arithmetic in
`scoring/combine.py`; it exists so a reader auditing a surprising weight
(e.g. an "outcome" fact weighted at 3 next to five "outcome" facts weighted
at 1) can see why without reverse-engineering intent from the case alone.
Reserve it for facts whose weight is actually exceptional — most facts
should rely on the category default with no `weight_reason` at all.

## Intended reader/task

Each `gold.json` carries a case-level `intent` object stating what the
transformation is supposed to preserve *for*:

```json
"intent": {
  "reader": "who this outline is for",
  "task": "what they need to do with it",
  "rationale": "optional: why the weights below are shaped the way they are"
}
```

This is deliberately the smallest representation that makes weights
interpretable — not a persona system, not product requirements, not a
task ontology. `scoring/combine.py` surfaces it at the case level in
`results/combined.json` and lists it per case in `results/SCORES.md`
purely for human interpretation; it is not an input to any score.
`intent` currently provides three things, and no more:
interpretation of an already-set weight, a referent future re-weighting
work can be checked against, and something a reader can use to judge
whether `task_weighted_fact_retention` actually matches this case's
consumption task. It does not make the legacy category-default weights
task-derived — see "Weight semantics" above and "Next experiment: blinded
task-weight re-annotation" below.

## Next experiment: blinded task-weight re-annotation (not run in this suite yet)

The open question "Weight semantics" leaves unanswered: *are these weights
actually task-sensitive, or just category defaults with a task description
attached after the fact?* The smallest measurement that would answer it,
deferred to a future change rather than run here:

1. For each retained case, give an annotator only: `source.md`, the
   case's `intent.reader`/`intent.task`, and the gold semantic units
   (fact/relation/question text, without ids revealing anything else).
2. Hide from that annotator: the model renderings, the skim/standard/deep
   labels, the judge verdicts, the existing `weight` values, and the
   existing scores.
3. Ask the annotator to assign an importance weight to each fact based
   solely on the stated task — no access to the category-default heuristic.
4. Compare those task-derived weights against the current category-derived
   weights already in `gold.json`.
5. Re-run `scoring/combine.py`'s arithmetic against the already-recorded
   fact-retention verdicts in `judged/*.json` (no re-judging needed) using
   the new weights, and see whether: scores change materially, mode
   rankings (skim/standard/deep) change, or the apparent
   skim/standard/deep frontier shifts.

If that comparison shows the two weight sets converge, the category
heuristic gets to keep being used with more confidence. If it diverges
materially, that is itself the finding, and only then would this corpus's
weights be revised — as its own change, not folded into a metric-naming
correction.

## Scoring dimensions (decomposable — no master scalar)

Every case reports these, computed by `scoring/deterministic.py` (no
judgment, reuses the real linter) and `scoring/combine.py` (arithmetic over
judge verdicts already recorded in each case's `judged/<tier>.json`):

- **task-weighted fact retention** (`task_weighted_fact_retention`, alias
  `weighted_retention`) and **unweighted retention** — see above for the
  formula and what `weight` currently does (and does not) mean; a case
  with zero gold facts reports both as `None`/`null`, never `0.0`
- **relation retention** — fraction of gold relationships (causal,
  dependency, temporal, supersession, comparative) whose *relationship*,
  not just both endpoints, survives
- **recoverability** — fraction of gold questions answerable from the
  outline alone (a usefulness *proxy*, not a direct usefulness measurement
  — see above)
- **unsupported-claim count** and **unverified-claim count** — see
  correction below; neither is the same as "absent from the gold fact list"
- **structural conformance** — a gate (violation count from the unmodified
  linter), reported alongside the above, never blended into them
- **compression ratio / reduction%** — reported as a cost, never rewarded
  on its own (see `RESULTS.md` §2 for why)

None of these combine into a "semantic sufficiency score" — see "Semantic
sufficiency vs. task-weighted fact retention" above for why.

### No density composite

No "meaning per word" density composite is computed anywhere in this
suite, and task-weighted fact retention does not create one either — it is
not divided by size or word count anywhere. Round-1 evidence showed every
such formula is *negatively* correlated with actual usefulness — see
`RESULTS.md`.

## Hallucination / unsupported-claim correction (read before trusting that number)

An isolated judge sees only `gold.json` and the outline — never
`source.md` — so it can only say a claim is *not covered by the gold fact
list*, which is **not the same as unsupported by the source**. Gold is a
curated, weighted subset of the source, not an exhaustive transcript.

Every entry in `judged/<tier>.json`'s `hallucinations` list is expected to
carry a `source_supported` boolean, set by checking the exact claim against
`source.md` directly. That field is a **tri-state**, not a bool:
`source_supported: false` (confirmed unsupported), `source_supported: true`
(confirmed supported), or the key absent entirely (not yet checked).
`unsupported_claim_count` (the canonical "confirmed unsupported" metric)
counts only explicit `source_supported: false` entries — an entry that
simply hasn't been checked yet is **never** silently treated as
unsupported. It instead counts toward `unverified_claim_count`, so "not
yet adjudicated" and "confirmed unsupported" can never be conflated. Every
entry in this corpus's current `judged/*.json` already carries an explicit
`source_supported` value, so `unverified_claim_count` is `0` everywhere
today — this is a safety net for future judging runs, not a change to any
existing number. The raw judge-flagged count is kept as
`flagged_vs_gold_count` for transparency, but is not something to gate on
— in this corpus it was 20 and the corrected count is 0 (every flagged
claim was verbatim or near-verbatim source text gold's fact list simply
hadn't extracted).

**If you re-run judging**, give the unsupported-claim check — and only that
check — access to `source.md`; keep the fact/relation/question checks
source-blind (that isolation is what makes retention/recoverability
grading trustworthy). Do not restore the "no matching gold fact ⇒
hallucination" heuristic.

## Re-running

```
python3 scoring/deterministic.py   # word counts, compression, lint gate
python3 scoring/combine.py         # merges in judged/*.json -> results/
python3 scoring/spr.py             # experimental: SPR + blinded weight comparison -> results/
```

Regenerating `renderings/` or `judged/` (i.e. actually re-generating
outlines or re-judging them) is a manual/agent-driven step, not a script in
this repo — see `RESULTS.md` §5 for the protocol used to produce the
current canonical files.
