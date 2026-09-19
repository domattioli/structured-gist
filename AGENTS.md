# AGENTS.md

Repo = one Claude Code skill: `structured-gist`. Renders explain/recap output as nested outline, not paragraph. This file = agent-facing quick-ref. Source of truth = `skills/structured-gist/SKILL.md`; read it before implementing/extending anything here, this file is a summary not a spec.

## Install + invoke

```
/plugin marketplace add domattioli/structured-gist
/plugin install structured-gist
/structured-gist [skim|standard|deep] [block|responsive]
```

No args → skim + block, on every surface. `responsive` = explicit opt-in, never auto-picked by surface.

Presets (opt-in, branches optional — omit what the source doesn't support): `/structured-gist summary` (session recap), `/structured-gist report` alias `findings` (finding-first).

Trigger phrases (any → activate): structured-gist, gist mode, gist this, outline this, bullet this, notes mode, structure this, break this down, distill this, give me the gist, make this skimmable, tighten this up, condense this.

## Ladder — 4 roles, fixed, never mix

- concept `-` : top claim, outermost depth only, ~3 words
- attribute `▸` : "parent HAS A ___", named property, NOT a step
- enumerator `I./A.` depth1, `i./a.` depth2+ : ordered/grouped parts, family = absolute depth not first-seen
- explanation `↪` : full prose, usually leaf, never compressed even under text-compression layers

No plain bullets. No `▸`→`▸` self-nest. No mixing families as siblings.

## Render mode — block default, responsive opt-in

- `block` = default everywhere: fenced, literal glyphs, 4-space rungs, hard-wrap at 64 cols (R11)
- `responsive` = opt-in for a markdown-rendering surface (GitHub, chat): real GFM list, glyph-free, role = typography (bold attr, literal enum label, plain-prose leaf). Never carry block glyphs or 4-space rungs into it.
- `inline` = deprecated, do not use, breaks on GitHub (renders as code block)

## Before you edit

1. Run linter: `python3 skills/structured-gist/tests/lint_outline.py < your_output.md` — 15 rules, stdlib only, zero exceptions.
2. Run tests: `pytest skills/structured-gist/tests/` before any PR.
3. Bump `version:` in SKILL.md frontmatter + add benchmark.md row on any behavior change — no exceptions, unmeasured bumps flagged.
4. `skills/structured-gist/` = source of truth. `plugins/structured-gist/.claude-plugin/plugin.json` + the `plugins/structured-gist/skills/structured-gist` symlink just point at it — don't duplicate skill content there.

5. Before a release: `bash skills/structured-gist/scripts/validate_plugin.sh` — validates the plugin through the `skills/` symlink (the stock validator skips it) + checks SKILL.md and plugin.json versions agree. Skips cleanly without the `claude` CLI.

## Scope

Structure only. Never touches wording/compression (that's a separate, optional layer). Never invokes itself recursively. Independence = the test: turning text-compression on/off must never change the tree shape.
