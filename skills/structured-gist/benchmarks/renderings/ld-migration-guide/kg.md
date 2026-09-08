```text
- Scheduler migration ▸ Prerequisites a. runtime 4.2 or later b. declarative config format c. provisioned workflow namespace ↪ incremental, both systems side by side, no big-bang cutover, no maintenance window
- Four stages I. shadowing ↪ dry-run flag records would-be executions with no side effects; compare a full cycle since timezone edge cases appear at boundaries II. takeover ↪ one transaction enables live and disables legacy, refusing on unexplained divergence III. verification ↪ two tagged cycles compared against baseline; regressions beyond twenty percent page the owning team IV. cleanup ↪ the only irreversible step; legacy history archived ninety days
- Special cases A. dependency-graph jobs ↪ migrated as a dependency-closed group computed from the legacy graph B. reporting-database jobs ↪ credentials rotate at takeover, vault-injected replacing environment-scoped
```
