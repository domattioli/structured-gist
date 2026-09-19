# Fixture — declaration malformed (fidelity negative case)

The declared hedge occurs inside the declared claim-key itself, the
declaration shape that would otherwise make the hedge check pass
unconditionally. Lints clean; fails only the fidelity declaration-validity
check.

<!--
source: Support notes recorded that timeout errors may spike during cache warm-up, correlated with a rising request rate.
hedge: may
claim-key: timeout errors may spike
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
```
