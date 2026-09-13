# Semantic Preservation Recall (SPR): experiment findings

This is a measurement-only follow-up to PR #12 (`eval: narrow
weighted-fact-retention naming, fix empty-fact/source-support edge cases`).
It runs the blinded task-weight re-annotation PR #12's `README.md` deferred
("Next experiment: blinded task-weight re-annotation") and, on top of that,
tests a candidate broader metric -- Semantic Preservation Recall (SPR) --
that promotes relations from a side diagnostic to a first-class weighted
semantic unit alongside facts. **No rendering, judging, `SKILL.md`,
grammar, linter, or scoring in `scoring/combine.py` changed.** Every number
here is either a fresh blinded annotation or pure arithmetic over
already-committed `judged/*.json` verdicts.

**Success criterion this experiment set out to answer:** when task
importance is annotated independently and relations are treated as
first-class semantic units, does weighted semantic recall explain
structured-gist's known successes and failures better than weighted fact
retention alone? **Answer: partially.** SPR does surface exactly the
causal-collapse failure this suite already suspected (§5), and the blinded
re-annotation shows the category heuristic is, at best, a moderate proxy
for task importance (§2) -- but SPR also has real, demonstrable failure
modes (§6) that argue against promoting it to primary status yet.
Classification: **A, promising experimental metric** (§8).

## 1. Annotation protocol

Per-case, a **fresh, isolated agent** (no access to the ongoing
conversation, no filesystem access to this repository, and no tool use
beyond writing its own output file) was given, and only given:

- the case's `source.md`, verbatim
- the case's `intent.reader` and `intent.task`
- every gold fact's `id` + `text` + `source_quote`
- every gold relation's `id` + `type` + `text` + `fact_ids` + `source_quote`

It was explicitly denied: the current `weight` values, `weight_reason`,
model renderings, skim/standard/deep labels, judge verdicts, existing
scores, and regression thresholds. It rated every fact and every relation
on the integer scale the brief specified:

```
1 = supporting -- useful context but losing it does not materially impair the task
2 = material    -- meaningfully contributes to performing the task
3 = critical    -- losing it can prevent, reverse, or materially mislead the task
```

**Design choice: `category` was withheld from the annotator, not just
"not used."** The brief allows showing category as descriptive metadata.
This suite went further and withheld it entirely, because category is
literally the input the legacy heuristic used to assign weights
(decision/constraint/negation/failure ~3, cause_rationale/outcome/
next_action ~2.5, unresolved_question ~2, descriptive ~1) -- showing it
risked the annotator reconstructing that exact heuristic instead of judging
task-importance independently, which would have made the comparison in §2
circular. Relation `type` (causal/dependency/temporal_order/
contrast_supersession/comparative_outcome) *was* shown, because no
weighting scheme existed for relations before this experiment -- there was
nothing to anchor on.

Output artifacts: `scoring/blind_weights/<case_id>.json`, one per case, with
schema:

```json
{
  "case_id": "...",
  "annotation_protocol": "blinded-task-importance-v1",
  "fact_weights": {"f1": 2, "f2": 3},
  "relation_weights": {"r1": 3, "r2": 1},
  "rationale": {"f7": "one-line reason for a non-obvious weight"}
}
```

This is a **separate artifact, not a mutation of `gold.json`**. Every
existing `weight` value in every `gold.json` is byte-for-byte unchanged by
this PR -- see "Preserve old weights" in the brief and the design rationale
in `README.md`. `scoring/spr.py` reads legacy weights in exactly one place
(`compare_weights()`, a side-by-side descriptive comparison) and never
mixes them into any score; `scoring/test_spr.py::
test_legacy_gold_weight_never_leaks_into_spr_arithmetic` is a regression
test for that boundary specifically.

All 8 retained cases were annotated: 178 facts, 53 relations total.

## 2. Weight comparison: category heuristic vs. blinded task weights

**Corpus-level:** mean exact agreement **46.1%**, mean absolute difference
**0.69** (on the legacy weight's own {1, 2, 2.5, 3} scale -- not directly
"ordinal steps," see caveat below), mean Spearman rho **0.30** (weak-to
-moderate positive rank correlation; one case is *negative*).

Exact agreement uses round-half-up on the legacy scale (2.5 -> 3) because
the two scales don't natively align (legacy has a `2.5` rung, blinded does
not) -- a documented modeling choice, not a neutral fact. Mean absolute
difference is reported on the legacy scale's raw units for the same reason,
so treat it as a relative-magnitude signal, not an exact count of ordinal
steps.

| case | n facts | exact agreement | mean abs diff (legacy scale) | Spearman rho |
|---|---|---|---|---|
| causality-heavy-explain | 20 | 0.55 | 0.65 | 0.329 |
| cause-chain-reversal | 20 | 0.50 | 0.475 | 0.574 |
| migration-tristate | 19 | 0.526 | 0.737 | 0.245 |
| **near-identical-numbers** | 14 | **0.286** | **1.036** | **-0.274** |
| negation-and-true-peers | 20 | 0.60 | 0.525 | 0.689 |
| real-benchmark-archaeology | 24 | 0.417 | 0.604 | 0.248 |
| real-hook-discovery | 15 | 0.333 | 0.833 | 0.149 |
| synthetic-scale-verylarge | 46 | 0.478 | 0.674 | 0.459 |

(Full detail: `results/weight_comparison.json`; generated table:
`results/SPR_SCORES.md`.)

**Verdict: the category heuristic was, at best, a moderate proxy for task
importance -- it did not "already know" what mattered.** No case exceeds
60% exact agreement; correlation ranges from strongly positive
(`negation-and-true-peers`, 0.69) to actually negative
(`near-identical-numbers`, -0.27). This confirms, with fresh evidence, what
`README.md`'s "Weight semantics" section already flagged as a hypothesis
from inspection alone.

**The `near-identical-numbers` counterexample `README.md` predicted was
directly confirmed by blind annotation.** `README.md` named `f2`, `f6`,
`f9`, `f12` -- the four exact-identifier facts (two commit SHAs, a version
number, a release-candidate tag) -- as category-`descriptive` weight-1
facts in a case whose entire stated task is *"precise recall of exact
identifiers under compression."* The blinded annotator, with no access to
that category label, independently rated **all four of them weight 3
(critical)**:

| fact | legacy weight (category: descriptive) | blind weight | text |
|---|---|---|---|
| f2 | 1 | 3 | Service A's change shipped at commit `abc1234` |
| f6 | 1 | 3 | Service B's change shipped at commit `def5678` |
| f9 | 1 | 3 | Service C bumped to version `2.3.1` |
| f12 | 1 | 3 | Service D targeted version `2.4.0-rc1` |

That is the single largest confirmation that blinded task-weighting is
measuring something the category heuristic missed, not just adding noise --
this is why `near-identical-numbers` has the corpus's lowest exact
agreement (0.286) and only negative Spearman rho (-0.27): several
*other* facts in the same case (`f4`, `f8` -- the causal-rationale
sentences explaining *why* each timeout changed) moved from legacy 2.5 down
to blind weight 1, because losing the *reason* for a timeout change, while
regrettable, does not prevent this case's stated task (citing the *value*)
the way losing the identifier itself would.

## 3. Formulas

All three reuse the `STATUS_SCORE` encoding already established in
`scoring/combine.py` (retained=1.0, partial=0.5, omitted/mutated/lost=0.0)
and read **only** from `scoring/blind_weights/<case>.json` -- never from
`gold.json`'s legacy `weight` field (see `scoring/spr.py` module docstring
and `test_legacy_gold_weight_never_leaks_into_spr_arithmetic`):

```
blinded_task_weighted_fact_recall =
    sum(blind_weight_v * retention_v for fact v) / sum(blind_weight_v)

task_weighted_relation_recall =
    sum(blind_weight_e * retention_e for relation e) / sum(blind_weight_e)

semantic_preservation_recall (SPR) =
    ( sum(blind_weight_v * retention_v for fact v)
    + sum(blind_weight_e * retention_e for relation e) )
    / ( sum(blind_weight_v for fact v) + sum(blind_weight_e for relation e) )
```

No lambda/coefficient between facts and relations. No separate
normalization + 50/50 average. Each annotated unit contributes to SPR in
direct proportion to its own blinded weight -- see §7 for whether that
turned out to be a sound choice.

Hand-calculable check (also `scoring/test_spr.py::
test_hand_calculable_example_from_brief`):

```
facts:     weight 3 retained -> 3.0   |  weight 1 partial -> 0.5
relations: weight 3 lost     -> 0.0   |  weight 2 retained -> 2.0
total preserved = 3.0 + 0.5 + 0.0 + 2.0 = 5.5
total possible  = 3 + 1 + 3 + 2 = 9
SPR = 5.5 / 9 = 0.6111...
```

A case with zero gold facts or zero gold relations reports the affected
component as `None`/`null` (never a fabricated `0.0`), matching
`combine.py`'s existing convention -- `scoring/test_spr.py` covers this for
facts-only, relations-only, and both-empty.

## 4. Results

Full generated table: `results/SPR_SCORES.md` (33 case/tier/level rows) and
machine-readable `results/spr.json`. Regenerate with:

```
python3 scoring/deterministic.py && python3 scoring/combine.py && python3 scoring/spr.py
```

Corpus-level `skim`/`standard`/`deep` means (sonnet tier, legacy vs. SPR):

| level | legacy task_weighted_fact_retention (mean) | SPR (mean) |
|---|---|---|
| skim | 0.316 | 0.336 |
| standard | 0.828 | 0.813 |
| deep | 0.968 | 0.972 |

**The `skim < standard < deep` frontier is unchanged**, both in aggregate
and per-case: no `(case, tier)` triple in the corpus has SPR violate that
ordering (`scoring/spr.py`'s output was checked programmatically for
monotonicity violations across all 11 `(case, tier)` series; none found).
The apparent standard-mode "knee" (the point where most of the retention
value has already been captured) is essentially unchanged -- see §9.

## 5. Behavior on the known pressure cases

### `causality-heavy-explain` -- the case that motivated this PR

This is the sharpest result in the corpus. At `standard` (sonnet):

| metric | value |
|---|---|
| legacy `task_weighted_fact_retention` | **0.80** |
| `blinded_task_weighted_fact_recall` | 0.783 |
| unweighted `relation_retention` (legacy) | 0.5625 |
| `task_weighted_relation_recall` | 0.5625 (all 8 relations rated blind-weight 3, so this collapses to the unweighted number -- see §6) |
| **`semantic_preservation_recall`** | **0.7143** |
| critical units (weight 3) lost / partial / total | **4 / 6 / 21** |

A fact-only score at 0.80 reads as "mostly fine." SPR at 0.7143, alongside
**4 of this case's blind-weight-3 units lost outright at `standard`**,
tells a materially more honest story: this is the causal-collapse failure
mode the case exists to provoke, and SPR moves toward reflecting it (though
it does not collapse as far as raw relation retention, 0.5625, because it
is a blend, not a replacement). At `deep`, all three numbers converge near
1.0 (legacy 0.9722, SPR 0.961), and critical losses drop to 0/2/21 --
consistent with `README.md`'s existing finding that `deep` recovers what
`standard` drops here.

**One caveat that is itself a finding (see §6):** all 8 of this case's
relations were independently rated blind-weight 3 by the annotator (a
ceiling effect). That means `task_weighted_relation_recall` here is
*numerically identical* to the legacy unweighted `relation_retention` --
weighting added zero additional differentiation for relations in this
specific case, even though it did differentiate among facts.

### `cause-chain-reversal` -- does weighting the correct causal relation matter?

`r3` (`contrast_supersession`: "the initial apparent root cause, pool
exhaustion, is superseded by the actual root cause, the missing index") is
the single relation that most directly answers this case's stated task
("know which diagnosis turned out to be correct"). The blind annotator
independently rated it weight 3 with the rationale *"directly states the
diagnosis reversal, the exact answer the task requires."* `r3` is `partial`
at haiku/skim and sonnet/skim, `retained` everywhere else -- and those are
exactly the rows where SPR sits furthest below 1.0 relative to legacy fact
retention (e.g. haiku/standard: legacy 0.5707, SPR 0.5806 -- close, but
with 2 critical units lost at that row that the fact-only number does not
surface at all). This is real signal, not overreach: the metric is
weighting the thing the case is actually testing.

### `migration-tristate` -- do status-distinction relations matter beyond isolated facts?

`r5` (`contrast_supersession`: distinguishing auth-service's *permanent*
non-migration from notifications-service's *scheduled-but-not-yet* status)
was independently rated weight 3, rationale: *"explicitly guards against
the exact mix-up the task names."* It is `partial` at haiku/skim, `retained`
everywhere else. At haiku/`standard`, one blind-weight-3 fact (`f10`,
tracing the search-service migration's revert story) is lost, pulling SPR
(0.6964) below legacy fact retention (0.7442) at that row -- SPR is
correctly penalizing a status-distinction loss that a fact-only score
under-weighted.

### `near-identical-numbers` -- does blinded weighting elevate identifiers the heuristic missed?

Yes -- covered in full in §2. This is the corpus's clearest positive result
for the core hypothesis motivating this experiment.

### `synthetic-scale-verylarge` -- does the metric still find the buried critical item?

The buried root-cause facts (`f10` "idempotency check missing," blind
weight 2; `f11` "fix not shipped," blind weight 3; `f12` "top-priority
item," blind weight 3) are the case's central pressure-test target. At
`skim`, **haiku omits all three outright** (`f10`/`f11`/`f12` all
`omitted`); **sonnet only partially preserves two of three** (`f10`
omitted, `f11`/`f12` partial). This shows up directly in the critical-loss
diagnostic: sonnet/skim is 3 lost / 6 partial / 9 total critical units,
haiku/skim is **7 lost** / 2 partial / 9 total -- a much starker
model-sensitivity signal than the aggregate SPR gap (0.2701 vs. 0.1782)
alone communicates. The metric does not let the ~40 routine/resolved facts
in this very-large case dilute that signal away, because those facts are
almost all blind-weighted 1 (32 of 46 facts are weight 1 -- see §6's
"ceiling/floor" note) and so contribute little to either the numerator or
denominator relative to the handful of weight-3 units.

## 6. Failure modes found (actively tried to falsify SPR)

**(a) Relation-weight ceiling effect erases differentiation in exactly the
cases relations matter most.** Two of 8 cases --
`causality-heavy-explain` (all 8 relations) and `negation-and-true-peers`
(all 4 relations) -- got a uniform blind weight of 3 on every single
relation. In both cases, `task_weighted_relation_recall` is then
*mathematically identical* to the legacy unweighted `relation_retention`
(confirmed by direct comparison: every row matches to 4 decimal places).
Both are pressure tests specifically about relation preservation, so this
is not a corner case -- it is a failure mode concentrated exactly where the
metric is supposed to add the most value. It suggests either (i) a 1-3
scale is too coarse for a case where a human annotator genuinely judges
every relation as load-bearing, or (ii) these two cases are constructed
such that every stated relation really is necessary for the task, in which
case uniform weight-3 is the *correct* judgment and the "failure" is that
SPR then offers no more signal than the unweighted metric already did --
which is itself worth knowing, not a bug to silently paper over.

**(b) Relation-heavy cases show a real, if modest, volume-penalty
correlation.** Across all 33 scored `(case, tier, level)` rows, the
Pearson correlation between a case's *relation share of total blind
weight* (`sum(relation weights) / sum(all weights)`, fixed per case) and
`(SPR - legacy_fact_retention)` is **r = -0.38**: cases where relations
carry more of the total weight tend to see SPR pulled down relative to
fact-only retention more often. This is exactly the failure mode the PR
brief asked to check for ("relation-heavy cases become disproportionately
penalized merely because they contain more annotated relations"). r = -0.38
across 8 cases / 33 rows is suggestive, not proof -- and it is also
confounded with the genuine finding in §5 that relation loss is a real
failure mode this corpus's outputs actually exhibit at `standard`. This
suite cannot cleanly separate "SPR over-penalizes relation volume" from
"relation-heavy cases genuinely lose more meaning at `standard`" with 8
cases. Flagged as an open question, not resolved here.

**(c) Granularity sensitivity is a structural property of the linear-recall
formula, not something this fixed 8-case corpus can empirically rule out.**
Because SPR is `sum(weight * retention) / sum(weight)`, splitting one
weight-3 fact into two weight-3 facts describing the same content changes
the total weight from 3 to 6 while (if both survive with the same
retention verdict) preserving the same weighted-numerator-to-denominator
ratio *only if both halves get the identical verdict*. If a rendering
preserves one half and drops the other (a realistic outcome once a single
proposition is split), the same underlying content now contributes 0.5
instead of a clean 0/1, silently changing the score based on how gold was
authored, not how the rendering performed. This is a known, general
property of linear content-unit recall formulas (it is the reason
Pyramid-style summarization evaluation treats unit-splitting as an
annotation-protocol risk, not just a curiosity) and applies here without
modification. This suite's existing gold facts were authored by hand
before this experiment and were not re-split to test this -- flagged as a
real risk for any *future* gold authoring, not a demonstrated defect in the
current 8 retained cases.

**(d) Fact/relation double-counting is bounded, but not zero, by
construction.** A relation's `fact_ids` reference facts that are *also*
independently scored as facts (e.g. `causality-heavy-explain`'s `r8`
covers `f15`-`f20` and is itself blind-weighted 3, while `f15`-`f20` are
also independently weighted and scored as facts). This means content near
a heavily-annotated relation can influence SPR twice -- once as a fact, once
as part of a relation -- while content with no annotated relation touching
it only influences SPR once. This is inherent to treating facts and
relations as two separate annotated-unit pools summed into one
denominator, exactly as the brief specifies; it was not "fixed" here
because doing so would mean deviating from the brief's explicit formula.
Flagged as a known property, not a defect this PR silently patches.

**(e) A high SPR can still coexist with real task failure the score doesn't
surface on its own -- this is why the critical-loss diagnostic exists as a
*separate*, un-collapsed field.** `migration-tristate` haiku/`standard`
scores SPR 0.6964 with only 1 critical unit lost out of 12 -- a healthy-
enough-looking bulk score sitting next to a single potentially
task-breaking status confusion. Without `critical_units_lost` reported
alongside SPR (never folded into it, per the brief), that one loss would be
invisible inside an aggregate in the high 0.6s. This is not a flaw unique
to SPR (fact-only retention has the same property), but it reinforces why
this PR keeps the diagnostic un-collapsed rather than trying to fix the
problem by further complicating the formula.

## 7. Do facts and relations legitimately share one scale?

No principled reason was found to say they *cannot* -- both are annotated,
by the same blinded protocol, on the same integer 1-3 task-importance
scale, and the hand-calculable arithmetic in §3 treats them identically by
design. What *was* found is that the scale saturates faster for relations
than for facts in this corpus (**60.4%** of all annotated relations (32/53)
are blind-weight 3, vs. **41.0%** of facts (73/178) -- computed from
`scoring/blind_weights/*.json` across all 8 cases), which is consistent
with §6(a)'s ceiling-effect finding but does not, on its own, invalidate
sharing one scale -- it may simply reflect that relations in a causally
-dense or negation-dense case really are disproportionately critical (a
relation, by construction, only gets annotated in this corpus's gold data
when it was judged worth recording at all, so a skew toward "critical" is
plausible on its own terms, not obviously an annotation artifact). This suite did not find a
principled reason to add a coefficient between facts and relations, and
per the brief's explicit instruction, none was added to paper over this
observation.

## 8. Classification

**A. Promising experimental metric.** Keep the machinery and results
(`scoring/spr.py`, `scoring/blind_weights/`, `results/spr.json`,
`results/SPR_SCORES.md`, this document) but **do not** promote SPR into
`SKILL.md`, top-level benchmark claims, an acceptance threshold, or a
replacement for `task_weighted_fact_retention` / `relation_retention` as
independently reported dimensions.

Why not (B) durable secondary or higher, yet: the corpus is 8 cases: the
weight-comparison stats (§2) and the relation-volume correlation (§6b) are
suggestive, not conclusive, at that sample size, and §6(a)'s ceiling effect
means the metric currently adds zero differentiation in 2 of 8 cases for
the relation half of its own formula. Why not (D) rejected: §5's
`causality-heavy-explain` and `near-identical-numbers` results are genuine,
reproducible confirmations of this suite's core hypothesis -- SPR is not
merely "another number," it demonstrably surfaces a specific known failure
(causal collapse) that fact-only retention hides, using an
independently-sourced weight rather than a hand-tuned one.

## 9. Direct answers to the brief's findings questions

1. **Did blinded task weighting materially differ from category
   weighting?** Yes -- 46% mean exact agreement, mean Spearman rho 0.30,
   one case (`near-identical-numbers`) with *negative* correlation. Not a
   rubber stamp of the heuristic.
2. **Did the new weights change mode rankings or the apparent standard
   -mode knee?** No case had its skim/standard/deep ordering change under
   SPR vs. legacy retention, and the aggregate knee position (skim ~0.32,
   standard ~0.82, deep ~0.97) is essentially unchanged.
3. **Did weighted relations add meaningful signal?** Mixed. Yes in
   `cause-chain-reversal` and `migration-tristate` (§5), where a single
   task-critical relation's status materially explains a gap between SPR
   and legacy fact retention. No/zero-added-signal in
   `causality-heavy-explain` and `negation-and-true-peers`, where the
   ceiling effect (§6a) makes the weighted and unweighted relation numbers
   identical.
4. **Does SPR better represent known failures such as causal collapse?**
   Yes, directly -- §5's `causality-heavy-explain` result (SPR 0.7143 with
   4 critical losses vs. legacy fact retention 0.80 reading as "mostly
   fine") is exactly the case this PR brief was written to test.
5. **Where does SPR still fail?** §6(a)-(e): relation-weight ceiling
   effects, a modest but real relation-volume correlation, unresolved
   granularity sensitivity (structural, not yet empirically triggered in
   this corpus), bounded fact/relation double-counting by construction, and
   the standing need for critical-loss to remain a separate, un-collapsed
   diagnostic rather than trusting the scalar alone.
6. **Is there enough evidence to retain it as a durable metric?** Not yet
   at "durable secondary" confidence -- see §8's reasoning. Retained as
   experimental.
7. **Is there enough evidence to call it a primary benchmark metric?** No.
   §8 explicitly rejects (C) and (worse) any implicit promotion.

## 10. What this PR intentionally did not do (deferred)

- Did not re-annotate weights with more than one annotator per case (no
  inter-annotator agreement / reliability statistic beyond the
  legacy-vs-blind comparison in §2).
- Did not resolve the relation-weight ceiling effect (§6a) -- e.g. by
  giving annotators a finer scale or forcing rank-ordering among relations
  within a case. Flagged as a real design question for any follow-up.
- Did not empirically test granularity sensitivity (§6c) by re-splitting
  or re-merging any gold fact/relation -- the risk is documented
  analytically, not demonstrated on this corpus.
- Did not resolve fact/relation double-counting (§6d) -- e.g. by
  down-weighting a fact's independent contribution when it is already
  covered by a heavily-weighted relation. The brief's formula was
  implemented as specified.
- Did not compute a combined SPR-and-compression rate/Pareto view (the
  brief explicitly excludes this: compression stays a separately-reported
  cost axis).
- Did not blend recoverability, source support, or structural conformance
  into SPR -- all three remain independently reported, per `README.md`'s
  existing decomposition.
- Did not add a second, larger corpus to test whether §2's weight
  -comparison statistics or §6(b)'s relation-volume correlation hold up at
  scale.
- Did not set any acceptance threshold on SPR (e.g. "standard must be >=
  X") -- consistent with `README.md`'s existing position that this suite
  defines no universal sufficiency cutoff.
