# Example — `caveman ultra` + `/structured-gist standard`

Orthogonal compose: same ladder structure, ultra-terse wording (caveman's doing, not structured-gist'), markers stay Latin.

Source: "Explain why the load_local_skills hook was needed."

```
- Discovery gap
    I. install_skills.sh consumer-only
        ↪ lacks .claude/manifest this repo has
    II. harness scans ~/.claude/skills/ @ start only
        ↪ registry built once; no hot reload

- Fix
    A. load_local_skills.sh @ SessionStart
        a. symlinks skills/<name>/
        b. idempotent, fail-open
    B. scope: ~.claude/skills/

- Result
    I. 77 skills load @ start
```

Structure identical to `standard`; only the wording compressed. Under `wenyan-*` the node text becomes 文言文 — markers (`-` `I.` `A.` `a.` `↪`) stay Latin.
