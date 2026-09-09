```text
- Discovery gap
    ▸ Root cause
        a. load_local_skills assumed
        `.claude/` layout
            ↪ expected a manifest at
            `.claude/skills.manifest.json` and
            skill dirs under `.claude/skills/`,
            but this repo's skills live
            top-level, in `skills/`
        b. harness scans `~/.claude/skills/`
        once, at startup
            ↪ no hot reload, so a missed skill
            never showed up the rest of the
            session

- The fix
    I. walk repo for `skills/<name>/SKILL.md`
        ↪ maxdepth 2 skips nested
        `tests/fixtures/` dirs
    II. validate frontmatter, then symlink
    into `~/.claude/skills/`
        ↪ skips names already linked rather
        than clobbering
    III. verify each new link
        ↪ confirms it resolves and its
        version parses, so broken links fail
        loudly

- Result
    A. 77 skills load at session start
    B. consumer repos get skill updates
    automatically
        ↪ next bootstrap; no manual resync
        step needed
```
