```text
- Missing skills
    ▸ Symptom
        ↪ newly-added skills never showed up for consumer
        repos
    ▸ Cause
        a. installer `load_local_skills` path mismatch
            ↪ it looked for a manifest at
            `.claude/skills.manifest.json` and skill
            directories under `.claude/skills/`, but this
            repo keeps its skills at the top level, in
            `skills/`
        b. nothing symlinked into `~/.claude/skills/`
        c. no hot reload
            ↪ the harness only scans `~/.claude/skills/` once
            at startup, so a skill that missed the initial
            scan never appeared for the rest of the session
- Fix
    I. walk repo for `skills/<name>/SKILL.md`
        ↪ the search is capped at `maxdepth 2` so fixture
        directories nested deeper under `tests/fixtures/`
        are not mistaken for real skills
    II. validate each match's frontmatter
    III. symlink into `~/.claude/skills/`
        ↪ any name already linked is skipped rather than
        clobbered
    IV. verify every new link
        ↪ confirms the symlink resolves and the target's
        version field parses, so a broken link fails
        loudly instead of silently
- Outcome
    A. all 77 skills load
    B. consumer repos auto-update
        ↪ updates are picked up the next time a session
        bootstraps, with no manual resync step required
```
