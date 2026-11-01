---
name: structured-gist
version: "0.10.0"
benchmark: fact_retention_delta
description: 'Rewrite explanatory or process-recap prose as a nested lecture-note outline on a fixed marker ladder (concept → attribute → enumerator → `↪` explanation; no plain bullets). Use for agent "what I did and why" recaps, concept / trade-off / cause-chain explanations, session handoffs (`/structured-gist summary`), and finding-first reports (`/structured-gist report`, alias `findings`). Triggers: "structured-gist", "sg", "gist this", "outline this", "notes mode", "sg report", "sg summary", or any request to restructure explanatory text into a skimmable hierarchy. Do NOT use for code, commit messages, bot-template fields or footers, single-fact answers, security or irreversible-action warnings, or when plain prose is requested. Changes structure only, never wording (independent of caveman).'
---

# structured-gist — hierarchical lecture-note output

Replace paragraph printouts (esp. "what I did + my reasoning" recaps) with nested, skimmable outline. Concept, attribute, enumerator nodes = terse structure; `↪` = prose explanation. Marker type = meaning, never random. Structure only; wording untouched (independent of caveman). ~2-minute read; detail in `reference/`.

## Activation

On-demand: `/structured-gist [block [width N|auto]|responsive]`. Granularity: `standard` only. No mode → `block` (default, all surfaces). `responsive` = explicit opt-in for GitHub issue/PR/comment bodies or chat-app replies needing real GFM nested list.

`width` sets block-mode R11 line budget. Resolution, first match wins:
1. explicit `width N` or `width auto`
2. width the consumer repo's AGENTS.md pins for that surface
3. terminal replies only: host terminal-width hint (`term_cols=N`), resolved as `auto`
4. 64

`auto` = clamp(N−8, 32, 120), N = terminal width in columns. Explicit `width N` used as given, no cap. Files, committed fences, tool-posted bodies (issue, PR, comment) skip the hint → 64 unless width set explicitly or pinned. `STRUCTURED_GIST_WIDTH` = linter's default knob; model does not read it. See `## Render modes`.

Lexicon triggers: "structured-gist", "sg", "in structured-gist", "gist mode", "gist this", "outline this", "notes mode", "structure this", "distill this" (+ optional mode word).
Elevatable: repository instructions may mandate as session default (+ default mode), like caveman.
Off: "stop structured-gist" / explicit prose request.

**Session-summary preset: `/structured-gist summary` (alias `session-summary`).** One-call handoff-shaped recap; caller gives no structure. Does NOT call `handoff` skill (fuller retro). Sections = `-` concepts; contents = `▸` / enumerators / `↪`:

```text
- Session summary
    ▸ Changed
        a. <area> — <what changed>
    ▸ Decisions
        ↪ <decision + one-line rationale>
    ▸ Next
        i. <ordered next step>
    ▸ State
        a. branch <name>
        b. PR <#/status>
    ▸ Open questions
        ↪ <question still unresolved>
```

(Enumerators under `▸` sit at depth 2 → lowercase family `a.`/`i.`, per depth-keyed ladder below; `▸` occupies depth 1.)

**Preset-omission contract (every preset, summary included).** Branch names optional, not required slots; omit any the source does not support. Preset never changes marker ladder or adds a role.

**Report preset: `/structured-gist report` (alias `findings`).** Finding-first. One top concept per supported finding; findings = peers, never one packaging root. Never invent a finding. Optional branches — Question, Method, Observed, Inferred, Next — only when source-supported. No generic Intro/Background/Conclusion heading; context nests under its finding. Under Method: ordered steps → lowercase ordinal (`i.`/`ii.`); unordered components → lowercase nominal (`a.`/`b.`). Method itself = named `▸` branch, never ordinal node. Granularity, render mode apply unchanged; no new marker roles.

```text
- <finding>
    ▸ Method
        ↪ <how it was checked>
    ▸ Observed
        a. <what was seen>
    ▸ Next
        ↪ <follow-up action>
```

**Activation is verify-don't-assume (same bar as caveman).** Attempt real Skill call (`/structured-gist`, or mode in effect); success → say so. On `Unknown skill` (skill not loaded at container start) emit exactly one line — `structured-gist NOT loaded → emulating from SKILL.md` — then apply outline rules manually from this file. NEVER claim "structured-gist active" without successful Skill call. Missing skill never blocks the turn — emulate, continue.

Optional advisory Stop-hook activation nudge for consumer repos: `reference/activation-hooks.md`.

## When — primary target

Default-render as outline when active:
- agent **process/recap prose** — "what I did and why" (main case)
- explanations — concept / system / trade-off / cause-chain

NOT only on explicit "explain X". NOT on carve-outs below.

## Marker taxonomy

**Consistent depth-ladder — marker type conveys meaning, never random.** One rung per nesting level; never skip. Rung = depth, not role: concept may parent enumerator directly. **No plain bullet** — every sub-item enumerates.

Role ladder, outer to inner: **Concept → Attribute → Enumerator → Explanation.**

| role | marker | answers | word budget |
|---|---|---|---|
| **concept** | `-` (L1 only) | "what is this?" — a top concept, claim, or outcome | ~≤3 words |
| **attribute** | `▸` | "what does the parent *have*?" — a named property of the parent | ≤4 words |
| **enumerator** | `I. II.` / `A. B.` at **depth 1** · `i. ii.` / `a. b.` at **depth ≥2** | "the parent is *composed of* these ordered/grouped parts" | ≤6 words deep tiers |
| **explanation** | `↪` (hook arrow) | "what needs explaining or qualifying about the parent?" (e.g. why / how) — the one LONG prose sentence | no cap |

Who/what/where/when/why/how/whether = content prompts, not marker selectors; "why" alone does not pick `↪`. Match by role: top claim → concept, named property → attribute, ordered or grouped part → enumerator, explanation → `↪`.

**Attribute vs. enumerator.** Child reads "the parent *has a* ___" (purpose, component, constraint, property) → **attribute** (`▸`). Enumerators = genuinely ordered or grouped *parts/steps/evidence*. Flattening to sibling `-` or mislabeling as enumerator loses the relation. Example: `▸ Marker ladder` = attribute *of* structured-gist, not peer concept, not step.

**Ordinal vs nominal** picks enumerator family by content:
- **ordinal** (roman: `I.`/`i.`) when ORDER matters — sequence, steps, ranking.
- **nominal** (letter: `A.`/`a.`) when items = distinct GROUPED peers, order-agnostic.

Attributes inherently nominal (property has name, not position); no ordinal `▸` variant.

**Advisory attribute-name lexicon (not linter-enforced).** Common names: Purpose, Mechanism, Actor, Location, Timing, Certainty. Scope = boundary, Trigger = initiating condition; neither is catch-all "where"/"when". "Whether" = proposition to resolve; confidence degree = Certainty. Prefer source's own names; omit unsupported ones.

**`▸` occupies a depth rung like any marker.** Enumerators directly under concept sit at depth 1 (uppercase `I.`/`A.`); enumerators directly under `▸` sit at **depth 2** → lowercase `i.`/`a.`. Ladder keyed by absolute depth, not "first enumerator encountered." (Linter rule R1.)

Child-set = one family; never mix `I.` and `A.`, or `▸` and enumerator, as siblings. Emit literal glyphs (GFM collapses real ordered lists to `1.`). Indent: `## Spacing`.

**No-self-nesting.** Concepts only at L1; enumerators alternate roman↔letter → only attributes can self-nest. **`▸` MUST NOT be direct child of `▸`.** Property-of-a-property → interpose non-leaf `↪` or enumerator. Linter rule R8.

**Leaf marker is `↪` (hook arrow), NOT `→`.** Plain `→` reserved for inline cause-effect (`X → Y`) inside node text (caveman wording convention) → MUST NOT appear as marker. `↪` always starts its own indented line (structure); `→` only mid-line (wording).

**Preserve source relation wording.** Keep source's relation wording; keep endpoints identifiable. Association, correlation, uncertain link never rewritten as causal `→`.

## Length gradient

Word budget — terse by default at EVERY level (recursive):
- enumerator node = terse **concept**; denotes, does not explain
- higher tiers fewest words; deeper MAY use a few more *only when needed*
- long explanatory sentence → `↪` leaf, never enumerator
- shallow node wordier than own descendants = anti-pattern

**Connective-clause test (R12, any depth).** Node carrying reasoning connective — `because`, `since`, `so that`, `given that`, `as a result`, `which means`, or parenthetical doing same job (`(…, never verified against …)`) — = two nodes wearing one marker. Claim stays; reasoning → `↪` child. L1 not exempt (incl. `Net assessment`-style top bullet). Linter rule R12 flags `because`, `since` and `so that` on any non-`↪` node; quoted spans exempt.

**Delimiter-split test (R9, any depth).** Punctuation forces same split. Structural node (concept `-`, attribute `▸`, enumerator) appending content after **spaced dash** (` - ` / ` — `), **colon**, **semicolon**, **arrow** `→`, or inside **parenthetical** `(…)` = two nodes wearing one marker — **unless tail is only 1–2 words** (terse qualifier like `scope: user dir` or `(default)` stays inline). **>2 words** after delimiter → split: head stays, tail → nested child (`↪` leaf when it explains, enumerator when genuine part). Exemptions: `↪` leaf itself (prose home; colon/dash/arrow *inside* `↪` sentence fine), **intra-word hyphens** (`lecture-note` = one word; only space-flanked dash counts), inline code (`` `file:line` `` never counts), **HTML entities** (`&amp;` / `&#x27;`; trailing `;` not prose semicolon). Linter rule R9. *Chained* mid-line `→` (`X → Y; Z → W`) packs multiple facts under one marker → trips R9; **single** `X → Y` causality idiom (≤2-word tail) stays exempt. Worked before/after: `examples/splice-to-subtree.md`.

**Double-marker test (R10, any depth).** Node *content* must not begin with second marker glyph: `▸ • target`, `- • target`, `- → foo` all fail. ONE ladder marker per node; never prefix content with `•`, `→`, `↪`, `▸`, or another `-`. Emulating by hand → indent with spaces, single ladder glyph, no markdown `-`/`•` fallback. Mid-text `X → Y` fine (R10 checks *leading* glyph only). Arrow (`↪`/`→`) markers exempt. Linter rule R10.

## Hook-arrow `↪` — the explanatory node

- `↪` = ONLY place prose explanation lives; enumerator + attribute nodes carry meaning by structure + terse content
- **usually a leaf** — one key cause-effect / elaboration per branch; rare, not every line
- **may be non-leaf branch-summary**: `↪` MAY carry deeper children when it previews subtree below ("gist, detail follows"). Non-leaf `↪` MUST be **first child** of parent (summary precedes detail); `↪` after siblings stays leaf. Linter rule R4.
- **subtree-preview guideline** — non-leaf `↪` only when one-line orientation helps, OR as `▸`→`▸` interposer. Not every branch; reinflates toward prose.
- always own indented line; never mid-line (that = `→`)
- **not caveman-compressed** — enumerator wording may compress; `↪` explanation stays full readable clause

## Nest by dependency

- child **belongs-to / depends-on** parent → real tree, not flat list dump
- nesting depth mirrors actual dependency structure

**Observed-versus-inferred (advisory).** Source distinguishes observation from inference → preserve it. Separate branches only when grouping would blur status; otherwise keep attribution explicit inside `↪`. Never infer evidential status from wording alone; never manufacture missing evidence.

## Pre-emit check

Run over every outline before sending. Cold renders by strongest model tier broke R7, R1, R9 most often (#22).

1. **Word caps (R7).** Count words per structural node: concept ≤3, attribute ≤4, enumerator at depth ≥2 ≤6. Over cap → move extra words to `↪` child.
2. **Enumerator case (R1).** Read each enumerator's absolute depth. Depth 1 → `I.`/`A.`; depth ≥2 → `i.`/`a.`, including every enumerator under `▸`.
3. **Delimiter tails (R9).** On each structural node find spaced dash, colon, semicolon, `→` or parenthetical. More than 2 words after it → split tail into child.
4. **Arrow rarity (R5).** Per top-level block, leaf `↪` nodes must not outnumber other nodes. Too many → merge or drop weakest leaves.
5. **Siblings (R6, R8).** One marker family per child-set. No `▸` directly under `▸`.
6. **Line width (R11, `block` only).** Hard-wrap any line past resolved budget; continuation keeps marker line's indent.
7. **Connectives (R12).** No `because`, `since` or `so that` on a structural node. Move the reason to a `↪` child.
8. **Concept echo (R13).** An attribute directly under a top concept must not repeat the concept's exact text. `- Properties` → `▸ Properties` fails.
9. **Question-word attributes (R14).** An attribute must not start with What, Why, How, When, Where, Which or Who. Write `▸ Cause`, not `▸ Why it happened`.
10. **Count prefixes (R15).** A top concept must not start with a number or count-word (`Three`, `Several`, `Many`, …). `- Three findings` fails; write `- Findings`.

Terseness never overrides this pass. Caveman or another wording layer pulls toward fewer nodes → keep split, compress words inside each node.

## Granularity

One level: `standard`. Surface tree through L3 as content needs. Keep concept spine + enumerated parts. Surface `↪` where it carries cause, qualifier, or hedge.

`skim` and `deep` archived (no current benchmark evidence): `docs/archive/granularity/` at repository root. Asked for either → render `standard`, say level archived.

**Granularity and render mode are independent.** Granularity = how much tree surfaces. Render mode (`block`/`responsive`/`inline`, `## Render modes`) = display container only. Neither changes marker ladder or which linter rule fires: the same 16 rules gate every render mode.

## Spacing

**Indent: 4 spaces per rung in `block`** (L1=0, L2=4, L3=8, `↪`=parent content +4). Single source of truth for indent. `responsive`: 2 spaces per rung (real GFM nesting).

**Block-mode line wrap (R11).** Max line width incl. indent = **budget per `## Activation`** (64 chars default; hint → clamp(N−8, 32, 120); `width N` → N). Overflow soft-wraps to column 0, wrecking ladder → hard-wrap yourself: continuation lines carry leading whitespace **identical** to marker line's indent; no hanging indent, no glyph. Every node type, `↪` included. `inline` and `responsive` UNAFFECTED (renderer wraps). Full spec + worked wrap: `reference/render-modes.md`.

**No blank line between siblings** in `block` or `responsive`.

## Emphasis taxonomy

Applies to **markdown-rendered modes** (`responsive`, and deprecated `inline`). `block`: everything in fence literal → no emphasis.
- L1 top concepts → **bold** (scannable concept spine)
- inline + sparing, deeper: `code` → literal tokens (paths, ids, values, verbatim errors) · *italic* → term-of-art first mention · ~~strike~~ → rejected/deprecated
- `<u>underline</u>` → definition anchor (best-effort; surface lacks `<u>` → fall back *italic*)
- never alters marker ladder or nesting

## Leaf preservation

Code blocks + tables = intact leaf nodes under owning node. Never flatten into node text.

## Hedge preservation

Preserve source hedges with the claim they govern, collapsed output included. Hedge stays in claim text or immediately attached `↪`. Certainty branch only when hedge scope unambiguous. Never turn hedged source claim into unhedged heading.

## Carve-outs

- single-fact / no hierarchy → no forced nesting
- security / irreversible-action warnings → plain clarity wins (align caveman auto-clarity)
- non-explanatory status ("done", tool results)
- code / commit messages / bot-template fixed fields (A–G) / footers / markers
- explicit prose request → prose that turn

*Which* GitHub surfaces render as `responsive` outlines, and which template/footer scaffolding stays verbatim = consuming repo's authoring **policy**, not a rule of this skill. Skill supplies only the `responsive` render mechanism (`## Render modes`).

## Render modes

Same outline, two active containers, **scoped by surface**; only wrapper differs.

| surface | mode |
|---|---|
| monospace/terminal + committed `.md` fences, faithful spacing, copy-paste clean | `block` — ONE fenced ` ```text ` code block, whole outline; R11 hard-wrap applies |
| **any markdown-rendering surface** — GitHub issue/PR/comment bodies AND chat-app replies (Claude Code app/web, or any variable-viewport renderer) — **opt-in via explicit `responsive` mode; `block` is the default everywhere** | `responsive` — real GFM list items, 2-space/rung real list nesting, no fence; **glyph-free since v0.3.9**: the renderer already draws a bullet per item, so carrying `▸`/`↪` inside the content produced `• ▸` double markers (render-layer R10). Role moves to typography — attribute → `- **Bold Name**`, enumerator → literal label content (`- a. tool execution`), explanation leaf → plain prose item (no `↪`). The renderer wraps to its own box width — R11 does NOT apply |
| ~~GitHub prose via literal-glyph 4-space rungs~~ | `inline` — **DEPRECATED (v0.3.8).** Its ≥6-space (depth-2+) rungs render as **indented code blocks** on GFM (wide, non-wrapping, horizontal-scroll boxes) and its depth-1 `▸` lines as emoji-led paragraphs — the exact GitHub-rendering mess `responsive` fixes. Retained only so pre-v0.3.8 committed outlines still lint; never pick it for a new GitHub body. |

`inline` = deprecated, lint-only; never pick it for new output. Full spec (fence-tag rationale, per-mode cost tradeoffs, block-mode wrapping, responsive worked example, why `inline` breaks on GFM): `reference/render-modes.md`.

## Worked example

Same "Agentic harness" tree, two ways. `Capabilities` = attribute; its parts enumerate below it.

**`block` — default everywhere, literal glyphs, 4-space rungs, fenced (` ```text `):**

```text
- Agentic harness
    ▸ Purpose
        ↪ a raw text-predictor gains the ability to act
    ▸ Capabilities
        a. tool execution
        b. control loop
    ▸ Output
        ↪ an acting agent
- Control loop
    I. assemble context
    II. emit tool calls
    III. harness executes
        ↪ side effects hit the real world: files, shell, network
    IV. repeat until done / budget cap
```

**`responsive` — opt-in for GitHub/chat, glyph-free, 2-space real-list nesting, no fence:**

```
- **Agentic harness**
  - **Purpose**
    - a raw text-predictor gains the ability to act
  - **Capabilities**
    - a. tool execution
    - b. control loop
  - **Output**
    - an acting agent
- **Control loop**
  - I. assemble context
  - II. emit tool calls
  - III. harness executes
    - side effects hit the real world: files, shell, network
  - IV. repeat until done / budget cap
```

**Do not mix them.** `block` glyphs in `responsive` double with renderer bullet (`• ▸`); 4-space rungs render as GFM code blocks past depth 1. Detail: `reference/render-modes.md` `## Responsive mode`.

`Purpose`, `Capabilities`, `Output` = **attributes of** agentic harness; `Control loop` = separate concept, ordered steps (`I.`–`IV.`). More examples: `examples/{standard,attribute,report}.md`.

## Caveman coexistence

Orthogonal — caveman = wording, structured-gist = structure.

**Independence (load-bearing)**: structured-gist NEVER invokes, activates, or implies caveman, and changes no wording itself. caveman OFF → nodes use normal prose. caveman *separately* active → caveman compresses enumerator wording, **never the `↪` leaf** (stays readable explanation). Structure (ladder / nesting / `↪`) identical either way. Token throughput restructures, it does not compress — that is the independence test.

Holds in every caveman mode (lite, full, ultra, wenyan-lite, wenyan-full, wenyan-ultra): structure unchanged; markers stay **Latin even under wenyan**. Per-mode table + invariants: `reference/composition.md`.

On public reader-facing prose surfaces, a separate public-prose wording skill, if you use one, owns wording inside nodes and `↪` leaves — not caveman.

Carve-outs align: caveman auto-clarity yields for security/irreversible warnings → structured-gist also yields to plain clarity. Public-surface wording ownership + caveman compose-per-node steps: `reference/composition.md`.

## Limitations

- Robustness axis = structural conformance only; perturbation-stability term cut twice (`benchmarks/scoring.md`).
- Linter checks structure, not sentence quality or truth. Compliant outline can still carry jargon, weak claims, or misrepresent source.
- General hedge enforcement needs source-vs-output comparison; deferred to held hedge-fidelity backlog item. Shipped fidelity check covers only declared statements in this repo's own example and fixtures.
- Relation-wording preservation enforced only over those same declared statements, not arbitrary sources.
- Benchmark scorer never calls model, network, or randomness at scoring time; if those are unavailable it cannot fail for their absence.

## Install

`/plugin marketplace add domattioli/structured-gist`, then `/plugin install structured-gist`. Full detail: `reference/install.md`.
