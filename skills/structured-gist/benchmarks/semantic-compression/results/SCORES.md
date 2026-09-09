# Semantic-compression eval suite: canonical scores (generated, do not hand-edit)

Regenerate with `python3 scoring/deterministic.py && python3 scoring/combine.py`.

## regression

**Case intent** (what each case's fact weights are importance-*for* -- see README.md "Intended reader/task"; cases without one predate this schema field):

- `near-identical-numbers` -- reader: an engineer who needs to act on the exact values in this recap (cite a version, path, or SHA) without re-reading the source; task: precise recall of exact identifiers under compression -- near-miss numbers/paths/SHAs must not become interchangeable.
- `real-benchmark-archaeology` -- reader: a teammate resuming an in-progress investigation; task: know what's already established, what's still unresolved, and which named identifiers to search for next.
- `real-hook-discovery` -- reader: an engineer resuming this debugging thread later, or a teammate picking it up cold; task: confirm what broke, why, and whether the fix is complete enough to trust without re-reading the full investigation.

| case | tier | level | src_w | out_w | reduction% | conform_viol | semSufficiency | relRetention | omission% | unsupported_claims | recoverability |
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

**Case intent** (what each case's fact weights are importance-*for* -- see README.md "Intended reader/task"; cases without one predate this schema field):

- `causality-heavy-explain` -- reader: an engineer who needs to reason about the causal mechanism, e.g. to judge whether the same feedback loop could recur elsewhere; task: understand why the cascade happened in causal order, not just which facts are true. _this case exists to pressure-test relation retention specifically -- a flattened list that keeps every fact but drops the causal chain fails this task even at high fact retention_
- `cause-chain-reversal` -- reader: someone reading this after the fact (postmortem, handoff) who needs to act on the real cause; task: know which diagnosis turned out to be correct, not just the order theories were proposed in. _an outline that faithfully reports the initial theory but drops the reversal is actively misleading for this task, even though the initial-theory facts are individually true_
- `migration-tristate` -- reader: a lead tracking migration status across systems; task: know the exact current status of each system without confusing similar-sounding states (done vs. scheduled vs. will-not vs. reverted vs. in-progress).
- `negation-and-true-peers` -- reader: a stakeholder getting a status update spanning several unrelated workstreams; task: know what did and did NOT happen in each workstream independently, without inferring a shared cause or hierarchy that isn't there. _negations here are load-bearing -- dropping a negation changes what the fact means, not just how much detail survives_
- `synthetic-scale-verylarge` -- reader: someone triaging a large weekly ops digest under time pressure; task: find the one item that actually needs attention among many that don't, without reading the full source. _most 'outcome' facts here are deliberately low-weight because they are resolved noise (f2-f4, f14-f15); f10-f12 (the true root cause and its unresolved status) are weighted high because missing them defeats the reader's actual task even though they share a category with the noise facts_

| case | tier | level | src_w | out_w | reduction% | conform_viol | semSufficiency | relRetention | omission% | unsupported_claims | recoverability |
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
