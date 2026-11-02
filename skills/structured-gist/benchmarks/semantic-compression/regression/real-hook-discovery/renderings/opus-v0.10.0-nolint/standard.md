```text
- Skill discovery bug
    ▸ Symptom
        ↪ newly-added skills never showed up for consumer
        repos
    ▸ Cause
        a. expected paths
            ↪ the install flow, `load_local_skills`, looked for
            a manifest at `.claude/skills.manifest.json` and
            skill directories under `.claude/skills/`
        b. actual location
            ↪ this repo keeps its skills at the top level, in
            `skills/`, not under a `.claude/` prefix at all
    ▸ Effect
        i. nothing symlinked
            ↪ the paths never matched, so nothing ever got
            symlinked into `~/.claude/skills/`
        ii. skill never appeared
            ↪ the harness only scans `~/.claude/skills/` once
            at startup, with no hot reload, so a skill that
            missed the initial scan never appeared for the
            rest of the session, no matter how long you waited
- Fix
    I. walk repo
        ↪ finds every `skills/<name>/SKILL.md`, capped at
        `maxdepth 2` so fixture directories nested deeper
        under `tests/fixtures/` are not mistaken for skills
    II. validate frontmatter
    III. symlink skill directory
        ↪ links into `~/.claude/skills/`, skipping any name
        already linked rather than clobbering it
    IV. verify new links
        ↪ confirms each symlink resolves and the target's
        version field parses, so a broken link fails loudly
        instead of silently
- Outcome
    A. 77 skills load
        ↪ all 77 skills load at session start
    B. automatic updates
        ↪ any consumer repo picks up skill updates the next
        time it bootstraps a session, with no manual resync
        step required
```
