```text
- Discovery gap
    A. load_local_skills assumed `.claude/`
    layout
    B. repo keeps skills top-level, in `skills/`
    C. harness scans once, no hot reload

- The fix
    I. walk, validate, symlink into
    `~/.claude/skills/`
    II. verify each new link

- Result
    A. 77 skills load at session start
    B. consumer repos auto-update
```
