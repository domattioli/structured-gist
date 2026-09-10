# Findability (Evidence Access Cost): findings (measurement only)

`scoring/findability.py` tests structured-gist's practical thesis, which is
**not** "fewer words" — it is **"hierarchical structure makes the important
information easier to locate."** This is Eval B of a two-eval
measurement-only PR (Eval A: `WORDING_FIDELITY_FINDINGS.md`, unchanged by
this revision). Neither eval changes `SKILL.md`, the grammar, the linter,
or any existing rendering, judge verdict, or gold semantic judgment.

Named conservatively, per the PR brief: **Evidence Access Cost**, not
"reading speed," "human findability," or "time-to-answer" — this is a
deterministic proxy, not a timed-reader study (see "Whether a human study
is warranted" below).

**This is a revision.** A second review of this eval, after its first
corpus run, found a second methodological confound in the baseline this
module compared the gist against. This document now describes the fixed
methodology and a from-scratch re-run of the corpus. The two prior
baselines are kept in the code (as documented diagnostics, never deleted)
and described below as a record of how the methodology got here — that
history is itself useful evidence of the refinement, not something to
hide.

## The critical design requirement: control for compression

The obvious wrong experiment is: compare a fact's position in the full,
unabridged `source.md` against its position in a much shorter gist, and
conclude the gist is "easier to navigate" because the fraction is smaller.
That mostly measures **deletion**, not organization — a gist is short by
design, so of course a fact sits at a smaller fraction of it. The fix has
to hold the actual evidence content constant on both sides and vary only
its *order*. Getting this right took two attempts.

## Failure mode 1: the literal per-question baseline is mathematically degenerate

The PR brief's literal 5-step baseline construction is **per question**:
resolve that one question's own support-unit IDs, locate their spans,
dedupe, keep source order, concatenate — nothing else. This module
initially implemented exactly that, then proved (and unit-tested, see
`test_naive_per_question_baseline_is_always_fully_traversed`) that it
cannot work:

**Claim.** If a baseline contains *only* the required evidence for one
question and nothing else, then EAC and EvidenceSpan computed against that
baseline are unconditionally **1.0**, for any nonempty set of required
spans.

**Proof.** The baseline is the union of the required spans, merged and
placed in source order — there is no other content in it. The *last*
required unit, by definition, ends exactly where the baseline itself ends
(there is nothing after it to include). So "tokens traversed before all
required evidence is available" (`EAC`'s numerator) always equals "total
tokens in representation" (its denominator): `EAC = 1.0`. The same
argument makes the *first* required unit start exactly where the baseline
starts, so `EvidenceSpan = 1.0` too. This holds for a single support unit
(trivially — it IS the whole baseline) and for any number of them (the
first and last merged spans are, respectively, the first and last content
in the baseline, by construction). `naive_per_question_baseline_tokens()`
is kept in the module (unused by scoring) purely as the executable version
of this proof.

## Failure mode 2 (found in review, fixed by this revision): the case-level all-gold baseline still let compression leak in

The fix for failure mode 1 was a **case-level** baseline: build one
baseline per case from *all* of that case's gold facts and relations (not
just one question's), and reuse it for every question in the case
(`build_case_baseline`). This is still in the module, and it correctly
solved failure mode 1's degeneracy — non-trivial baseline values are
achievable (`test_evidence_reordered_closer_to_start_improves_gist_eac`
and its mirror still pass, unchanged).

But a case-level all-gold baseline has its own, more subtle problem: it
contains **every** gold fact/relation for the case, regardless of whether
a *given rendering* actually retained it. A `skim` rendering routinely
retains only a small fraction of a case's gold units — that's the whole
point of skim. Comparing that skim gist's positions against a baseline
sized to the case's *entire* gold content means the two sides of the
comparison do not hold the same evidence after all:

- baseline: built from (in one representative case) ~284 tokens of nearly
  all of that case's annotated content
- skim gist: ~36 tokens containing only the small subset skim actually
  retained

Question eligibility only required that *this question's own* support
units be retained and alignable — it never required the *rest* of the
case-level baseline's content to have survived in the gist too. So the
denominator on the baseline side reflected "how big is this case's gold
content," while the denominator on the gist side reflected "how much did
this rendering keep" — two different things, silently compared as if they
were the same. Deletion/compression was still affecting the result, just
one level removed from failure mode 1's more obvious version of the same
problem. The prior write-up's claim that "both sides hold the same
evidence content" was not yet true.

## The fix: the retained-unit baseline

The corrected construction compares the **same set of retained semantic
units** in two different orders — not a case-level superset on one side
and a rendering-specific subset on the other.

For each **(case, tier, level)**, build a strict retained set **R**:

> A gold fact/relation belongs to R only if (a) its verdict status in
> *this specific rendering* is exactly `"retained"` (a separate
> exploratory view allows `"retained"` or `"partial"`, reported
> separately, never mixed into the strict numbers), (b) its
> `source_quote` aligns deterministically in `source.md`, and (c) the
> judge's recorded evidence for it aligns deterministically in *this
> specific rendering*. No partial units in the strict view. No fuzzy
> matching, ever — exact normalized-token containment only (same
> `text_norm.py` machinery as before). A unit failing any check is
> **excluded** from R, with the specific reason(s) recorded
> (`retained_set.strict.excluded` in `results/findability.json`) — it then
> cannot appear on either side of the comparison, so deletion can never
> earn credit.

Then build **two orderings over exactly R**:

1. **Source-order baseline** — sort R by original position in
   `source.md`.
2. **Gist-order representation** — sort the *same* units in R by their
   aligned position in the structured-gist rendering.

Same cards, different shuffle. `build_retained_units` (in
`scoring/findability.py`) constructs R and the two orderings;
`assert_identical_retained_sets` is a hard runtime assertion (also
directly unit-tested,
`test_assert_identical_retained_sets_catches_a_real_mismatch`) that the
two rankings cover exactly the same unit-id set — a unit the gist deleted
is excluded from R entirely and therefore cannot appear in either ranking
(`test_deleted_unit_absent_from_both_orderings`).

**Tie handling.** Multiple units may align to the same source span or the
same gist position. Ranking breaks ties deterministically: source side
sorts by `(source_start, source_end, unit_id)`; gist side sorts by
`(gist_start, gist_end, unit_id)` — never by incidental JSON/dict
iteration order (`test_ties_at_same_source_position_break_by_unit_id`,
`test_ties_at_same_gist_position_break_by_unit_id`,
`test_deterministic_ordering_regardless_of_dict_insertion_order`).

**Duplicate / relation overlap handling.** A fact and a relation may quote
overlapping (or identical) source text — common in this corpus (every one
of the 8 cases exhibits it). For this metric, each is still its own
semantic unit and gets its own rank; they are never collapsed into one
just because their spans coincide
(`test_relation_and_fact_sharing_source_span_remain_separate_units`). This
is a deliberate difference from the diagnostic token baseline below, which
*does* dedupe overlapping spans at the token level — the retained-unit
metric is about semantic-unit accessibility, not literal byte traversal,
so two independently-judged units both being locatable is exactly what it
should measure, even if their underlying text overlaps.

## Metric definitions

### Headline: unit-rank Evidence Access Cost (over R)

For each strict-scorable question (every required unit in R):

```
EAC_source = rank(last required unit, source order) / |R|
EAC_gist   = rank(last required unit, gist order)   / |R|
delta_eac  = EAC_gist - EAC_source
```

Ranks are **1-indexed, cumulative traversal**: the first of `|R|` retained
units is rank 1 (`EAC = 1/|R|`), the last (`|R|`-th) is rank `|R|`
(`EAC = 1.0`) — simpler and more defensible than token-normalized EAC for
this primary comparison, and directly hand-verified
(`test_rank_normalization_first_and_last_of_ten`: first of 10 -> 0.1,
tenth -> 1.0). Negative `delta_eac` means the gist makes all required
evidence available earlier, holding the retained content constant.

### Locality (multi-unit questions)

```
Span_source = (rank(last) - rank(first) + 1) / |R|
Span_gist   = (rank(last) - rank(first) + 1) / |R|      # gist order
delta_span  = Span_gist - Span_source
```

Negative `delta_span` means the required units became more clustered.
Both source above use the identical retained set R and the identical
required-unit ranks; only the ordering differs.

### Diagnostic only: the old token-normalized, case-level-baseline metric

`build_case_baseline`, `score_question_view`, `finalize_view` (unchanged
code, unchanged numbers — see "Verification" below) are kept in the module
and still computed for every question, reported under
`diagnostic_token_eac` in `results/findability.json` and in a clearly
labeled section of `results/FINDABILITY_SCORES.md`. This is Failure mode
2's construction, described above — it is **no longer the headline causal
claim about organization**. It remains useful as a diagnostic (it still
reports non-degenerate, hand-verified token positions and spans, and its
numbers are a documented data point in this methodology's own history),
but nothing in this document's conclusions should be read as resting on
it.

### Other diagnostics (unchanged)

- **Token convention** — identical to Eval A: `scoring/text_norm.py`'s
  `tokenize()`.
- **Structural traversal diagnostic** (multi-support questions only): which
  output node holds each required unit's evidence, the depth of their
  lowest common ancestor, and how many other nodes sit between the first
  and last one in reading order. Unaffected by this revision (gated on the
  same per-unit alignment/retention checks as before — see "Eligibility"
  below) — its numbers are unchanged: **58.8%** of the 51 multi-support
  eligible questions have zero intervening nodes between their first and
  last required unit; average LCA depth **1.12**.

## Alignment

Unchanged from the original corpus run — same normalizer, same
deterministic exact-token-containment rule, no fuzzy matching, no model
calls:

- **Source side**: gold `source_quote` -> exact token-sequence match in
  `source.md`. All 231 gold facts+relations across all 8 cases align
  exactly; zero corpus-integrity failures.
- **Gist side**: judge-recorded `evidence` -> exact token-sequence match in
  the rendering, including the multi-fragment (`"..."` / `" / "`) and
  marker-prefix handling described previously. 574/599 (95.8%) of
  `"retained"`-status evidence strings align exactly; the remainder are
  reported as `unaligned_in_rendering`, never fuzzy-matched.

This machinery is exactly what both `align_units_to_source` (feeding R)
and the diagnostic case-level baseline now share — refactored into one
function so the two paths can never silently diverge in what counts as an
alignment success.

## Eligibility

Strict scoring requires every unit in a question's `fact_ids` to be in R:
status exactly `"retained"`, source-aligned, and rendering-aligned. Any
failure marks the question `not_findability_scorable`, with the specific
reason(s) recorded per unit — never a silently shrunk required set. An
**exploratory** view (`"partial"` allowed alongside `"retained"`) is
computed and reported separately.

**This eligibility criterion is unchanged from the original run** — it was
never the confounded part; the confound was in what the baseline's
denominator was built from, not in which questions were scorable. Rerunning
the corpus under the corrected methodology therefore reproduces the exact
same eligibility numbers, re-derived directly from `results/findability.json`
(not carried over from the prior write-up):

**Corpus-wide strict eligibility: 156/264 (59.1%)** — identical to the
prior run.

| level | eligible | total | % |
|---|---|---|---|
| skim | 17 | 88 | 19.3 |
| standard | 61 | 88 | 69.3 |
| deep | 78 | 88 | 88.6 |

By test class: `pressure-tests` 111/192 (57.8%), `regression` 45/72
(62.5%).

## Results (re-derived from a from-scratch re-run of the corpus)

Full machine-readable output: `results/findability.json` — every
question's `unit_rank.strict`/`unit_rank.exploratory`, the diagnostic
`diagnostic_token_eac`, and each rendering's `retained_set.strict.excluded`
(why any given unit did not make it into R). Generated table:
`results/FINDABILITY_SCORES.md`. Regenerate with `python3
scoring/findability.py` (deterministic, no model/network/randomness).

### Headline: unit-rank EAC / locality span (strict-eligible only)

**By question type**

| question type | n | avg ΔEAC | avg Δlocality-span |
|---|---|---|---|
| factual | 108 | +0.0237 | +0.0086 |
| relational | 48 | **-0.0262** | +0.0013 |

**By support-unit count**

| support | n | avg ΔEAC | avg Δlocality-span |
|---|---|---|---|
| single | 105 | +0.0020 | +0.0000 |
| multi | 51 | **+0.0215** | +0.0194 |

**By granularity level**

| level | n | avg ΔEAC | avg Δlocality-span |
|---|---|---|---|
| skim | 17 | **+0.0147** | +0.0000 |
| standard | 61 | +0.0083 | +0.0103 |
| deep | 78 | +0.0070 | +0.0046 |

**By test class**

| class | n | avg ΔEAC |
|---|---|---|
| regression | 45 | +0.0029 |
| pressure-tests | 111 | +0.0105 |

**By question type × support-unit count** (the split that turned out to
matter — see "Reassessing the multi-support claim" below)

| type × support | n | avg ΔEAC |
|---|---|---|
| relational, single | 36 | **-0.0354** |
| relational, multi | 12 | +0.0016 |
| factual, single | 69 | +0.0214 |
| factual, multi | 39 | +0.0276 |

**By model, where both exist** (`cause-chain-reversal`, `migration-tristate`,
`synthetic-scale-verylarge`)

| model | n | avg ΔEAC |
|---|---|---|
| sonnet | 120 | +0.0057 |
| haiku | 36 | **+0.0171** |

### Diagnostic only: the old token-normalized, case-level-baseline metric

Kept for direct comparison, unchanged from the original run (byte-verified
identical — see "Verification"):

| question type | n | avg ΔEAC (diagnostic) |
|---|---|---|
| factual | 108 | +0.0251 |
| relational | 48 | -0.0369 |

## Reassessing the prior findings

The prior write-up's numbers were produced by a confounded baseline
(Failure mode 2) and are **not** treated here as a target the corrected
numbers need to reproduce. Each of the prior claims is checked directly
against the corrected, from-scratch numbers above.

**1. "Relational questions benefit more than factual questions."**
**Survives**, same sign, similar order of magnitude: relational -0.0262 vs.
factual +0.0237 (previously -0.0369 vs. +0.0251). The direction and rough
shape of this split hold under the corrected, compression-controlled
comparison.

**2. "Multi-support benefits more than single-support."** **Does NOT
survive — it reverses.** Previously multi -0.0123 (better) vs. single
+0.0150 (worse). Corrected: multi **+0.0215** (worse) vs. single +0.0020
(roughly neutral). Breaking this down further by type × support shows
*why*: the old multi-support number was almost entirely riding on
relational questions being disproportionately multi-support in the
uncorrected metric. Once the retained-unit set is held constant,
relational-single questions are the actual driver of the relational
benefit (-0.0354, n=36), while relational-multi is close to neutral
(+0.0016, n=12) and both factual buckets (single +0.0214, multi +0.0276)
are mild regressions of similar size. **Multi-support, independent of
question type, is not where the benefit lives — relational content is.**
This is a materially different, more precise claim than the prior one, and
the prior "multi-support benefits" framing is retracted, not merely
softened.

**3. "Skim regresses."** **Survives, but far more weakly than reported.**
Previously +0.0978 (the largest deviation from zero in the whole table).
Corrected: **+0.0147** — still the worst-performing level and still a
regression, but roughly 85% smaller. Most of the originally reported skim
penalty was an artifact of comparing skim's small gist against a
much-larger case-level all-gold baseline (Failure mode 2) — once both
sides are restricted to what skim actually retained, skim is a *mild* net
negative, not a dramatic one.

**4. "Standard is near-neutral."** **Does NOT survive.** Previously -0.0022
(essentially zero, slightly favorable). Corrected: **+0.0083** — a small
but real regression, not neutral.

**5. "Deep modestly improves."** **Does NOT survive — it reverses.**
Previously -0.0075 (the best-performing level). Corrected: **+0.0070** — a
small regression, in the same direction as skim and standard. Under the
corrected metric, **all three granularity levels show a mild net
regression** in unit-rank EAC; they differ mainly in how large that
regression is (skim worst, then standard, then deep), not in sign.

**Summary of what changed and why:** the previous per-level story
("skim bad, standard fine, deep good") was largely an artifact of
Failure-mode-2's baseline getting progressively less mismatched at higher
granularity (a `deep` rendering retains most of a case's gold content, so
its case-level-all-gold baseline was a much closer match to what the gist
itself held than `skim`'s was) — not evidence that deeper renderings
genuinely reorganize evidence better. Once the baseline is restricted to
exactly what each rendering retained, that gradient mostly disappears: all
three levels look similarly (mildly) worse for unit-rank EAC, and the
one clearly-surviving, mechanistically sensible signal is the
relational/factual split (claim #1), sharpened to specifically
relational-*single*-support questions (claim #2's replacement).

## Corpus conclusions (rewritten from the corrected numbers)

**1. For already-preserved information, does hierarchy reduce evidence-
access cost, holding retained content constant?** Mostly no, on average —
factual +0.0237, relational -0.0262. The overall picture is closer to "a
small net cost with one specific, real exception" than "small but positive
overall."

**2. Where is the exception?** Relational questions, and specifically
single-support relational questions (-0.0354, n=36) — not multi-support
questions in general (see reassessment #2 above). A single-support
relational question ("why did A cause B?" answered by one causal relation
unit) benefits from the relation being lifted near a well-organized
grouping; a multi-fact relational question spreads its benefit thin across
more required units and lands close to neutral (+0.0016).

**3. Does the surviving benefit hold after controlling for compression?**
**Yes — this is the entire point of the retained-unit-baseline exercise.**
Both sides of every comparison now hold the literal same set of semantic
units; only their order differs. Relational-single's -0.0354 cannot be
explained by "the gist is shorter" — a shorter gist's advantage is
already stripped out by construction (both sides are ranked over the same
`|R|`).

**4. Which granularity mode is worst?** Skim, by a real if now much
smaller margin (+0.0147 vs. standard +0.0083 vs. deep +0.0070) — but,
unlike the prior write-up, deep does not "win"; it is simply the least-bad
of three mild regressions, not a genuine improvement.

**5. Is there a model difference?** A new cut this revision adds: on the
three cases judged under both models, Haiku shows a larger average
regression (+0.0171, n=36) than Sonnet (+0.0057, n=120) — consistent with,
though not proof of, Haiku's renderings reorganizing retained evidence less
favorably. Too small an n (36) to treat as more than a suggestive
secondary observation; flagged here rather than folded into the headline
claim.

**6. Is the deterministic proxy strong enough to keep as a regression
metric?** Not yet, on its own, as a pass/fail gate — same conclusion as
before, now on firmer ground: only 59.1% of combinations are
strict-scorable, and the one surviving directional claim (relational-
single) is a narrower slice of the data (n=36) than the previous, broader
"relational or multi-support" framing (n=51+48 combined, overlapping). It
is, however, worth watching **the relational-single-support ΔEAC** as a
narrower, more honest regression signal than before, plus the eligibility
rate itself as a cheap check that retention hasn't regressed enough to
break this eval's ability to measure anything.

**7. Would a later human timing study be worth doing?** Yes, and now
specifically targeted at the *narrower* surviving claim — single-support
relational questions — rather than "relational and/or multi-support" in
general, since the multi-support half of that prior claim did not survive
independent scrutiny.

## Pressure checks (actively tried to falsify this measure)

- **Shorter output getting a free advantage** — this is now addressed
  structurally, not just by design intent: R is built from what each
  specific rendering retained, so a shorter gist's denominator (`|R|`) is
  exactly as small as the units it actually kept and could align — it
  gets no additional advantage from being compared against a
  larger, unrelated baseline (that was precisely Failure mode 2, now
  fixed).
- **Evidence near the beginning of source making hierarchy look worse
  unfairly** — `test_single_required_unit_moved_earlier_in_gist_improves_
  eac` and its mirror `test_single_required_unit_moved_later_in_gist_
  regresses_eac` (and the locality-span pair
  `test_two_required_units_clustered_closer_in_gist_improves_locality_
  span` / `test_two_required_units_spread_farther_in_gist_regresses_
  locality_span`) confirm the metric responds correctly to both
  directions using hand-computed ranks.
- **The old "multi-support benefits" claim being a confound of question
  type, not support count** — checked directly and confirmed: see
  "Reassessing the multi-support claim" above and the type × support
  cross-tab. This is exactly the kind of thing this pressure-check
  section exists to catch, and it was caught by re-deriving the numbers
  from scratch rather than assuming the prior split would hold.
- **Omitted evidence being rewarded** — cannot happen by construction: a
  unit whose status is not `"retained"` (strict) is excluded from R
  entirely (`test_deleted_unit_absent_from_both_orderings`,
  `test_omitted_required_unit_makes_unit_rank_question_ineligible`).
- **A fact and a relation sharing a source span silently merging into one
  unit** — checked directly:
  `test_relation_and_fact_sharing_source_span_remain_separate_units`
  proves both remain distinct, separately-ranked units even when their
  spans are identical.
- **Ties (same source position, or same gist position) depending on
  incidental JSON/dict order** — checked directly:
  `test_ties_at_same_source_position_break_by_unit_id`,
  `test_ties_at_same_gist_position_break_by_unit_id`, and
  `test_deterministic_ordering_regardless_of_dict_insertion_order` all
  pass with retained-set dicts built in scrambled insertion order.
- **Normalized position hiding large absolute traversal differences** —
  same caveat as before: this eval reports only normalized (0-1)
  fractions. `results/findability.json` retains `gist_token_count` and
  each rendering's `retained_set.*.size` (`|R|`) for anyone who wants to
  re-weight by absolute scale.

## Promotion classification

**B — useful experimental metric; not yet a durable regression gate, and
narrower than previously believed.** The corrected methodology is stronger
in one specific sense (the comparison is now genuinely compression-
controlled — both sides hold the literal same retained units) but the
corpus-level story is *less* uniformly favorable than the prior write-up
suggested: the granularity gradient (skim bad, deep good) and the
multi-support claim both do not survive independent scrutiny, leaving only
the relational/factual split — sharpened to relational-single-support
specifically — as a claim with a clean, mechanistically sensible,
directionally consistent, and now compression-controlled basis. That is
still a real and interesting result, but it is a narrower one than
previously claimed, obtained only after finding and fixing a *second* real
baseline confound. Promotion to A would need: more cases (8 is small for
a metric with this much per-question variance), confirmation that the
relational-single-support benefit replicates on a larger corpus, and
likely the human-timing validation flagged in reassessment item #7 before
trusting the proxy alone as a gate.
