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

`wRetention` above is this suite's original name for what the "Semantic
sufficiency" section below formalizes; `results/combined.json` reports it
under both `weighted_retention` (unchanged) and `semantic_sufficiency`
(same value, formal name). These baseline numbers are **observed reference
points from the renderings currently committed, not a formal definition of
"sufficient" and not a required threshold** — there is no universal
acceptable-sufficiency cutoff defined anywhere in this suite. Likewise,
`skim < standard < deep` is something this corpus currently shows, not a
semantic requirement; a strong `skim` output is allowed to outperform a
weak `standard` one, and a future case that does so is a finding, not a
bug in the suite.

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

## Semantic sufficiency

**How much of the information that matters to the case's intended
reader/task survived the transformation?**

```
semantic_sufficiency = sum(weight_i * retention_i for fact i) / sum(weight_i)
```

where `retention_i` is `1.0` retained, `0.5` partial, `0.0`
omitted/mutated (`scoring/combine.py`'s `STATUS_SCORE`). This is not a new
metric: it is this suite's original `weighted_retention` calculation,
formalized under its intended meaning. `scoring/combine.py` emits both
keys with an identical value — `weighted_retention` is kept only so the
baselines already written down in this file and in `RESULTS.md` still
mean what they said; there are not two independently-computed "how much
meaning survived" numbers in this suite.

Semantic sufficiency is reported **alongside**, never blended into:
compression ratio/reduction%, relation retention, recoverability,
unsupported claims, omission/mutation rate, or structural conformance. A
high semantic-sufficiency score can still hide a real relation-loss
failure — see `causality-heavy-explain` at `standard`: 0.80 sufficiency
next to 0.5625 relation retention, i.e. facts mostly survived while the
causal chain between them did not. That is the frontier this suite wants
visible, not collapsed into one scalar. No "sufficiency per word" or
similarly blended efficiency composite is computed anywhere in this suite
(see "No density composite" below).

## Weight semantics

A fact's `weight` in `gold.json` means **the importance of preserving that
fact for the case's stated `intent.reader` and `intent.task`** (see
"Intended reader/task" below) — not a universal importance ranking. The
category buckets already used across this corpus (decision/constraint/
negation/failure ≈ 3, cause_rationale/outcome/next_action ≈ 2.5,
unresolved_question ≈ 2, descriptive ≈ 1) remain a reasonable **default**
for hand-authoring a new case, but category never implies that every fact
in it must carry the default weight: the same "outcome" category holds
weight-1 facts (routine, resolved noise in `synthetic-scale-verylarge`)
and weight-3 facts (the corrected root cause in the same case) side by
side, because those facts are not equally important to that case's reader.
A descriptive implementation detail can be critical for a code reviewer; a
next-action can be critical in a handoff and peripheral in an explanatory
summary — weight is set per fact, per case, for that reason.

Where a fact's weight was set specifically *because* of its case's
reader/task rather than by category default, the fact may carry an
optional `weight_reason` string — a one-line audit trail, not a rubric.
It is not consumed by any arithmetic in `scoring/combine.py`; it exists so
a reader auditing a surprising weight (e.g. an "outcome" fact weighted at
3 next to five "outcome" facts weighted at 1) can see why without
reverse-engineering intent from the case alone.

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

## Scoring dimensions (decomposable — no master scalar)

Every case reports these, computed by `scoring/deterministic.py` (no
judgment, reuses the real linter) and `scoring/combine.py` (arithmetic over
judge verdicts already recorded in each case's `judged/<tier>.json`):

- **semantic sufficiency** (`semantic_sufficiency`, alias
  `weighted_retention`) and **unweighted retention** — see above for the
  formula and what `weight` now means
- **relation retention** — fraction of gold relationships (causal,
  dependency, temporal, supersession, comparative) whose *relationship*,
  not just both endpoints, survives
- **recoverability** — fraction of gold questions answerable from the
  outline alone
- **unsupported-claim count** — see correction below; NOT the same as
  "absent from the gold fact list"
- **structural conformance** — a gate (violation count from the unmodified
  linter), reported alongside the above, never blended into them
- **compression ratio / reduction%** — reported as a cost, never rewarded
  on its own (see `RESULTS.md` §2 for why)

### No density composite

No "meaning per word" density composite is computed anywhere in this
suite, and semantic sufficiency does not create one either — it is not
divided by size or word count anywhere. Round-1 evidence showed every such
formula is *negatively* correlated with actual usefulness — see
`RESULTS.md`.

## Hallucination / unsupported-claim correction (read before trusting that number)

An isolated judge sees only `gold.json` and the outline — never
`source.md` — so it can only say a claim is *not covered by the gold fact
list*, which is **not the same as unsupported by the source**. Gold is a
curated, weighted subset of the source, not an exhaustive transcript.

Every entry in `judged/<tier>.json`'s `hallucinations` list therefore
carries a `source_supported` boolean, set by checking the exact claim
against `source.md` directly. `unsupported_claim_count` (the canonical
metric) counts only `source_supported: false` entries. The raw
judge-flagged count is kept as `flagged_vs_gold_count` for transparency,
but is not something to gate on — in this corpus it was 20 and the
corrected count is 0 (every flagged claim was verbatim or near-verbatim
source text gold's fact list simply hadn't extracted).

**If you re-run judging**, give the unsupported-claim check — and only that
check — access to `source.md`; keep the fact/relation/question checks
source-blind (that isolation is what makes retention/recoverability
grading trustworthy). Do not restore the "no matching gold fact ⇒
hallucination" heuristic.

## Re-running

```
python3 scoring/deterministic.py   # word counts, compression, lint gate
python3 scoring/combine.py         # merges in judged/*.json -> results/
```

Regenerating `renderings/` or `judged/` (i.e. actually re-generating
outlines or re-judging them) is a manual/agent-driven step, not a script in
this repo — see `RESULTS.md` §5 for the protocol used to produce the
current canonical files.
