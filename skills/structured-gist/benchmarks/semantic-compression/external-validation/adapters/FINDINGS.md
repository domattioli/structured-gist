# Adapter findings

Methodological, not performance-oriented — nothing here says anything
about how structured-gist performs on this corpus, because nothing in
this session generated a structured-gist output. See `README.md` (the
selection report, PR #19) for corpus-level provenance; this document
covers only the semantic-gold adapter layer built in this session.

## Adapter quality

| dataset | cases | facts (min/median/max) | relations (min/median/max) | critical units (min/median/max) | explicit/inferred relations | multi-evidence cases with 0 relations |
|---|---|---|---|---|---|---|
| qmsum | 24 | 4 / 11 / 26 | 0 / 2 / 5 | 3 / 5 / 10 | 34 explicit / 16 inferred | 2 |
| qasper | 10 | 2 / 3 / 6 | 0 / 0 / 2 | 0 / 3 / 3 | 5 explicit / 0 inferred | 5 |
| hotpotqa | 8 | 2 / 2 / 3 | 0 / 1 / 1 | 1 / 3 / 3 | 0 explicit / 7 inferred | 0 |

Totals: QMSum 279 facts / 50 relations / 139 critical units; Qasper 37
facts / 5 relations / 21 critical units; HotpotQA 17 facts / 7 relations
/ 17 critical units.

**Provenance success rate: 100%.** `adapters/validate_derived_gold.py`
requires every fact/relation's `derived_from` to resolve to a real
`native_evidence` id and every `source_quote` (fact, and explicit
relations) to resolve verbatim in `source.md`; all 42 committed cases
pass this check with zero exceptions as of this session's final commit —
but that 100% is the result of an active repair process (see "What went
wrong and was fixed" below), not a first-pass outcome.

**Multi-evidence cases with zero relations** (7 total: 2 QMSum, 5 Qasper)
are not gaps — the protocol explicitly allows an empty relation list when
a question is answered by independent facts that don't need connecting
(task brief: "if the answer depends only on independent facts, relations
may legitimately be empty"). Qasper's 5-of-7 rate is notably higher than
QMSum's 2-of-12 multi-evidence rate; this is plausibly because Qasper's
evidence-distance pressure set (see PR #19's `README.md`) was
specifically selected for spatially separated evidence, which does not
imply the two locations state a *relationship* — they may simply be two
independent supporting facts the reader must both see.

### QMSum's large fact counts (qmsum-23: 26, qmsum-24: 26 after fixes)

Flagged during design (`ADAPTER_DESIGN.md` §4) as a gaming risk to watch.
Checked against source size: these are not the corpus's largest
source-word-count cases (7,279 and 8,103 words respectively, vs. a
24,000+ max size actually observed elsewhere in the pool during corpus
selection) — the original annotator's stated reason (compound,
multi-part product-design questions covering several distinct decision
points in one long evidence span) held up under the coverage audit, which
flagged *additional* missing content in both cases rather than flagging
over-atomization. Treated as legitimate, not gaming.

## What went wrong and was fixed (read this before trusting the numbers above)

This is the most important section of this document. The pipeline was:
Stage A (blind decomposition) → calibration (7 cases, double-annotated +
adjudicated) → Stage A production (remaining 35 cases, single-pass) →
mechanical `source_quote` verbatim-fidelity repair → coverage audit (all
42 cases, independent pass) → targeted fixes from the audit → Stage B
(independent weighting).

**Mechanical repair pass.** The first full run of
`validate_derived_gold.py` against all 42 freshly-annotated cases failed
with **46 problems**, concentrated in QMSum: many facts/relations quoted
source text with spacing that didn't match `source.md` exactly (a
copy-transcription slip, not a content error — QMSum's committee-domain
transcripts use normal prose spacing, and several facts had acquired
ASR-tokenization-style spaces around punctuation that don't exist in the
actual source), and several quotes used "..." to stitch together
non-contiguous spans (breaking the "exact verbatim substring" rule). A
scripted repair (`/tmp/repair_quotes2.py`, not committed — a one-off
utility, not part of the adapter) mechanically fixed 40 of 46 via
whitespace-normalization matching and longest-resolvable-ellipsis-segment
extraction; the remaining 6 (5 QMSum quotes that had genuinely drifted
from verbatim — e.g. a fact's `text` ran on past where its cited quote's
sentence actually ends, effectively completing a cut-off sentence with
non-quoted words — plus one Qasper fact citing a paragraph outside its
case's designated `native_evidence`) were fixed by hand, checking each
against `source.md` directly. **Lesson for a future re-run of this
pipeline: the Stage-A prompt should be strengthened to warn explicitly
against reformatting/normalizing quoted punctuation and against
ellipsis-stitching** — this class of error was systematic enough (affecting
9 of 24 QMSum cases initially) that it's worth fixing at the prompt level,
not just the repair-script level, next time.

**Coverage audit found substantial issues in QMSum specifically.** Of 24
QMSum cases, **17 got `issues_found`** (7 `pass`) — including 3 of the 7
calibration+adjudication cases, meaning double-annotation and adjudication
did *not* fully catch these. The issue types: missing task-critical facts
(most common), a systemic "fact text extends past what its own
`source_quote` actually says" pattern (several facts appended an unquoted
clause from a different speaker's later turn), one relation asserting a
firm "decision" that the case's own `corpus_defect_notes` already said
never happened (only "interesting" was expressed), and one speaker
misattribution. **Qasper and HotpotQA fared much better**: 2/10 Qasper
cases and 2/8 HotpotQA cases got `issues_found`, and every one of those
was a minor granularity split (one fact bundling two independent claims)
rather than missing/fabricated content — HotpotQA's audit also caught one
case (hotpotqa-07) where the original annotator's "genuinely
unrecoverable" corpus-defect claim was itself wrong (a connecting sentence
did exist in `source.md`, just outside `native_evidence`; the note was
corrected, no relation was added, since adding one would have required
citing evidence outside the case's native_evidence set — see
`ADAPTER_DESIGN.md`'s evidence-scope rule).

All flagged issues were fixed with targeted correction passes (not
re-annotation) that read the specific `coverage_audit.json` finding plus
`source.md`, and either added a properly-quoted missing fact/relation,
narrowed an over-claiming fact's `text` to what its `source_quote`
actually supports, or corrected a relation's claim. Every fix was
re-verified by `validate_derived_gold.py` (verbatim `source_quote`,
`derived_from` resolves to real `native_evidence`).

**What this means for trusting QMSum's derived gold:** the *final*,
post-fix state passes every mechanical check this session can run, and a
second independent HotpotQA-style audit-of-the-audit was not performed
(would require a third annotation pass and was judged out of scope for
this session — see "Qasper/HotpotQA classification" below for why they
didn't need it as urgently). QMSum's higher single-pass error rate (no
double-annotation beyond the 3 calibration cases) is the main reason its
classification below is **B, not A** — see "Classification."

## Reliability (calibration)

Calibration sample: 3 QMSum (qmsum-01/02/03) + 2 Qasper (qasper-01/02) +
2 HotpotQA (hotpotqa-01/02), each independently decomposed twice
(annotator A, annotator B), compared with `calibration/compare_calibration.py`
(deliberately simple overlap diagnostics, not a sophisticated agreement
metric — per the task brief), then adjudicated by a third, independent
pass per `adapters/ADJUDICATION_PROTOCOL.md`.

| case | fact count A/B (ratio) | native-evidence-id Jaccard | quote overlap A→B / B→A | relation-existence agreement | adjudication |
|---|---|---|---|---|---|
| qmsum-01 | 11/12 (0.92) | 1.0 | 0.72 / 0.62 | yes | reconciled |
| qmsum-02 | 10/12 (0.83) | 1.0 | 0.79 / 0.70 | yes | reconciled |
| qmsum-03 | 14/17 (0.82) | 1.0 | 0.46 / 0.39 | yes | reconciled |
| qasper-01 | 6/5 (0.83) | 1.0 | 0.84 / 0.95 | yes | reconciled |
| qasper-02 | 3/3 (1.00) | 1.0 | 1.00 / 1.00 | yes | reconciled |
| hotpotqa-01 | 2/4 (0.50) | 1.0 | 0.62 / 0.50 | yes | reconciled |
| hotpotqa-02 | 2/3 (0.67) | 1.0 | 0.82 / 0.67 | yes | reconciled |

**Native-evidence-id Jaccard is 1.0 for all 7 cases** — both independent
annotators always agreed on *which* evidence mattered, even when they
disagreed on how finely to decompose it. **Relation-existence agreement
is 7/7.** No case was `irreconcilable`. This is what justified proceeding
to single-pass annotation for the remaining 35 cases rather than stopping
per the task brief's explicit off-ramp ("if agreement is poor, stop and
report that rather than mass-producing unreliable derived gold").

**Independent confirmation of corpus defects.** Both annotators,
working independently with no access to each other's output,
flagged the *same* two native-data problems: qmsum-03's reference_answer
("the final English SmartKom demo will be presented...") is unrelated to
its query ("What was the status of transcription?") and evidence
entirely, and hotpotqa-02's reference_answer ("psilocin") is inconsistent
with the question ("which compound is converted to psilocin") given the
evidence states psilocybin is what converts to psilocin. Both were
independently verified against the frozen native `external_gold.json`
and confirmed genuine (see "Corpus defects found" below) — this
convergence is itself a reliability signal, not just a defect report.

**Granularity variance is the main disagreement axis, not content
disagreement.** hotpotqa-01's 0.50 fact-count ratio (A: 2 facts, B: 4
facts) is the extreme case; inspection showed B's extra facts included
one (interventionist-policy support) not actually needed to answer the
question, which the adjudicator excluded per the "task-relevant, not just
source-supported" adjudication rule — i.e., the disagreement was about
scope discipline, not about what the source says.

## Coverage-audit findings

| dataset | cases audited | pass | issues_found | issue types found |
|---|---|---|---|---|
| qmsum | 24 | 7 | 17 | missing facts, fact text exceeding its own quote, relations asserting unsupported outcomes/resolutions, one speaker misattribution |
| qasper | 10 | 8 | 2 | granularity only (fact bundling two claims) |
| hotpotqa | 8 | 6 | 2 | one missed-recoverable-relation correction, one granularity split |

All flagged issues were corrected (see "What went wrong and was fixed").
No case was left with a known, unaddressed coverage-audit finding as of
this session's final commit — `coverage_audit.json` remains committed
per-case as the historical record of what was found, even where the
inventory has since been corrected (it is not re-run after fixes; a
future session could re-audit to confirm the fixes actually closed every
finding, which this session did not independently re-verify beyond
`validate_derived_gold.py`'s mechanical checks).

## Corpus defects found (native data, not this session's annotation)

Recorded per-case in `derived_gold.json.corpus_defect_notes` (the
authoritative, detailed record — this is a summary). Roughly 15 of 42
cases (18 QMSum-side counts include some fix-traceability notes, not all
severity-equal) carry at least one note; the clearest, most consequential
ones, independently confirmed against the frozen native
`external_gold.json`:

- **qmsum-03**: reference_answer is about an unrelated meeting/topic
  ("SmartKom demo") — query and evidence are about transcription status.
  **Do not use for recoverability scoring against the native
  reference_answer.**
- **hotpotqa-02**: reference_answer ("psilocin") is inconsistent with the
  question given the evidence (psilocybin, not psilocin, is what
  converts). **Do not use for recoverability scoring against the native
  reference_answer.**
- **qmsum-04**: reference_answer says "GGT bins," evidence supports "FFT
  bins" — likely upstream typo.
- **qmsum-06**: reference_answer's VTS-technique claim doesn't match what
  the evidence says VTS is for.
- **qmsum-08**: reference_answer cites a different meeting ID (Bmr013)
  than this case's own (Bmr014).
- **qasper-06, qasper-08, qasper-10**: reference_answer content partially
  outside the case's designated `native_evidence` (numeric results only
  in a table this corpus doesn't retain; a question/evidence wording
  mismatch; a reference answer segment that doesn't address "how big").
- **hotpotqa-07**: the question's full claim isn't jointly supported by
  the two given `native_evidence` sentences; a connecting sentence exists
  in `source.md` but wasn't part of the dataset's own evidence annotation
  for this question.

None of these were "fixed" by altering native data (forbidden — see
`ADAPTER_DESIGN.md`/task brief). Where the defect affects only the answer
field, the derived fact/relation inventory itself remains valid for
fact/relation-retention-based metrics; only recoverability-against-native-
answer should be treated with caution for the specific cases above.

## Classification

- **QMSum: B** — usable experimentally, but conclusions need caution. Rich,
  varied inventory (139 critical units across 279 facts), reliability
  demonstrated on the calibration sample, but 17/24 cases needed real
  correction after a single annotation pass (not just calibration-level
  granularity differences) and only 3/24 were double-annotated. Treat
  QMSum-based findings as suggestive until a second independent
  reliability check (ideally a larger calibration sample, or a full
  second-pass audit) is run.
- **Qasper: A** — derived gold is strong enough for full semantic
  evaluation. Small, clean inventory; coverage audit found only two minor
  granularity issues in 10 cases; the known native-data limitations
  (qasper-06/08/10) are already flagged and don't implicate the adapter's
  own fact/relation extraction, which was found sound.
- **HotpotQA: A**, with its standing `pressure_only: true` caveat — very
  stable, homogeneous inventory (modal 2 facts + 1 relation), coverage
  audit found only minor issues in 2/8 cases, and the audit itself
  demonstrated real value (correcting one case's defect note rather than
  just rubber-stamping it). Never pool into a combined score with
  QMSum/Qasper — see `../README.md`'s "Intended roles."

## Unresolved / left for the next session

- QMSum's B classification means a second reliability pass (wider
  calibration, or a full second coverage audit specifically re-checking
  whether this session's fixes actually closed every finding) is
  recommended before QMSum-based semantic scores are treated as
  conclusive, not just suggestive.
- `coverage_audit.json` is not re-run after fixes; nothing confirms the
  17 fixed QMSum cases wouldn't surface new findings under a fresh,
  independent audit pass.
- The ~15 cases with corpus_defect_notes should be reviewed case-by-case
  before being used for any metric that depends on the native
  `reference_answer` specifically (recoverability); fact/relation-based
  metrics (retention, SPR) are unaffected by these particular defects
  since they don't depend on the answer field.
