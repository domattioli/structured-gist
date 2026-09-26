# Example — `caveman ultra` + `/structured-gist standard`

Orthogonal compose: same ladder structure, ultra-terse wording (caveman's doing, not structured-gist'), markers stay Latin.

Source: "Explain why a web app added a request cache."

```
- Latency problem
    I. every req hit DB
        ↪ same queries repeated; DB = bottleneck
    II. no reuse between reqs
        ↪ each req own connection; no shared state

- Fix
    A. cache layer added
        a. keyed by query params
        b. TTL, fail-open
    B. cuts DB load 80%

- Result
    I. faster resp times
```

Structure identical to `standard`; only the wording compressed. Under `wenyan-*` the node text becomes 文言文 — markers (`-` `I.` `A.` `a.` `↪`) stay Latin.
