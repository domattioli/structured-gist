# Semantic-compression eval suite: canonical scores (generated, do not hand-edit)

Regenerate with `python3 scoring/deterministic.py && python3 scoring/combine.py`.

## regression

| case | tier | level | src_w | out_w | reduction% | conform_viol | wRetention | relRetention | omission% | unsupported_claims | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| near-identical-numbers | sonnet | skim | 276 | 50 | 81.88 | 0 | 0.3115 | 0.25 | 57.1 | 0 | 0.5 |
| near-identical-numbers | sonnet | standard | 276 | 160 | 42.03 | 7 | 0.9508 | 0.9167 | 0 | 0 | 1.0 |
| near-identical-numbers | sonnet | deep | 276 | 255 | 7.61 | 6 | 1.0 | 1.0 | 0 | 0 | 1.0 |
| real-benchmark-archaeology | sonnet | skim | 466 | 74 | 84.12 | 0 | 0.4658 | 0.5 | 33.3 | 0 | 0.5625 |
| real-benchmark-archaeology | sonnet | standard | 466 | 190 | 59.23 | 3 | 0.8846 | 0.9167 | 4.2 | 0 | 0.8125 |
| real-benchmark-archaeology | sonnet | deep | 466 | 344 | 26.18 | 2 | 0.9658 | 1.0 | 0 | 0 | 0.875 |
| real-hook-discovery | sonnet | skim | 231 | 49 | 78.79 | 0 | 0.3923 | 0.6 | 40.0 | 0 | 0.6875 |
| real-hook-discovery | sonnet | standard | 231 | 125 | 45.89 | 0 | 0.9538 | 0.9 | 0 | 0 | 1.0 |
| real-hook-discovery | sonnet | deep | 231 | 167 | 27.71 | 0 | 1.0 | 1.0 | 0 | 0 | 1.0 |

## pressure-tests

| case | tier | level | src_w | out_w | reduction% | conform_viol | wRetention | relRetention | omission% | unsupported_claims | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| causality-heavy-explain | sonnet | skim | 369 | 51 | 86.18 | 0 | 0.5556 | 0.0625 | 20.0 | 0 | 0.5625 |
| causality-heavy-explain | sonnet | standard | 369 | 166 | 55.01 | 6 | 0.8 | 0.5625 | 5.0 | 0 | 0.9375 |
| causality-heavy-explain | sonnet | deep | 369 | 333 | 9.76 | 6 | 0.9722 | 0.9375 | 0 | 0 | 1.0 |
| cause-chain-reversal | haiku | skim | 361 | 16 | 95.57 | 0 | 0.101 | 0.0833 | 85.0 | 0 | 0.3125 |
| cause-chain-reversal | haiku | standard | 361 | 71 | 80.33 | 2 | 0.5707 | 0.5 | 30.0 | 0 | 0.625 |
| cause-chain-reversal | haiku | deep | 361 | 133 | 63.16 | 8 | 0.8333 | 0.9167 | 10.0 | 0 | 0.9375 |
| cause-chain-reversal | sonnet | skim | 361 | 90 | 75.07 | 0 | 0.6414 | 0.6667 | 15.0 | 0 | 0.8125 |
| cause-chain-reversal | sonnet | standard | 361 | 356 | 1.39 | 0 | 0.9747 | 1.0 | 0 | 0 | 0.8125 |
| cause-chain-reversal | sonnet | deep | 361 | 411 | -13.85 | 0 | 1.0 | 1.0 | 0 | 0 | 1.0 |
| migration-tristate | haiku | skim | 280 | 29 | 89.64 | 2 | 0.25 | 0.1667 | 68.4 | 0 | 0.3125 |
| migration-tristate | haiku | standard | 280 | 127 | 54.64 | 5 | 0.7442 | 0.75 | 15.8 | 0 | 0.6875 |
| migration-tristate | haiku | deep | 280 | 252 | 10.0 | 20 | 0.9884 | 1.0 | 0 | 0 | 1.0 |
| migration-tristate | sonnet | skim | 280 | 27 | 90.36 | 0 | 0.314 | 0.25 | 57.9 | 0 | 0.3125 |
| migration-tristate | sonnet | standard | 280 | 144 | 48.57 | 0 | 0.9477 | 0.9167 | 0 | 0 | 1.0 |
| migration-tristate | sonnet | deep | 280 | 189 | 32.5 | 0 | 1.0 | 1.0 | 0 | 0 | 1.0 |
| negation-and-true-peers | sonnet | skim | 272 | 46 | 83.09 | 1 | 0.0316 | 0.125 | 95.0 | 0 | 0.0625 |
| negation-and-true-peers | sonnet | standard | 272 | 225 | 17.28 | 1 | 0.9895 | 1.0 | 0 | 0 | 1.0 |
| negation-and-true-peers | sonnet | deep | 272 | 241 | 11.4 | 1 | 0.9895 | 1.0 | 0 | 0 | 1.0 |
| synthetic-scale-verylarge | haiku | skim | 1313 | 61 | 95.35 | 3 | 0.1579 | 0.25 | 73.9 | 0 | 0.1875 |
| synthetic-scale-verylarge | haiku | standard | 1313 | 240 | 81.72 | 14 | 0.5553 | 0.625 | 21.7 | 0 | 1.0 |
| synthetic-scale-verylarge | haiku | deep | 1313 | 733 | 44.17 | 43 | 0.9079 | 0.9167 | 2.2 | 0 | 1.0 |
| synthetic-scale-verylarge | sonnet | skim | 1313 | 72 | 94.52 | 0 | 0.2526 | 0.25 | 58.7 | 0 | 0.3125 |
| synthetic-scale-verylarge | sonnet | standard | 1313 | 462 | 64.81 | 0 | 0.7316 | 0.7917 | 8.7 | 0 | 1.0 |
| synthetic-scale-verylarge | sonnet | deep | 1313 | 972 | 25.97 | 2 | 0.9947 | 0.9583 | 0 | 0 | 1.0 |
