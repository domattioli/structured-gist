# Findability (Evidence Access Cost): canonical scores (generated, do not hand-edit)

Measurement only -- see `../FINDABILITY_FINDINGS.md` for full methodology. **Headline metric is unit-rank EAC / locality span**, computed over the retained-unit set `R` this specific (case, tier, level) rendering actually retained and could align -- source order vs. gist order over the identical set `R`, so compression/deletion cannot affect either number. The older token-normalized, case-level-baseline EAC is reported separately as a diagnostic only (see `FINDABILITY_FINDINGS.md` "Failure mode 2"). Regenerate with `python3 scoring/findability.py`.

| case | tier | level | qtype | support units | |R| | eligible (strict) | source EAC | gist EAC | delta EAC | source span | gist span | delta span |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| causality-heavy-explain | sonnet | skim | relational | 1 | - | no (r7:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | skim | relational | 2 | - | no (r1:status=lost,unaligned_in_rendering,r2:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | skim | relational | 1 | - | no (r4:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | skim | factual | 2 | - | no (f11:status=partial,f12:status=partial) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | skim | relational | 1 | - | no (r8:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | skim | factual | 1 | 7 | yes | 1.0 | 1.0 | 0.0 | 0.1429 | 0.1429 | 0.0 |
| causality-heavy-explain | sonnet | skim | factual | 2 | 7 | yes | 0.5714 | 0.5714 | 0.0 | 0.2857 | 0.2857 | 0.0 |
| causality-heavy-explain | sonnet | skim | relational | 2 | 7 | yes | 0.5714 | 0.5714 | 0.0 | 0.2857 | 0.2857 | 0.0 |
| causality-heavy-explain | sonnet | standard | relational | 1 | 17 | yes | 0.5882 | 0.5882 | 0.0 | 0.0588 | 0.0588 | 0.0 |
| causality-heavy-explain | sonnet | standard | relational | 2 | - | no (r2:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | standard | relational | 1 | - | no (r4:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | standard | factual | 2 | - | no (f12:status=partial) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | standard | relational | 1 | 17 | yes | 1.0 | 0.9412 | -0.0588 | 0.0588 | 0.0588 | 0.0 |
| causality-heavy-explain | sonnet | standard | factual | 1 | 17 | yes | 0.9412 | 1.0 | 0.0588 | 0.0588 | 0.0588 | 0.0 |
| causality-heavy-explain | sonnet | standard | factual | 2 | 17 | yes | 0.7059 | 0.7059 | 0.0 | 0.1176 | 0.1176 | 0.0 |
| causality-heavy-explain | sonnet | standard | relational | 2 | 17 | yes | 0.7059 | 0.7059 | 0.0 | 0.1176 | 0.1176 | 0.0 |
| causality-heavy-explain | sonnet | deep | relational | 1 | 26 | yes | 0.7308 | 0.7308 | 0.0 | 0.0385 | 0.0385 | 0.0 |
| causality-heavy-explain | sonnet | deep | relational | 2 | 26 | yes | 0.2692 | 0.2692 | 0.0 | 0.1154 | 0.1154 | 0.0 |
| causality-heavy-explain | sonnet | deep | relational | 1 | 26 | yes | 0.5 | 0.4615 | -0.0385 | 0.0385 | 0.0385 | 0.0 |
| causality-heavy-explain | sonnet | deep | factual | 2 | 26 | yes | 0.6154 | 0.6154 | 0.0 | 0.1154 | 0.1154 | 0.0 |
| causality-heavy-explain | sonnet | deep | relational | 1 | 26 | yes | 1.0 | 0.9615 | -0.0385 | 0.0385 | 0.0385 | 0.0 |
| causality-heavy-explain | sonnet | deep | factual | 1 | 26 | yes | 0.9615 | 1.0 | 0.0385 | 0.0385 | 0.0385 | 0.0 |
| causality-heavy-explain | sonnet | deep | factual | 2 | 26 | yes | 0.8077 | 0.8077 | 0.0 | 0.0769 | 0.0769 | 0.0 |
| causality-heavy-explain | sonnet | deep | relational | 2 | 26 | yes | 0.8077 | 0.8077 | 0.0 | 0.0769 | 0.0769 | 0.0 |
| cause-chain-reversal | haiku | skim | factual | 1 | 2 | yes | 1.0 | 1.0 | 0.0 | 0.5 | 0.5 | 0.0 |
| cause-chain-reversal | haiku | skim | factual | 2 | - | no (f11:status=omitted,unaligned_in_rendering,f12:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | relational | 1 | - | no (r3:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | relational | 2 | - | no (f15:status=omitted,unaligned_in_rendering,f16:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | factual | 2 | - | no (f17:status=omitted,unaligned_in_rendering,f18:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | relational | 1 | - | no (r6:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | factual | 1 | - | no (f19:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | factual | 1 | - | no (f10:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | factual | 1 | 9 | yes | 0.2222 | 0.2222 | 0.0 | 0.1111 | 0.1111 | 0.0 |
| cause-chain-reversal | haiku | standard | factual | 2 | 9 | yes | 0.5556 | 1.0 | 0.4444 | 0.2222 | 0.6667 | 0.4445 |
| cause-chain-reversal | haiku | standard | relational | 1 | - | no (r3:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | relational | 2 | - | no (f16:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | factual | 2 | - | no (f18:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | relational | 1 | - | no (r6:status=partial,unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | factual | 1 | - | no (f19:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | factual | 1 | - | no (f10:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | deep | factual | 1 | 21 | yes | 0.1429 | 0.1429 | 0.0 | 0.0476 | 0.0476 | 0.0 |
| cause-chain-reversal | haiku | deep | factual | 2 | 21 | yes | 0.5238 | 0.6667 | 0.1429 | 0.1429 | 0.2857 | 0.1428 |
| cause-chain-reversal | haiku | deep | relational | 1 | 21 | yes | 0.5714 | 0.4762 | -0.0952 | 0.0476 | 0.0476 | 0.0 |
| cause-chain-reversal | haiku | deep | relational | 2 | - | no (f16:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | deep | factual | 2 | 21 | yes | 0.8571 | 0.8095 | -0.0476 | 0.0952 | 0.1429 | 0.0477 |
| cause-chain-reversal | haiku | deep | relational | 1 | - | no (r6:status=partial,unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | deep | factual | 1 | 21 | yes | 0.9524 | 0.8571 | -0.0953 | 0.0476 | 0.0476 | 0.0 |
| cause-chain-reversal | haiku | deep | factual | 1 | 21 | yes | 0.381 | 0.5238 | 0.1428 | 0.0476 | 0.0476 | 0.0 |
| cause-chain-reversal | sonnet | skim | factual | 1 | 11 | yes | 0.2727 | 0.2727 | 0.0 | 0.0909 | 0.0909 | 0.0 |
| cause-chain-reversal | sonnet | skim | factual | 2 | 11 | yes | 0.6364 | 0.6364 | 0.0 | 0.1818 | 0.1818 | 0.0 |
| cause-chain-reversal | sonnet | skim | relational | 1 | - | no (r3:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | skim | relational | 2 | - | no (f16:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | skim | factual | 2 | - | no (f18:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | skim | relational | 1 | - | no (r6:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | skim | factual | 1 | - | no (f19:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | skim | factual | 1 | - | no (f10:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | standard | factual | 1 | 25 | yes | 0.12 | 0.12 | 0.0 | 0.04 | 0.04 | 0.0 |
| cause-chain-reversal | sonnet | standard | factual | 2 | 25 | yes | 0.56 | 0.64 | 0.08 | 0.12 | 0.24 | 0.12 |
| cause-chain-reversal | sonnet | standard | relational | 1 | 25 | yes | 0.6 | 0.68 | 0.08 | 0.04 | 0.04 | 0.0 |
| cause-chain-reversal | sonnet | standard | relational | 2 | 25 | yes | 0.8 | 0.8 | 0.0 | 0.12 | 0.12 | 0.0 |
| cause-chain-reversal | sonnet | standard | factual | 2 | 25 | yes | 0.88 | 0.88 | 0.0 | 0.08 | 0.08 | 0.0 |
| cause-chain-reversal | sonnet | standard | relational | 1 | 25 | yes | 0.28 | 0.2 | -0.08 | 0.04 | 0.04 | 0.0 |
| cause-chain-reversal | sonnet | standard | factual | 1 | 25 | yes | 0.96 | 0.96 | 0.0 | 0.04 | 0.04 | 0.0 |
| cause-chain-reversal | sonnet | standard | factual | 1 | - | no (f10:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | deep | factual | 1 | 26 | yes | 0.1154 | 0.1154 | 0.0 | 0.0385 | 0.0385 | 0.0 |
| cause-chain-reversal | sonnet | deep | factual | 2 | 26 | yes | 0.5769 | 0.6538 | 0.0769 | 0.1154 | 0.1923 | 0.0769 |
| cause-chain-reversal | sonnet | deep | relational | 1 | 26 | yes | 0.6154 | 0.6923 | 0.0769 | 0.0385 | 0.0385 | 0.0 |
| cause-chain-reversal | sonnet | deep | relational | 2 | 26 | yes | 0.8077 | 0.8077 | 0.0 | 0.1154 | 0.1154 | 0.0 |
| cause-chain-reversal | sonnet | deep | factual | 2 | 26 | yes | 0.8846 | 0.8846 | 0.0 | 0.0769 | 0.0769 | 0.0 |
| cause-chain-reversal | sonnet | deep | relational | 1 | 26 | yes | 0.2692 | 0.1923 | -0.0769 | 0.0385 | 0.0385 | 0.0 |
| cause-chain-reversal | sonnet | deep | factual | 1 | 26 | yes | 0.9615 | 0.9615 | 0.0 | 0.0385 | 0.0385 | 0.0 |
| cause-chain-reversal | sonnet | deep | factual | 1 | 26 | yes | 0.4615 | 0.4231 | -0.0384 | 0.0385 | 0.0385 | 0.0 |
| migration-tristate | haiku | skim | factual | 1 | 3 | yes | 0.3333 | 0.3333 | 0.0 | 0.3333 | 0.3333 | 0.0 |
| migration-tristate | haiku | skim | factual | 2 | - | no (f8:status=omitted,unaligned_in_rendering,f9:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | skim | factual | 1 | - | no (f10:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | skim | factual | 1 | 3 | yes | 0.6667 | 0.6667 | 0.0 | 0.3333 | 0.3333 | 0.0 |
| migration-tristate | haiku | skim | factual | 1 | - | no (f13:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | skim | relational | 1 | - | no (r6:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | skim | factual | 1 | - | no (f4:status=partial) | - | - | - | - | - | - |
| migration-tristate | haiku | skim | factual | 1 | - | no (f15:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | standard | factual | 1 | 13 | yes | 0.4615 | 0.4615 | 0.0 | 0.0769 | 0.0769 | 0.0 |
| migration-tristate | haiku | standard | factual | 2 | 13 | yes | 0.6154 | 0.6154 | 0.0 | 0.1538 | 0.1538 | 0.0 |
| migration-tristate | haiku | standard | factual | 1 | - | no (f10:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | standard | factual | 1 | 13 | yes | 0.6923 | 0.6923 | 0.0 | 0.0769 | 0.0769 | 0.0 |
| migration-tristate | haiku | standard | factual | 1 | 13 | yes | 0.9231 | 0.9231 | 0.0 | 0.0769 | 0.0769 | 0.0 |
| migration-tristate | haiku | standard | relational | 1 | - | no (r6:status=partial,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | standard | factual | 1 | 13 | yes | 0.2308 | 0.2308 | 0.0 | 0.0769 | 0.0769 | 0.0 |
| migration-tristate | haiku | standard | factual | 1 | - | no (f15:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | deep | factual | 1 | 20 | yes | 0.4 | 0.4 | 0.0 | 0.05 | 0.05 | 0.0 |
| migration-tristate | haiku | deep | factual | 2 | 20 | yes | 0.5 | 0.5 | 0.0 | 0.1 | 0.1 | 0.0 |
| migration-tristate | haiku | deep | factual | 1 | 20 | yes | 0.55 | 0.55 | 0.0 | 0.05 | 0.05 | 0.0 |
| migration-tristate | haiku | deep | factual | 1 | 20 | yes | 0.6 | 0.6 | 0.0 | 0.05 | 0.05 | 0.0 |
| migration-tristate | haiku | deep | factual | 1 | 20 | yes | 0.7 | 0.75 | 0.05 | 0.05 | 0.05 | 0.0 |
| migration-tristate | haiku | deep | relational | 1 | 20 | yes | 1.0 | 1.0 | 0.0 | 0.05 | 0.05 | 0.0 |
| migration-tristate | haiku | deep | factual | 1 | 20 | yes | 0.2 | 0.2 | 0.0 | 0.05 | 0.05 | 0.0 |
| migration-tristate | haiku | deep | factual | 1 | 20 | yes | 0.8 | 0.8 | 0.0 | 0.05 | 0.05 | 0.0 |
| migration-tristate | sonnet | skim | factual | 1 | 4 | yes | 0.25 | 0.5 | 0.25 | 0.25 | 0.25 | 0.0 |
| migration-tristate | sonnet | skim | factual | 2 | - | no (f8:status=omitted,unaligned_in_rendering,f9:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | factual | 1 | - | no (f10:status=partial) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | factual | 1 | - | no (f11:status=partial) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | factual | 1 | - | no (f13:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | relational | 1 | - | no (r6:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | factual | 1 | - | no (f4:status=partial) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | factual | 1 | - | no (f15:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | sonnet | standard | factual | 1 | 21 | yes | 0.3333 | 0.381 | 0.0477 | 0.0476 | 0.0476 | 0.0 |
| migration-tristate | sonnet | standard | factual | 2 | 21 | yes | 0.4762 | 0.5238 | 0.0476 | 0.0952 | 0.0952 | 0.0 |
| migration-tristate | sonnet | standard | factual | 1 | 21 | yes | 0.5714 | 0.5714 | 0.0 | 0.0476 | 0.0476 | 0.0 |
| migration-tristate | sonnet | standard | factual | 1 | 21 | yes | 0.619 | 0.619 | 0.0 | 0.0476 | 0.0476 | 0.0 |
| migration-tristate | sonnet | standard | factual | 1 | 21 | yes | 0.7143 | 0.7619 | 0.0476 | 0.0476 | 0.0476 | 0.0 |
| migration-tristate | sonnet | standard | relational | 1 | 21 | yes | 1.0 | 0.9524 | -0.0476 | 0.0476 | 0.0476 | 0.0 |
| migration-tristate | sonnet | standard | factual | 1 | 21 | yes | 0.1429 | 0.2381 | 0.0952 | 0.0476 | 0.0476 | 0.0 |
| migration-tristate | sonnet | standard | factual | 1 | 21 | yes | 0.8095 | 0.8095 | 0.0 | 0.0476 | 0.0476 | 0.0 |
| migration-tristate | sonnet | deep | factual | 1 | 24 | yes | 0.3333 | 0.4167 | 0.0834 | 0.0417 | 0.0417 | 0.0 |
| migration-tristate | sonnet | deep | factual | 2 | 24 | yes | 0.4583 | 0.5417 | 0.0834 | 0.0833 | 0.125 | 0.0417 |
| migration-tristate | sonnet | deep | factual | 1 | 24 | yes | 0.5417 | 0.5833 | 0.0416 | 0.0417 | 0.0417 | 0.0 |
| migration-tristate | sonnet | deep | factual | 1 | 24 | yes | 0.5833 | 0.625 | 0.0417 | 0.0417 | 0.0417 | 0.0 |
| migration-tristate | sonnet | deep | factual | 1 | 24 | yes | 0.6667 | 0.75 | 0.0833 | 0.0417 | 0.0417 | 0.0 |
| migration-tristate | sonnet | deep | relational | 1 | 24 | yes | 1.0 | 0.9583 | -0.0417 | 0.0417 | 0.0417 | 0.0 |
| migration-tristate | sonnet | deep | factual | 1 | 24 | yes | 0.1667 | 0.2917 | 0.125 | 0.0417 | 0.0417 | 0.0 |
| migration-tristate | sonnet | deep | factual | 1 | 24 | yes | 0.7917 | 0.7917 | 0.0 | 0.0417 | 0.0417 | 0.0 |
| near-identical-numbers | sonnet | skim | factual | 1 | 4 | yes | 0.25 | 0.25 | 0.0 | 0.25 | 0.25 | 0.0 |
| near-identical-numbers | sonnet | skim | factual | 1 | 4 | yes | 0.5 | 0.5 | 0.0 | 0.25 | 0.25 | 0.0 |
| near-identical-numbers | sonnet | skim | relational | 1 | 4 | yes | 1.0 | 1.0 | 0.0 | 0.25 | 0.25 | 0.0 |
| near-identical-numbers | sonnet | skim | factual | 2 | - | no (f2:status=omitted,unaligned_in_rendering,f6:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | skim | factual | 2 | - | no (f10:status=partial,unaligned_in_rendering,f11:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | skim | factual | 2 | - | no (f13:status=partial,unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | skim | factual | 1 | - | no (f14:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | skim | relational | 2 | - | no (r2:status=lost,unaligned_in_rendering,r3:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | standard | factual | 1 | 16 | yes | 0.0625 | 0.0625 | 0.0 | 0.0625 | 0.0625 | 0.0 |
| near-identical-numbers | sonnet | standard | factual | 1 | 16 | yes | 0.3125 | 0.3125 | 0.0 | 0.0625 | 0.0625 | 0.0 |
| near-identical-numbers | sonnet | standard | relational | 1 | 16 | yes | 0.9375 | 0.9375 | 0.0 | 0.0625 | 0.0625 | 0.0 |
| near-identical-numbers | sonnet | standard | factual | 2 | - | no (f2:status=partial,unaligned_in_rendering,f6:status=partial,unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | standard | factual | 2 | 16 | yes | 0.625 | 0.625 | 0.0 | 0.125 | 0.125 | 0.0 |
| near-identical-numbers | sonnet | standard | factual | 2 | 16 | yes | 0.75 | 0.75 | 0.0 | 0.125 | 0.125 | 0.0 |
| near-identical-numbers | sonnet | standard | factual | 1 | 16 | yes | 0.875 | 0.875 | 0.0 | 0.0625 | 0.0625 | 0.0 |
| near-identical-numbers | sonnet | standard | relational | 2 | 16 | yes | 0.5 | 0.4375 | -0.0625 | 0.3125 | 0.3125 | 0.0 |
| near-identical-numbers | sonnet | deep | factual | 1 | 19 | yes | 0.0526 | 0.0526 | 0.0 | 0.0526 | 0.0526 | 0.0 |
| near-identical-numbers | sonnet | deep | factual | 1 | 19 | yes | 0.3158 | 0.3158 | 0.0 | 0.0526 | 0.0526 | 0.0 |
| near-identical-numbers | sonnet | deep | relational | 1 | 19 | yes | 0.9474 | 0.9474 | 0.0 | 0.0526 | 0.0526 | 0.0 |
| near-identical-numbers | sonnet | deep | factual | 2 | 19 | yes | 0.3684 | 0.3684 | 0.0 | 0.3158 | 0.3158 | 0.0 |
| near-identical-numbers | sonnet | deep | factual | 2 | 19 | yes | 0.6842 | 0.7368 | 0.0526 | 0.1053 | 0.2105 | 0.1052 |
| near-identical-numbers | sonnet | deep | factual | 2 | - | no (f13:unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | deep | factual | 1 | 19 | yes | 0.8947 | 0.8947 | 0.0 | 0.0526 | 0.0526 | 0.0 |
| near-identical-numbers | sonnet | deep | relational | 2 | 19 | yes | 0.5263 | 0.4211 | -0.1052 | 0.3158 | 0.2632 | -0.0526 |
| negation-and-true-peers | sonnet | skim | factual | 1 | - | no (f5:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | factual | 1 | - | no (f6:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | factual | 2 | - | no (f14:status=omitted,unaligned_in_rendering,f15:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | relational | 1 | - | no (r1:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | factual | 2 | - | no (f17:status=omitted,unaligned_in_rendering,f18:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | relational | 1 | - | no (r3:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | relational | 1 | - | no (r2:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | relational | 1 | - | no (r4:status=partial) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | standard | factual | 1 | 21 | yes | 0.2857 | 0.2857 | 0.0 | 0.0476 | 0.0476 | 0.0 |
| negation-and-true-peers | sonnet | standard | factual | 1 | 21 | yes | 0.3333 | 0.3333 | 0.0 | 0.0476 | 0.0476 | 0.0 |
| negation-and-true-peers | sonnet | standard | factual | 2 | 21 | yes | 0.7619 | 0.7619 | 0.0 | 0.0952 | 0.0952 | 0.0 |
| negation-and-true-peers | sonnet | standard | relational | 1 | - | no (r1:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | standard | factual | 2 | 21 | yes | 0.8571 | 0.8571 | 0.0 | 0.0952 | 0.0952 | 0.0 |
| negation-and-true-peers | sonnet | standard | relational | 1 | 21 | yes | 1.0 | 0.9524 | -0.0476 | 0.0476 | 0.0476 | 0.0 |
| negation-and-true-peers | sonnet | standard | relational | 1 | 21 | yes | 0.5714 | 0.5714 | 0.0 | 0.0476 | 0.0476 | 0.0 |
| negation-and-true-peers | sonnet | standard | relational | 1 | 21 | yes | 0.1429 | 0.0952 | -0.0477 | 0.0476 | 0.0476 | 0.0 |
| negation-and-true-peers | sonnet | deep | factual | 1 | - | no (f5:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | deep | factual | 1 | 19 | yes | 0.2632 | 0.2632 | 0.0 | 0.0526 | 0.0526 | 0.0 |
| negation-and-true-peers | sonnet | deep | factual | 2 | 19 | yes | 0.7368 | 0.7368 | 0.0 | 0.1579 | 0.1053 | -0.0526 |
| negation-and-true-peers | sonnet | deep | relational | 1 | 19 | yes | 0.6842 | 0.6316 | -0.0526 | 0.0526 | 0.0526 | 0.0 |
| negation-and-true-peers | sonnet | deep | factual | 2 | 19 | yes | 0.8947 | 0.8947 | 0.0 | 0.1053 | 0.1053 | 0.0 |
| negation-and-true-peers | sonnet | deep | relational | 1 | - | no (r3:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | deep | relational | 1 | - | no (r2:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | deep | relational | 1 | - | no (r4:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 3 | - | no (f3:status=partial) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 2 | - | no (f6:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | relational | 2 | - | no (r2:status=partial,f13:status=partial) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | relational | 1 | - | no (r3:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 3 | - | no (f16:status=partial,f17:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 3 | - | no (f18:status=partial,f19:status=partial,f20:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 1 | - | no (f23:status=partial) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 1 | 7 | yes | 1.0 | 1.0 | 0.0 | 0.1429 | 0.1429 | 0.0 |
| real-benchmark-archaeology | sonnet | standard | factual | 3 | - | no (f1:status=partial,unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | standard | factual | 2 | - | no (f5:status=partial,unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | standard | relational | 2 | - | no (r2:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | standard | relational | 1 | 21 | yes | 0.5714 | 0.5714 | 0.0 | 0.0476 | 0.0476 | 0.0 |
| real-benchmark-archaeology | sonnet | standard | factual | 3 | 21 | yes | 0.7143 | 0.7143 | 0.0 | 0.1429 | 0.1429 | 0.0 |
| real-benchmark-archaeology | sonnet | standard | factual | 3 | - | no (f20:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | standard | factual | 1 | 21 | yes | 0.9524 | 0.9524 | 0.0 | 0.0476 | 0.0476 | 0.0 |
| real-benchmark-archaeology | sonnet | standard | factual | 1 | 21 | yes | 1.0 | 1.0 | 0.0 | 0.0476 | 0.0476 | 0.0 |
| real-benchmark-archaeology | sonnet | deep | factual | 3 | - | no (f1:status=partial,unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | deep | factual | 2 | - | no (f5:status=partial,unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | deep | relational | 2 | 27 | yes | 0.4444 | 0.4444 | 0.0 | 0.0741 | 0.0741 | 0.0 |
| real-benchmark-archaeology | sonnet | deep | relational | 1 | 27 | yes | 0.5185 | 0.5185 | 0.0 | 0.037 | 0.037 | 0.0 |
| real-benchmark-archaeology | sonnet | deep | factual | 3 | 27 | yes | 0.6667 | 0.6667 | 0.0 | 0.1481 | 0.1481 | 0.0 |
| real-benchmark-archaeology | sonnet | deep | factual | 3 | 27 | yes | 0.8148 | 0.8148 | 0.0 | 0.1481 | 0.1481 | 0.0 |
| real-benchmark-archaeology | sonnet | deep | factual | 1 | 27 | yes | 0.963 | 0.9259 | -0.0371 | 0.037 | 0.037 | 0.0 |
| real-benchmark-archaeology | sonnet | deep | factual | 1 | 27 | yes | 1.0 | 1.0 | 0.0 | 0.037 | 0.037 | 0.0 |
| real-hook-discovery | sonnet | skim | factual | 3 | - | no (f1:status=partial,f2:status=partial) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | skim | relational | 1 | - | no (r1:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | skim | relational | 2 | - | no (r2:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | skim | factual | 2 | - | no (f8:status=omitted,unaligned_in_rendering,f9:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | skim | factual | 1 | - | no (f11:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | skim | relational | 1 | 6 | yes | 0.6667 | 0.6667 | 0.0 | 0.1667 | 0.1667 | 0.0 |
| real-hook-discovery | sonnet | skim | factual | 1 | 6 | yes | 1.0 | 1.0 | 0.0 | 0.1667 | 0.1667 | 0.0 |
| real-hook-discovery | sonnet | skim | factual | 1 | - | no (f15:status=partial) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | standard | factual | 3 | 16 | yes | 0.1875 | 0.1875 | 0.0 | 0.1875 | 0.1875 | 0.0 |
| real-hook-discovery | sonnet | standard | relational | 1 | - | no (r1:status=partial) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | standard | relational | 2 | 16 | yes | 0.3125 | 0.375 | 0.0625 | 0.125 | 0.1875 | 0.0625 |
| real-hook-discovery | sonnet | standard | factual | 2 | 16 | yes | 0.5625 | 0.5625 | 0.0 | 0.125 | 0.125 | 0.0 |
| real-hook-discovery | sonnet | standard | factual | 1 | 16 | yes | 0.75 | 0.8125 | 0.0625 | 0.0625 | 0.0625 | 0.0 |
| real-hook-discovery | sonnet | standard | relational | 1 | 16 | yes | 0.6875 | 0.6875 | 0.0 | 0.0625 | 0.0625 | 0.0 |
| real-hook-discovery | sonnet | standard | factual | 1 | 16 | yes | 0.9375 | 0.9375 | 0.0 | 0.0625 | 0.0625 | 0.0 |
| real-hook-discovery | sonnet | standard | factual | 1 | 16 | yes | 1.0 | 1.0 | 0.0 | 0.0625 | 0.0625 | 0.0 |
| real-hook-discovery | sonnet | deep | factual | 3 | 19 | yes | 0.1579 | 0.1579 | 0.0 | 0.1579 | 0.1579 | 0.0 |
| real-hook-discovery | sonnet | deep | relational | 1 | 19 | yes | 0.2105 | 0.2632 | 0.0527 | 0.0526 | 0.0526 | 0.0 |
| real-hook-discovery | sonnet | deep | relational | 2 | 19 | yes | 0.3684 | 0.4211 | 0.0527 | 0.1053 | 0.1579 | 0.0526 |
| real-hook-discovery | sonnet | deep | factual | 2 | 19 | yes | 0.5789 | 0.5789 | 0.0 | 0.1053 | 0.1053 | 0.0 |
| real-hook-discovery | sonnet | deep | factual | 1 | 19 | yes | 0.7368 | 0.7895 | 0.0527 | 0.0526 | 0.0526 | 0.0 |
| real-hook-discovery | sonnet | deep | relational | 1 | 19 | yes | 0.6842 | 0.6842 | 0.0 | 0.0526 | 0.0526 | 0.0 |
| real-hook-discovery | sonnet | deep | factual | 1 | 19 | yes | 0.9474 | 0.9474 | 0.0 | 0.0526 | 0.0526 | 0.0 |
| real-hook-discovery | sonnet | deep | factual | 1 | 19 | yes | 1.0 | 1.0 | 0.0 | 0.0526 | 0.0526 | 0.0 |
| synthetic-scale-verylarge | haiku | skim | relational | 1 | - | no (r3:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | factual | 1 | - | no (f5:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | relational | 2 | - | no (f7:status=omitted,unaligned_in_rendering,f8:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | factual | 2 | - | no (f11:status=omitted,unaligned_in_rendering,f12:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | relational | 1 | - | no (r6:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | factual | 2 | 5 | yes | 0.4 | 0.4 | 0.0 | 0.4 | 0.4 | 0.0 |
| synthetic-scale-verylarge | haiku | skim | relational | 1 | - | no (r11:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | factual | 1 | - | no (f43:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | standard | relational | 1 | - | no (r3:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | standard | factual | 1 | - | no (f5:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | standard | relational | 2 | - | no (f7:status=partial,f8:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | standard | factual | 2 | 22 | yes | 0.2273 | 0.2273 | 0.0 | 0.1364 | 0.1364 | 0.0 |
| synthetic-scale-verylarge | haiku | standard | relational | 1 | 22 | yes | 0.5 | 0.4545 | -0.0455 | 0.0455 | 0.0455 | 0.0 |
| synthetic-scale-verylarge | haiku | standard | factual | 2 | 22 | yes | 0.6364 | 0.6364 | 0.0 | 0.0909 | 0.0909 | 0.0 |
| synthetic-scale-verylarge | haiku | standard | relational | 1 | - | no (r11:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | standard | factual | 1 | 22 | yes | 0.8636 | 0.8636 | 0.0 | 0.0455 | 0.0455 | 0.0 |
| synthetic-scale-verylarge | haiku | deep | relational | 1 | 50 | yes | 0.36 | 0.36 | 0.0 | 0.02 | 0.02 | 0.0 |
| synthetic-scale-verylarge | haiku | deep | factual | 1 | 50 | yes | 0.1 | 0.18 | 0.08 | 0.02 | 0.02 | 0.0 |
| synthetic-scale-verylarge | haiku | deep | relational | 2 | - | no (f7:status=partial,f8:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | deep | factual | 2 | 50 | yes | 0.26 | 0.32 | 0.06 | 0.06 | 0.06 | 0.0 |
| synthetic-scale-verylarge | haiku | deep | relational | 1 | 50 | yes | 0.54 | 0.5 | -0.04 | 0.02 | 0.02 | 0.0 |
| synthetic-scale-verylarge | haiku | deep | factual | 2 | 50 | yes | 0.62 | 0.62 | 0.0 | 0.04 | 0.04 | 0.0 |
| synthetic-scale-verylarge | haiku | deep | relational | 1 | 50 | yes | 0.96 | 0.92 | -0.04 | 0.02 | 0.02 | 0.0 |
| synthetic-scale-verylarge | haiku | deep | factual | 1 | 50 | yes | 0.9 | 0.96 | 0.06 | 0.02 | 0.02 | 0.0 |
| synthetic-scale-verylarge | sonnet | skim | relational | 1 | - | no (r3:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | factual | 1 | - | no (f5:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | relational | 2 | - | no (f7:status=omitted,unaligned_in_rendering,f8:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | factual | 2 | - | no (f11:status=partial,f12:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | relational | 1 | 6 | yes | 0.5 | 0.5 | 0.0 | 0.1667 | 0.1667 | 0.0 |
| synthetic-scale-verylarge | sonnet | skim | factual | 2 | - | no (r8:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | relational | 1 | - | no (r11:status=lost,unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | factual | 1 | - | no (f43:status=omitted,unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | standard | relational | 1 | 31 | yes | 0.2581 | 0.0323 | -0.2258 | 0.0323 | 0.0323 | 0.0 |
| synthetic-scale-verylarge | sonnet | standard | factual | 1 | 31 | yes | 0.0323 | 0.0645 | 0.0322 | 0.0323 | 0.0323 | 0.0 |
| synthetic-scale-verylarge | sonnet | standard | relational | 2 | - | no (f7:status=partial,f8:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | standard | factual | 2 | 31 | yes | 0.1935 | 0.2581 | 0.0646 | 0.0968 | 0.0968 | 0.0 |
| synthetic-scale-verylarge | sonnet | standard | relational | 1 | - | no (r6:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | standard | factual | 2 | - | no (r8:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | standard | relational | 1 | 31 | yes | 0.9355 | 0.8387 | -0.0968 | 0.0323 | 0.0323 | 0.0 |
| synthetic-scale-verylarge | sonnet | standard | factual | 1 | 31 | yes | 0.871 | 0.9677 | 0.0967 | 0.0323 | 0.0323 | 0.0 |
| synthetic-scale-verylarge | sonnet | deep | relational | 1 | 56 | yes | 0.375 | 0.0357 | -0.3393 | 0.0179 | 0.0179 | 0.0 |
| synthetic-scale-verylarge | sonnet | deep | factual | 1 | 56 | yes | 0.0893 | 0.1964 | 0.1071 | 0.0179 | 0.0179 | 0.0 |
| synthetic-scale-verylarge | sonnet | deep | relational | 2 | 56 | yes | 0.1786 | 0.25 | 0.0714 | 0.0536 | 0.0536 | 0.0 |
| synthetic-scale-verylarge | sonnet | deep | factual | 2 | 56 | yes | 0.2857 | 0.3571 | 0.0714 | 0.0536 | 0.0536 | 0.0 |
| synthetic-scale-verylarge | sonnet | deep | relational | 1 | 56 | yes | 0.5536 | 0.5536 | 0.0 | 0.0179 | 0.0179 | 0.0 |
| synthetic-scale-verylarge | sonnet | deep | factual | 2 | 56 | yes | 0.625 | 0.625 | 0.0 | 0.0357 | 0.0357 | 0.0 |
| synthetic-scale-verylarge | sonnet | deep | relational | 1 | 56 | yes | 0.9643 | 0.8929 | -0.0714 | 0.0179 | 0.0179 | 0.0 |
| synthetic-scale-verylarge | sonnet | deep | factual | 1 | 56 | yes | 0.9107 | 0.9643 | 0.0536 | 0.0179 | 0.0179 | 0.0 |

## Delta EAC / delta locality-span by question type (strict-eligible, unit-rank)

| question type | n | avg delta EAC | avg delta locality-span |
|---|---|---|---|
| factual | 108 | 0.0237 | 0.0086 |
| relational | 48 | -0.0262 | 0.0013 |

## Delta EAC / delta locality-span by granularity level (strict-eligible, unit-rank)

| level | n | avg delta EAC | avg delta locality-span |
|---|---|---|---|
| skim | 17 | 0.0147 | 0.0 |
| standard | 61 | 0.0083 | 0.0103 |
| deep | 78 | 0.007 | 0.0046 |

## Delta EAC by support-unit count (single vs. multi-support, strict-eligible, unit-rank)

| support | n | avg delta EAC | avg delta locality-span |
|---|---|---|---|
| single | 105 | 0.002 | 0.0 |
| multi | 51 | 0.0215 | 0.0194 |

**Strict eligibility (unit-rank):** 156/264 (case, tier, level, question) combinations were strict-findability-scorable (59.1%). See `results/findability.json` for the per-question `reasons` on every ineligible one, and each rendering's `retained_set.strict.excluded` for why any given unit did not make it into `R`.

## Diagnostic only: token-normalized, case-level-baseline EAC (no longer the headline metric -- see `FINDABILITY_FINDINGS.md` "Failure mode 2")

| question type | n | avg delta EAC (diagnostic, token-based) |
|---|---|---|
| factual | 108 | 0.0251 |
| relational | 48 | -0.0369 |
