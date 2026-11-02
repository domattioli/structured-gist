```text
- billing-service
    ▸ Status
        ↪ Fully migrated; the cutover completed last month.
    ▸ Fallback
        ↪ The old billing infrastructure has been decommissioned
        entirely, so no fallback path is left even if wanted.
- notifications-service
    ▸ Status
        ↪ Not started; nothing has moved and it still runs
        entirely on the old infrastructure today.
    ▸ Timing
        ↪ Scheduled to migrate next quarter, once the billing
        cutover's lessons are folded into the migration runbook.
- auth-service
    ▸ Status
        ↪ Explicitly not going to be migrated, at least not
        under the current plan.
    ▸ Reason
        ↪ It carries a large amount of bespoke compliance logic
        that would be expensive and risky to port, and the team
        judged the migration risk not worth the benefit.
    ▸ Decision
        ↪ Final for now, not a scheduling delay.
- search-service
    ▸ Status
        ↪ Migrated, then rolled back; it is back on the old
        infrastructure, fully reverted.
    ▸ History
        i. attempted two months ago
        ii. ran about three weeks
        iii. reverted after user-hit bugs
            ↪ Users hit data-consistency bugs where search
            results lagged behind the source-of-truth database
            in ways the old infrastructure never exhibited.
    ▸ Open decision
        ↪ Whether to attempt the migration again has not been
        decided.
- reporting-service
    ▸ Status
        ↪ Mid-migration, actively in progress right now.
    ▸ Cut over
        ↪ Some endpoints already serve production traffic on
        the new infrastructure.
    ▸ Remaining
        ↪ The rest are served from the old infrastructure until
        their own cutover is scheduled.
    ▸ Distinction
        ↪ The only service on this list running on both
        infrastructures at once.
```
