# Semantic-compression: durable findings and curation record

This is a condensed record of a round-1 exploratory experiment (11 cases,
skim/standard/deep, two model tiers, full write-up since removed — this
file is the durable replacement, not a museum of the original). It exists
to explain *why* the 8 cases in `regression/` and `pressure-tests/` were
kept and what each one is protecting or provoking. See `README.md` for how
to use the suite day to day.

## 1. The lesson that motivated this suite

The round-1 experiment set out to answer: *does semantic compression add
signal beyond structural conformance and word-count reduction?* It did,
but not in the shape originally expected — the exploration's own headline
result argues against the metric family it set out to build:

- **Compression correlates negatively with usefulness.** Across all 45
  (case, tier, level) rows measured in round 1, raw compression
  (`reduction_pct`) correlated with recoverability at **r = -0.75**, and
  every "meaning-per-word" density formula tried (weighted units / 100
  output words, a mutation-penalized variant, a recoverability-per-word
  variant, retention-per-compression-ratio) was **also negatively
  correlated** (r = -0.18 to -0.27), while plain weighted retention
  correlated at **r = 0.94**. A composite that divides meaning by size
  rewards `skim` for saying almost nothing, not for being useful.
  **Conclusion baked into this suite: compression is reported as its own
  number (a cost/rate), never folded into a "quality per word" score.**
- **Structural conformance stayed a weak predictor of meaning** (r ≈
  0.2–0.25 against retention/relation-retention/recoverability),
  confirming it belongs as a pass/fail gate, not a score that trades off
  against semantic quality — this suite keeps that split.
- **Omission and relation-loss were the real failure modes here, not
  mutation.** Across every fact judged in the retained cases (and in the
  cases removed, per §3), not one was ever marked "present but meaning
  changed." Failures were either *silence* (omission, expected and
  heaviest at `skim`) or a flattened structure that dropped a relationship
  while keeping both its endpoints (see `causality-heavy-explain` below) —
  never a silently altered fact.
- **The skim→standard jump carries almost all the retention value.** Mean
  weighted retention across the original 11-case corpus: skim 0.37,
  standard 0.89, deep 0.99. Standard→deep buys a further ~0.10 retention
  for real word-count cost; skim→standard buys ~0.52. This suite's
  regression baselines are set at `standard`/`deep`, not `skim`, for
  exactly this reason — `skim` is *supposed* to lose most things, so a
  regression check there mostly measures noise, not degradation.
- **Pressure tests report a diagnostic verdict per case, not an averaged
  score.** A relation-collapse case that scores badly on relation
  retention while scoring fine on fact retention is *working as a
  pressure test* — averaging those two numbers into one would hide the
  exact thing the case exists to show.

These are evaluation principles for how this suite is read and extended.
They are not new normative rules for `SKILL.md` or the linter, and none of
`SKILL.md`, the linter, or the grammar changed as a result of this
curation.

## 2. Hallucination correction

Round 1's isolated judges (correctly, by design) never saw `source.md` —
only `gold.json` and the outline — so "no matching gold fact" was the only
signal available for flagging a claim as unsupported. That signal is
wrong: gold is a curated, weighted subset of the source (12–46 facts per
case, biased toward decisions/constraints/negations/causes/outcomes/
failures/questions/actions), not an exhaustive transcript of it. Anything
true-but-low-value that gold didn't bother extracting looks, to a
source-blind judge, identical to an invented claim.

Verification: every one of the 20 hallucination flags surviving into the 8
retained cases was checked directly against its `source.md` by exact or
near-exact substring match. **All 20 were verbatim or near-verbatim source
text** — e.g. `cause-chain-reversal`'s outline saying on-call "spent the
first twenty minutes" on the wrong theory and pulled "query-level tracing"
is literal source wording; `synthetic-scale-verylarge`'s "CPU spike during
a traffic burst" and "cache layer serving outdated pricing data" are exact
source phrases. **Corrected unsupported-claim count for this suite: 0.**

Each retained `judged/<tier>.json` now carries `source_supported: true` on
every one of those 20 entries; `scoring/combine.py` only counts
`source_supported: false` entries toward the canonical
`unsupported_claim_count`. See `README.md`'s correction section for the
protocol to use if this suite is re-judged in the future (give the
unsupported-claim check, and only that check, access to `source.md`).

## 3. What was removed and why

Round 1 built 11 cases; 3 were cut as redundant with a case that tests the
same failure mode more sharply, per "if two cases test essentially the
same failure mode, keep the stronger one":

- **`synthetic-scale-large`** (large synthetic multi-thread recap) — same
  failure family as the retained `synthetic-scale-verylarge`
  (structural-complexity-at-scale, model-sensitivity), without the buried-
  critical-failure hook that makes the very-large case a sharper, more
  diagnostic pressure test. Its own round-1 result (sonnet `skim`
  collapsing to 0.0 weighted retention, pure section labels) is already
  echoed, less starkly, by the case kept.
- **`superseded-decision`** (an early decision explicitly reversed later)
  — the same failure mode as the retained `cause-chain-reversal`
  ("supersession or root-cause reversal" is one bullet in the original
  brief, not two), and `cause-chain-reversal` is the richer case (20 facts
  vs. 14, 6 relations vs. 5, plus the only pressure test with dual-tier
  haiku data showing a much sharper skim-level capability gap).
- **`already-structured-changelog`** (a source that's already a terse
  list) — its interesting property, "don't invent false hierarchy over
  genuinely flat content," is already covered by the retained
  `negation-and-true-peers`, which tests the same thing (flat true peers)
  plus negation preservation in one case.

Also removed as scaffolding that would confuse a future maintainer about
what's canonical, not as evidence:
- The flat `corpus/` / `renderings/` / `judged/` top-level layout (11
  cases' worth) — superseded by the per-case `regression/<id>/` and
  `pressure-tests/<id>/` layout, which answers "which class is this"
  without cross-referencing a separate index.
- The original `REPORT.md` (~770 lines) and `results/REPORT_TABLES.md` —
  their substance is either obsolete (density-formula comparisons this
  suite explicitly rejects, per §1) or preserved here in compressed form.
  This file and `README.md` are the durable replacements.
- The 4 candidate density formulas (`sem_density_100`,
  `net_sem_density_100`, `recoverability_density_100`,
  `retention_per_compression`) — removed from `scoring/combine.py`
  entirely, not merely unused, per §1's finding that all four are
  negatively correlated with usefulness. Do not re-add a density
  composite without new evidence that overturns that finding.

## 4. Model-sensitivity evidence (why 3 pressure tests carry a haiku tier)

| case | level | conformance violations (sonnet) | conformance violations (haiku) | wRetention (sonnet) | wRetention (haiku) |
|---|---|---|---|---|---|
| `cause-chain-reversal` | deep | 0 | 8 | 1.00 | 0.83 |
| `migration-tristate` | deep | 0 | 20 | 1.00 | 0.99 |
| `synthetic-scale-verylarge` | deep | 2 | 43 | 0.99 | 0.91 |

The breakpoint shows up on the **conformance** curve (mechanical
line-wrap/depth-ladder discipline, R11/R1/R7) well before the **retention**
curve — a weaker model at `large`+ scale still says approximately the
right things but reliably fails to format them per the grammar's rungs.
This is the concrete evidence for keeping haiku renderings on exactly
these 3 cases rather than adding a general cross-model sweep.

## 5. Protocol used to produce the current canonical files

For reproducibility, not because this suite runs it automatically:
1. **Generation**: a fresh subagent per (case, tier), with no prior
   context, reads `SKILL.md` cold and `source.md`, and writes block-mode
   `skim.md`/`standard.md`/`deep.md` — never hand-authored by whoever wrote
   the gold data, to avoid grading the grammar against itself.
2. **Judging**: a fresh, isolated subagent per (case, tier) reads
   `gold.json` and the three renderings only (never the source), and
   scores every fact/relation/question with a required evidence quote.
3. **Unsupported-claim correction**: every flagged claim was separately
   checked against `source.md` directly (§2) — this step is the one
   place source access is required, and is why it is kept as a distinct
   pass rather than folded into step 2's source-blind judging.
4. **Scoring**: `scoring/deterministic.py` (word counts, compression,
   linter gate) and `scoring/combine.py` (retention/relation/
   recoverability/unsupported-claim arithmetic) are deterministic, source
   is unchanged, and rerunning them against the same `renderings/`+
   `judged/` files reproduces `results/` byte-for-byte.

## 6. Intent metadata and measurement-vocabulary correction (two follow-up PRs)

**PR A** added case-level intent metadata on top of this document's
`weighted_retention` number, without changing the arithmetic in §1 or any
score recorded above:

- Each case's `gold.json` gained an `intent` (reader/task, optional
  rationale) so a fact's `weight` has an explicit referent: what it is
  *supposed* to encode importance for. The category buckets this file and
  `README.md` describe remain a default for hand-authoring a new case, not
  a claim that every fact in a category is equally important.
- That PR also introduced a `semantic_sufficiency` scored key, aliased to
  `weighted_retention` — reviewed and corrected by **PR B**, below, before
  merge, because adding `intent` after the fact does not prove the
  existing weights were actually derived from it, and the name
  `semantic_sufficiency` claimed more than the arithmetic supported (see
  `README.md` "Semantic sufficiency vs. task-weighted fact retention").

**PR B** (this correction) renamed that scored key to
`task_weighted_fact_retention` — the precise claim: retained gold facts,
weighted for importance, nothing about relationship preservation or task
completion, never divided by compression. `semantic_sufficiency` is no
longer emitted as a scored key at all; "semantic sufficiency" now names
only the broader, multi-dimensional evaluation question (task-weighted
fact retention + relation retention + recoverability + source support +
conformance + compression cost, reported as a profile, never combined).
PR B also:

- documented, in `README.md` "Weight semantics", that this corpus's
  weights were assigned primarily by the category-default heuristic, not
  derived per-case from `intent` — with `regression/near-identical-numbers`
  as a concrete counterexample (exact-identifier facts still sit at
  category-default weight `1` despite a task of precise identifier recall);
- left every existing `weight` value in every `gold.json` unchanged — this
  is a measurement-vocabulary and safety correction, not a reweighting, and
  a genuine re-annotation is deferred to the blinded experiment `README.md`
  describes under "Next experiment: blinded task-weight re-annotation";
- changed `score_semantic()`'s empty-fact-list behavior from `0.0` to
  `None`/`null` (a case with no gold facts is "not applicable", not "0% of
  meaning survived") — this suite has no zero-fact case today, so no
  existing score is affected;
- hardened `unsupported_claim_count` so a hallucination entry missing
  `source_supported` (not yet checked against `source.md`) counts toward a
  new `unverified_claim_count` instead of silently reading as "confirmed
  unsupported" — every entry in this corpus's current `judged/*.json`
  already carries an explicit `source_supported` value, so this is also a
  safety net, not a change to any existing number.

No case's `weighted_retention`/`task_weighted_fact_retention` value changed
as a result of either PR — `results/combined.json`'s diff across both is
additive keys only (`intent`, then `task_weighted_fact_retention` replacing
`semantic_sufficiency`, plus `unverified_claim_count`).
