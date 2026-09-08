```text
- Scheduler migration ↪ incremental, both systems side by side, no big-bang cutover ▸ Prerequisites a. runtime 4.2 or later b. declarative config format ↪ annotations must run converter first c. workflow namespace provisioned
- Four stages per job I. shadowing ↪ dry-run flag; engine records would-be executions, no side effects; compare one full cycle, timezone edge cases lurk II. takeover ↪ single transaction flips live and disables legacy; refuses on unexplained divergence III. verification ↪ two cycles tagged; regressions beyond 20% page the owning team, not platform IV. cleanup ↪ irreversible legacy deletion; history kept 90 days in archive
- Special cases A. dependency-graph jobs ↪ migrate as dependency-closed group, tool computes closure B. reporting-database jobs ↪ credentials rotated at takeover, vault replaces environment ▸ Duration ↪ ~two weeks calendar per service, mostly mandatory windows
```
