# AGENTS.md

Repo = one Claude Code skill: `structured-gist`. Renders explain/recap output as nested outline, not paragraph. This file = agent-facing quick-ref. Source of truth = `skills/structured-gist/SKILL.md`; read it before implementing/extending anything here, this file is a summary not a spec.

## Install + invoke

```
/plugin marketplace add domattioli/structured-gist
/plugin install structured-gist
/structured-gist [skim|standard|deep] [block|responsive]
```

No args → skim + surface-keyed mode (markdown surface → responsive, terminal → block).

Trigger phrases (any → activate): structured-gist, gist mode, gist this, outline this, bullet this, notes mode, structure this, break this down, distill this, give me the gist, make this skimmable, tighten this up, condense this.

## Ladder — 4 roles, fixed, never mix

- concept `-` : top claim, outermost depth only, ~3 words
- attribute `▸` : "parent HAS A ___", named property, NOT a step
- enumerator `I./A.` depth1, `i./a.` depth2+ : ordered/grouped parts, family = absolute depth not first-seen
- explanation `↪` : full prose, usually leaf, never compressed even under text-compression layers

No plain bullets. No `▸`→`▸` self-nest. No mixing families as siblings.

## Render mode — pick by surface

- markdown surface (GitHub, chat) → `responsive`: real GFM list, glyph-free, role = typography (bold attr, literal enum label, plain-prose leaf)
- terminal/plain-text → `block`: fenced, literal glyphs
- `inline` = deprecated, do not use, breaks on GitHub (renders as code block)

## Before you edit

1. Run linter: `python3 skills/structured-gist/tests/lint_outline.py < your_output.md` — 15 rules, stdlib only, zero exceptions.
2. Run tests: `pytest skills/structured-gist/tests/` before any PR.
3. Bump `version:` in SKILL.md frontmatter + add benchmark.md row on any behavior change — no exceptions, unmeasured bumps flagged.
4. `skills/structured-gist/` = source of truth. `plugins/structured-gist/plugin.json` just points at it — don't duplicate skill content there.

## Scope

Structure only. Never touches wording/compression (that's a separate, optional layer). Never invokes itself recursively. Independence = the test: turning text-compression on/off must never change the tree shape.
