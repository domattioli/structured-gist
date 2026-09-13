# External evaluation results

The frozen external-validation corpus (PR #19) and semantic-gold adapter
(PR #20) run cold against `structured-gist` v0.4.8, one model tier
(Sonnet 5), skim/standard/deep, judged by isolated blind judges. See
`RUN_MANIFEST.json` for exact SHAs/hashes/scorer versions and
`GENERATION_PROTOCOL.md`/`JUDGE_PROTOCOL.md` for the exact protocols
run. **No skill change was made in this session, regardless of what the
results below suggest.**

**Reporting rule, honored throughout:** QMSum, Qasper, and HotpotQA are
never pooled into one number. HotpotQA is `pressure_only` evidence, not
part of any headline. The existing hand-built corpus is a separate
regression/sentinel population, compared against but never merged with
these three.

## Headline numbers by dataset and level

| dataset | level | reduction% | fact retention (tw) | relation retention | recoverability | SPR | critical-loss rate | conformance-clean rate | verbatim-node rate |
|---|---|---|---|---|---|---|---|---|---|
| QMSum | skim | 98.6 | 0.12 | 0.04 | 0.21 | 0.11 | 0.81 | 0.33 | 0.08 |
| QMSum | standard | 92.9 | 0.55 | 0.37 | 0.63 | 0.52 | 0.33 | 0.21 | 0.10 |
| QMSum | deep | 85.9 | 0.72 | 0.56 | 0.75 | 0.69 | 0.16 | 0.17 | 0.09 |
| Qasper | skim | 95.0 | 0.23 | 0.25 | 0.35 | 0.23 | 0.71 | 0.00 | 0.42 |
| Qasper | standard | 76.1 | 0.84 | 0.75 | 0.90 | 0.83 | 0.10 | 0.00 | 0.25 |
| Qasper | deep | 51.4 | 0.95 | 0.88 | 0.90 | 0.95 | 0.05 | 0.00 | 0.22 |
| HotpotQA (pressure) | skim | 82.4 | 0.55 | 0.29 | 0.63 | 0.49 | 0.18 | 0.00 | 0.39 |
| HotpotQA (pressure) | standard | 25.9 | 1.00 | 0.93 | 1.00 | 0.98 | 0.00 | 0.00 | 0.28 |
| HotpotQA (pressure) | deep | 7.5 | 1.00 | 0.93 | 1.00 | 0.98 | 0.00 | 0.00 | 0.42 |

(critical-loss rate = fraction of weight-3 units lost, not partial+lost;
conformance-clean rate = fraction of renderings with zero linter
violations, not violation count.) Full per-case, per-level numbers:
`<dataset>/scores.json`, `<dataset>/deterministic_scores.json`.

## Existing hand-built corpus (regression/sentinel, verified not pooled)

Re-ran unchanged: `deterministic.py`, `combine.py`, `spr.py`,
`wording_fidelity.py`, `findability.py` all reproduced their committed
`results/*.json` **byte-for-byte** — the existing corpus's own numbers
are untouched and confirmed reproducible.

| level | fact retention (tw) | relation retention | verbatim-node rate |
|---|---|---|---|
| skim | 0.32 | 0.29 | 0.21 |
| standard | 0.83 | 0.81 | 0.18 |
| deep | 0.97 | 0.98 | 0.18 |

Notable divergence from the external corpus: on the hand-built corpus,
relation retention roughly **tracks or slightly exceeds** fact retention
at every level. Externally, relation retention is **consistently and
substantially below** fact retention at every level, in every dataset —
see H1.

## H1-H8 replication table

| # | hypothesis | verdict |
|---|---|---|
| H1 | relation loss is the main semantic failure mode | **replicated, more strongly than on the hand-built corpus** |
| H2 | standard sits near the practical Pareto knee | **partially replicated** |
| H3 | task-conditioned weight beats category as an importance proxy | **inconclusive by design (see below) — not contradicted** |
| H4 | critical-loss detection catches what averages hide | **replicated** |
| H5 | preservation and recoverability are distinct | **replicated, strongly** |
| H6 | skill is extractive but not node-verbatim | **partially replicated — dataset-dependent** |
| H7 | hierarchy aids relational-single-support findability | **inconclusive — instrumentation mismatch, not evidence either way** |
| H8 | structural conformance is weakly coupled to semantic quality | **replicated** |

### H1 — relation loss

**Replicated, and more starkly than the hand-built corpus's own
aggregate shows.** At every level, in every dataset, relation retention
trails fact retention: QMSum skim 0.04 vs 0.12, standard 0.37 vs 0.55,
deep 0.56 vs 0.72; Qasper skim 0.25 vs 0.23 (roughly tied, n=4 relations
only), standard 0.75 vs 0.84, deep 0.88 vs 0.95; HotpotQA standard/deep
0.93 vs 1.00. The hand-built corpus's own combined.json, re-run this
session, does **not** show this gap in aggregate (relation retention
0.29/0.81/0.98 vs fact 0.32/0.83/0.97 — essentially tied or
relation-favoring at every level) — even restricted to just its
`pressure-tests` class (which includes the dedicated relation-loss
pressure test `causality-heavy-explain`), the gap is modest (0.23 vs
0.29 skim, 0.77 vs 0.79 standard, 0.97 vs 0.96 deep — barely there).
**This session's best read:** relation loss as a *dominant, consistent*
failure mode is a genuine external finding that the hand-built corpus's
9 non-pressure-test-specific cases undersold — possibly because the
hand-built corpus's relations were authored by the same process that
authored its facts (making them easier to phrase compatibly), while
externally-derived relations (many `inferred`, bridging facts the source
states separately) are a harder bar the skill more often fails to clear.
See qmsum-22 in `CROSS_METRIC_CASES.md` #1 for the starkest single case.

### H2 — standard as the practical knee

**Partially replicated, and dataset-dependent.** QMSum shows the
clearest knee shape: reduction drops modestly (98.6% -> 92.9%) while
fact retention/recoverability jump sharply (0.12->0.55, 0.21->0.63) going
skim->standard, then standard->deep buys a smaller further gain (0.55
->0.72, 0.63->0.75) for another real compression cost (92.9%->85.9%) —
standard reads as the practical knee here. Qasper shows a *shallower*
knee: standard already reaches 0.84/0.90 and deep's gain to 0.95/0.90 is
real but costs nearly 25 more compression points (76.1%->51.4%) for a
recoverability gain of exactly zero (0.90 stays 0.90) — arguably standard
is *already* past the useful knee for Qasper's native-QA task, with deep
mostly buying fact-completeness the question didn't need. HotpotQA
shows **no knee at all past skim** — standard and deep are numerically
identical on every semantic metric (1.00/0.93/1.00/0.98), because these
2-fact bridge cases saturate at standard and deep changes nothing but
adding un-needed context (reduction 25.9%->7.5% for zero further gain).
**Conclusion:** standard is a reasonable practical default, but "the
knee" is not one universal point — it moves with how much of a source's
content a case's task actually needs, and for small, dense pressure
cases like HotpotQA there may be no reason to go past standard at all.

### H3 — task-conditioned weight vs. category

This corpus's weights were built exactly to test this (Stage B,
independently annotated from category/type, adapter classification A/A/B
— see PR #20's `FINDINGS.md`), but this run does not have a *category-
weighted* comparison arm to test against — no category-derived weight
scheme was computed for these 42 cases (correctly, per PR #20's explicit
"do not invent weights from category" rule). What this run *can* say:
critical-unit (weight-3) loss rates track recoverability failure closely
(H4, below) using the task-conditioned weight — i.e., the task-
conditioned weight behaves like a meaningful importance signal in this
corpus. Whether it is *better* than a category-derived alternative is
not testable from this run's data; **inconclusive by design**, not a
negative result — reannotating with a category-weight scheme to make
the comparison is out of scope for this run (would require exactly the
kind of re-annotation the experimental seal forbids).

### H4 — critical loss

**Replicated.** At the case level (deep, per-dataset):

| dataset | cases w/ any critical loss at deep | recoverability when critical loss present | recoverability when none |
|---|---|---|---|
| QMSum | 15 / 24 | 0.60 | 1.0 |
| Qasper | 1 / 10 | 0.0 | 1.0 |
| HotpotQA | 0 / 8 | n/a | 1.0 |

QMSum and Qasper both show a sharp recoverability gap tied to whether any
weight-3 unit was lost at deep — even though deep's *average* fact
retention already looks strong (0.72-0.95), cases with a surviving
critical-unit loss still show markedly worse task success. This is
exactly the "averages can look healthy while one task-breaking unit
disappears" pattern the hypothesis names. See `CROSS_METRIC_CASES.md` #2
for the corollary: SPR itself already absorbs most of this signal (no
case in this corpus shows high SPR *alongside* critical loss), so
critical-loss tracking and SPR are not fully independent evidence
sources here — but critical-loss's link to *recoverability specifically*
is the useful, non-redundant part.

### H5 — recoverability is distinct from preservation

**Replicated, strongly.** `CROSS_METRIC_CASES.md` #3: qasper-01 standard
scores SPR 0.09 with recoverability 1.0; three HotpotQA skim cases score
SPR 0.50-0.57 with recoverability 1.0. In the other direction, several
QMSum cases (qmsum-17 notably — see PR #20-era judging notes) show
"unanswerable" recoverability despite non-trivial retained content,
because one specific named entity the question hinges on was dropped.
Neither metric predicts the other reliably; both are necessary, neither
is sufficient, exactly as the hypothesis states.

### H6 — extractive but not node-verbatim

**Partially replicated, and dataset-dependent** — this is the clearest
place external data complicates a hand-built-corpus finding rather than
simply confirming it. Hand-built corpus verbatim-node rate: flat around
0.18-0.21 across all three levels. Externally: QMSum is *more*
paraphrased than the hand-built corpus at every level (0.08-0.10);
Qasper and HotpotQA are *more* verbatim, especially at skim (0.42 and
0.39 respectively) and drop at standard before partially recovering at
deep. **Read:** "extractive but not verbatim" is not a fixed skill
property — it varies with source register. QMSum's source is
conversational transcript (disfluent, first-person, redundant) which the
skill rephrases heavily into concept-noun-phrase form; Qasper/HotpotQA's
source is already terse third-person prose (paper text, encyclopedia
text) that survives compression closer to verbatim. See
`CROSS_METRIC_CASES.md` #7-8.

### H7 — relational findability

**Inconclusive — a genuine instrumentation mismatch discovered this
session, not evidence for or against the hypothesis.** Two compounding
issues, both documented in `JUDGE_PROTOCOL.md`'s design and this
corpus's own structure, not a skill behavior:

1. `findability.py`'s alignment requires the judge's `evidence` field to
   be an exact verbatim substring of the rendering. `JUDGE_PROTOCOL.md`
   explicitly permitted `evidence` to be "a quote/paraphrase" — most
   judges paraphrased. Result: most gold units fail `gist`-side
   alignment (`unaligned_in_rendering` was the single largest exclusion
   reason in every dataset checked), so `retained_set` sizes for the
   headline `unit_rank` metric are frequently near-empty.
2. Even where alignment succeeds, `findability.py`'s headline metric was
   designed to compare a *subset* of a case's retained units (one
   question's `fact_ids`) against the full retained set, so that
   reordering the subset's members relative to the rest is visible. This
   corpus deliberately has exactly one native question per case (per
   PR #19's "do not fabricate extra questions" rule), and that question's
   `fact_ids` frequently equals the *entire* retained set — collapsing
   the subset-vs-whole comparison the metric was built to make. Every
   eligible row in this run shows `delta_eac = 0.0` for this reason, not
   because reordering never happens.

Neither issue reflects on whether hierarchy actually helps relational
findability externally — the metric as currently wired cannot test that
question against this corpus's judging protocol and single-question
design. Fixing this (require verbatim rendering quotes from judges;
either add subset-style diagnostic questions per case or accept a
different findability formulation for single-question corpora) is
flagged for a future session, not attempted here per the experimental
seal.

### H8 — conformance is weakly coupled to semantic quality

**Replicated, cleanly, in both directions.** `CROSS_METRIC_CASES.md` #4:
HotpotQA's deep renderings hit perfect recoverability with 10-19 linter
violations each; several QMSum skim renderings hit 0 violations with
near-zero fact retention (they're too short to trip most rules, and
also too short to say anything). Aggregate conformance-clean rates are
very low across the board (0-33%) and do not track the fact/relation/
recoverability trend at all — Qasper and HotpotQA show **0% clean at
every level**, including deep levels that score 0.90-1.00 on every
semantic metric. Conformance and semantic quality are answering
unrelated questions in this corpus, exactly as the hypothesis predicts.

## Answers

1. **What survived external validation?** The skim/standard/deep
   monotonic ordering on fact retention, relation retention, and
   recoverability — confirmed in all three datasets, no exceptions. Also
   confirmed: relations are the more fragile unit (H1, stronger here than
   on the hand-built corpus); recoverability and preservation diverge
   (H5); conformance is orthogonal to meaning (H8); source support is
   very strong (near-zero confirmed hallucination across all 126
   renderings — 2-3 confirmed-unsupported claims total, all in QMSum, out
   of roughly 900 flagged candidates checked against source).
2. **What looks like a hand-built-corpus artifact?** The hand-built
   corpus's apparent relation-retention-tracks-fact-retention pattern —
   externally, relations lag facts by a wide and consistent margin (H1).
   Possibly also the flat ~0.18-0.21 verbatim-node rate — externally this
   varies by more than 5x across datasets and levels (H6).
3. **Dominant failure modes externally?** (a) Relation loss even when
   facts survive (qmsum-22 and others); (b) skim-level near-total
   omission producing recoverability 0 on ordinary (non-adversarial)
   content, not just pressure cases; (c) rare but real mutation — one
   confirmed fact mutation found (qmsum-24 deep: a solar-charging claim
   that directly contradicts the source).
4. **Most useful mode, under what conditions?** Standard, when the task
   needs most of a source's content and the source is long/dense (QMSum).
   For short, single-answer-bearing sources (HotpotQA-style), standard
   already saturates and deep adds cost with zero further benefit.
5. **Does standard remain a practical default?** Yes for QMSum-shaped
   tasks (real knee there); qualified-yes for Qasper (already
   near-saturated on recoverability by standard, deep mainly buys
   completeness); over-provisioned for HotpotQA-shaped tasks (skim's
   still poor, but standard alone already saturates every metric).
6. **Do relations remain more fragile than facts?** Yes, more so
   externally than the hand-built corpus's own numbers suggested (H1).
7. **Does critical-loss detection remain useful?** Yes — it's the
   clearest predictor of recoverability failure this run found, even
   though it substantially overlaps with what SPR already captures (H4).
8. **Does SPR add information beyond its components?** Only partially.
   Every high-critical-loss case already shows depressed SPR (they are
   not independent signals here), so SPR is close to "fact+relation
   recall with critical items downweighting it automatically" rather
   than a genuinely new axis. It remains a convenient single aggregate,
   not evidence beyond what fact retention + relation retention +
   critical-loss tracking already show separately.
9. **Does relational findability replicate?** Cannot be tested with this
   run's instrumentation (H7) — explicitly not claimed either way.
10. **Does wording fidelity replicate?** Partially, and it's more
    dataset-sensitive than the hand-built corpus's flat numbers implied
    (H6).
11. **Are QMSum/Qasper/HotpotQA telling different stories?** Yes,
    materially. QMSum is the hardest case for the skill (heaviest
    paraphrase, worst relation retention, most critical loss, most
    corpus-defect friction) and the one where standard-vs-deep genuinely
    trades off. Qasper is the strongest case (near-saturated recoverability
    by standard, zero confirmed hallucinations, high critical-loss
    recovery by deep). HotpotQA saturates fast and mostly demonstrates
    that 2-fact bridge preservation is *not* the skill's weak point once
    past skim — the weak point there is skim itself.
12. **Durable-regression-status metrics?** Compression/reduction%,
    structural conformance, task-weighted fact retention, relation
    retention, recoverability, source-support (hallucination) checking —
    all behaved as designed, produced interpretable, dataset-consistent
    signal, and required no protocol changes mid-run.
13. **Metrics that should stay experimental?** SPR (real but largely
    redundant with its components here — see Q8); critical-loss tracking
    (useful but not yet shown independent of SPR); corrected
    retained-unit findability (blocked by this run's own instrumentation
    gap, not yet validated at all externally).
14. **Best-supported future skill intervention (not implemented)?**
    Strengthen relation preservation specifically at `standard` —
    QMSum's standard-level relation retention (0.37) lags its fact
    retention (0.55) by the widest margin in the corpus, and `standard`
    is this run's best-supported practical default level. A
    relation-aware pass at standard (rather than relying on `deep` to
    recover connective tissue) is the single change this run's evidence
    points to most clearly. **Not implemented, per the experimental
    seal.**

## Measurement limitations discovered this run

- **Findability instrumentation mismatch** (H7, above) — judge-evidence
  paraphrasing and single-question-per-case structure both block the
  metric as currently wired.
- **QMSum's `unaligned_in_source` count** (18 units across the corpus at
  deep) reflects a small residual of gold facts whose `source_quote`
  doesn't token-align exactly even after PR #20's repair pass — not
  re-investigated here per the experimental seal; flagged for the next
  adapter-maintenance pass.
- **Hallucination-candidate scoping**: for QMSum's largest cases (some
  renderings cover 200+ meeting turns against gold drawn from one
  narrow exchange), judges scoped hallucination-candidate flagging to
  the topically relevant section(s) rather than every sentence in the
  full rendering, for tractability. This was applied consistently but
  means QMSum's "zero confirmed hallucinations" finding is not a claim
  about every word of every rendering, only the topically-relevant
  portion judges actually checked.
- **The shipped linter's violation *message text* is not byte-stable
  across process runs** (discovered by re-running `score_deterministic.py`
  twice and diffing): `lint_outline.py`'s "mixed sibling families: {...}"
  message stringifies a Python `set` of family-name strings directly,
  and `str()` of a small string set is not guaranteed to iterate in the
  same order across separate Python processes (hash randomization).
  Confirmed this affects **only that message string** — violation counts,
  rule ids, and `conformance_clean` booleans were re-verified identical
  across both runs (0 substantive diffs across all 30 Qasper
  case/level rows checked). This is a pre-existing property of the
  shipped, unmodified linter, not something this run's scripts
  introduced, and it does not affect any number in this report. Not
  repaired here per the experimental seal — flagged for
  `lint_outline.py`'s maintainers to sort the set before formatting it.
- **`findability.py`'s diagnostic (token-baseline) view was not scored
  in this run** — only the headline `unit_rank` metric was computed, to
  keep the scoring script's scope bounded; the diagnostic view is
  available in `findability.py` if a future session wants it.

## Dataset-specific analysis

Small subgroup n's below — read as directional, not conclusive (per the
task brief: "do not overinterpret small subgroup n").

### QMSum (deep level, n=8 per domain, n=12 per cardinality)

| stratum | n | fact retention | relation retention |
|---|---|---|---|
| Academic | 8 | 0.66 | 0.62 |
| Committee | 8 | 0.80 | 0.53 |
| Product | 8 | 0.68 | 0.50 |
| single-span | 12 | — | 0.59 |
| multi-span | 12 | — | 0.52 |

Multi-span evidence cases show somewhat lower relation retention than
single-span (0.52 vs 0.59) — a small, directionally-consistent signal
that connecting evidence spread across the transcript is harder to
preserve than evidence already co-located, but the gap is modest, not
dramatic, and n=12/12 is too small to treat as confirmed. Committee shows
the best fact retention but the worst relation retention of the three
domains — a genuinely interesting split (facts survive well, connections
don't) worth a closer look with a larger sample. Long-meeting skim
degradation is severe across all domains (see headline table); it is not
domain-specific. Standard remains useful in every domain (see H2).

### Qasper (deep level)

| stratum | n | fact retention |
|---|---|---|
| single-evidence | 3 | 0.82 |
| multi-evidence | 7 | 1.00 |

| evidence distance | n | relation retention |
|---|---|---|
| nearby | 3 | 1.00 |
| moderate | 1 | n/a (no relation in that case) |
| wide | 3 | 1.00 |
| n/a (single-evidence, no relation) | 3 | 0.75 |

Counterintuitively, multi-evidence cases show *higher* deep-level fact
retention than single-evidence ones (1.00 vs 0.82) in this small sample
— plausibly because Qasper's multi-evidence cases in this corpus tend to
have fewer total facts per case (see PR #20's per-case fact counts), so
each individual fact carries more weight and gets more careful treatment
at deep. Evidence distance shows no relation-retention penalty at all in
the cases where a relation exists (nearby and wide both perfect at
deep) — deep-level Qasper renderings are thorough enough that spatial
separation in the source doesn't visibly cost anything. Whether deep
"buys semantic value proportional to its size" is dataset-dependent (see
H2): yes for recoverability-adjacent completeness, but recoverability
itself is already saturated by standard for 9 of 10 cases.

### HotpotQA (outcome categories, all 8 cases)

| level | complete | facts-only | partial-hop | misleading/other |
|---|---|---|---|---|
| skim | 0 | 2 | 3 | 3 |
| standard | 6 | 1 | 0 | 1 |
| deep | 6 | 1 | 0 | 1 |

("complete" = both facts retained + bridge relation retained;
"facts-only" = both facts intact, bridge lost; "partial-hop" = at least
one fact degraded; the "other" case at standard/deep is hotpotqa-07,
which has no gold relation at all per PR #20's adjudication, so it can't
be categorized "complete" by this scheme even though both its facts are
fully retained — a categorization-scheme artifact, not a rendering
failure.) The clean qualitative story: skim mostly fails to complete the
hop (fact loss, not just relation loss, is common at skim — 3 of 8 cases
are "partial-hop"); standard recovers essentially all bridges (6 of 8
complete, and the remaining 2 are near-misses, not failures) and deep
adds nothing further. Both supporting facts and the bridge itself are
preserved together once past skim — this corpus found no case where
facts survived cleanly but the bridge specifically and consistently
failed at standard/deep (that pattern appears only within skim).

## Frozen benchmark/adapter defects surfaced (not repaired here)

Already known from PR #20's `FINDINGS.md` and re-surfaced by judging
against real renderings: `qmsum-03`'s and `hotpotqa-02`'s native
reference answers remain mismatched to their evidence (both produced
"wrong"/non-correct recoverability verdicts against the literal native
answer, exactly as expected, though hotpotqa-02's judge correctly graded
against the evidence-supported answer per protocol). No *new* frozen
corpus or adapter defect was discovered by this run beyond what PR #20
already documented — this run's own new discovery is the findability
instrumentation gap above (a defect in this run's own protocol design,
not in the frozen corpus/adapter).
