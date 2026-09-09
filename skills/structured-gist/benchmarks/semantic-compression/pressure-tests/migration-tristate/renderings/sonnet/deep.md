```text
- billing-service
    ▸ Status
        ↪ fully migrated, cutover completed last month
    ▸ Decommission
        ↪ old infrastructure fully decommissioned, no fallback
        even if wanted
- notifications-service
    ▸ Status
        ↪ not started, still fully on old infrastructure
    ▸ Timeline
        ↪ scheduled next quarter, once billing's lessons update
        the runbook
- auth-service
    ▸ Status
        ↪ will not migrate, under current plan
    ▸ Reasoning
        a. bespoke compliance logic
            ↪ costly and risky to port
        b. risk vs benefit
            ↪ migration risk judged not worth the benefit
    ▸ Finality
        ↪ final decision now, not a scheduling delay
- search-service
    ▸ Status
        ↪ migrated, then rolled back; now fully reverted to old
        infrastructure
    ▸ Attempt timeline
        i. migrated two months ago
        ii. ran about three weeks
        iii. reverted after data-consistency bugs
            ↪ results lagged the source-of-truth db, unlike old
            infrastructure
    ▸ Open question
        ↪ whether to re-attempt is undecided
- reporting-service
    ▸ Status
        ↪ mid-migration, actively in progress
    ▸ Cutover split
        a. some endpoints on new infrastructure
            ↪ already serving production traffic
        b. remaining endpoints on old infrastructure
            ↪ their own cutover not yet scheduled
    ▸ Distinction
        ↪ only service on both infrastructures at once
```
