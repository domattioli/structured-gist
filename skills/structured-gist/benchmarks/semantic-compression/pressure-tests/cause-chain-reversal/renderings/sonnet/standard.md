```text
- Outage onset
    ▸ Start
        ↪ The outage began at 14:02.
    ▸ First symptom
        ↪ On-call's first signal was a wave of database
        connection errors from the payments service.
- Pool-exhaustion theory
    I. initial diagnosis
        ↪ Connection errors were the first visible signal, so
        on-call assumed pool exhaustion from traffic and spent
        the first twenty minutes on that assumption.
    II. stopgap: raise pool
        ↪ At 14:24 the pool size was raised from 50 to 150.
    III. apparent confirmation
        ↪ Error rates dropped noticeably afterward, which felt
        like confirmation that pool exhaustion was the root
        cause.
- Secondary probe
    I. investigation resumes
        ↪ Error rates had not fully returned to normal, so a
        slower secondary investigation kept going in parallel.
    II. slow query found
        ↪ Query-level tracing showed the payments service's
        customer order-history lookup taking upward of eight
        seconds per call instead of its usual
        under-100-millisecond time.
    III. pool-starving mechanism
        ↪ Every slow call held a database connection open for
        its full duration, and under load enough connections
        were tied up simultaneously to starve everything else —
        the actual cause of the pool-exhaustion symptoms on-call
        had been treating as root cause.
- Root cause
    ▸ Reversed chain
        i. migration drops index
        ii. missing index slows query
        iii. slow query exhausts pool
    ▸ True cause
        ↪ The missing index, not the connection pool, was the
        actual root cause; both the slow query and the pool
        exhaustion were downstream symptoms of it.
- Stopgap limits
    ▸ Symptom reduced
        ↪ Raising the pool size only bought headroom, reducing
        how often the symptom surfaced.
    ▸ Not fixed
        ↪ It did nothing to fix the query itself, and the same
        slow-query behavior kept recurring under peak load.
- Index fix
    ▸ Action
        ↪ The missing index was added back later that day.
    ▸ Result
        ↪ Query time returned to under 100 milliseconds and the
        connection pileup was eliminated entirely.
- Postmortem verdict
    ▸ Pool size kept
        ↪ The pool size was left at 150 afterward since there
        was no reason to revert it.
    ▸ Verdict
        ↪ The postmortem was explicit that the pool increase was
        never the fix — the index was.
```
