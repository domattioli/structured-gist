# Fixture — hedge dropped (fidelity negative case)

The claim keeps its source relation wording, but the hedge governing the
claim is absent from both the claim node and any attached explanation leaf.
Lints clean; fails only the fidelity hedge-attachment check.

<!--
source: Support notes recorded that timeout errors may spike during cache warm-up, correlated with a rising request rate.
hedge: may
claim-key: spike during cache warm-up
relation: correlated with
endpoint-a: timeout errors
endpoint-b: request rate
supported-branches: Observed
-->

```text
- Cache warm-up timeouts
    ▸ Observed
        ↪ timeout errors spike during cache warm-up, correlated
        with a rising request rate
```
