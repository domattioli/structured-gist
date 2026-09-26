# structured-gist agent instructions

This repository contains the `structured-gist` Claude Code skill. It renders
explanations and process recaps as nested outlines. The source of truth is
`skills/structured-gist/SKILL.md`. Read it before changing the skill.

## Repository layout

- `skills/structured-gist/` contains the skill specification, references,
  examples, render code, scripts, benchmarks, and tests.
- `plugins/structured-gist/` contains the plugin manifest. Its skill entry is a
  symlink to `skills/structured-gist/`; do not duplicate the skill there.
- `.claude-plugin/marketplace.json` defines the repository marketplace.
- `docs/` contains architecture decisions and investigations.
- `specs/` contains project specifications, plans, and supporting artifacts.

## Install and invoke

```text
/plugin marketplace add domattioli/structured-gist
/plugin install structured-gist
/structured-gist [skim|standard|deep] [block [width N|auto]|responsive]
```

No arguments select `skim` and `block`. `responsive` is always an explicit
choice. The `summary` preset produces a session recap. The `report` preset,
also named `findings`, produces a finding-first outline. Preset branches are
optional and must be omitted when the source does not support them.

## Format contract

The four roles are fixed and must not be mixed:

- Concept: `-`, only at the outermost depth, normally no more than three words.
- Attribute: `▸`, a named property that reads as "the parent has a ...".
- Enumerator: `I.` or `A.` at depth 1 and `i.` or `a.` at deeper levels.
- Explanation: `↪`, full prose that is usually a leaf and is never compressed.

Do not use plain bullets. Do not nest `▸` directly below `▸`. Sibling nodes use
one marker family. Enumerator case follows absolute depth, not the first depth
where an enumerator appears.

`block` is the default on every surface. It uses one fenced `text` block,
literal glyphs, four-space depth increments, and a default 64-column line
budget. `responsive` is an explicit option for Markdown surfaces. It uses real
GitHub Flavored Markdown lists, two-space nesting, bold attributes, literal
enumerator labels, plain-prose explanation leaves, and no block-mode glyphs.
The legacy `inline` mode is deprecated and must not be used for new output.

The skill changes structure only. It does not change wording or invoke a text
compression layer. Turning text compression on or off must not change the
tree shape.

## Development and release checks

Run these before a pull request:

```bash
pytest skills/structured-gist/tests/
bash skills/structured-gist/tests/smoke.sh
```

Lint a generated outline with:

```bash
python3 skills/structured-gist/tests/lint_outline.py < your_output.md
```

Any behavior change requires a `version:` bump in `SKILL.md` and a row in
`skills/structured-gist/tests/benchmark.md`. Before a release, run:

```bash
bash skills/structured-gist/scripts/validate_plugin.sh
```

That script validates the marketplace and plugin layouts and checks that the
skill and plugin versions agree when the Claude CLI is available.

## Branch workflow

The default working branch is `development`. Releases use a pull request from
`development` to `main`. Never push directly to `main` and never force-push.

## Governance
This repo is a downstream consumer of `domattioli/DomI`.
Universal git, coding dispatch, secrets, session lifecycle, and communication rules live in DomI `.claude/policies/`.
Spec-kit artifacts for this repo live in DomI `specs/consumers/structured-gist/`, never in a local `.specify/` directory.
