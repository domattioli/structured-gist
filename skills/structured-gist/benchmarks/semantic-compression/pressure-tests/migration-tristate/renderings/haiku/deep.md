```text
- Platform migration status
    A. billing-service
        ▸ Status
            ↪ fully migrated to new infrastructure
        ▸ Timeline
            i. cutover completed last month
            ii. old infrastructure decommissioned
               entirely
        ▸ Implications
            ↪ no fallback path exists; commitment is
               irreversible even if we wanted one
    B. notifications-service
        ▸ Status
            ↪ not started; scheduled for next quarter
        ▸ Prerequisite
            ↪ will start after billing's cutover lessons
               are incorporated into the migration runbook
        ▸ Current state
            ↪ still running entirely on old infrastructure
    C. auth-service
        ▸ Status
            ↪ explicitly not migrating under current plan
        ▸ Technical challenges
            i. contains large amount of bespoke
               compliance logic
            ii. expensive and risky to port to new
               infrastructure
        ▸ Business decision
            ↪ migration risk not worth the benefit for
               this particular service
        ▸ Decision finality
            ↪ final for now; not a scheduling delay
    D. search-service
        ▸ Status
            ↪ attempted migration then rolled back;
               currently reverted to old infrastructure
        ▸ Attempt timeline
            i. migration attempted two months ago
            ii. ran on new infrastructure three weeks
        ▸ Failure mechanism
            ↪ users encountered data-consistency bugs
               where search results lagged behind
               source-of-truth database in ways old
               infrastructure never exhibited
        ▸ Current resolution
            ↪ fully reverted; decision on future
               re-attempt not yet made
    E. reporting-service
        ▸ Status
            ↪ currently mid-migration; actively in
               progress right now
        ▸ Endpoint distribution
            i. some endpoints already cut over to new
               infrastructure
            ii. cutover endpoints serving production
               traffic from new location
            iii. remaining endpoints still on old
               infrastructure
        ▸ Unique characteristic
            ↪ only service on this list running
               simultaneously on both infrastructures
```
