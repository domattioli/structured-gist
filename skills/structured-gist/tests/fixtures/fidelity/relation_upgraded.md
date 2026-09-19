# Fixture — relation upgraded (fidelity negative case)

The hedge stays attached to its claim, but the source's association is
rewritten as a causal arrow between the declared endpoints (reversed order).
Lints clean; fails only the fidelity relation-preservation check.

<!--
source: Support notes recorded that timeout errors may spike during cache warm-up, correlated with a rising request rate.
hedge: may
claim-key: spike during cache warm-up
relation: correlated with
endpoint-a: timeout errors
endpoint-b: request rate
supported-branches: Observed, Inferred
-->

```text
- Cache warm-up timeouts
    ▸ Observed
        ↪ timeout errors may spike during cache warm-up
    ▸ Inferred
        ↪ request rate → timeout errors
```
