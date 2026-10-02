# Example — `structured-gist` (standard granularity, the only level)

Source: "Explain why a web app added a request cache." Full ladder, soft cap 4, arrows carry the long clauses.

```
- Latency problem
    I. every request hit the database
        ↪ same queries repeated across requests; the DB
        became the bottleneck
    II. no reuse between requests
        ↪ each request opened its own connection; no shared
        state

- The fix
    A. request cache added
        a. keyed by query params
        b. TTL-based expiry
        c. fail-open
    B. cuts database load 80%

- Result
    I. faster response times
```

Ladder: `-` concept · `I./A.` first enumerator tier · `a./b.` deeper tier · `↪` long-sentence leaf.
