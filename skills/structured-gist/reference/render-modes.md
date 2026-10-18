# Render modes — full spec

Pointer target from `SKILL.md` `## Render modes`. Detail that a session only
needs when actually hand-wrapping a long block-mode line or explaining the
`text`-vs-`markdown` fence choice — not on every load.

## Why `text`, never `markdown` or bare

`markdown` makes the renderer syntax-**highlight** the outline (coloring `-`,
`**`, `#`); a bare fence lets some renderers auto-detect a language and
highlight anyway. `text` = plaintext = no highlighting. Tag the fence
` ```text ` always.

## Cost of each mode

- **`block`** — literal text, so inline `**bold**`, `code`, *italic*, and
  clickable `file:line` refs do NOT render. **Default mode on all surfaces.**
  Use for monospace/terminal output and committed `.md` fences, where GitHub's
  markdown rendering is irrelevant and faithful spacing is the win. R11 (below)
  applies — the linter owns line width since no renderer will wrap the fence
  for you.
- **`inline`** — **DEPRECATED (v0.3.8).** The literal glyphs (`I.` `A.` `i.` `↪`)
  aren't real GFM list items, so inline indented each rung 4 spaces to fake the
  nesting — but GFM reads a line indented ≥4 spaces past a list item's content
  column as an **indented code block**, so on GitHub depth-2+ rungs became
  wide non-wrapping code boxes and depth-1 `▸` lines became emoji-led
  paragraphs. Use `responsive` for GitHub instead (below); `inline` is kept
  only so pre-v0.3.8 committed outlines still lint.
- **`responsive`** (v0.3.7, glyph-free since v0.3.9) — a real GFM nested
  list, 2 spaces per rung, with no ladder glyph in the content: attribute →
  `- **Purpose**`, enumerator → `- a. tool execution`, explanation → a plain
  prose item. Every node is a real list item, so the renderer wraps each line
  to its own box width with a hanging indent and no code blocks. Correct on
  **any** markdown-rendering surface — GitHub issue/PR/comment bodies AND
  chat-app replies (Claude Code app/web, or any surface with a variable
  viewport). Opt-in only — `block` is the default on all surfaces; pick
  `responsive` explicitly when a real GFM nested list is wanted instead. No
  fence, no linter-side width budget, no continuation-line grammar to
  hand-author — R11 does not apply. Full spec + worked example:
  `## Responsive mode` below.

## Responsive mode

**Problem R11 (block mode) didn't solve.** v0.3.6's 64-char hard-wrap fixed
narrow (phone) viewports for MONOSPACE surfaces, but in a chat-app reply it
under-fills a wide desktop viewport — the box is capped at 64 chars even when
the actual pane is much wider (user, 2026-07-22: "the box is less wide").
Root cause: the linter doesn't know the reader's box width; only the
renderer does. `responsive` mode stops guessing and delegates.

**Rule (glyph-free since v0.3.9).** Every node is a genuine GFM unordered
list item; the renderer's own bullets + nesting carry the structure, so
**no ladder glyph appears in the content** — carrying `▸`/`↪` inside a real
list item produced `• ▸` double markers on any bullet-drawing renderer
(user screenshot, 2026-07-24 — the render-layer version of the R10
double-marker defect). Role moves to typography:
- **attribute** → `- **Purpose**` — bold, ≤4 words (bold already being the
  markdown-surface signal for the scannable spine)
- **enumerator** → literal label content, unchanged — `- a. tool execution`,
  `- I. assemble context` (a letter/roman label reads as enumeration, not a
  second bullet; real ordered-list syntax would renumber `1.`/`2.`/… and
  collapse the ordinal/nominal distinction)
- **explanation leaf** → a plain prose item with no `↪` — its role is
  evident as the prose leaf under a terse parent
- a depth-0 **concept** is a plain item — the list bullet `-` IS the
  concept marker (`- Agentic harness`)
- nesting is real GFM list indentation — **2 spaces per depth rung** (the
  GFM-standard indent for a `- ` bullet), not the 4-space rung `block`/
  `inline` use
- no fence — a fenced block always renders as literal monospace text, which
  is exactly what `responsive` is trying to avoid

**Worked example** — the `## Worked example` "Agentic harness" tree from
`SKILL.md`, same content, three ways:

Block (` ```text `, 4-space rungs, no real list — the linter enforces the
line-width budget):

```text
- Agentic harness
    ▸ Purpose
        ↪ a raw text-predictor gains the ability to act
    ▸ Capabilities
        a. tool execution
        b. control loop
```

Responsive (real GFM list, 2-space rungs, glyph-free, no fence — the
renderer enforces line width and draws the bullets):

```
- Agentic harness
  - **Purpose**
    - a raw text-predictor gains the ability to act
  - **Capabilities**
    - a. tool execution
    - b. control loop
```

Same ladder, same nesting depth, same content. The differences are the
wrapper (`block`'s fence + 4-space rungs vs. real list syntax + 2-space
rungs) and the role signal (`block`'s literal glyphs vs. typography — bold
attribute, literal enumerator label, plain prose leaf).

**WRONG — do not do this (#484).** Carrying `block`'s literal `▸`/`↪`
glyphs AND its 4-space rungs into a `responsive`-mode reply mixes two
containers: the glyphs double up with the renderer's own bullet (`• ▸`,
the render-layer R10 defect), and the 4-space rungs read as GFM indented
code blocks past depth 1. This exact shape shipped twice in one session
(issue #484 repro):

```
- **S2-rev mission**
    ▸ Goal
        ↪ find a state representation that lets RL agent complete meshing on all 7 domains, evidence-only, no cherry-picking
    ▸ Method
        a. Stage A
            ↪ cheap 2-domain CPU screen, filters candidates
        b. Stage B
            ↪ full 7-domain eval, only for Stage A survivors
```

**RIGHT — glyph-free, 2-space real-list nesting, same tree:**

```
- **S2-rev mission**
  - **Goal**
    - find a state representation that lets RL agent complete meshing on all 7 domains, evidence-only, no cherry-picking
  - **Method**
    - a. Stage A
      - cheap 2-domain CPU screen, filters candidates
    - b. Stage B
      - full 7-domain eval, only for Stage A survivors
```

Rule of thumb: if you are about to type `▸` or `↪` in a `responsive`-mode
reply, stop — those glyphs belong only to `block` mode's fenced text.

A long `↪` leaf in `responsive` mode can run to any length
on ONE physical line — the renderer wraps it visually; the linter does not
hard-wrap the source, and R11 never fires on it (`lint_outline.py` gates R11
to `is_block_mode` only; `responsive` lines are reclassified before R1–R10
run but always report `is_block_mode=False`, exactly like `inline`).

**Linter detection.** The linter checks both responsive forms: the v0.3.7
glyph form and, since v0.4.4, the v0.3.9 glyph-free form. In the
glyph-free form, an item at depth ≥ 1 whose whole content is one bold span
is read as an attribute, and a plain item at depth ≥ 1 is read as an
explanation leaf. A non-fenced outline is classified `responsive`
(instead of `inline`) only when at least one `- ` list item's content
itself starts with a non-dash ladder glyph (`▸`/`↪`/`→`/an ordinal or
nominal enumerator), or is a bold-only item at depth ≥ 1 — shapes `inline`
mode never produces, since `inline`
emits the bare glyph with no leading list dash past depth 0. This keeps
detection conservative: a plain `inline` outline (bare glyphs, no `- `
prefix on nested nodes) is never misclassified. Detected `responsive` lines
are rewritten to their `block`-equivalent form (list-item's own indent // 2,
re-indented at 4 spaces/rung, list bullet dropped except where it doubles as
the depth-0 concept marker) before R1–R10 run, so every other rule —
including R8 (no `▸` under `▸`) — validates identically regardless of which
of the three modes the source outline used.

## Block-mode line wrapping

A fenced line that overflows a narrow pane (phone portrait) soft-wraps back
to column 0 — the renderer's call, no markdown hang-indent hook available.
Symptom (user screenshot, 2026-07-22): continuation fragments like
"notes flagship" / "existing " landing flush-left, destroying the
indent ladder and skimmability.

**Rule (R11, v0.3.6 — user spec, verbatim): "new lines are ok but they
should have precisely identical indenting as the first line."** Keep each
block line within the **resolved budget (default 64)** including indent
(64 fits typical phone-portrait monospace). When a node's content — any node type, `↪` leaves included —
would overflow, hand-wrap it yourself:

- the marker line stays as-is, up to the resolved budget (default 64)
- every continuation line's leading whitespace is **IDENTICAL** to the
  marker line's own indent — same column, no deeper hang, no shallower
- **no marker glyph** on a continuation line (it is not a new node)

**Width knob (v0.5.0b2; terminal hint since v0.8.0).** The R11 line-width
budget is configurable for wider displays. The model resolves it in this
order, first match wins:

1. an explicit `width N` or `width auto` in the activation;
2. a width the consumer repo's AGENTS.md pins for that surface;
3. for terminal replies only, the host's terminal-width hint
   (`term_cols=N`), resolved as `auto`;
4. the default, 64 chars.

`auto` resolves to clamp(N − 8, 32, 120), where N is the terminal width in
columns. The 8 columns leave room for the host's gutter, the floor of 32
keeps a narrow pane usable, and the cap of 120 stops long `↪` prose from
filling a very wide pane. An explicit `width N` is used as given, with no
cap. The hint describes the terminal that shows the reply, so it applies to
terminal replies only. Files, committed fences, and tool-posted bodies
(issue, PR, and comment bodies) skip the hint and use 64 unless a width is
set explicitly or pinned; `test_lint.py` checks the SKILL.md and example
fences at 64.

The linter (`lint_outline.py --width`) follows the same rules for `N` and
`auto`, reading terminal columns from `COLUMNS` or the real tty; when
neither gives a width, `auto` falls back to 64. With no `--width`, the
linter reads the environment variable `STRUCTURED_GIST_WIDTH`, then uses
64. That variable is the linter's default knob; the model does not read
it. Lint a terminal reply with `--width <resolved N>`, the budget the
reply was rendered at; a plain run checks against 64 and flags wider
lines.

**Surface guide (advice, not a rule).**

| surface | suggested mode and width |
|---|---|
| terminal (CLI) reply | `block`, hint width per the order above |
| app or web chat reply | `block` at 64, or opt-in `responsive` |
| GitHub body or committed `.md` | `block` at 64, or explicit `responsive` |
| phone or narrow chat | `block` at 64, or `responsive` |

```
        ↪ this leaf runs long enough that a phone-width pane
        would soft-wrap it, so it is hand-wrapped here with
        continuation lines at the SAME indent as the marker.
```

Wrong (hanging indent — the pre-v0.3.6 shape, now an R11 violation):

```
        ↪ this leaf runs long enough that a phone-width pane
          would soft-wrap it — continuation drifted one rung
          deeper than the marker line above it
```

The linter (`lint_outline.py` R11) folds a markerless continuation line into
its owning node's text either way (structure), but separately flags (i) any
physical line over the resolved budget (default 64) and (ii) any continuation line whose
indent does not exactly match its marker line's indent — both checks fire
in `block` mode only (fenced content); `inline` mode is GitHub-rendered
markdown and wraps itself, so R11 does not apply there. Prefer splitting
one long node into two terse nodes over wrapping when the content allows it.

## Test-tooling note

The `examples/*.md` outlines use a **bare** fence (not ` ```text `) so the
line-count smoke check (`^```$`) stays simple — a test-tooling concession
only. **Emitted** block output still opens the fence with ` ```text `.
