# Semantic Preservation Recall (SPR): experimental results (generated, do not hand-edit)

**Experimental, not canonical.** This table is produced by `scoring/spr.py`, a measurement additive to `scoring/combine.py` -- see `../SPR_FINDINGS.md` for the full write-up and whether this metric should be kept. Regenerate with `python3 scoring/deterministic.py && python3 scoring/combine.py && python3 scoring/spr.py`.

## Blinded weight comparison (legacy category-derived vs. blinded task-derived, facts only)

| case | n facts | exact agreement | mean abs diff (legacy scale) | Spearman rho |
|---|---|---|---|---|
| causality-heavy-explain | 20 | 0.55 | 0.65 | 0.3287 |
| cause-chain-reversal | 20 | 0.5 | 0.475 | 0.5736 |
| migration-tristate | 19 | 0.5263 | 0.7368 | 0.2446 |
| near-identical-numbers | 14 | 0.2857 | 1.0357 | -0.274 |
| negation-and-true-peers | 20 | 0.6 | 0.525 | 0.6886 |
| real-benchmark-archaeology | 24 | 0.4167 | 0.6042 | 0.2478 |
| real-hook-discovery | 15 | 0.3333 | 0.8333 | 0.1491 |
| synthetic-scale-verylarge | 46 | 0.4783 | 0.6739 | 0.4588 |

## SPR and component metrics per (case, tier, level)

| case | tier | level | compression | legacy fact retention | blinded fact recall | weighted relation recall | SPR | recoverability | critical lost/partial/total | conform_viol |
|---|---|---|---|---|---|---|---|---|---|
| causality-heavy-explain | sonnet | skim | 86.18 | 0.5556 | 0.566 | 0.0625 | 0.4091 | 0.5625 | 10/7/21 | 0 |
| causality-heavy-explain | sonnet | standard | 55.01 | 0.8 | 0.783 | 0.5625 | 0.7143 | 0.9375 | 4/6/21 | 6 |
| causality-heavy-explain | sonnet | deep | 9.76 | 0.9722 | 0.9717 | 0.9375 | 0.961 | 1.0 | 0/2/21 | 6 |
| cause-chain-reversal | haiku | skim | 95.57 | 0.101 | 0.117 | 0.1 | 0.1129 | 0.3125 | 10/2/13 | 0 |
| cause-chain-reversal | haiku | standard | 80.33 | 0.5707 | 0.6064 | 0.5 | 0.5806 | 0.625 | 2/3/13 | 2 |
| cause-chain-reversal | haiku | deep | 63.16 | 0.8333 | 0.8617 | 0.9667 | 0.8871 | 0.9375 | 0/1/13 | 8 |
| cause-chain-reversal | sonnet | skim | 75.07 | 0.6414 | 0.6915 | 0.6667 | 0.6855 | 0.8125 | 0/5/13 | 0 |
| cause-chain-reversal | sonnet | standard | 1.39 | 0.9747 | 0.9787 | 1.0 | 0.9839 | 0.8125 | 0/0/13 | 0 |
| cause-chain-reversal | sonnet | deep | -13.85 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0/0/13 | 0 |
| migration-tristate | haiku | skim | 89.64 | 0.25 | 0.314 | 0.2308 | 0.2946 | 0.3125 | 4/5/12 | 2 |
| migration-tristate | haiku | standard | 54.64 | 0.7442 | 0.686 | 0.7308 | 0.6964 | 0.6875 | 1/5/12 | 5 |
| migration-tristate | haiku | deep | 10.0 | 0.9884 | 0.9767 | 1.0 | 0.9821 | 1.0 | 0/0/12 | 20 |
| migration-tristate | sonnet | skim | 90.36 | 0.314 | 0.3837 | 0.3462 | 0.375 | 0.3125 | 2/6/12 | 0 |
| migration-tristate | sonnet | standard | 48.57 | 0.9477 | 0.9302 | 0.8846 | 0.9196 | 1.0 | 0/2/12 | 0 |
| migration-tristate | sonnet | deep | 32.5 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0/0/12 | 0 |
| near-identical-numbers | sonnet | skim | 81.88 | 0.3115 | 0.3824 | 0.2812 | 0.35 | 0.5 | 5/3/12 | 0 |
| near-identical-numbers | sonnet | standard | 42.03 | 0.9508 | 0.8676 | 0.9062 | 0.88 | 1.0 | 0/4/12 | 7 |
| near-identical-numbers | sonnet | deep | 7.61 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0/0/12 | 6 |
| negation-and-true-peers | sonnet | skim | 83.09 | 0.0316 | 0.0294 | 0.125 | 0.0476 | 0.0625 | 15/2/17 | 1 |
| negation-and-true-peers | sonnet | standard | 17.28 | 0.9895 | 0.9804 | 1.0 | 0.9841 | 1.0 | 0/0/17 | 1 |
| negation-and-true-peers | sonnet | deep | 11.4 | 0.9895 | 0.9804 | 1.0 | 0.9841 | 1.0 | 0/0/17 | 1 |
| real-benchmark-archaeology | sonnet | skim | 84.12 | 0.4658 | 0.4717 | 0.5333 | 0.4853 | 0.5625 | 2/7/13 | 0 |
| real-benchmark-archaeology | sonnet | standard | 59.23 | 0.8846 | 0.8491 | 0.9667 | 0.875 | 0.8125 | 1/1/13 | 3 |
| real-benchmark-archaeology | sonnet | deep | 26.18 | 0.9658 | 0.9528 | 1.0 | 0.9632 | 0.875 | 0/1/13 | 2 |
| real-hook-discovery | sonnet | skim | 78.79 | 0.3923 | 0.4571 | 0.5833 | 0.4894 | 0.6875 | 3/2/8 | 0 |
| real-hook-discovery | sonnet | standard | 45.89 | 0.9538 | 0.9571 | 0.875 | 0.9362 | 1.0 | 0/2/8 | 0 |
| real-hook-discovery | sonnet | deep | 27.71 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0/0/8 | 0 |
| synthetic-scale-verylarge | haiku | skim | 95.35 | 0.1579 | 0.1667 | 0.2143 | 0.1782 | 0.1875 | 7/2/9 | 3 |
| synthetic-scale-verylarge | haiku | standard | 81.72 | 0.5553 | 0.5909 | 0.6429 | 0.6034 | 1.0 | 1/4/9 | 14 |
| synthetic-scale-verylarge | haiku | deep | 44.17 | 0.9079 | 0.9318 | 0.9048 | 0.9253 | 1.0 | 0/2/9 | 43 |
| synthetic-scale-verylarge | sonnet | skim | 94.52 | 0.2526 | 0.2727 | 0.2619 | 0.2701 | 0.3125 | 3/6/9 | 0 |
| synthetic-scale-verylarge | sonnet | standard | 64.81 | 0.7316 | 0.75 | 0.8095 | 0.7644 | 1.0 | 0/3/9 | 0 |
| synthetic-scale-verylarge | sonnet | deep | 25.97 | 0.9947 | 0.9924 | 0.9762 | 0.9885 | 1.0 | 0/0/9 | 2 |
