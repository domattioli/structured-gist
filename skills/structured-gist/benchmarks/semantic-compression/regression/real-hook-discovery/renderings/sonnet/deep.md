```text
- Discovery gap
    ▸ Symptom
        ↪ newly added skills never showed up for
        consumer repos
    ▸ Root cause
        a. load_local_skills assumed `.claude/`
        layout
            ↪ expected a manifest at
            `.claude/skills.manifest.json` and
            skill dirs under `.claude/skills/`
        b. repo keeps skills top-level, in
        `skills/`
            ↪ paths never matched, so nothing got
            symlinked into `~/.claude/skills/`
        c. harness scans `~/.claude/skills/` once,
        at startup
            ↪ no hot reload, so a skill missing the
            initial scan never appeared the rest of
            the session

- The fix
    I. walk repo for `skills/<name>/SKILL.md`
        ↪ maxdepth 2 so nested `tests/fixtures/`
        dirs aren't mistaken for real skills
    II. validate frontmatter of each match
    III. symlink skill dir into
    `~/.claude/skills/`
        ↪ skips names already linked rather than
        clobbering them
    IV. verify each new link
        a. symlink resolves
        b. version field parses
            ↪ so a broken link fails loudly
            instead of silently

- Result
    A. 77 skills load at session start
    B. consumer repos get skill updates
        ↪ automatically, next time it bootstraps a
        session; no manual resync step needed
```
