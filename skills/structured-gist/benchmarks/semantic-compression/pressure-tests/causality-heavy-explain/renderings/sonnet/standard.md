```text
- Synchronous design
    ▸ Handler behavior
        ↪ called the enrichment API directly, held
        the HTTP request open until it returned
    ▸ Downstream API
        ↪ already slow under normal conditions,
        often taking several seconds to respond
    ▸ Direct effects
        I. connection held open
        II. sender timeouts
        III. automatic retry
        IV. retry adds load
- Feedback loop
    A. ordinary traffic
        ↪ loop stays small enough to go unnoticed
    B. peak traffic
        ↪ loop cascades until retries dominate the
        receiver's capacity
- Queue-based redesign
    ▸ Trigger
        ↪ the peak-traffic cascade drove the decision
        to queue enrichment instead of calling it
        inline
    ▸ New flow
        I. acknowledge immediately
        II. hand off to worker
    ▸ Effect
        ↪ receiver latency no longer depends on
        enrichment latency, so the two are decoupled
- Retry storm eliminated
    I. no timeout
        ↪ a slow call no longer produces a
        sender-facing timeout
    II. no retry
        ↪ no timeout means no retry
    III. failure mode gone
        ↪ the retry-storm failure mode is gone
        entirely, not just reduced
```
