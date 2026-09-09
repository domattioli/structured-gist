# SCU-Recall vs. Weighted Retention Correlation Analysis

## 1. Definition and Basis

**SCU-Recall Definition (FR-026a):**
SCU-recall is the unweighted fraction of gold facts recorded as retained (partial counting as one half), computed from the same per-case gold fact lists the existing scorer uses.

Scoring: For each fact in the gold set, the status from the judged verdict is mapped as follows:
- `retained` → 1.0
- `partial` → 0.5
- `omitted` → 0.0
- `mutated` → 0.0

SCU-recall = sum of these status scores / total number of facts per case.

**Basis for Correlation:**
To ensure a single, consistent value per case:
- **Model:** Sonnet (Claude 3.5 Sonnet)
- **Level:** Standard (default compression level)
- **Rationale:** The sonnet-standard combination exists for all 8 benchmark cases in the frozen snapshot. This is the default/canonical configuration used in the existing benchmark harness, ensuring the correlation is computed against a representative, real condition rather than a synthetic subset.

## 2. Data Pairs (n=8)

Computed from `skills/structured-gist/benchmarks/semantic-compression/results/combined.json` (frozen snapshot of 8 cases):

| Case | SCU-recall | weighted_retention |
|------|------------|-------------------|
| causality-heavy-explain | 0.8000 | 0.8000 |
| cause-chain-reversal | 0.9750 | 0.9747 |
| migration-tristate | 0.9211 | 0.9477 |
| near-identical-numbers | 0.8929 | 0.9508 |
| negation-and-true-peers | 0.9750 | 0.9895 |
| real-benchmark-archaeology | 0.8542 | 0.8846 |
| real-hook-discovery | 0.9667 | 0.9538 |
| synthetic-scale-verylarge | 0.7391 | 0.7316 |

## 3. Spearman Rank Correlation

**Computed coefficient: ρ = 0.9702**

**Sample size: n = 8**

**Statistical power note:** A correlation coefficient at n=8 is low-powered. The 95% confidence interval around this estimate is wide, and a replication on an independent sample of the same size could plausibly yield coefficients anywhere from roughly 0.85 to 0.99. However, at ρ=0.97, even the lower tail of uncertainty is well above the 0.8 threshold that decides the branch; the reading is not borderline.

## 4. Interpretation

The rank correlation of ρ = 0.9702 indicates an extremely strong monotonic relationship: as SCU-recall increases, weighted_retention increases in nearly the same rank order across cases. The two metrics are nearly redundant—they rank the cases almost identically.

This high correlation, combined with the fact that weighted_retention is already tracked and computed in the existing benchmark harness (FR-012), means that adding a separate SCU-recall column would provide minimal new information beyond what weighted_retention already captures.

## 5. Recommendation

Per FR-027: Since ρ (0.9702) >= 0.8, issue #1 ("Add an SCU-recall column to track unweighted retention separately") should be closed as duplicative of the existing weighted_retention metric.
