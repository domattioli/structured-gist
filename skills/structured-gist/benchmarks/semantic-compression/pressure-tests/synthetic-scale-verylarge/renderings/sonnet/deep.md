```text
- Checkout-service reliability
    A. six alerts fired this week
        ↪ five were minor and resolved quickly; only the fourth
        carried real financial impact, stayed unresolved at the
        code level, and was missed by automated monitoring
    B. alert one — CPU spike
        ↪ a brief spike during a traffic burst; the autoscaler
        added capacity automatically and the alert cleared in 3
        minutes, no human involvement needed
    C. alert two — latency warning
        ↪ fired during a routine deploy; resolved on its own
        once the deploy finished and traffic normalized across
        the new pods, about 5 minutes total
    D. alert three — stale cache
        ↪ a cache layer served slightly outdated pricing data;
        an engineer manually flushed the affected keys and it
        cleared in about 8 minutes, no customer-facing impact
        confirmed
    E. alert four — top priority
        ↪ a race condition in the payment-confirmation retry
        path caused duplicate charges: two retries fired close
        enough together that both read the confirmation status
        before either wrote it, letting a stale check pass a
        second charge through
        i. impact
            ↪ roughly 140 customers charged twice for the same
            order within a 40-minute window, between about 09:10
            and 09:50
        ii. detection
            ↪ error rate and latency both stayed within normal
            bounds throughout, so no alert or monitoring signal
            caught it; discovered about six hours later when a
            support ticket flagged an unexpected duplicate
            charge and an engineer traced it to the retry logs
        iii. response
            ↪ the team confirmed the full ~140-customer blast
            radius and issued refunds to all of them the same
            day the ticket came in, before the postmortem was
            finished
        iv. root cause
            ↪ the retry path is missing an idempotency check
            that would prevent a second confirmation from ever
            being processed for the same order, regardless of
            timing
        v. status
            ↪ a design for the check exists but hasn't been
            reviewed; the single highest-priority unresolved
            item on the team's board, since the race condition
            is still live in production and could recur until it
            ships
    F. alert five — disk-space warning
        ↪ a log volume approaching capacity; a log-rotation job
        was triggered manually and the warning cleared in about
        2 minutes
    G. alert six — 500-error spike
        ↪ traced to an outage in an unrelated dependent service,
        not any fault in checkout-service itself; resolved on
        its own once the dependency recovered about 6 minutes
        later

- Mobile release train
    ↪ four independent patch releases this week, v3.14.1 through
    v3.14.4, unrelated to the checkout-service and data-platform
    workstreams
    I. v3.14.1 — launch-crash fix
        ↪ fixed a crash on app launch affecting users on one
        specific older OS version; the fix was a one-line null
        check and shipped the same day it was found
    II. v3.14.2 — overlap fix
        ↪ a button overlapped the status bar on devices with a
        particular screen-notch shape; purely cosmetic, no
        functional impact
    III. v3.14.3 — dependent hotfix
        ↪ a rushed hotfix for a login-flow regression that
        v3.14.1's own change introduced: its null check was
        slightly too aggressive and also suppressed a legitimate
        error state, so v3.14.3 narrowed the condition; the only
        release in this train that depended on another, since
        v3.14.1 needed this follow-up correction
    IV. v3.14.4 — accessibility setting
        ↪ added a new setting letting users disable a specific
        animation, in response to accessibility feedback;
        unrelated to the other three releases and to either of
        the other two workstreams

- Data-platform connector maintenance
    ↪ five source connectors broke this week from the same
    failure class — upstream schema drift, where a source system
    added or renamed a column without notice and the connector's
    fixed mapping broke on ingest, failing the load until the
    mapping was updated
    A. crm-connector — column renamed
        ↪ broke Monday when the source CRM renamed lead_status
        to pipeline_stage; the mapping was updated the same day
    B. billing-events-connector — column added
        ↪ broke Tuesday when a new currency_code column was
        added upstream with no corresponding mapping entry;
        updated to include it, defaulting historical rows to the
        existing single-currency assumption
    C. support-tickets-connector — column renamed
        ↪ broke Wednesday for the same reason as crm-connector —
        priority renamed to severity — and was fixed the same
        way, a mapping update
    D. inventory-connector — column dropped
        ↪ broke Thursday when warehouse_region_legacy was
        dropped entirely rather than renamed; the mapping was
        updated to stop referencing it and read
        warehouse_region, which had already existed in parallel
        for months
    E. marketing-events-connector — column renamed
        ↪ broke Friday for the same schema-drift reason as the
        others — campaign_id renamed to campaign_uuid — and was
        fixed the same way as the rest
    F. drift-detection follow-up
        ↪ the fifth same-class failure in five days prompted a
        proposal to alert on schema drift before a connector
        fails at ingest, rather than after; not started, logged
        as a next-quarter candidate, unrelated to the other two
        workstreams

- On-call documentation cleanup
    ↪ unrelated to the three workstreams above; the on-call
    runbook was reorganized this week
    ▸ Problem
        ↪ the runbook had grown to cover 40 alert types across a
        dozen services, but its table of contents hadn't been
        updated in over a year, so several sections were
        effectively unreachable without a full-text search
    ▸ Trigger
        ↪ a new hire's feedback that they couldn't find the
        right section under time pressure during their first
        on-call shift, during a real page — not any incident of
        the runbook itself causing a mishandled alert
    ▸ Reorganization
        a. one runbook split per service
        b. top-level index added, linking all
        c. nine sections archived (decommissioned services)
        ↪ no alert-handling instructions changed in this pass;
        every surviving section's actual guidance is
        byte-for-byte the same as before, only the file layout
        and the index changed
    ▸ Open item
        ↪ three of the newly split-out files still need their
        code-owner metadata updated to point at the right team;
        tracked as a small cleanup task with no urgency
```
