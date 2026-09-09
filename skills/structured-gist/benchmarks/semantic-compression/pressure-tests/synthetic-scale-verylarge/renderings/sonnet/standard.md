```text
- Checkout-service reliability
    A. five minor alerts
        ↪ CPU spike, deploy latency, stale cache, disk space,
        and a dependent-service outage — cleared within minutes
        via autoscaling, self-resolution, or a quick manual fix;
        no lasting impact
    B. alert four: duplicate charges
        ↪ a payment-retry race condition let roughly 140
        customers get charged twice over a 40-minute window;
        missed by monitoring throughout, discovered six hours
        later via a support ticket, refunded the same day
    C. top-priority fix pending
        ↪ the retry path needs an idempotency check; a design
        exists but is unreviewed, and the race condition is
        still live in production — ranked above every other open
        item

- Mobile release train
    I. v3.14.1 — launch-crash fix
        ↪ a one-line null check fixed a launch crash on one
        older OS version; shipped the same day it was found
    II. v3.14.2 — overlap fix
        ↪ a button overlapped the status bar on a particular
        screen-notch shape; purely cosmetic, no functional
        impact
    III. v3.14.3 — dependent hotfix
        ↪ v3.14.1's null check was too aggressive and also
        suppressed a legitimate error state, so v3.14.3 narrowed
        the condition — the only release in this train that
        depended on another
    IV. v3.14.4 — accessibility setting
        ↪ lets users disable a specific animation, added for
        accessibility feedback; unrelated to the other releases
        and to the other workstreams

- Data-platform connector maintenance
    A. crm-connector — column renamed
        ↪ lead_status renamed to pipeline_stage upstream;
        mapping updated the same day
    B. billing-events-connector — column added
        ↪ a new currency_code column arrived with no mapping
        entry; added, defaulting historical rows to the existing
        single-currency assumption
    C. support-tickets-connector — column renamed
        ↪ priority renamed to severity, the same failure as
        crm-connector; fixed the same way, a mapping update
    D. inventory-connector — column dropped
        ↪ warehouse_region_legacy was dropped in favor of
        warehouse_region, which had already existed in parallel
        for months; mapping updated to stop referencing the
        dropped column
    E. marketing-events-connector — column renamed
        ↪ campaign_id renamed to campaign_uuid; fixed the same
        way as the rest
    F. drift-detection follow-up
        ↪ the fifth same-class failure in five days prompted a
        proposal to alert on schema drift before ingest fails,
        rather than after; not started, logged as a next-quarter
        candidate

- On-call documentation cleanup
    ▸ Trigger
        ↪ a new hire couldn't find the right section under time
        pressure during a real page — not any incident of the
        runbook itself causing a mishandled alert
    ▸ Reorganization
        a. one runbook split per service
        b. top-level index added, linking all files
        c. nine sections archived (decommissioned services)
        ↪ no alert-handling guidance changed — every surviving
        section's instructions are byte-for-byte the same; only
        layout and the index changed
    ▸ Open item
        ↪ three newly split files still need code-owner metadata
        updated to the right team — a minor cleanup with no
        urgency
```
