```text
- Attachment storage decision ↪ object store bytes + relational metadata chosen ▸ Requirements a. files to 100 MB b. region-pinned regulated tenants c. p95 download under two seconds d. ~40 TB first year
- Options A. bytes in database ↪ rejected: 15x storage footprint, degraded backups, pool contention B. dedicated document store ↪ rejected: third system to operate, no new capability, zero team experience C. object store + metadata rows ↪ selected
- Selected design I. two-phase upload i. pending row, signed URL issued ii. confirmation flips row active II. nightly reconciliation ↪ deletes 24h-pending orphans, flags missing objects as bugs III. region pinning via per-bucket config IV. signed URLs serve downloads directly ↪ 1.4 s p95 measured, slowest region ▸ Accepted costs a. tenant deletion spans two systems b. restores can resurrect deleted metadata ↪ reconciliation flag is the detector, runbook runs it post-restore
```
