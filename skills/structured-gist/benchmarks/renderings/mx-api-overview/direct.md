```text
- Public API ▸ Resources a. projects ↪ billing and permission boundary; all else belongs to exactly one b. datasets ↪ versioned tabular data; writes create immutable versions c. jobs ↪ async operations: imports, exports, transformations ▸ Auth ↪ scoped tokens: project, role, expiry a. reader lists and downloads b. writer adds versions, submits jobs c. admin manages tokens, deletes d. ninety-day expiry, code 4012 warning week
- Integrator traps A. rate limits per token ↪ shared token throttles parallel workers; one token per worker B. idempotency key required ↪ retries without one duplicate jobs C. version numbers not contiguous ↪ failed writes consume numbers; treat as opaque ordered identifiers
- Deprecation policy I. announced 180 days before removal II. warning header on every response III. machine-readable changelog notice day one
```
