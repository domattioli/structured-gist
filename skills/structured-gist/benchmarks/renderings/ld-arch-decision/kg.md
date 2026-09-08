```text
- Attachment storage ▸ Requirements a. files to 100 megabytes b. region-pinned regulated tenants c. p95 download under two seconds d. about 40 terabytes first year ↪ object-store bytes with relational metadata chosen over in-database bytes and a dedicated document store
- Rejected options A. bytes in the database ↪ fifteenfold storage growth degrades backup and restore; large reads contend with transactional queries B. dedicated document store ↪ a third system to operate with no new capability and zero team production experience
- Selected design I. two-phase upload ↪ pending metadata row plus signed URL, then a confirmation flips the row active II. nightly reconciliation ↪ deletes day-old pending orphans and flags missing objects as bugs III. per-bucket region pinning IV. signed URLs serve downloads ↪ bytes bypass the application servers; 1.4 seconds p95 measured from the slowest region
- Accepted costs A. tenant deletion spans two systems B. restores can resurrect metadata ↪ the reconciliation missing-object flag detects it; the restore runbook runs it immediately
```
