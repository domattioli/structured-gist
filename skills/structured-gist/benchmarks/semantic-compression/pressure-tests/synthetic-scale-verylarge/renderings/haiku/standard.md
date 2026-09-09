```text
- Checkout-service reliability
    ▸ Six alerts
        a. Five routine (auto/quick resolution)
            i. CPU spike
            ii. Deploy latency
            iii. Stale cache
            iv. Disk space
            v. Dependency outage
        b. One critical: double-charge race condition
            ↪ Race in retry path; payment check read stale state
            ↪ ~140 customers charged twice (40-min window)
            ↪ Missed by monitoring; discovered via support ticket
            ↪ Refunds issued same day; idempotency fix unreviewed
            ↪ Highest-priority; race condition still live
- Mobile app release train
    ▸ Four releases (v3.14.1–v3.14.4)
        a. v3.14.1: crash on older OS
            ↪ fixed with one-line null check
        b. v3.14.2: button overlapped with notch
            ↪ cosmetic; no functional impact
        c. v3.14.3: login regression hotfix
            ↪ v3.14.1's null check too aggressive, suppressed error
            ↪ hotfix narrowed the condition
        d. v3.14.4: accessibility feature
            ↪ disable animation setting; user feedback response
- Data-platform connector maintenance
    ▸ Five schema-drift failures
        i. crm-connector: lead_status to pipeline_stage
        ii. billing-events-connector: new currency_code column
        iii. support-tickets-connector: priority to severity
        iv. inventory-connector: dropped warehouse_region_legacy
        v. marketing-events-connector: campaign_id to campaign_uuid
    ▸ Follow-up item
        ↪ add drift detection to alert before ingest failure
        ↪ not yet started; next-quarter candidate
- On-call documentation cleanup
    ▸ Runbook reorganization
        a. Split single file into per-service files
        b. Added top-level index linking all files
        c. Archived 9 sections for decommissioned services
    ▸ Implementation details
        ↪ No alert-handling guidance changed; layout only
        ↪ Prompted by new hire feedback (couldn't locate section)
    ▸ Follow-up item
        ↪ Update code-owner metadata on 3 files (minor)
```
