```text
- Checkout outage
    ▸ Onset
        ↪ It started at 14:02; the first signal on-call saw was
        a wave of database connection errors from the payments
        service.
    ▸ Initial theory
        ↪ Connection errors were first visible in the logs, so
        the theory was that traffic had exhausted the connection
        pool; on-call spent twenty minutes on that assumption.
    ▸ Stopgap
        ↪ Pool size was raised from 50 to 150 at 14:24, and
        error rates dropped noticeably, which felt like
        confirmation of pool exhaustion as root cause.
    ▸ Residue
        ↪ Error rates were not fully normal, so a slower
        secondary investigation kept going in parallel.
- Cause chain
    I. schema migration
        ↪ It shipped two days earlier and silently dropped an
        index the query depended on.
    II. slow order-history query
        ↪ Query-level tracing found it taking upward of eight
        seconds per call instead of under 100 milliseconds.
    III. connections held open
        ↪ Each slow call held a connection for the full
        duration, and under load enough were tied up at once
        to starve everything else.
    IV. pool exhaustion
        ↪ This was the symptom on-call had been treating as
        the root cause; it was downstream of the slow query.
- Root cause
    ▸ Culprit
        ↪ The missing index was the root cause, not the
        connection pool.
- Pool increase
    ▸ Effect
        ↪ It only bought headroom and reduced how often the
        symptom surfaced; it did not fix the query, and the
        slow-query behavior kept recurring under peak load.
    ▸ Status
        ↪ The size was left at 150 afterward, as there was no
        reason to revert it.
- Resolution
    ▸ Fix
        ↪ Later that day the missing index was added back,
        bringing the query under 100 milliseconds and
        eliminating the connection pileup entirely.
    ▸ Postmortem
        ↪ The team was explicit that the pool increase was
        never the fix; the index was.
```
