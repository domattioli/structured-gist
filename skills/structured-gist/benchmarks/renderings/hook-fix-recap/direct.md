```text
- Skill loading broken ▸ Causes a. install_skills.sh consumer-flow only ↪ expects manifest DomI lacks, looks under .claude/skills/ b. harness scans once at start ↪ ~/.claude/skills/ read at session start, no hot reload
- Fix ↪ load_local_skills.sh at SessionStart ▸ Properties a. symlinks each skills dir b. idempotent c. fails open ▸ Result ↪ all 77 skills load
```
