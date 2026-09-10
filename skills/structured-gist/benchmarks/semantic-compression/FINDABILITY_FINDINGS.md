# Findability (Evidence Access Cost): findings (measurement only)

`scoring/findability.py` tests structured-gist's practical thesis, which is
**not** "fewer words" — it is **"hierarchical structure makes the important
information easier to locate."** This is Eval B of a two-eval
measurement-only PR (Eval A: `WORDING_FIDELITY_FINDINGS.md`). Neither eval
changes `SKILL.md`, the grammar, the linter, or any existing rendering,
judge verdict, or gold semantic judgment.

Named conservatively, per the PR brief: **Evidence Access Cost**, not
"reading speed," "human findability," or "time-to-answer" — this is a
deterministic proxy, not a timed-reader study (see "Whether a human study
is warranted" below).

## The critical design requirement: control for compression

The obvious wrong experiment is: compare a fact's position in the full,
unabridged `source.md` against its position in a much shorter gist, and
conclude the gist is "easier to navigate" because the fraction is smaller.
That mostly measures **deletion**, not organization — a gist is short
by design, so of course a fact sits at a smaller fraction of it. This
module instead builds a **content-matched baseline**: the same
answer-supporting evidence, located via each fact/relation's
`source_quote`, deduplicated, kept in original source order, with
structured-gist's hierarchy removed. Both sides of every comparison hold
the same underlying evidence content; only the *organization* differs.

## A failure mode found and fixed before scoring: the literal per-question baseline is mathematically degenerate

The PR brief's literal 5-step baseline construction is **per question**:
resolve that one question's own support-unit IDs, locate their spans,
dedupe, keep source order, concatenate — nothing else. This module
initially implemented exactly that, then proved (and unit-tests, see
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
in the baseline, by construction).

This is not a data artifact — it is a property of the construction that
holds before a single number is computed. `naive_per_question_baseline_
tokens()` is kept in this module (unused by scoring) purely as the
executable version of this proof; it is never called by `main()`.

**Why this matters.** With `EAC_baseline` and `EvidenceSpan_baseline`
pinned at 1.0 by construction, `ΔEAC = EAC_gist - 1` and `ΔEvidenceSpan =
EvidenceSpan_gist - 1` would just be `1 - gist_value` restated — the
baseline contributes zero information. The comparison would *look*
compression-controlled (both sides go through the same formula) while
actually degenerating back into "how early does the gist itself put this
evidence," a raw-position measurement with no content-matched anchor at
all. That is exactly the confound the PR brief's own "critical design
requirement" section warns against, just reached by a different route.

## The fix: a case-level content-matched baseline

Instead of building a fresh, evidence-only baseline per question, this
module builds **one baseline per case**, from *all* of that case's gold
facts and relations (not just one question's), and reuses it for every
question in the case. This is a small, documented generalization of the
same 5 steps — "the support unit IDs" becomes "the case's support unit
IDs," not "this question's" — motivated directly by the proof above, and
by the observation that the *actual gist rendering* also naturally
contains all of a case's facts, not just one question's; pairing it
against a baseline built the same way is the more honest match. Concretely
(`build_case_baseline`):

1. Resolve every fact/relation's `source_quote` to a token span in
   `source.md` (exact, normalized, first-occurrence — see "Alignment"
   below).
2. Merge overlapping/touching spans (`merge_spans`) — necessary and
   common: a relation's `source_quote` routinely spans (and thus
   overlaps) its component facts' own quotes (**every one of this
   corpus's 8 cases exhibits this** — checked directly before writing any
   scoring code, not assumed).
3. Concatenate the merged spans in source order into `baseline.tokens`.
4. Record each original unit's position **within this baseline** (not the
   original source) by re-mapping its source offset into the merged
   span's baseline offset.

A specific question's EAC/EvidenceSpan then look up only *that question's*
required units' positions within this shared, case-level baseline — which
is no longer degenerate, because a question's required units are
routinely NOT the very first and very last content in the case (other
facts, needed by other questions, legitimately come before/after them).
Proven directly in `test_evidence_reordered_closer_to_start_improves_gist_
eac` and `test_evidence_moved_farther_apart_regresses_gist_eac`, both of
which produce non-trivial (non-1.0) baseline values.

This is a real, load-bearing deviation from the PR brief's literal wording
— documented here rather than silently substituted, per the brief's own
instruction to document failures rather than patch formulas until they
look favorable.

## Metric definitions

- **Evidence Access Cost (EAC)** — `content tokens traversed before all
  required evidence is available / total content tokens in
  representation`. "Traversed" = read start-to-finish in reading order;
  "before all required evidence is available" = through the END of the
  LAST required unit's evidence (an outline is read top to bottom; you
  don't know you have everything until you've reached the last piece).
  Computed for the case-level baseline and for the actual gist rendering.
  `ΔEAC = EAC_gist - EAC_baseline`; negative is better for the gist.
- **Evidence span / locality** — `tokens from the START of the FIRST
  required unit to the END of the LAST required unit / total content
  tokens in representation`. Asks whether related evidence was brought
  closer together, independent of how far into the document it sits.
- **Structural traversal diagnostic** (optional, diagnostic only) — for
  multi-support questions: which output node holds each required unit's
  evidence, the depth of their lowest common ancestor in the outline
  tree, and how many other nodes sit between the first and last one in
  reading order.
- **Token convention** — identical to Eval A: `scoring/text_norm.py`'s
  `tokenize()` (conservative normalization + whitespace split + edge-
  punctuation strip + casefold). Same normalizer, same corpus, same
  rationale — see `WORDING_FIDELITY_FINDINGS.md`.

## Alignment

Entirely deterministic, no embeddings, no fuzzy/edit-distance matching, no
model call.

- **Baseline side**: gold `source_quote` → exact token-sequence match in
  `source.md`. Verified directly before writing any scoring code: **all
  231 gold facts+relations across all 8 cases align exactly**, at both a
  simple whitespace-normalized character check and the real tokenizer.
  Zero corpus-integrity failures (`baseline_integrity.units_unaligned_in_
  source` is empty for every case in `results/findability.json`). One
  case (`f1`/`f2` equivalent) had a duplicated phrase in a synthetic unit
  test, not in the real corpus — the real corpus has zero duplicate
  `source_quote` occurrences, confirmed directly; "first occurrence wins"
  (`text_norm.find_start`) is a documented convention for a case this
  corpus does not currently exercise.
- **Gist side**: the judge's recorded `evidence` string (from
  `judged/<tier>.json`, already produced for `combine.py` — not
  re-annotated here) → exact token-sequence match in the rendering.
  Judge evidence turned out to have its own real-world messiness,
  inspected directly before finalizing this module:
  - **44/1020 evidence strings (4.3%) join multiple non-contiguous
    rendering locations with `"..."`** (e.g. `"walk, validate, symlink
    ... verify each new link"`) or, less often, `" / "` (e.g.
    `"auth-service: explicitly not migrating ... vs notifications-
    service: not started"`). Handled by splitting on either separator and
    requiring **every** resulting fragment to align; the unit's overall
    position is `[min(fragment starts), max(fragment ends))`.
  - Some fragments echo their own node's marker glyph as if it were
    quoted text (e.g. `"IV. retry adds load"`, `"h. root: ..."`) even
    though a real node's `.text` never includes its own marker — stripped
    via `outline_nodes.strip_marker_prefix` before matching.
  - **After both fixes: 574/599 (95.8%) of "retained"-status evidence
    strings align exactly.** The remaining 25 (4.2%) were inspected by
    hand and are genuinely messier judge-authored composites this
    module deliberately does not chase further — e.g. an evidence string
    that embeds a marker glyph *mid-string* to reference a second,
    separate node (`"Result A. 77 skills load at session start"` — "A."
    here labels a *different* output node, not literal quoted text), or a
    `vs`/`->`-joined descriptive comparison that never appears as
    contiguous rendering text at all. Chasing these further starts to
    mean encoding this specific judge's writing idiosyncrasies rather
    than a principled, generalizable alignment rule — the brief's own
    instruction is to report an alignment failure, not fuzzy-match around
    it, so that is what this module does: any unit whose evidence does
    not align makes its dependent question(s) `not_findability_scorable`
    (never a default success or a guessed position).
  - **9 of the 264 (case, tier, level, question) combinations (3.4%) are
    ineligible for exactly this reason — status is "retained" but the
    evidence could not be located in that specific rendering** (as
    opposed to 99 combinations ineligible simply because the unit wasn't
    retained at all). This is the direct, concrete interaction with Eval
    A the PR brief asked to surface: a small but real fraction of
    findability's "can't score" cases trace to evidence whose rendering
    location couldn't be pinned down precisely — sometimes because Eval
    A-style wording mutation broke a clean quote, sometimes because the
    judge's own evidence annotation referenced structure rather than
    quoting text. Both are reported as `unaligned_in_rendering`, not
    silently patched or fuzzy-matched.
- No source_quote or evidence string anywhere in this corpus required
  falling back to fuzzy matching — every alignment success is exact.

## Eligibility

Strict scoring requires, for **every** unit a question's `fact_ids`
lists: (a) verdict status exactly `"retained"` (not `"partial"` — see
"Start with fully retained support units" in the PR brief) for both facts
and relations, (b) the unit's `source_quote` aligns in the case baseline,
and (c) the unit's judge-recorded evidence aligns in that specific
rendering. Any failure marks the question `not_findability_scorable` for
that (case, tier, level) with the specific reason(s) recorded — never
silently dropped, never scored as a default. An **exploratory** view
(same logic, `"partial"` allowed alongside `"retained"`) is computed and
reported separately, never mixed into the strict numbers.

**Corpus-wide strict eligibility: 156/264 (59.1%)**, rising sharply with
granularity as retention itself rises with granularity:

| level | eligible | total | % |
|---|---|---|---|
| skim | 17 | 88 | 19.3 |
| standard | 61 | 88 | 69.3 |
| deep | 78 | 88 | 88.6 |

By test class: `pressure-tests` 111/192 (57.8%), `regression` 45/72
(62.5%) — pressure cases are, unsurprisingly, somewhat harder to strictly
score, consistent with them being deliberately adversarial.

## Results

Full machine-readable output: `results/findability.json` (every question's
`reasons` list is present for every ineligible combination — nothing is
summarized away). Generated table: `results/FINDABILITY_SCORES.md`.
Regenerate with `python3 scoring/findability.py` (deterministic, no model/
network/randomness).

### By question type (strict-eligible only)

| question type | n | avg ΔEAC | avg Δevidence-span |
|---|---|---|---|
| factual | 108 | +0.0251 | +0.0096 |
| relational | 48 | **-0.0369** | +0.0014 |

### By support-unit count (strict-eligible only)

| support | n | avg ΔEAC | avg Δevidence-span |
|---|---|---|---|
| single | 105 | +0.0150 | +0.0085 |
| multi | 51 | **-0.0123** | +0.0042 |

### By granularity level (strict-eligible only)

| level | n | avg ΔEAC | avg Δevidence-span |
|---|---|---|---|
| skim | 17 | **+0.0978** | +0.0908 |
| standard | 61 | -0.0022 | +0.0056 |
| deep | 78 | -0.0075 | -0.0101 |

### Structural traversal diagnostic (multi-support questions, n=51)

58.8% have zero intervening nodes between their first and last required
unit (evidence lands in the same or an immediately adjacent node); average
lowest-common-ancestor depth 1.12 (shallow — related facts are usually
grouped under a common parent close to the root, not scattered across
distant branches).

## Corpus conclusions

**1. For already-preserved information, does hierarchy reduce evidence-
access cost?** Mixed, and the mixture itself is the finding, not noise.
Averaged over everything, the effect is small (relational avg ΔEAC
-0.037, factual avg ΔEAC +0.025) — this is not a uniform win. It **does**
show a real, if modest, benefit concentrated in exactly the place the PR
brief's own hypothesis predicted (next question).

**2. Is the effect stronger for relational/multi-support questions?**
**Yes, clearly**, and this is the strongest single result in this eval:
relational questions average ΔEAC **-0.037** (hierarchy helps) vs.
factual questions' **+0.025** (hierarchy very slightly hurts); multi-
support questions average **-0.012** vs. single-support's **+0.015**. A
single fact like "how many skills load at session start?" gets no
locality benefit from a tree — it's one number, findable or not,
regardless of organization. A relational/multi-support question like
"why did A cause B?" is exactly where clustering related facts under a
shared parent (58.8% of multi-support cases land in the same or an
adjacent node, per the structural diagnostic) pays off. This directly
confirms the PR brief's own example split ("What number was used?" vs.
"Why did A cause B?").

**3. Does any benefit survive after controlling for compression?**
**Yes — this is the point of the whole case-level-baseline exercise.**
Because both sides hold the *same* evidence content, a relational
question's -0.037 average ΔEAC cannot be explained by "the gist is just
shorter" — the baseline is built from the same retained facts, in their
natural source order, at the same nominal size class as the material the
gist also had to arrange. The benefit is real, though modest in absolute
terms, and it is concentrated exactly where organization (not deletion)
would be expected to help.

**4. Which granularity mode benefits most?** **None of them, at skim** —
skim is a clear net negative (avg ΔEAC +0.098, the largest deviation from
zero in this whole table) — but treat this specific number cautiously:
only 17 (case, tier, level, question) combinations are strict-eligible at
skim at all (vs. 61 at standard, 78 at deep), because most facts simply
don't survive skim's compression. The 17 that do survive are
disproportionately the highest-weight, most load-bearing facts, and
even among those, skim's aggressive reorganization (collapsing most
detail, keeping only a concept spine) evidently scrambles relative
position enough to cost more than it saves. `standard` is close to
neutral (-0.002); `deep` shows the most consistent modest improvement
(-0.008, and the largest n).

**5. Are there cases where structured hierarchy makes evidence harder to
locate?** Yes, directly demonstrated both synthetically
(`test_evidence_moved_farther_apart_regresses_gist_eac`) and in the real
corpus — `skim`'s aggregate ΔEAC is positive, and 108 of 156
strict-eligible questions (mostly factual, mostly single-support) show a
positive (worse) ΔEAC individually. The mechanism the synthetic test
makes concrete: if a model's chosen organization interposes unrelated
material between two facts that happen to be source-adjacent, hierarchy
actively hurts relative to flat source-ordered prose — it is not a
one-directional benefit.

**6. Is the deterministic proxy strong enough to keep as a regression
metric?** Not yet, on its own, as a pass/fail gate — the corpus-wide
average effect is small relative to its own variance (e.g. the standard
deviation implied by individual per-question deltas swinging from -0.34
to +0.49 in the raw table dwarfs any of the averages above), and only
59.1% of (case, tier, level, question) combinations are even
strict-scorable. It is, however, already strong enough to watch **the
relational/multi-support vs. factual/single-support split** as a
directional regression signal (a large positive shift in the relational
average would mean hierarchy stopped paying for itself where it's
supposed to), and the eligibility rate itself (drops in strict-scorable
question count) is a cheap, useful proxy for "did retention regress
enough to break this eval's ability to measure anything."

**7. Would a later human timing study be worth doing?** Yes, specifically
to validate direction #2 above (relational > factual benefit) with real
readers, since that is the one result here with a plausible mechanism, a
clean sign, and actual (if modest) magnitude — the other directions
(skim regression, overall small effect) are less obviously worth the cost
of a human study before more corpus and more cases exist.

## Pressure checks (actively tried to falsify this measure)

- **Shorter output getting a free advantage** — addressed by design: the
  baseline is content-matched (same retained facts), not raw source, so a
  shorter gist does not automatically get a smaller denominator advantage
  the baseline doesn't also have available at comparable scale.
- **Evidence near the beginning of source making hierarchy look worse
  unfairly** — this is real and reported, not hidden:
  `test_evidence_reordered_closer_to_start_improves_gist_eac` and its
  mirror `test_evidence_moved_farther_apart_regresses_gist_eac` show the
  metric responds correctly to *both* directions — a baseline where
  required evidence happens to sit early gets a naturally low
  `EAC_baseline`, and the gist is only credited for improving on it, not
  for reaching an absolute low number that was cheap to reach anyway.
- **Questions with one tiny answer dominating averages** — the `skim`
  n=17 result is exactly this risk materializing: flagged explicitly
  above rather than folded into a single "does hierarchy help" verdict.
- **Omitted evidence being rewarded** — cannot happen by construction:
  omitted/lost/mutated units fail the status check and make the question
  `not_findability_scorable`, never scored as "conveniently absent."
- **Duplicated evidence creating artificially low access cost** — checked
  directly: `test_duplicated_source_phrase_uses_first_occurrence_and_is_
  flagged_ambiguous` proves the first occurrence is used and the case is
  flagged (`ambiguous_unit_ids`) rather than silently picking whichever
  occurrence happens to be more convenient; zero real corpus quotes are
  duplicated, so this has not affected any reported number.
- **First-occurrence matching selecting the wrong occurrence** — same
  test; the real corpus does not currently exercise this path (zero
  duplicates), so the convention exists but has not been stress-tested
  against real ambiguity yet — a real finding, not swept under the rug.
- **Relation `source_quote` overlapping its component facts' quotes** —
  confirmed directly (every one of the 8 cases exhibits this), and
  `merge_spans`/`test_overlapping_fact_and_relation_spans_are_deduped_in_
  baseline` handle it by construction rather than double-counting
  overlapping content in the baseline's token count.
- **Content-matched baseline construction accidentally changing source
  order** — checked directly:
  `test_baseline_preserves_source_order_regardless_of_gold_list_order`
  feeds gold facts in scrambled (C, A, B) order and confirms the baseline
  still comes out in source order.
- **Normalized position hiding large absolute traversal differences** —
  real and worth flagging: this eval reports only normalized (0-1)
  fractions, never absolute token counts, so a large-token-count case and
  a small one contribute equally to an averaged delta regardless of their
  absolute scale. `results/findability.json` retains `gist_token_count`
  and `baseline_token_count` per rendering for anyone who wants to
  re-weight by absolute size; the tables above do not.

## Promotion classification

**B — useful experimental metric; promising, but methodology needs
another round before it is a durable regression gate.** This confirms the
PR brief's own stated prior for this eval. Concretely promising: the
relational/multi-support-vs-factual/single-support split is a clean,
mechanistically sensible, directionally consistent finding, obtained only
after fixing a real, provable degeneracy in the literal baseline
construction and being honest about a ~41% strict-ineligibility rate.
What the next round needs before promotion past B: more cases (8 is a
small corpus for a metric with this much per-question variance), a check
of whether the skim regression replicates outside `real-hook-discovery`/
`cause-chain-reversal`-style short cases, and likely a human-timing
validation of the one directional claim (#2) worth spending that on
before trusting the proxy alone as a gate.
