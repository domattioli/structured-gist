```text
- Checkout outage 14:02
    ▸ Initial diagnosis (incorrect)
        i. symptoms: connection errors from
        payments service
        ii. theory: pool exhaustion
        iii. mitigation: raised pool 50 → 150
        iv. outcome: error rates dropped noticeably
    ▸ Parallel investigation
        a. examined query-level tracing data
        b. found slow query: >8 seconds
        c. query typical: <100 milliseconds
        d. query: customer order history lookups
        e. slow query held connection open for
        entire duration
        f. simultaneous connections starved other queries
        g. pool exhaustion: downstream effect, not root
        h. root: 2-day-old migration dropped index
    ▸ Actual fix
        i. added missing index back
        ii. query performance: >8s → <100ms
        iii. resolved connection pileup entirely
        iv. pool left at 150 (no revert)
    ▸ Team postmortem
        ↪ pool size increase was temporary headroom
        only, not the actual fix; the missing index
        was the root cause
```
