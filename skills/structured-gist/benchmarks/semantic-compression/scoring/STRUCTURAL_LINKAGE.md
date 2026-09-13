# Structural-linkage diagnostic (generated)

Regenerate with `python3 scoring/structural_linkage.py` from the semantic-compression directory.
Positive proximity advantage means gold-linked facts are closer than random fact pairs.

## Method decisions

- Tree distance: edge count via LCA; for paths `a` and `b`, `len(a) + len(b) - 2 * len(LCA(a, b))`.
- Multi-node facts: minimum path-combination distance; this asks whether any node carrying the fact makes the linkage structurally available.
- Permutation baseline: 1,000 deterministic draws per rendering, each sampling the real pair count without replacement from that rendering's locatable fact pairs. This gives stable diagnostic resolution while remaining fast.
- Effect size: `(null_mean_distance - real_mean_distance) / null_mean_distance`. Positive values are the fractional distance reduction versus random pairs; null percentiles are descriptive only.
- Order partial credit: mean pass rate across eligible consecutive ordinal-sibling pairs. Only consecutive pairs whose endpoints resolve to ordinal-enumerator siblings under one parent are eligible.
- Case rollup: median rendering proximity advantage; the median limits one tier's topology from dominating. Effective independent n is about eight cases, so no corpus-wide p-value is computed.

## Rendering results

| case | tier | real mean distance | null mean distance | proximity advantage | null percentile | order relations | mean order score |
|---|---|---:|---:|---:|---:|---:|---:|
| causality-heavy-explain | sonnet | 4.067 | 5.065 | 0.197 | 0.999 | 2 | 1 |
| cause-chain-reversal | haiku | 2.727 | 3.244 | 0.159 | 0.956 | 1 | 1 |
| cause-chain-reversal | sonnet | 4.471 | 5.651 | 0.209 | 1.000 | 1 | 1 |
| migration-tristate | haiku | 2.333 | 4.098 | 0.431 | 1.000 | 0 | — |
| migration-tristate | sonnet | 3.407 | 5.428 | 0.372 | 1.000 | 0 | — |
| near-identical-numbers | sonnet | 1.882 | 3.479 | 0.459 | 1.000 | 0 | — |
| negation-and-true-peers | sonnet | 1.429 | 3.562 | 0.599 | 1.000 | 0 | — |
| real-benchmark-archaeology | sonnet | 2.500 | 5.114 | 0.511 | 1.000 | 0 | — |
| real-hook-discovery | sonnet | 1.286 | 4.638 | 0.723 | 1.000 | 0 | — |
| synthetic-scale-verylarge | haiku | 2.308 | 5.405 | 0.573 | 1.000 | 0 | — |
| synthetic-scale-verylarge | sonnet | 2.117 | 4.743 | 0.554 | 1.000 | 0 | — |

## Case rollup

Case effect = median rendering proximity advantage. No corpus-wide p-value is computed.

| case | renderings | case effect |
|---|---:|---:|
| causality-heavy-explain | 1 | 0.197 |
| cause-chain-reversal | 2 | 0.184 |
| migration-tristate | 2 | 0.401 |
| near-identical-numbers | 1 | 0.459 |
| negation-and-true-peers | 1 | 0.599 |
| real-benchmark-archaeology | 1 | 0.511 |
| real-hook-discovery | 1 | 0.723 |
| synthetic-scale-verylarge | 2 | 0.563 |

## Across-case distribution

n=8; min=0.184; Q1=0.350; median=0.485; mean=0.455; Q3=0.572; max=0.723.

Limitations: shared endpoints remain dependent; grammar non-conformance can confound a null result; topic-oriented source sections can make proximity reflect topical grouping.
