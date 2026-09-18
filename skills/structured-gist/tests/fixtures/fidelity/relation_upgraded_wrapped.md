# Fixture — relation upgraded, wrapped (fidelity negative case)

Same defect as relation_upgraded.md — the source's association is
rewritten as a causal arrow between the declared endpoints — but the
arrow text is itself split across a hard-wrapped continuation line,
so the check must merge continuations before it can catch this.
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
        ↪ engineers noted the steadily rising request rate →
        timeout errors during cache warm-up
```
