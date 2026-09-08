```text
- API resources A. projects ↪ the billing and permission boundary; everything else belongs to exactly one B. datasets ↪ versioned tabular data; every write creates an immutable version C. jobs ↪ asynchronous imports, exports, transformations over datasets
- Auth A. scoped tokens ↪ project, role, expiry; reader lists and downloads, writer adds versions and jobs, admin manages tokens and deletes; ninety-day cap with code 4012 in the final week
- Integrator traps A. rate limits per token ↪ shared tokens throttle parallel workers; issue one per worker B. idempotency key required ↪ retries without one create duplicate jobs C. versions not contiguous ↪ failed writes consume numbers; treat versions as opaque ordered identifiers
- Deprecation policy I. announced 180 days ahead II. warning header every response III. machine-readable changelog notice
```
