```text
- Checkout outage 14:02
    ▸ Initial diagnosis (incorrect)
        i. symptoms: connection errors
        ii. theory: pool exhaustion
        iii. mitigation: raised pool 50 → 150
        iv. result: errors dropped (felt correct)
    ▸ Root cause
        a. slow query: 8+ seconds (usual <100ms)
        b. cause: missing index from migration
    ▸ Actual fix
        i. added missing index
        ii. query restored to <100ms
    ▸ Postmortem
        ↪ pool increase was mitigation only, not fix;
        index was root cause
```
