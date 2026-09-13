# Cross-metric cases

Concrete (case, level) instances where two metrics diverge — these are
more diagnostic than another mean. Pulled mechanically from
`hypothesis_results.json`'s case-level rows; commentary below is this
session's read of why each one is informative. Full per-unit detail is in
each case's `evaluation/<dataset>/judgments/<case-id>.json` and
`evaluation/<dataset>/scores.json`.

## 1. High fact recall / low relation recall

**qmsum-22, standard and deep**: task-weighted fact retention 0.85, but
relation retention **0.0** (the single gold relation is `lost` at both
levels). Per the judge, the rendering states the content behind both
endpoint facts but never connects them — exactly the "do not infer that
retaining both endpoint facts means the relationship survived" case the
judge protocol was built to catch. This is the cleanest, starkest example
in the whole corpus of facts surviving compression while the connective
tissue between them does not.

## 2. High SPR alongside nonzero critical loss

**None found.** Every row with `critical_lost_frac > 0` also has SPR
below 0.8 in this corpus. This is not surprising by construction — a
weight-3 (critical) unit dominates SPR's denominator enough that losing
one visibly drags the aggregate down — but it's worth stating plainly:
in this corpus, SPR and the critical-loss diagnostic are *not*
independent evidence. A future session relying on SPR as a summary
should not assume it can miss what critical-loss tracking catches; here,
it mostly can't (see H8/Q8 in `RESULTS.md`).

## 3. Low-ish SPR / successful native recoverability

**qasper-01, standard**: SPR 0.09 (most facts/relations omitted or
partial), yet recoverability **1.0** — the judge could still answer the
native question correctly from what little survived. **hotpotqa-06,
hotpotqa-08, hotpotqa-02, all at skim**: SPR in the 0.5-0.57 range, but
recoverability **1.0** in every case — HotpotQA's comparison/bridge
questions are frequently answerable "by elimination" once even one
distractor-adjacent detail survives, without the formal gold bridge
surviving at all. This is direct evidence for H5: preservation and
task-success are measuring genuinely different things, not one subsuming
the other.

## 4. High recoverability / poor structural conformance

**hotpotqa-01/02/03/04, deep** (and several standard levels): perfect or
near-perfect recoverability (1.0) alongside 10-19 linter violations each.
**Reverse direction** — perfect conformance (0 violations) with severe
semantic loss: **qmsum-13, qmsum-16, qmsum-19, qmsum-20, qmsum-21, skim**
all show 0 conformance violations *and* fact retention at or near 0
(0.0-0.29). Skim renderings are frequently short enough to be trivially
linter-clean while being semantically empty — conformance says nothing
about whether the (small) amount of content present is the *right*
content. Both directions of H8 are directly demonstrated in this corpus.

## 5. Strong compression / catastrophic task failure

**qasper-01/02/04/05 skim, qmsum-03 skim** (representative of the general
pattern, not exhaustive): 97-99% reduction alongside recoverability
**0.0**. This is the modal skim-level failure across all three datasets,
not an isolated outlier — see `RESULTS.md`'s H2 discussion.

## 6. Weak compression / little semantic improvement

Not cleanly observed as a distinct failure mode in this corpus — QMSum's
deep level averages 85.9% reduction with 0.72 fact retention (the
weakest compression among all three datasets' deep levels), and even
there fact retention keeps climbing over standard's 92.9%-reduction/0.55
point rather than plateauing. No case showed materially worse compression
buying no incremental preservation; the closest analogue is HotpotQA's
standard-to-deep transition, where reduction barely changes (25.9% ->
7.5%) while fact retention/recoverability are already saturated at 1.0
by standard — deep buys essentially nothing further there, but it isn't
"weak compression for no gain" so much as "diminishing returns after
saturation" (see H2/Q5).

## 7. Good wording fidelity / semantic loss

**QMSum skim, all cases**: verbatim-node rate is actually *higher* at
skim (0.079) than standard/deep in relative terms is not true here
(skim/standard/deep are 0.079/0.096/0.085 — roughly flat) — but skim's
fact retention (0.12) is far below its verbatim-node rate would suggest
if "verbatim wording" were read as a preservation proxy. The two
metrics are answering different questions (does surviving text quote the
source vs. how much of gold survives at all) and should not be conflated
— skim is not "faithful but complete," it is simply short.

## 8. Paraphrased wording / excellent semantic retention

**Qasper deep**: verbatim-node rate 0.22 (well below skim's 0.42) while
fact retention is at its corpus maximum (0.946) and recoverability 0.9.
Qasper's deep renderings preserve gold facts thoroughly while wording
them more in the renderer's own words than skim does — the inverse of
the intuitive "more verbatim = more faithful" assumption, consistent
with wording fidelity and semantic preservation being genuinely
orthogonal measurements (see H6).
