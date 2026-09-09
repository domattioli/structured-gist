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

| case | class | property / failure mode protected | canonical baseline |
|---|---|---|---|
| `regression/real-hook-discovery` | regression | semantic retention + relation retention + recoverability + conformance on an ordinary small realistic recap | `standard`/`deep`: wRetention ≥ 0.95, 0 conformance violations, monotone skim<standard<deep |
| `regression/real-benchmark-archaeology` | regression | same, on a richer realistic recap with unresolved questions and named identifiers | `standard`/`deep`: wRetention ≥ 0.88, unsupported_claim_count = 0 |
| `regression/near-identical-numbers` | regression | exact-value fidelity (numbers/paths/versions/SHAs) under compression | `standard`/`deep`: wRetention ≥ 0.95, unsupported_claim_count = 0 |
| `pressure-tests/causality-heavy-explain` | pressure | **relation collapse** — a causal chain flattened to a bare list, losing the links between steps even when the individual facts survive | `standard` relRetention is *known low* (0.56) vs. wRetention 0.80 — regression = relRetention dropping further, or `deep`'s 0.94 dropping |
| `pressure-tests/migration-tristate` | pressure | **lost status distinction** — 5 systems with different, easily-confused migration statuses (done/scheduled/will-not/reverted/in-progress) | `standard`/`deep` (sonnet): wRetention ≥ 0.95, no status collapsed to a generic bucket |
| `pressure-tests/negation-and-true-peers` | pressure | **lost negation + fake hierarchy on true peers** — 4 flat independent workstreams with load-bearing negations | `standard`/`deep`: wRetention ≥ 0.98, relRetention = 1.0, no invented shared parent |
| `pressure-tests/cause-chain-reversal` | pressure | **root-cause reversal / supersession** — an initial diagnosis is later overturned by better evidence; must preserve *which* cause is real | `standard`/`deep` (sonnet): wRetention ≥ 0.97; **haiku tier included** — this is also the sharpest model-sensitivity signal (see below) |
| `pressure-tests/synthetic-scale-verylarge` | pressure | **compression cliff + buried critical exception + structural-conformance collapse at scale** — 1 critical incident buried among many minor ones across 4 independent threads, 1,313 source words | `skim` is *expected* to lose most substance (wRetention 0.25) but must keep the critical item as its own distinct top-level entry, not merged into the minor bucket; **haiku tier's conformance collapses to 43 violations at `deep`** vs. sonnet's 2 — the clearest model-independence breakpoint found |

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

## Scoring dimensions (decomposable — no master scalar)

Every case reports these, computed by `scoring/deterministic.py` (no
judgment, reuses the real linter) and `scoring/combine.py` (arithmetic over
judge verdicts already recorded in each case's `judged/<tier>.json`):

- **weighted / unweighted retention** — fraction of gold facts recoverable
  from the outline, weighted by category (decision/constraint/negation/
  failure = 3, cause/outcome/next-action = 2.5, unresolved question = 2,
  descriptive = 1)
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

No "meaning per word" density composite is computed anywhere in this
suite. Round-1 evidence showed every such formula is *negatively*
correlated with actual usefulness — see `RESULTS.md`.

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
