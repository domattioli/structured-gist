# self-explain.md — rule index + consolidation notes

Pointer target from `examples/self-explain.md`. This is context *about* the
example, not the example itself — it doesn't belong in `examples/` (an
example should be the demonstration, not an essay about the demonstration),
so it lives here per the progressive-disclosure pattern the rest of this
skill's `reference/` already uses.

## Rule index

`examples/self-explain.md` renders structured-gist describing its own marker
mechanics, so its standard block naturally demonstrates: the
depth-ladder (dash → ordinal/nominal → deeper ordinal/nominal), the
ordinal-vs-nominal choice, the hook-arrow `↪` leaf (single-depth and
multi-depth), length gradient (terser at shallow depth), and
nest-by-dependency. The three-level version (skim, standard, deep) is archived
at `docs/archive/granularity/self-explain-three-levels.md`.

A few rules describe properties of the skill as a whole rather than
something a self-referential outline about its own marker mechanics would
naturally trigger. Named here instead of forced into the outline:

- **render modes** (`## Render modes`) — `block` = one fenced code block
  (chat/terminal); `inline` = raw markdown lines (GitHub), needs a blank
  line between siblings since the literal glyphs aren't real GFM list items.
- **emphasis taxonomy** (`## Emphasis taxonomy`) — `inline` mode only: bold
  L1 concepts, `code`/*italic*/~~strike~~ sparingly deeper, `<u>` for
  definition anchors.
- **carve-outs** (`## Carve-outs`) — security/irreversible warnings,
  single-fact replies, code/commits/template fields, explicit prose
  requests all skip outlining.
- **caveman coexistence** (`## Caveman coexistence`) — wording compresses
  per whatever caveman level is active; the `↪` leaf is exempt regardless;
  markers stay Latin even under `wenyan-*`.
- **install** (`## Install`) — this repo marketplace skill, pulled via
  `skills.manifest.json` / the sync contract; never vendored.

GitHub-authoring (which surfaces render as `inline` outlines, which
template/footer scaffolding stays verbatim) is intentionally **absent**
from this index as of v0.2.11/ — it was never a rule of this skill. It
was this repo comment-discipline policy defined in terms of ``'s
own template grammar, wearing a structured-gist section; it now lives at
, owned by the skill
that actually defines the templates.

## Consolidation

`examples/self-explain.md` proves most rules on its OWN self-description.
`examples/standard.md` and `examples/caveman-combo.md` are the
pytest-linted fixtures (`tests/test_lint.py`) proving the same properties,
including caveman-wording independence, on a different topic (the
`load_local_skills` hook). `skim.md` and `deep.md` moved to
`docs/archive/granularity/` in v0.6.0.
