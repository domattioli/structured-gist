This recap covers four workstreams that ran in parallel this week and don't intersect with each other at all: checkout-service reliability, the mobile app release train, data-platform connector maintenance, and an on-call documentation cleanup. They're grouped here only because they happened in the same week, not because any of them relates to the others.

## Checkout-service reliability

Checkout-service had six separate alerts fire this week. Most of them were minor and resolved quickly, but reading them in order matters less than knowing which one actually mattered.

The first alert was a brief CPU spike during a traffic burst; the autoscaler added capacity automatically and the alert cleared in 3 minutes with no human involvement needed.

The second alert was a latency warning that fired during a routine deploy; it resolved on its own once the deploy finished and traffic normalized across the new pods, about 5 minutes total.

The third alert was a stale-cache warning, where a cache layer was serving slightly outdated pricing data; an engineer manually flushed the affected cache keys and the warning cleared in about 8 minutes, with no customer-facing impact confirmed afterward.

The fourth alert is the one that actually matters most out of all six, even though it sits in the middle of this list and looks, from the alert name alone, no different from the others. A race condition in the payment-confirmation retry path caused approximately 140 customers to be charged twice for the same order within a 40-minute window, between roughly 09:10 and 09:50. The retry path was supposed to check whether a payment had already been confirmed before retrying a confirmation call, but under a specific timing condition — two retries firing close enough together that both read the confirmation status before either one wrote it — the check ran against stale state and let a second, duplicate charge through. This was not caught by any alert or monitoring signal at the time, because the retry path's error rate and latency both stayed within normal bounds throughout the window; nothing about the metrics the team already watches would have flagged it. It was discovered only afterward, roughly six hours later, when a customer support ticket flagged an unexpected duplicate charge and an engineer traced it back to the retry path's logs. Once found, the team confirmed the full blast radius at approximately 140 affected customers and issued refunds to all of them the same day the ticket came in, before the postmortem was even finished. The root cause has been identified precisely: the retry path is missing an idempotency check that would prevent a second confirmation from ever being processed for the same order, regardless of timing. That fix has not shipped yet — a design for the idempotency check exists but has not been reviewed. It is the single highest-priority unresolved action coming out of this week for checkout-service, ranked above every other open item on the team's board, specifically because the underlying race condition is still live in production and could recur at any time until the idempotency check ships.

The fifth alert was a disk-space warning on a log volume approaching capacity; a log-rotation job was triggered manually and the warning cleared in about 2 minutes.

The sixth alert was a brief spike in 500 errors traced to an outage in an unrelated dependent service, not any fault in checkout-service itself; it resolved on its own once the dependency recovered about 6 minutes later.

Across all six alerts, only the fourth involved real financial impact to customers, only the fourth is still unresolved at the code level, and only the fourth was missed by automated monitoring rather than caught by it. The other five were unremarkable operational noise of the kind the team sees most weeks.

## Mobile app release train

The mobile app shipped four patch releases this week, v3.14.1 through v3.14.4, and they are independent of both the checkout-service work above and the data-platform work below.

v3.14.1 fixed a crash on app launch that affected users on one specific older OS version; the fix was a one-line null check and shipped the same day it was found.

v3.14.2 fixed a visual layout bug where a button overlapped with the status bar on devices with a particular screen notch shape; purely cosmetic, no functional impact.

v3.14.3 was a rushed hotfix for a login-flow regression introduced by v3.14.1's own change; the null check from v3.14.1 was slightly too aggressive and also suppressed a legitimate error state, so v3.14.3 narrowed the condition. This is the one release in the four that depended on a previous one in the same train — v3.14.3 exists specifically because v3.14.1 needed a follow-up correction, not because of anything unrelated.

v3.14.4 added a new setting to let users disable a specific animation, in response to accessibility feedback; unrelated to the other three releases in this train and unrelated to either of the other two workstreams in this recap.

## Data-platform connector maintenance

Five source connectors in the data-platform ETL pipeline needed the same class of fix this week: upstream schema drift, where a source system added or renamed a column without notice and the connector's fixed schema mapping broke on ingest, failing the load for that connector until someone updated its mapping.

The `crm-connector` broke Monday when the source CRM renamed a `lead_status` column to `pipeline_stage`; the mapping was updated the same day.

The `billing-events-connector` broke Tuesday when a new `currency_code` column was added upstream with no corresponding mapping entry; the connector was updated to include it, defaulting historical rows to the existing single-currency assumption.

The `support-tickets-connector` broke Wednesday for the same reason as `crm-connector` — a renamed column, this time `priority` to `severity` — and was fixed the same way, a mapping update.

The `inventory-connector` broke Thursday when an upstream column was dropped entirely rather than renamed, `warehouse_region_legacy`, which the connector had still been reading; the mapping was updated to stop referencing the dropped column and to read the newer `warehouse_region` column that had already existed in parallel for months.

The `marketing-events-connector` broke Friday for the same schema-drift reason as the others, a renamed `campaign_id` becoming `campaign_uuid`, and was fixed the same way as the rest.

Because this is the fifth time in as many days that the same failure class hit a different connector, a follow-up item was opened to add schema-drift detection that alerts before a connector fails at ingest time, rather than after, so future occurrences of this exact pattern surface as a warning instead of a failed load. That detection work has not started; it is logged as a next-quarter candidate, not yet scheduled, and is unrelated to both the checkout-service and mobile-release workstreams above.

## On-call documentation cleanup

Separately, and unrelated to any of the three workstreams above, the on-call runbook was reorganized this week. The runbook had grown to cover 40 different alert types across a dozen services, but its table of contents hadn't been updated in over a year, so several sections were effectively unreachable without a full-text search. The reorganization split the single runbook file into one file per service, added a top-level index linking all of them, and archived nine sections describing alerts for services that have since been fully decommissioned and no longer exist. No alert-handling instructions were changed in this pass — every surviving section's actual guidance is byte-for-byte the same as before, only the file layout and the index changed. This work was prompted by a new hire's feedback during their first on-call shift that they couldn't find the right section under time pressure during a real page, not by any incident of the runbook itself causing a mishandled alert. The remaining open item here is minor: three of the newly split-out files still need their code-owner metadata updated to point at the right team, tracked as a small cleanup task with no urgency.
