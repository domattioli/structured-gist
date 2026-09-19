# Wording fidelity: canonical scores (generated, do not hand-edit)

Measurement only -- see `../WORDING_FIDELITY_FINDINGS.md` for what this found. Regenerate with `python3 scoring/wording_fidelity.py`.

| case | tier | level | semantic nodes | verbatim-node rate | extractive coverage (>=1 / >=2 / >=3) | novel spans (>=3 tok) | longest novel span |
|---|---|---|---|---|---|---|---|
| causality-heavy-explain | sonnet | skim | 15 | 0.2667 | 0.7778 / 0.2778 / 0.0 | 2 | 15 |
| causality-heavy-explain | sonnet | standard | 30 | 0.2 | 0.8529 / 0.5368 / 0.3162 | 7 | 12 |
| causality-heavy-explain | sonnet | deep | 42 | 0.1667 | 0.866 / 0.6701 / 0.5395 | 15 | 8 |
| cause-chain-reversal | haiku | skim | 3 | 0.0 | 0.8462 / 0.3077 / 0.0 | 2 | 6 |
| cause-chain-reversal | haiku | standard | 14 | 0.2143 | 0.7895 / 0.4035 / 0.0526 | 5 | 11 |
| cause-chain-reversal | haiku | deep | 22 | 0.0455 | 0.7568 / 0.4414 / 0.1892 | 9 | 9 |
| cause-chain-reversal | sonnet | skim | 22 | 0.0455 | 0.7353 / 0.2353 / 0.0 | 6 | 26 |
| cause-chain-reversal | sonnet | standard | 41 | 0.0732 | 0.8921 / 0.7175 / 0.5651 | 15 | 9 |
| cause-chain-reversal | sonnet | deep | 44 | 0.0682 | 0.8856 / 0.7139 / 0.5395 | 17 | 9 |
| migration-tristate | haiku | skim | 6 | 0.0 | 0.8696 / 0.2609 / 0.0 | 3 | 9 |
| migration-tristate | haiku | standard | 25 | 0.12 | 0.8039 / 0.451 / 0.2941 | 8 | 13 |
| migration-tristate | haiku | deep | 45 | 0.1778 | 0.8213 / 0.6135 / 0.4396 | 11 | 9 |
| migration-tristate | sonnet | skim | 10 | 0.5 | 0.5882 / 0.1176 / 0.0 | 1 | 15 |
| migration-tristate | sonnet | standard | 27 | 0.1852 | 0.7949 / 0.5043 / 0.2991 | 8 | 11 |
| migration-tristate | sonnet | deep | 40 | 0.175 | 0.8322 / 0.5906 / 0.3624 | 10 | 11 |
| near-identical-numbers | sonnet | skim | 8 | 0.25 | 0.6905 / 0.5238 / 0.0 | 2 | 7 |
| near-identical-numbers | sonnet | standard | 20 | 0.3 | 0.8786 / 0.7571 / 0.4429 | 4 | 5 |
| near-identical-numbers | sonnet | deep | 28 | 0.2857 | 0.9031 / 0.7797 / 0.5859 | 8 | 7 |
| negation-and-true-peers | sonnet | skim | 18 | 0.5 | 0.6429 / 0.3571 / 0.0 | 4 | 5 |
| negation-and-true-peers | sonnet | standard | 31 | 0.3871 | 0.9175 / 0.8041 / 0.6598 | 3 | 6 |
| negation-and-true-peers | sonnet | deep | 47 | 0.4255 | 0.8866 / 0.7526 / 0.5567 | 5 | 5 |
| real-benchmark-archaeology | sonnet | skim | 18 | 0.0 | 0.8571 / 0.3214 / 0.0714 | 3 | 20 |
| real-benchmark-archaeology | sonnet | standard | 32 | 0.0938 | 0.8544 / 0.4241 / 0.1835 | 12 | 12 |
| real-benchmark-archaeology | sonnet | deep | 43 | 0.1163 | 0.8904 / 0.6711 / 0.4917 | 16 | 10 |
| real-hook-discovery | sonnet | skim | 10 | 0.2 | 0.7179 / 0.4359 / 0.2308 | 4 | 10 |
| real-hook-discovery | sonnet | standard | 17 | 0.1176 | 0.7685 / 0.5648 / 0.3981 | 5 | 9 |
| real-hook-discovery | sonnet | deep | 24 | 0.1667 | 0.8252 / 0.6923 / 0.5524 | 7 | 7 |
| registrar-hedge | haiku | skim | 7 | 0.2857 | 0.7714 / 0.4857 / 0.4286 | 4 | 5 |
| registrar-hedge | haiku | standard | 26 | 0.2692 | 0.8133 / 0.5361 / 0.3434 | 9 | 15 |
| registrar-hedge | haiku | deep | 53 | 0.0566 | 0.7627 / 0.4746 / 0.2847 | 18 | 23 |
| registrar-hedge | opus-v0.4.12 | skim | 45 | 0.4 | 0.8393 / 0.5714 / 0.4286 | 12 | 12 |
| registrar-hedge | opus-v0.4.12 | standard | 74 | 0.4054 | 0.8415 / 0.6599 / 0.5216 | 20 | 7 |
| registrar-hedge | opus-v0.4.12 | deep | 105 | 0.3238 | 0.7841 / 0.5418 / 0.4114 | 31 | 12 |
| registrar-hedge | opus-v0.5.0b1 | skim | 17 | 0.2941 | 0.8587 / 0.587 / 0.4783 | 5 | 11 |
| registrar-hedge | opus-v0.5.0b1 | standard | 50 | 0.34 | 0.8636 / 0.6182 / 0.5182 | 12 | 12 |
| registrar-hedge | opus-v0.5.0b1 | deep | 103 | 0.2816 | 0.8352 / 0.6147 / 0.5256 | 20 | 13 |
| registrar-hedge | sonnet | skim | 7 | 0.2857 | 0.7714 / 0.4857 / 0.4286 | 4 | 5 |
| registrar-hedge | sonnet | standard | 26 | 0.2692 | 0.8133 / 0.5361 / 0.3434 | 9 | 15 |
| registrar-hedge | sonnet | deep | 53 | 0.0566 | 0.7627 / 0.4746 / 0.2847 | 18 | 23 |
| synthetic-scale-verylarge | haiku | skim | 12 | 0.3333 | 0.8776 / 0.4286 / 0.2245 | 4 | 10 |
| synthetic-scale-verylarge | haiku | standard | 45 | 0.2 | 0.8923 / 0.4462 / 0.1795 | 17 | 11 |
| synthetic-scale-verylarge | haiku | deep | 114 | 0.1491 | 0.9612 / 0.6979 / 0.4168 | 23 | 14 |
| synthetic-scale-verylarge | sonnet | skim | 15 | 0.2 | 0.7895 / 0.2632 / 0.1228 | 5 | 16 |
| synthetic-scale-verylarge | sonnet | standard | 39 | 0.1282 | 0.9291 / 0.6478 / 0.4444 | 20 | 31 |
| synthetic-scale-verylarge | sonnet | deep | 62 | 0.2097 | 0.9791 / 0.8396 / 0.756 | 21 | 11 |

## Verbatim-node rate by role (concept/attribute/enumerator/explanation), aggregated across all cases

| role | nodes | verbatim | verbatim-node rate |
|---|---|---|---|
| attribute | 355 | 70 | 0.1972 |
| concept | 171 | 87 | 0.5088 |
| enumerator | 550 | 132 | 0.24 |
| explanation | 459 | 48 | 0.1046 |
