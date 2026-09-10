# Findability (Evidence Access Cost): canonical scores (generated, do not hand-edit)

Measurement only -- see `../FINDABILITY_FINDINGS.md` for what this found and why the baseline is case-level. Regenerate with `python3 scoring/findability.py`.

| case | tier | level | qtype | support units | eligible (strict) | baseline EAC | gist EAC | delta EAC | baseline span | gist span | delta span |
|---|---|---|---|---|---|---|---|---|---|---|---|
| causality-heavy-explain | sonnet | skim | relational | 1 | no (r7:status=lost,r7:unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | skim | relational | 2 | no (r1:status=lost,r1:unaligned_in_rendering,r2:status=lost,r2:unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | skim | relational | 1 | no (r4:status=lost,r4:unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | skim | factual | 2 | no (f11:status=partial,f12:status=partial) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | skim | relational | 1 | no (r8:status=lost,r8:unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | skim | factual | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0528 | 0.0833 | 0.0305 |
| causality-heavy-explain | sonnet | skim | factual | 2 | yes | 0.8169 | 0.7222 | -0.0947 | 0.0775 | 0.1667 | 0.0892 |
| causality-heavy-explain | sonnet | skim | relational | 2 | yes | 0.8169 | 0.7222 | -0.0947 | 0.0775 | 0.1667 | 0.0892 |
| causality-heavy-explain | sonnet | standard | relational | 1 | yes | 0.7394 | 0.5294 | -0.21 | 0.0634 | 0.0441 | -0.0193 |
| causality-heavy-explain | sonnet | standard | relational | 2 | no (r2:status=lost,r2:unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | standard | relational | 1 | no (r4:status=lost,r4:unaligned_in_rendering) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | standard | factual | 2 | no (f12:status=partial) | - | - | - | - | - | - |
| causality-heavy-explain | sonnet | standard | relational | 1 | yes | 1.0 | 0.9044 | -0.0956 | 0.0528 | 0.0368 | -0.016 |
| causality-heavy-explain | sonnet | standard | factual | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0528 | 0.0221 | -0.0307 |
| causality-heavy-explain | sonnet | standard | factual | 2 | yes | 0.8169 | 0.6471 | -0.1698 | 0.0775 | 0.0441 | -0.0334 |
| causality-heavy-explain | sonnet | standard | relational | 2 | yes | 0.8169 | 0.6471 | -0.1698 | 0.0775 | 0.0441 | -0.0334 |
| causality-heavy-explain | sonnet | deep | relational | 1 | yes | 0.7394 | 0.6529 | -0.0865 | 0.0634 | 0.0206 | -0.0428 |
| causality-heavy-explain | sonnet | deep | relational | 2 | yes | 0.257 | 0.2199 | -0.0371 | 0.1021 | 0.0893 | -0.0128 |
| causality-heavy-explain | sonnet | deep | relational | 1 | yes | 0.412 | 0.3952 | -0.0168 | 0.0423 | 0.0275 | -0.0148 |
| causality-heavy-explain | sonnet | deep | factual | 2 | yes | 0.6197 | 0.5223 | -0.0974 | 0.162 | 0.0928 | -0.0692 |
| causality-heavy-explain | sonnet | deep | relational | 1 | yes | 1.0 | 0.9347 | -0.0653 | 0.0528 | 0.0172 | -0.0356 |
| causality-heavy-explain | sonnet | deep | factual | 1 | yes | 1.0 | 0.9931 | -0.0069 | 0.0528 | 0.0172 | -0.0356 |
| causality-heavy-explain | sonnet | deep | factual | 2 | yes | 0.8169 | 0.7869 | -0.03 | 0.0775 | 0.0825 | 0.005 |
| causality-heavy-explain | sonnet | deep | relational | 2 | yes | 0.8169 | 0.7869 | -0.03 | 0.0775 | 0.0825 | 0.005 |
| cause-chain-reversal | haiku | skim | factual | 1 | yes | 0.1209 | 0.6154 | 0.4945 | 0.049 | 0.3846 | 0.3356 |
| cause-chain-reversal | haiku | skim | factual | 2 | no (f11:status=omitted,f11:unaligned_in_rendering,f12:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | relational | 1 | no (r3:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | relational | 2 | no (f15:status=omitted,f15:unaligned_in_rendering,f16:status=omitted,f16:unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | factual | 2 | no (f17:status=omitted,f17:unaligned_in_rendering,f18:status=omitted,f18:unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | relational | 1 | no (r6:status=lost,r6:unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | factual | 1 | no (f19:status=omitted,f19:unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | skim | factual | 1 | no (f10:status=omitted,f10:unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | factual | 1 | yes | 0.1209 | 0.2105 | 0.0896 | 0.049 | 0.0526 | 0.0036 |
| cause-chain-reversal | haiku | standard | factual | 2 | yes | 0.6536 | 1.0 | 0.3464 | 0.0686 | 0.4561 | 0.3875 |
| cause-chain-reversal | haiku | standard | relational | 1 | no (r3:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | relational | 2 | no (f16:status=omitted,f16:unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | factual | 2 | no (f18:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | relational | 1 | no (r6:status=partial,r6:unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | factual | 1 | no (f19:status=omitted,f19:unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | standard | factual | 1 | no (f10:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | deep | factual | 1 | yes | 0.1209 | 0.1351 | 0.0142 | 0.049 | 0.027 | -0.022 |
| cause-chain-reversal | haiku | deep | factual | 2 | yes | 0.6536 | 0.6306 | -0.023 | 0.0686 | 0.0991 | 0.0305 |
| cause-chain-reversal | haiku | deep | relational | 1 | yes | 0.7255 | 0.6306 | -0.0949 | 0.1111 | 0.0991 | -0.012 |
| cause-chain-reversal | haiku | deep | relational | 2 | no (f16:status=omitted,f16:unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | deep | factual | 2 | yes | 0.8922 | 0.7658 | -0.1264 | 0.085 | 0.1171 | 0.0321 |
| cause-chain-reversal | haiku | deep | relational | 1 | no (r6:status=partial,r6:unaligned_in_rendering) | - | - | - | - | - | - |
| cause-chain-reversal | haiku | deep | factual | 1 | yes | 0.9444 | 0.8198 | -0.1246 | 0.0523 | 0.0541 | 0.0018 |
| cause-chain-reversal | haiku | deep | factual | 1 | yes | 0.585 | 0.6306 | 0.0456 | 0.0523 | 0.045 | -0.0073 |
| cause-chain-reversal | sonnet | skim | factual | 1 | yes | 0.1209 | 0.2059 | 0.085 | 0.049 | 0.0588 | 0.0098 |
| cause-chain-reversal | sonnet | skim | factual | 2 | yes | 0.6536 | 0.6176 | -0.036 | 0.0686 | 0.1029 | 0.0343 |
| cause-chain-reversal | sonnet | skim | relational | 1 | no (r3:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | skim | relational | 2 | no (f16:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | skim | factual | 2 | no (f18:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | skim | relational | 1 | no (r6:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | skim | factual | 1 | no (f19:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | skim | factual | 1 | no (f10:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | standard | factual | 1 | yes | 0.1209 | 0.1397 | 0.0188 | 0.049 | 0.0254 | -0.0236 |
| cause-chain-reversal | sonnet | standard | factual | 2 | yes | 0.6536 | 0.6254 | -0.0282 | 0.0686 | 0.0698 | 0.0012 |
| cause-chain-reversal | sonnet | standard | relational | 1 | yes | 0.7255 | 0.6571 | -0.0684 | 0.1111 | 0.0317 | -0.0794 |
| cause-chain-reversal | sonnet | standard | relational | 2 | yes | 0.8072 | 0.7937 | -0.0135 | 0.0817 | 0.1048 | 0.0231 |
| cause-chain-reversal | sonnet | standard | factual | 2 | yes | 0.8922 | 0.8635 | -0.0287 | 0.085 | 0.0603 | -0.0247 |
| cause-chain-reversal | sonnet | standard | relational | 1 | yes | 0.2908 | 0.2063 | -0.0845 | 0.0588 | 0.0349 | -0.0239 |
| cause-chain-reversal | sonnet | standard | factual | 1 | yes | 0.9444 | 0.927 | -0.0174 | 0.0523 | 0.0317 | -0.0206 |
| cause-chain-reversal | sonnet | standard | factual | 1 | no (f10:status=partial) | - | - | - | - | - | - |
| cause-chain-reversal | sonnet | deep | factual | 1 | yes | 0.1209 | 0.1199 | -0.001 | 0.049 | 0.0218 | -0.0272 |
| cause-chain-reversal | sonnet | deep | factual | 2 | yes | 0.6536 | 0.6785 | 0.0249 | 0.0686 | 0.1717 | 0.1031 |
| cause-chain-reversal | sonnet | deep | relational | 1 | yes | 0.7255 | 0.7057 | -0.0198 | 0.1111 | 0.0272 | -0.0839 |
| cause-chain-reversal | sonnet | deep | relational | 2 | yes | 0.8072 | 0.8229 | 0.0157 | 0.0817 | 0.0899 | 0.0082 |
| cause-chain-reversal | sonnet | deep | factual | 2 | yes | 0.8922 | 0.8828 | -0.0094 | 0.085 | 0.0518 | -0.0332 |
| cause-chain-reversal | sonnet | deep | relational | 1 | yes | 0.2908 | 0.1771 | -0.1137 | 0.0588 | 0.03 | -0.0288 |
| cause-chain-reversal | sonnet | deep | factual | 1 | yes | 0.9444 | 0.9373 | -0.0071 | 0.0523 | 0.0272 | -0.0251 |
| cause-chain-reversal | sonnet | deep | factual | 1 | yes | 0.585 | 0.5068 | -0.0782 | 0.0523 | 0.0218 | -0.0305 |
| migration-tristate | haiku | skim | factual | 1 | yes | 0.3174 | 0.6522 | 0.3348 | 0.0652 | 0.2174 | 0.1522 |
| migration-tristate | haiku | skim | factual | 2 | no (f8:status=omitted,f8:unaligned_in_rendering,f9:status=omitted,f9:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | skim | factual | 1 | no (f10:status=omitted,f10:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | skim | factual | 1 | yes | 0.5261 | 0.8696 | 0.3435 | 0.0261 | 0.2174 | 0.1913 |
| migration-tristate | haiku | skim | factual | 1 | no (f13:status=omitted,f13:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | skim | relational | 1 | no (r6:status=lost,r6:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | skim | factual | 1 | no (f4:status=partial) | - | - | - | - | - | - |
| migration-tristate | haiku | skim | factual | 1 | no (f15:status=omitted,f15:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | standard | factual | 1 | yes | 0.3174 | 0.4314 | 0.114 | 0.0652 | 0.049 | -0.0162 |
| migration-tristate | haiku | standard | factual | 2 | yes | 0.4565 | 0.5784 | 0.1219 | 0.1391 | 0.1373 | -0.0018 |
| migration-tristate | haiku | standard | factual | 1 | no (f10:status=omitted,f10:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | standard | factual | 1 | yes | 0.5261 | 0.6275 | 0.1014 | 0.0261 | 0.049 | 0.0229 |
| migration-tristate | haiku | standard | factual | 1 | yes | 0.6478 | 0.8333 | 0.1855 | 0.0696 | 0.0882 | 0.0186 |
| migration-tristate | haiku | standard | relational | 1 | no (r6:status=partial,r6:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | standard | factual | 1 | yes | 0.1565 | 0.2549 | 0.0984 | 0.0261 | 0.0588 | 0.0327 |
| migration-tristate | haiku | standard | factual | 1 | no (f15:status=omitted,f15:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | haiku | deep | factual | 1 | yes | 0.3174 | 0.3333 | 0.0159 | 0.0652 | 0.029 | -0.0362 |
| migration-tristate | haiku | deep | factual | 2 | yes | 0.4565 | 0.4734 | 0.0169 | 0.1391 | 0.1304 | -0.0087 |
| migration-tristate | haiku | deep | factual | 1 | yes | 0.5 | 0.5169 | 0.0169 | 0.0435 | 0.0338 | -0.0097 |
| migration-tristate | haiku | deep | factual | 1 | yes | 0.5261 | 0.5749 | 0.0488 | 0.0261 | 0.0483 | 0.0222 |
| migration-tristate | haiku | deep | factual | 1 | yes | 0.6478 | 0.7005 | 0.0527 | 0.0696 | 0.0531 | -0.0165 |
| migration-tristate | haiku | deep | relational | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0739 | 0.0483 | -0.0256 |
| migration-tristate | haiku | deep | factual | 1 | yes | 0.1565 | 0.1932 | 0.0367 | 0.0261 | 0.029 | 0.0029 |
| migration-tristate | haiku | deep | factual | 1 | yes | 0.7348 | 0.7826 | 0.0478 | 0.0435 | 0.0338 | -0.0097 |
| migration-tristate | sonnet | skim | factual | 1 | yes | 0.3174 | 0.5882 | 0.2708 | 0.0652 | 0.1765 | 0.1113 |
| migration-tristate | sonnet | skim | factual | 2 | no (f8:status=omitted,f8:unaligned_in_rendering,f9:status=omitted,f9:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | factual | 1 | no (f10:status=partial) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | factual | 1 | no (f11:status=partial) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | factual | 1 | no (f13:status=omitted,f13:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | relational | 1 | no (r6:status=lost,r6:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | factual | 1 | no (f4:status=partial) | - | - | - | - | - | - |
| migration-tristate | sonnet | skim | factual | 1 | no (f15:status=omitted,f15:unaligned_in_rendering) | - | - | - | - | - | - |
| migration-tristate | sonnet | standard | factual | 1 | yes | 0.3174 | 0.3248 | 0.0074 | 0.0652 | 0.0598 | -0.0054 |
| migration-tristate | sonnet | standard | factual | 2 | yes | 0.4565 | 0.453 | -0.0035 | 0.1391 | 0.1197 | -0.0194 |
| migration-tristate | sonnet | standard | factual | 1 | yes | 0.5 | 0.5214 | 0.0214 | 0.0435 | 0.0598 | 0.0163 |
| migration-tristate | sonnet | standard | factual | 1 | yes | 0.5261 | 0.6068 | 0.0807 | 0.0261 | 0.0684 | 0.0423 |
| migration-tristate | sonnet | standard | factual | 1 | yes | 0.6478 | 0.6923 | 0.0445 | 0.0696 | 0.0427 | -0.0269 |
| migration-tristate | sonnet | standard | relational | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0739 | 0.0769 | 0.003 |
| migration-tristate | sonnet | standard | factual | 1 | yes | 0.1565 | 0.2479 | 0.0914 | 0.0261 | 0.0769 | 0.0508 |
| migration-tristate | sonnet | standard | factual | 1 | yes | 0.7348 | 0.7778 | 0.043 | 0.0435 | 0.0427 | -0.0008 |
| migration-tristate | sonnet | deep | factual | 1 | yes | 0.3174 | 0.302 | -0.0154 | 0.0652 | 0.0403 | -0.0249 |
| migration-tristate | sonnet | deep | factual | 2 | yes | 0.4565 | 0.4295 | -0.027 | 0.1391 | 0.1208 | -0.0183 |
| migration-tristate | sonnet | deep | factual | 1 | yes | 0.5 | 0.4832 | -0.0168 | 0.0435 | 0.047 | 0.0035 |
| migration-tristate | sonnet | deep | factual | 1 | yes | 0.5261 | 0.5638 | 0.0377 | 0.0261 | 0.0671 | 0.041 |
| migration-tristate | sonnet | deep | factual | 1 | yes | 0.6478 | 0.6913 | 0.0435 | 0.0696 | 0.0604 | -0.0092 |
| migration-tristate | sonnet | deep | relational | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0739 | 0.0537 | -0.0202 |
| migration-tristate | sonnet | deep | factual | 1 | yes | 0.1565 | 0.2081 | 0.0516 | 0.0261 | 0.0201 | -0.006 |
| migration-tristate | sonnet | deep | factual | 1 | yes | 0.7348 | 0.7584 | 0.0236 | 0.0435 | 0.0336 | -0.0099 |
| near-identical-numbers | sonnet | skim | factual | 1 | yes | 0.0706 | 0.2619 | 0.1913 | 0.0706 | 0.2143 | 0.1437 |
| near-identical-numbers | sonnet | skim | factual | 1 | yes | 0.2824 | 0.4762 | 0.1938 | 0.0529 | 0.2143 | 0.1614 |
| near-identical-numbers | sonnet | skim | relational | 1 | yes | 0.9294 | 0.9524 | 0.023 | 0.1294 | 0.0476 | -0.0818 |
| near-identical-numbers | sonnet | skim | factual | 2 | no (f2:status=omitted,f2:unaligned_in_rendering,f6:status=omitted,f6:unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | skim | factual | 2 | no (f10:status=partial,f10:unaligned_in_rendering,f11:status=omitted,f11:unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | skim | factual | 2 | no (f13:status=partial,f13:unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | skim | factual | 1 | no (f14:status=omitted,f14:unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | skim | relational | 2 | no (r2:status=lost,r2:unaligned_in_rendering,r3:status=lost,r3:unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | standard | factual | 1 | yes | 0.0706 | 0.1786 | 0.108 | 0.0706 | 0.0571 | -0.0135 |
| near-identical-numbers | sonnet | standard | factual | 1 | yes | 0.2824 | 0.3286 | 0.0462 | 0.0529 | 0.0571 | 0.0042 |
| near-identical-numbers | sonnet | standard | relational | 1 | yes | 0.9294 | 0.9143 | -0.0151 | 0.1294 | 0.1643 | 0.0349 |
| near-identical-numbers | sonnet | standard | factual | 2 | no (f2:status=partial,f2:unaligned_in_rendering,f6:status=partial,f6:unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | standard | factual | 2 | yes | 0.6529 | 0.5357 | -0.1172 | 0.1353 | 0.0857 | -0.0496 |
| near-identical-numbers | sonnet | standard | factual | 2 | yes | 0.7412 | 0.6286 | -0.1126 | 0.0882 | 0.0786 | -0.0096 |
| near-identical-numbers | sonnet | standard | factual | 1 | yes | 0.8 | 0.6571 | -0.1429 | 0.0529 | 0.0286 | -0.0243 |
| near-identical-numbers | sonnet | standard | relational | 2 | yes | 0.4588 | 0.4214 | -0.0374 | 0.2706 | 0.2429 | -0.0277 |
| near-identical-numbers | sonnet | deep | factual | 1 | yes | 0.0706 | 0.1454 | 0.0748 | 0.0706 | 0.0264 | -0.0442 |
| near-identical-numbers | sonnet | deep | factual | 1 | yes | 0.2824 | 0.2863 | 0.0039 | 0.0529 | 0.0264 | -0.0265 |
| near-identical-numbers | sonnet | deep | relational | 1 | yes | 0.9294 | 0.9251 | -0.0043 | 0.1294 | 0.1366 | 0.0072 |
| near-identical-numbers | sonnet | deep | factual | 2 | yes | 0.3176 | 0.304 | -0.0136 | 0.2471 | 0.1586 | -0.0885 |
| near-identical-numbers | sonnet | deep | factual | 2 | yes | 0.6529 | 0.5727 | -0.0802 | 0.1353 | 0.141 | 0.0057 |
| near-identical-numbers | sonnet | deep | factual | 2 | no (f13:unaligned_in_rendering) | - | - | - | - | - | - |
| near-identical-numbers | sonnet | deep | factual | 1 | yes | 0.8 | 0.7048 | -0.0952 | 0.0529 | 0.0396 | -0.0133 |
| near-identical-numbers | sonnet | deep | relational | 2 | yes | 0.4588 | 0.4229 | -0.0359 | 0.2706 | 0.2599 | -0.0107 |
| negation-and-true-peers | sonnet | skim | factual | 1 | no (f5:status=omitted,f5:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | factual | 1 | no (f6:status=omitted,f6:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | factual | 2 | no (f14:status=omitted,f14:unaligned_in_rendering,f15:status=omitted,f15:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | relational | 1 | no (r1:status=lost,r1:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | factual | 2 | no (f17:status=omitted,f17:unaligned_in_rendering,f18:status=omitted,f18:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | relational | 1 | no (r3:status=lost,r3:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | relational | 1 | no (r2:status=lost,r2:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | skim | relational | 1 | no (r4:status=partial) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | standard | factual | 1 | yes | 0.2336 | 0.2526 | 0.019 | 0.0287 | 0.0309 | 0.0022 |
| negation-and-true-peers | sonnet | standard | factual | 1 | yes | 0.3115 | 0.299 | -0.0125 | 0.0779 | 0.0464 | -0.0315 |
| negation-and-true-peers | sonnet | standard | factual | 2 | yes | 0.7336 | 0.6959 | -0.0377 | 0.0656 | 0.0515 | -0.0141 |
| negation-and-true-peers | sonnet | standard | relational | 1 | no (r1:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | standard | factual | 2 | yes | 0.8975 | 0.8918 | -0.0057 | 0.0779 | 0.0619 | -0.016 |
| negation-and-true-peers | sonnet | standard | relational | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0656 | 0.0928 | 0.0272 |
| negation-and-true-peers | sonnet | standard | relational | 1 | yes | 0.5328 | 0.5876 | 0.0548 | 0.0492 | 0.0567 | 0.0075 |
| negation-and-true-peers | sonnet | standard | relational | 1 | yes | 0.0943 | 0.1598 | 0.0655 | 0.0656 | 0.1289 | 0.0633 |
| negation-and-true-peers | sonnet | deep | factual | 1 | no (f5:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | deep | factual | 1 | yes | 0.3115 | 0.299 | -0.0125 | 0.0779 | 0.0464 | -0.0315 |
| negation-and-true-peers | sonnet | deep | factual | 2 | yes | 0.7336 | 0.7113 | -0.0223 | 0.0656 | 0.0361 | -0.0295 |
| negation-and-true-peers | sonnet | deep | relational | 1 | yes | 0.7172 | 0.7835 | 0.0663 | 0.0492 | 0.1443 | 0.0951 |
| negation-and-true-peers | sonnet | deep | factual | 2 | yes | 0.8975 | 0.9072 | 0.0097 | 0.0779 | 0.0515 | -0.0264 |
| negation-and-true-peers | sonnet | deep | relational | 1 | no (r3:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | deep | relational | 1 | no (r2:unaligned_in_rendering) | - | - | - | - | - | - |
| negation-and-true-peers | sonnet | deep | relational | 1 | no (r4:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 3 | no (f3:status=partial) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 2 | no (f6:status=omitted,f6:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | relational | 2 | no (r2:status=partial,f13:status=partial) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | relational | 1 | no (r3:status=lost,r3:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 3 | no (f16:status=partial,f17:status=omitted,f17:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 3 | no (f18:status=partial,f19:status=partial,f20:status=omitted,f20:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 1 | no (f23:status=partial) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | skim | factual | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0831 | 0.1071 | 0.024 |
| real-benchmark-archaeology | sonnet | standard | factual | 3 | no (f1:status=partial,f1:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | standard | factual | 2 | no (f5:status=partial,f5:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | standard | relational | 2 | no (r2:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | standard | relational | 1 | yes | 0.4737 | 0.5 | 0.0263 | 0.0305 | 0.0506 | 0.0201 |
| real-benchmark-archaeology | sonnet | standard | factual | 3 | yes | 0.5623 | 0.5696 | 0.0073 | 0.0886 | 0.0633 | -0.0253 |
| real-benchmark-archaeology | sonnet | standard | factual | 3 | no (f20:status=omitted,f20:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | standard | factual | 1 | yes | 0.9169 | 0.8671 | -0.0498 | 0.0914 | 0.0506 | -0.0408 |
| real-benchmark-archaeology | sonnet | standard | factual | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0831 | 0.1203 | 0.0372 |
| real-benchmark-archaeology | sonnet | deep | factual | 3 | no (f1:status=partial,f1:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | deep | factual | 2 | no (f5:status=partial,f5:unaligned_in_rendering) | - | - | - | - | - | - |
| real-benchmark-archaeology | sonnet | deep | relational | 2 | yes | 0.4432 | 0.4485 | 0.0053 | 0.0305 | 0.0764 | 0.0459 |
| real-benchmark-archaeology | sonnet | deep | relational | 1 | yes | 0.4737 | 0.4784 | 0.0047 | 0.0305 | 0.0299 | -0.0006 |
| real-benchmark-archaeology | sonnet | deep | factual | 3 | yes | 0.5623 | 0.5515 | -0.0108 | 0.0886 | 0.0698 | -0.0188 |
| real-benchmark-archaeology | sonnet | deep | factual | 3 | yes | 0.7507 | 0.7409 | -0.0098 | 0.1884 | 0.1728 | -0.0156 |
| real-benchmark-archaeology | sonnet | deep | factual | 1 | yes | 0.9169 | 0.9003 | -0.0166 | 0.0914 | 0.0532 | -0.0382 |
| real-benchmark-archaeology | sonnet | deep | factual | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0831 | 0.0664 | -0.0167 |
| real-hook-discovery | sonnet | skim | factual | 3 | no (f1:status=partial,f2:status=partial) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | skim | relational | 1 | no (r1:status=lost,r1:unaligned_in_rendering) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | skim | relational | 2 | no (r2:status=lost,r2:unaligned_in_rendering) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | skim | factual | 2 | no (f8:status=omitted,f8:unaligned_in_rendering,f9:status=omitted,f9:unaligned_in_rendering) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | skim | factual | 1 | no (f11:status=omitted,f11:unaligned_in_rendering) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | skim | relational | 1 | yes | 0.6223 | 0.6154 | -0.0069 | 0.0904 | 0.1026 | 0.0122 |
| real-hook-discovery | sonnet | skim | factual | 1 | yes | 0.9043 | 0.9231 | 0.0188 | 0.0372 | 0.1538 | 0.1166 |
| real-hook-discovery | sonnet | skim | factual | 1 | no (f15:status=partial) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | standard | factual | 3 | yes | 0.1596 | 0.2407 | 0.0811 | 0.1596 | 0.1667 | 0.0071 |
| real-hook-discovery | sonnet | standard | relational | 1 | no (r1:status=partial) | - | - | - | - | - | - |
| real-hook-discovery | sonnet | standard | relational | 2 | yes | 0.3564 | 0.4352 | 0.0788 | 0.1383 | 0.1944 | 0.0561 |
| real-hook-discovery | sonnet | standard | factual | 2 | yes | 0.5319 | 0.5463 | 0.0144 | 0.1011 | 0.0556 | -0.0455 |
| real-hook-discovery | sonnet | standard | factual | 1 | yes | 0.6755 | 0.6667 | -0.0088 | 0.0532 | 0.0648 | 0.0116 |
| real-hook-discovery | sonnet | standard | relational | 1 | yes | 0.6223 | 0.5926 | -0.0297 | 0.0904 | 0.0463 | -0.0441 |
| real-hook-discovery | sonnet | standard | factual | 1 | yes | 0.9043 | 0.8796 | -0.0247 | 0.0372 | 0.0556 | 0.0184 |
| real-hook-discovery | sonnet | standard | factual | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0957 | 0.1204 | 0.0247 |
| real-hook-discovery | sonnet | deep | factual | 3 | yes | 0.1596 | 0.2378 | 0.0782 | 0.1596 | 0.1119 | -0.0477 |
| real-hook-discovery | sonnet | deep | relational | 1 | yes | 0.2181 | 0.3007 | 0.0826 | 0.0585 | 0.0629 | 0.0044 |
| real-hook-discovery | sonnet | deep | relational | 2 | yes | 0.3564 | 0.4615 | 0.1051 | 0.1383 | 0.1608 | 0.0225 |
| real-hook-discovery | sonnet | deep | factual | 2 | yes | 0.5319 | 0.5804 | 0.0485 | 0.1011 | 0.0769 | -0.0242 |
| real-hook-discovery | sonnet | deep | factual | 1 | yes | 0.6755 | 0.7063 | 0.0308 | 0.0532 | 0.0559 | 0.0027 |
| real-hook-discovery | sonnet | deep | relational | 1 | yes | 0.6223 | 0.6434 | 0.0211 | 0.0904 | 0.0629 | -0.0275 |
| real-hook-discovery | sonnet | deep | factual | 1 | yes | 0.9043 | 0.8811 | -0.0232 | 0.0372 | 0.042 | 0.0048 |
| real-hook-discovery | sonnet | deep | factual | 1 | yes | 1.0 | 1.0 | 0.0 | 0.0957 | 0.1189 | 0.0232 |
| synthetic-scale-verylarge | haiku | skim | relational | 1 | no (r3:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | factual | 1 | no (f5:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | relational | 2 | no (f7:status=omitted,f7:unaligned_in_rendering,f8:status=omitted,f8:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | factual | 2 | no (f11:status=omitted,f11:unaligned_in_rendering,f12:status=omitted,f12:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | relational | 1 | no (r6:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | factual | 2 | yes | 0.6286 | 0.6327 | 0.0041 | 0.0323 | 0.102 | 0.0697 |
| synthetic-scale-verylarge | haiku | skim | relational | 1 | no (r11:status=lost,r11:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | skim | factual | 1 | no (f43:status=omitted,f43:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | standard | relational | 1 | no (r3:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | standard | factual | 1 | no (f5:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | standard | relational | 2 | no (f7:status=partial,f8:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | standard | factual | 2 | yes | 0.2885 | 0.2923 | 0.0038 | 0.0463 | 0.041 | -0.0053 |
| synthetic-scale-verylarge | haiku | standard | relational | 1 | yes | 0.5554 | 0.4718 | -0.0836 | 0.0151 | 0.0462 | 0.0311 |
| synthetic-scale-verylarge | haiku | standard | factual | 2 | yes | 0.6286 | 0.5795 | -0.0491 | 0.0323 | 0.0154 | -0.0169 |
| synthetic-scale-verylarge | haiku | standard | relational | 1 | no (r11:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | standard | factual | 1 | yes | 0.9279 | 0.9128 | -0.0151 | 0.0301 | 0.0308 | 0.0007 |
| synthetic-scale-verylarge | haiku | deep | relational | 1 | yes | 0.3767 | 0.3603 | -0.0164 | 0.0355 | 0.0452 | 0.0097 |
| synthetic-scale-verylarge | haiku | deep | factual | 1 | yes | 0.1033 | 0.2149 | 0.1116 | 0.0312 | 0.0162 | -0.015 |
| synthetic-scale-verylarge | haiku | deep | relational | 2 | no (f7:status=partial,f8:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | haiku | deep | factual | 2 | yes | 0.2885 | 0.3118 | 0.0233 | 0.0463 | 0.0452 | -0.0011 |
| synthetic-scale-verylarge | haiku | deep | relational | 1 | yes | 0.5554 | 0.4556 | -0.0998 | 0.0151 | 0.0097 | -0.0054 |
| synthetic-scale-verylarge | haiku | deep | factual | 2 | yes | 0.6286 | 0.5493 | -0.0793 | 0.0323 | 0.0113 | -0.021 |
| synthetic-scale-verylarge | haiku | deep | relational | 1 | yes | 0.9709 | 0.9386 | -0.0323 | 0.0431 | 0.0517 | 0.0086 |
| synthetic-scale-verylarge | haiku | deep | factual | 1 | yes | 0.9279 | 0.9612 | 0.0333 | 0.0301 | 0.0194 | -0.0107 |
| synthetic-scale-verylarge | sonnet | skim | relational | 1 | no (r3:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | factual | 1 | no (f5:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | relational | 2 | no (f7:status=omitted,f7:unaligned_in_rendering,f8:status=omitted,f8:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | factual | 2 | no (f11:status=partial,f12:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | relational | 1 | yes | 0.5554 | 0.4912 | -0.0642 | 0.0151 | 0.0702 | 0.0551 |
| synthetic-scale-verylarge | sonnet | skim | factual | 2 | no (r8:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | relational | 1 | no (r11:status=lost,r11:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | skim | factual | 1 | no (f43:status=omitted,f43:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | standard | relational | 1 | yes | 0.3767 | 0.13 | -0.2467 | 0.0355 | 0.1253 | 0.0898 |
| synthetic-scale-verylarge | sonnet | standard | factual | 1 | yes | 0.1033 | 0.1206 | 0.0173 | 0.0312 | 0.0355 | 0.0043 |
| synthetic-scale-verylarge | sonnet | standard | relational | 2 | no (f7:status=partial,f8:status=partial) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | standard | factual | 2 | yes | 0.2885 | 0.234 | -0.0545 | 0.0463 | 0.052 | 0.0057 |
| synthetic-scale-verylarge | sonnet | standard | relational | 1 | no (r6:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | standard | factual | 2 | no (r8:unaligned_in_rendering) | - | - | - | - | - | - |
| synthetic-scale-verylarge | sonnet | standard | relational | 1 | yes | 0.9709 | 0.8629 | -0.108 | 0.0431 | 0.0638 | 0.0207 |
| synthetic-scale-verylarge | sonnet | standard | factual | 1 | yes | 0.9279 | 0.948 | 0.0201 | 0.0301 | 0.0449 | 0.0148 |
| synthetic-scale-verylarge | sonnet | deep | relational | 1 | yes | 0.3767 | 0.0352 | -0.3415 | 0.0355 | 0.0275 | -0.008 |
| synthetic-scale-verylarge | sonnet | deep | factual | 1 | yes | 0.1033 | 0.1978 | 0.0945 | 0.0312 | 0.0198 | -0.0114 |
| synthetic-scale-verylarge | sonnet | deep | relational | 2 | yes | 0.1808 | 0.244 | 0.0632 | 0.0635 | 0.0451 | -0.0184 |
| synthetic-scale-verylarge | sonnet | deep | factual | 2 | yes | 0.2885 | 0.3264 | 0.0379 | 0.0463 | 0.0209 | -0.0254 |
| synthetic-scale-verylarge | sonnet | deep | relational | 1 | yes | 0.5554 | 0.5418 | -0.0136 | 0.0151 | 0.0176 | 0.0025 |
| synthetic-scale-verylarge | sonnet | deep | factual | 2 | yes | 0.6286 | 0.5978 | -0.0308 | 0.0323 | 0.0165 | -0.0158 |
| synthetic-scale-verylarge | sonnet | deep | relational | 1 | yes | 0.9709 | 0.922 | -0.0489 | 0.0431 | 0.0385 | -0.0046 |
| synthetic-scale-verylarge | sonnet | deep | factual | 1 | yes | 0.9279 | 0.9681 | 0.0402 | 0.0301 | 0.0286 | -0.0015 |

## Delta EAC / delta evidence-span by question type (strict-eligible only)

| question type | n | avg delta EAC | avg delta evidence-span |
|---|---|---|---|
| factual | 108 | 0.0251 | 0.0096 |
| relational | 48 | -0.0369 | 0.0014 |

## Delta EAC / delta evidence-span by granularity level (strict-eligible only)

| level | n | avg delta EAC | avg delta evidence-span |
|---|---|---|---|
| skim | 17 | 0.0978 | 0.0908 |
| standard | 61 | -0.0022 | 0.0056 |
| deep | 78 | -0.0075 | -0.0101 |

## Delta EAC by support-unit count (single vs. multi-support, strict-eligible only)

| support | n | avg delta EAC | avg delta evidence-span |
|---|---|---|---|
| single | 105 | 0.015 | 0.0085 |
| multi | 51 | -0.0123 | 0.0042 |

**Strict eligibility:** 156/264 (case, tier, level, question) combinations were strict-findability-scorable (59.1%). See `results/findability.json` for the per-question `reasons` on every ineligible one.
