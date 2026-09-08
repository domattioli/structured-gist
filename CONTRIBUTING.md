# Contributing

## Reporting a bug

Open an issue with a minimal repro: the input outline (or prompt) and the expected vs. actual linter/render output. "The linter should catch X but doesn't" is more useful with the actual fixture text than a description of it.

## Proposing a change

Open an issue first for anything that changes behavior — a new rule, a render-mode change, a new trigger phrase. Small fixes (typos, a broken link, a clearer error message) can go straight to a PR.

## Development

- `skills/structured-gist/SKILL.md` is the complete specification. Read it before changing linter behavior.
- Linter: `python3 skills/structured-gist/tests/lint_outline.py < your_output.md` (15 rules, stdlib only, zero dependencies).
- Tests: `pytest skills/structured-gist/tests/`. Run before every PR.
- Any rule change needs a fixture pair (`good_*.md` / `bad_*.md`) and a test asserting both.

## Good patterns

- One rule, one PR. A linter-rule change and a docs fix are two PRs, not one.
- New rules ship with both a passing and a failing fixture — a rule nobody can prove fires (or doesn't) is unverifiable.
- Bump `version:` in `SKILL.md` frontmatter and add a row to `skills/structured-gist/tests/benchmark.md` for any behavior change, with a real measured number, not a description.
- Keep the `↪` explanation node exempt from any wording-compression change you're testing elsewhere — it's supposed to stay full prose regardless of what else changes.

## Anti-patterns

- Don't add a "mode" for a one-off case. If a rule needs an exception, name the exception in the rule, don't fork the renderer.
- Don't relax a linter rule to make a specific bad example pass. Fix the example, or open an issue arguing the rule itself is wrong.
- Don't change render-mode defaults without checking both `block` and `responsive` output — a fix for one surface has broken the other before.
- Don't submit a rule change without a fixture. "I tested it manually" isn't reproducible by the next contributor.

## Code style

Shell and Python only, stdlib preference throughout — the linter has zero runtime dependencies by design. Match the existing style in the file you're editing rather than introducing a new one.
