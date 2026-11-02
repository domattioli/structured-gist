```text
- Skill discovery bug
    ▸ Symptom
        ↪ Newly-added skills never showed up for consumer repos.
    ▸ Cause
        a. install flow looked in wrong place
            ↪ `load_local_skills` looked for a manifest at
            `.claude/skills.manifest.json` and expected skill
            directories under `.claude/skills/`.
        b. repo layout differs
            ↪ This repo keeps its skills at the top level, in
            `skills/`, with no `.claude/` prefix at all.
        c. no hot reload
            ↪ The paths never matched, so nothing was symlinked
            into `~/.claude/skills/`. The harness scans that
            directory only once at startup, so a skill that
            missed the initial scan never appeared for the rest
            of the session, however long you waited.
    ▸ Fix
        i. walk repo for skills
            ↪ It finds every `skills/<name>/SKILL.md`, capping
            the search at `maxdepth 2` so fixture directories
            nested deeper under `tests/fixtures/` are not
            mistaken for real skills.
        ii. validate frontmatter first
        iii. symlink skill directory
            ↪ The script links it into `~/.claude/skills/`,
            skipping any name already linked rather than
            clobbering it.
        iv. verify created links
            ↪ As a last step it walks every link it just
            created and confirms the symlink resolves and the
            target's version field parses, so a broken link
            fails loudly instead of silently.
    ▸ Result
        a. all 77 skills load at startup
        b. consumer repos update automatically
        c. no manual resync needed
```
