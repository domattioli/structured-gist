```text
- Platform migration status
    A. billing-service — fully migrated
        ▸ Status details
            i. cutover completed last month
            ii. old infrastructure decommissioned
            iii. no fallback path available
    B. notifications-service — scheduled for next quarter
        ▸ Timing constraint
            ↪ will start after billing lessons are
               folded into the migration runbook
    C. auth-service — explicitly not migrating
        ▸ Rationale
            i. contains bespoke compliance logic
            ii. expensive and risky to port
            iii. risk not justified by benefit
    D. search-service — attempted then reverted
        ▸ Attempt timeline
            i. attempted two months ago
            ii. ran for three weeks
        ▸ Failure reason
            ↪ users encountered data-consistency bugs;
               search results lagged behind database
    E. reporting-service — in-progress
        ▸ Hybrid state
            i. some endpoints already cutover
            ii. rest still on old infrastructure
            iii. running both simultaneously
```
