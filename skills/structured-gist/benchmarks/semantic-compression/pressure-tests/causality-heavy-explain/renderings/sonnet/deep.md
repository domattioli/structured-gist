```text
- Synchronous design
    ▸ Handler behavior
        ↪ handler called the downstream enrichment
        API directly, held the HTTP request open
        until that call returned
    ▸ Downstream API
        ↪ already slow under normal conditions,
        often taking several seconds to respond
    ▸ Direct effects
        I. connection held open
            ↪ because the handler waited synchronously,
            a slow call held the sender's connection
            open for that same duration
        II. sender timeouts
            ↪ under real load, some calls ran long
            enough to exceed the sender's timeout, so
            timeouts hit a meaningful fraction of
            requests
        III. automatic retry
            ↪ senders that see a timeout assume failure
            and retry by design, so every timeout
            produced a retry
        IV. retry adds load
            ↪ each retry was itself a new synchronous
            call to the same slow endpoint, so retries
            added pressure instead of relieving it
- Feedback loop
    A. ordinary traffic
        ↪ the loop stays small enough to go unnoticed
    B. peak traffic
        ↪ the same loop runs hot enough to cascade
        through compounding stages
            i. queue depth grows faster than drains
            ii. latency climbs further
            iii. timeout rate climbs further
            iv. retry volume climbs further
            v. retries dominate capacity
                ↪ receiver ends up spending most of
                its capacity on retried requests
                instead of new ones
- Queue-based redesign
    ▸ Trigger
        ↪ the peak-traffic cascade drove the decision
        to put a message queue in front of the
        enrichment step
    ▸ New flow
        I. acknowledge immediately
            ↪ receiver acknowledges the sender right
            away on receipt, instead of waiting on
            enrichment
        II. hand off to worker
            ↪ enrichment work goes to a worker process
            instead of being done inline
    ▸ Effect
        ↪ receiver latency no longer depends on the
        enrichment API's latency, so the two are
        decoupled
- Retry storm eliminated
    I. no timeout
        ↪ a slow downstream call no longer produces a
        sender-facing timeout
    II. no retry
        ↪ no timeout means no retry
    III. failure mode gone
        ↪ the specific retry-storm failure mode that
        caused the cascades is gone entirely, not just
        less frequent
```
