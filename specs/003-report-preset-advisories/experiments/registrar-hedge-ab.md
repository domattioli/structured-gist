# registrar-hedge A/B: does the v0.5.0b1 skill text change hedge survival?

**Date**: 2026-09-18 · **Status**: exploratory, one case, three samples per arm. Not a benchmark result.

## Question

v0.5.0b1 adds a `## Hedge preservation` section and an advisory attribute lexicon to `SKILL.md`. The rest of the benchmark suite rescoring frozen renderings shows the change broke no scorer, but says nothing about what a model generates when it reads the new text. This experiment asks whether the new text changes hedge survival on the one pressure test built around a hedge.

## Method

Follows the protocol in `skills/structured-gist/benchmarks/semantic-compression/RESULTS.md` §5, with the deviations listed below.

1. **Arms.** Old text = `SKILL.md` at `969cb9d` (v0.4.12). New text = `SKILL.md` at `d79f665` (v0.5.0b1). The two files were given to generators under neutral names (`SKILL_A.md`, `SKILL_B.md`).
2. **Generation.** Six fresh Opus subagents, three per arm, no prior context. Each read one skill file and `pressure-tests/registrar-hedge/source.md`, was told not to invoke any skill or read any other file, and wrote `skim.md`, `standard.md`, `deep.md` in block mode. All 18 outlines are archived under `registrar-hedge-ab/{old,new}-{1,2,3}/`.
3. **Hedge check (deterministic).** `hedge_probe.py` (this directory) merges wrapped continuation lines, finds the node naming a registrar candidate, and reports whether a hedge word sits on that node, on an attached `↪` child, or on its parent.
4. **Corpus tiers.** Sample 1 of each arm was chosen before any output was inspected and stored as tiers `opus-v0.4.12` and `opus-v0.5.0b1` under the case's `renderings/`.
5. **Judging.** Three fresh, isolated Fable subagents, one per set (existing `sonnet` renderings, `opus-v0.4.12`, `opus-v0.5.0b1`), under blind set labels. Each saw only `gold.json` and its three renderings, never the source. The judge was instructed to mark an epistemic fact `mutated` when its qualifier is removed.
6. **Source-support pass.** Every judge-flagged claim (25 total) was checked against `source.md` by the orchestrating session; one was marked unsupported (`opus-v0.4.12/deep`: "rather than acting for them", an inferred contrast).
7. **Verification of the judge.** Every non-omitted fact verdict carries an evidence quote; all 146 quotes were confirmed verbatim against the rendering they cite (0 unverifiable).

### Deviations from the recorded protocol

- The other eight cases were judged by Sonnet-tier agents. These three verdicts were judged by Fable, so `registrar-hedge` is comparable across its own tiers but not strictly with the other cases.
- The hedge word list was extended after seeing outputs (`candidates`, `possible`, `likeliest` added) and the claim pattern was narrowed from `squarespace domains|registrar` to the candidate names, because the first pattern also matched the "identify registrar" steps. Both changes were applied to both arms.

## Observed

### Hedge survival (18 outlines, deterministic check plus a manual read of the four skims that name no candidate)

| | old text | new text |
|---|---|---|
| candidate named, hedge attached | 7 of 7 | 7 of 7 |
| skim collapses candidates, keeps "registrar unconfirmed" | 1 | 1 |
| skim reduces to a bare `▸ Registrar`, hedge gone | 1 (`old-3`) | 1 (`new-3`) |
| **outlines keeping the hedge** | **8 of 9** | **8 of 9** |

No judge verdict in any tier or level marks fact `f6` (the hedged registrar claim) as `mutated`. Where `f6` is present, its hedge is present.

### Judged metrics, sample 1 of each arm (from `results/combined.json`)

| tier / level | compression ratio | task-weighted fact retention | relation retention | recoverability | lint violations |
|---|---|---|---|---|---|
| sonnet / skim | 0.11 | 0.27 | 0.2 | 0.50 | 0 |
| sonnet / standard | 0.50 | 0.75 | 0.8 | 0.95 | 14 |
| sonnet / deep | 0.91 | 0.92 | 0.9 | 1.00 | 26 |
| opus-v0.4.12 / skim | 0.56 | 0.64 | 0.5 | 0.70 | 0 |
| opus-v0.4.12 / standard | 1.11 | 0.97 | 0.9 | 1.00 | 1 |
| opus-v0.4.12 / deep | 1.57 | 1.00 | 0.9 | 1.00 | 7 |
| opus-v0.5.0b1 / skim | 0.29 | 0.41 | 0.5 | 0.35 | 2 |
| opus-v0.5.0b1 / standard | 0.71 | 0.64 | 0.6 | 0.75 | 0 |
| opus-v0.5.0b1 / deep | 1.45 | 1.00 | 0.9 | 1.00 | 4 |

### Word counts, all samples (source = 381 words)

| sample | skim | standard | deep |
|---|---|---|---|
| old-1 | 215 | 423 | 598 |
| old-2 | 123 | 322 | 488 |
| old-3 | 101 | 306 | 515 |
| new-1 | 109 | 272 | 554 |
| new-2 | 220 | 485 | 641 |
| new-3 | 127 | 352 | 495 |

### Linter conformance of cold-read generations

| set | outlines passing `lint_outline.py` | most-violated rules |
|---|---|---|
| Opus, old text | 1 of 9 | R7 ×14, R1 ×4, R6 ×4, R9 ×3, R5 ×3 |
| Opus, new text | 2 of 9 | R7 ×16, R5 ×7, R9 ×3 |
| existing sonnet + haiku renderings | 2 of 6 | not broken down |

## Inferred

- **Hedge survival shows no difference between arms (8 of 9 each).** This is a ceiling effect: Opus kept the hedge nearly always under either text, so this case cannot show whether the new section helps. The new text says hedges are preserved "including in collapsed output"; one of three new-text skims still dropped it.
- **The judged retention gap between the two Opus tiers is confounded by length and should not be read as an effect of the text.** Each arm produced one long sample and two short ones. The long one happened to be sample 1 in the old arm and sample 2 in the new arm, so the pre-registered choice of sample 1 compares a 215-word skim against a 109-word skim. Retention tracks length in this table. Judging samples 2 and 3 would be needed before any claim.
- **Both Opus `standard` and `deep` outlines are longer than the source** (compression ratio above 1.0) in every sample. At those levels the outline restructures rather than compresses.
- **A model reading `SKILL.md` cold mostly fails the skill's own linter, under either text.** Word caps (R7) dominate. The new text is no worse; with nine outlines per arm, "better" is not supported. This is the more consequential observation and is independent of this feature.
- Two new-text generators used the new vocabulary (`▸ Certainty`; `▸ Likely` / `▸ Possible`). Recorded as an observation only; it was noticed after the fact and no metric was defined for it in advance.

## Next

- Judge samples 2 and 3 of each arm so the retention comparison is not a single, length-confounded pair.
- A hedge pressure test that is not at ceiling is needed to measure the new section: more hedged facts per source, or a weaker generator tier.
- The cold-read linter failure rate deserves its own investigation (R7 word caps first).
