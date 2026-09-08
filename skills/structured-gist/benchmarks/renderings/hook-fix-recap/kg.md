```text
- Skill loading broken ▸ Installer flaw ↪ install_skills.sh serves only the consumer-repo flow, expecting a manifest DomI lacks and looking under .claude/skills/ ▸ Harness flaw ↪ the harness scans ~/.claude/skills/ once at session start with no hot reload
- Fix I. load_local_skills.sh at SessionStart II. symlinks each skills directory III. idempotent and fails open ↪ never blocks the session; all 77 skills load
```
