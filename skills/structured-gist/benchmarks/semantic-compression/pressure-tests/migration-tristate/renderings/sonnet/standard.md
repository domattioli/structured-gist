```text
- billing-service
    ▸ Status
        ↪ fully migrated; old infrastructure decommissioned, no
        fallback remains
- notifications-service
    ▸ Status
        ↪ not started, still fully on old infrastructure
    ▸ Timeline
        ↪ scheduled next quarter, after billing's lessons update
        the runbook
- auth-service
    ▸ Status
        ↪ will not migrate under the current plan
    ▸ Reasoning
        ↪ compliance logic too costly and risky to port; risk
        judged not worth the benefit
    ▸ Finality
        ↪ final decision now, not a scheduling delay
- search-service
    ▸ Status
        ↪ migrated, ran about three weeks, then rolled back; now
        fully reverted
    ▸ Rollback cause
        ↪ results lagged the source-of-truth database, unlike
        old infrastructure
    ▸ Open question
        ↪ whether to re-attempt is undecided
- reporting-service
    ▸ Status
        ↪ mid-migration: some endpoints already cut to new
        infrastructure, rest still on old awaiting their cutover
    ▸ Distinction
        ↪ only service running on both infrastructures at once
```
