# Example — `structured-gist deep`

Source: "Explain why a web app added a request cache." Exhaustive — full ladder, ordered steps as `I.`, grouped as `a.`, arrows surfaced.

```
- Latency problem
    I. every request hit the database
        a. no caching layer existed
        b. queries repeated across users
            ↪ hot endpoints re-ran the same joins → the DB
            became the bottleneck
    II. no reuse between requests
        ↪ each request opened its own connection; no shared
        state

- The fix
    I. identify cacheable endpoints
        a. read-heavy, low write frequency
        b. exclude user-specific data
    II. add cache layer
        a. keyed by query params
        b. TTL-based expiry
    III. verify hit rate
        a. monitor cache metrics
        b. tune TTL

- Result
    I. database load cut 80%
    II. most requests now served from cache
        ↪ cache warms automatically after deploy
```

Ordered loop steps → `I. II. III.`; grouped items → `a. b.`; long clauses → `↪` leaves.
