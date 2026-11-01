```text
- Recap scope
    ▸ Grouping
        ↪ Four workstreams ran in parallel this week and do not
        intersect; they are grouped only because they happened
        in the same week.
- Checkout reliability
    ▸ Alerts
        a. CPU spike
            ↪ Autoscaler added capacity during a traffic burst;
            cleared in 3 minutes with no human involvement.
        b. Deploy latency warning
            ↪ Fired during a routine deploy; resolved on its own
            once traffic normalized across new pods, about 5
            minutes.
        c. Stale-cache warning
            ↪ A cache layer served slightly outdated pricing
            data; an engineer manually flushed the affected keys
            and it cleared in about 8 minutes, with no
            customer-facing impact confirmed afterward.
        d. Duplicate charges
            ▸ Impact
                ↪ About 140 customers were charged twice for the
                same order within a 40-minute window, roughly
                09:10 to 09:50.
            ▸ Cause
                ↪ A race condition in the payment-confirmation
                retry path: two retries fired close enough
                together that both read the confirmation status
                before either wrote it, so the check ran against
                stale state and let a duplicate charge through.
                The retry path is missing an idempotency check.
            ▸ Detection
                ↪ No alert or monitoring signal caught it, as
                the retry path's error rate and latency stayed
                within normal bounds. A support ticket flagged
                the duplicate charge roughly six hours later and
                an engineer traced it through the retry path's
                logs.
            ▸ Response
                ↪ The full blast radius was confirmed at about
                140 customers and all were refunded the same day
                the ticket came in, before the postmortem was
                finished.
            ▸ Fix status
                ↪ A design for the idempotency check exists but
                has not been reviewed; the fix has not shipped.
            ▸ Priority
                ↪ Highest-priority unresolved action for
                checkout-service, ranked above every other open
                item on the board, as the race condition is
                still live in production and could recur at any
                time until the check ships.
        e. Disk-space warning
            ↪ A log volume approached capacity; a log-rotation
            job was triggered manually and it cleared in about 2
            minutes.
        f. Dependency 500 spike
            ↪ Traced to an outage in an unrelated dependent
            service, not a checkout-service fault; resolved on
            its own about 6 minutes later.
    ▸ Comparison
        ↪ Only the fourth alert had real financial impact, is
        still unresolved at the code level, and was missed by
        automated monitoring; the other five were unremarkable
        operational noise.
- Mobile releases
    ▸ Releases
        a. v3.14.1 launch crash
            ↪ Fixed a crash on launch for users on one specific
            older OS version with a one-line null check; shipped
            the same day it was found.
        b. v3.14.2 layout bug
            ↪ A button overlapped the status bar on devices with
            a particular screen notch shape; purely cosmetic, no
            functional impact.
        c. v3.14.3 hotfix
            ↪ Rushed fix for a login-flow regression introduced
            by v3.14.1's change: the null check was slightly too
            aggressive and also suppressed a legitimate error
            state, so v3.14.3 narrowed the condition.
        d. v3.14.4 animation setting
            ↪ Added a setting to disable a specific animation,
            in response to accessibility feedback.
    ▸ Dependencies
        ↪ v3.14.3 is the only release that depends on an earlier
        one in the train, v3.14.1. The other releases and the
        train as a whole are independent of the other
        workstreams.
- Connector maintenance
    ▸ Failure class
        ↪ Upstream schema drift: a source system added or
        renamed a column without notice, the connector's fixed
        schema mapping broke on ingest, and the load failed
        until the mapping was updated. Five source connectors in
        the data-platform ETL pipeline were hit.
    ▸ Connectors
        a. `crm-connector` Monday
            ↪ The source CRM renamed `lead_status` to
            `pipeline_stage`; the mapping was updated the same
            day.
        b. `billing-events-connector` Tuesday
            ↪ A new `currency_code` column was added upstream
            with no mapping entry; the connector was updated to
            include it, defaulting historical rows to the
            existing single-currency assumption.
        c. `support-tickets-connector` Wednesday
            ↪ Same reason as crm-connector, a renamed column,
            `priority` to `severity`; fixed the same way, by a
            mapping update.
        d. `inventory-connector` Thursday
            ↪ An upstream column, `warehouse_region_legacy`, was
            dropped entirely rather than renamed; the mapping
            stopped referencing it and now reads the newer
            `warehouse_region`, which had existed in parallel
            for months.
        e. `marketing-events-connector` Friday
            ↪ `campaign_id` was renamed to `campaign_uuid`;
            fixed the same way as the rest.
    ▸ Follow-up
        ↪ As this was the fifth time in as many days that the
        same failure class hit a different connector, an item
        was opened to add schema-drift detection that alerts
        before a connector fails at ingest, not after. That work
        has not started; it is logged as a next-quarter
        candidate, not yet scheduled.
- Runbook cleanup
    ▸ Problem
        ↪ The on-call runbook covered 40 alert types across a
        dozen services, but its table of contents had not been
        updated in over a year, so several sections were
        effectively unreachable without a full-text search.
    ▸ Changes
        a. split into per-service files
        b. added top-level index
        c. archived nine decommissioned sections
            ↪ They described alerts for services since fully
            decommissioned that no longer exist.
    ▸ Guidance
        ↪ No alert-handling instructions changed; every
        surviving section's guidance is byte-for-byte the same,
        and only the file layout and index changed.
    ▸ Trigger
        ↪ A new hire's feedback during their first on-call
        shift: they could not find the right section under time
        pressure during a real page. No incident of the runbook
        causing a mishandled alert prompted it.
    ▸ Open item
        ↪ Three of the newly split-out files still need their
        code-owner metadata updated to point at the right team;
        a small cleanup task with no urgency.
```
