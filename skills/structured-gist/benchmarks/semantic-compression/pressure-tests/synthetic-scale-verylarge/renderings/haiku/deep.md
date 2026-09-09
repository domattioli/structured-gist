```text
- Checkout-service reliability
    ▸ Six alerts (most routine; one critical)
        a. Routine alerts (five)
            i. CPU spike (traffic burst)
                ↪ autoscaler added capacity automatically
                ↪ resolved in 3 minutes
            ii. Latency warning (during deploy)
                ↪ traffic normalized across new pods
                ↪ resolved in 5 minutes
            iii. Stale-cache warning
                ↪ cache layer serving outdated pricing data
                ↪ engineer manually flushed affected cache
                  keys
                ↪ resolved in 8 minutes
                ↪ no customer-facing impact confirmed
                  afterward
            iv. Disk-space warning (log volume)
                ↪ log-rotation job triggered manually
                ↪ resolved in 2 minutes
            v. 500 errors (dependency outage)
                ↪ outage in unrelated dependent service
                ↪ not a fault in checkout-service
                ↪ resolved in 6 minutes once dependency
                  recovered
        b. Critical incident: double-charge race condition
            ↪ Payment-confirmation retry path race condition
            ↪ Two retries firing close together both read
              confirmation status before either wrote it
            ↪ Both read stale state; second charge went
              through
            ↪ Approximately 140 customers charged twice
            ↪ Window: 40 minutes (roughly 09:10–09:50)
            ↪ Discovery: customer support ticket 6 hours later
            ↪ Response: team confirmed 140 affected customers
            ↪ Refunds issued same day, before postmortem
              finished
            ↪ Root cause: missing idempotency check
            ↪ Would prevent second confirmation regardless
              of timing
            ↪ Status: fix design exists but not yet reviewed
            ↪ Risk: race condition still live in production
            ↪ Priority: single highest-priority unresolved
              action
            ↪ Ranked above every other item on team board
    ▸ Alert patterns
        ↪ Only critical incident involved real financial
          impact
        ↪ Only critical incident still unresolved at code
          level
        ↪ Only critical incident missed by automated
          monitoring
        ↪ Other five were unremarkable operational noise
- Mobile app release train
    ▸ Four patch releases (v3.14.1–v3.14.4)
        a. v3.14.1: crash on older OS version
            ↪ crash on one specific older OS version
            ↪ fixed with one-line null check
            ↪ shipped same day it was found
        b. v3.14.2: button layout bug
            ↪ button overlapped with status bar
            ↪ affected devices with particular screen notch
              shape
            ↪ purely cosmetic, no functional impact
        c. v3.14.3: regression hotfix (depends on v3.14.1)
            ↪ v3.14.1's null check was too aggressive
            ↪ null check also suppressed legitimate error
              state
            ↪ v3.14.3 narrowed the condition
            ↪ v3.14.3 exists specifically as follow-up
              correction
        d. v3.14.4: accessibility setting
            ↪ new setting to disable specific animation
            ↪ in response to accessibility feedback
            ↪ unrelated to other three releases
            ↪ unrelated to checkout-service and data-platform
              workstreams
- Data-platform connector maintenance
    ▸ Schema-drift failures (five connectors, same fix class)
        a. crm-connector (Monday)
            ↪ source CRM renamed lead_status to pipeline_stage
            ↪ connector's fixed schema mapping broke on ingest
            ↪ mapping updated same day
        b. billing-events-connector (Tuesday)
            ↪ new currency_code column added upstream
            ↪ no corresponding mapping entry
            ↪ connector updated to include it
            ↪ historical rows defaulted to single-currency
              assumption
        c. support-tickets-connector (Wednesday)
            ↪ source renamed priority column to severity
            ↪ fixed same way (mapping update)
        d. inventory-connector (Thursday)
            ↪ upstream column dropped: warehouse_region_legacy
            ↪ connector still reading the dropped column
            ↪ mapping updated to stop referencing dropped
              column
            ↪ mapping updated to read warehouse_region
              (already existed in parallel for months)
        e. marketing-events-connector (Friday)
            ↪ campaign_id renamed to campaign_uuid
            ↪ fixed same way as others (mapping update)
    ▸ Pattern recognition
        ↪ fifth time in five days same failure class hit
          different connector
        ↪ pattern repeat triggered follow-up item
    ▸ Follow-up item
        ↪ add schema-drift detection
        ↪ alerts before connector fails at ingest time
        ↪ future: surface as warning instead of failed load
        ↪ not yet started; logged as next-quarter candidate
        ↪ unrelated to checkout-service and mobile-release
          workstreams
- On-call documentation cleanup
    ▸ Runbook history
        ↪ runbook grew to cover 40 different alert types
        ↪ across a dozen services
        ↪ table of contents not updated over a year
        ↪ several sections unreachable without full-text
          search
    ▸ Reorganization (layout only; no guidance changed)
        a. split single runbook file into one per service
        b. added top-level index linking all new files
        c. archived 9 sections for decommissioned services
    ▸ Motivation for change
        ↪ new hire during first on-call shift couldn't
          find right section
        ↪ couldn't find it under time pressure during real
          page
        ↪ feedback prompted this reorganization
        ↪ not prompted by incident where runbook caused
          mishandled alert
    ▸ Implementation note
        ↪ every surviving section's guidance
          byte-for-byte same
        ↪ only file layout and index changed
    ▸ Follow-up item
        ↪ update code-owner metadata on three newly split
          files
        ↪ point code-owner metadata at right team
        ↪ tracked as small cleanup task with no urgency
```
