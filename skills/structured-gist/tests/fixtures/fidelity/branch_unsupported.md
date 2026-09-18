# Fixture — branch unsupported (fidelity negative case)

Hedge stays attached, relation wording is preserved, but the outline
carries a `▸ Next` branch that the declared `supported-branches` does
not list — a manufactured branch. Lints clean; fails only the
fidelity branch-support check.

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
        ↪ timeout errors may spike during cache warm-up,
        correlated with a rising request rate
    ▸ Next
        ↪ pre-warm cache before peak traffic
```
