```text
- Skill discovery bug
    ▸ Symptom
        ↪ Newly-added skills never showed up for consumer repos.
    ▸ Cause
        ↪ `load_local_skills` expected a manifest at
        `.claude/skills.manifest.json` and skill directories
        under `.claude/skills/`, but this repo keeps skills at
        top-level `skills/`, so the paths never matched.
    ▸ Consequence
        i. nothing symlinked into `~/.claude/skills/`
        ii. harness scans only at startup
            ↪ There is no hot reload, so a skill that missed the
            initial scan never appeared for the rest of the
            session, however long you waited.
- Fix
    ▸ Steps
        i. find every `skills/<name>/SKILL.md`
            ↪ The search is capped at `maxdepth 2` so fixture
            directories nested deeper under `tests/fixtures/`
            are not mistaken for real skills.
        ii. validate each frontmatter
        iii. symlink into `~/.claude/skills/`
            ↪ Any name already linked is skipped rather than
            clobbered.
        iv. verify each new link
            ↪ Confirms the symlink resolves and the target's
            version field parses, so a broken link fails loudly
            instead of silently.
- Result
    ▸ Outcome
        a. all 77 skills load at session start
        b. consumer repos pick up updates
            ↪ This happens automatically the next time a repo
            bootstraps a session, with no manual resync step.
```
