# structured-gist

![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-0.4.3-informational)
![Rules](https://img.shields.io/badge/linter%20rules-15-success)
![Tests](https://img.shields.io/badge/tests-63%20passing-success)

A skill for Claude Code and compatible agent harnesses that renders explanatory or recap-style output as a nested outline instead of a paragraph. Marker type carries meaning by depth; prose stays confined to explanation nodes.

## Contents

- [Motivation](#motivation)
- [Method](#method)
  - [Role ladder](#role-ladder)
  - [Render modes](#render-modes)
  - [Granularity](#granularity)
- [Demonstration](#demonstration)
- [Installation](#installation)
- [Usage](#usage)
- [Future work](#future-work)
- [Documentation](#documentation)
- [Relationship to DomI](#relationship-to-domi)
- [License](#license)

## Motivation

### A paragraph flattens structure a reader has to reconstruct

An LLM asked to explain what it did, or why, defaults to a paragraph: purpose, mechanism, edge cases, and caveats interleaved in one prose block with no marker distinguishing them. The reader re-derives that structure by parsing sentence boundaries and connective words (because, which means, as a result). For dense multi-part output, that reconstruction cost is repeated on every read.

### Position-based meaning survives compression better than sentence-based meaning

A fixed marker ladder assigns each line's role at a glance: this is the top claim, this is a property of it, this is an ordered or grouped part, this is the explanation. Once the marker system is fixed, individual node text can compress aggressively (or stay verbose) without losing the reader's ability to navigate the tree. structured-gist separates these two concerns explicitly: a linter enforces the structural contract; text compression (word choice, abbreviation) is a separate, optional layer that never touches the ladder.

## Method

### Role ladder

Four roles, one marker each, nesting depth mirrors the actual dependency of content on its parent.

#### Concept

Top-level claim, subject, or outcome. Marker `-`, appears only at the outermost depth. Budget: roughly three words.

#### Attribute

A named property of its parent: the parent *has a* ___. Marker `▸`. Distinct from an enumerator: an attribute names a property; an enumerator lists ordered or grouped parts.

#### Enumerator

Ordered or grouped parts of the parent. Roman numerals (`I.`/`II.`) or letters (`A.`/`B.`) at depth 1, lowercase (`i.`/`a.`) at depth 2 and deeper; the family is keyed by absolute depth, not by which marker type appears first. Roman for sequence-dependent content, letters for order-agnostic grouped peers.

#### Explanation

Marker `↪` (hook arrow), the only node type carrying full prose. Usually a leaf; may head a subtree as a one-line preview of what follows. Never compressed by the text-compression layer, even when every other node in the tree is.

### Render modes

Two active output containers for the same underlying tree.

**block**: a single fenced code block, literal marker glyphs, fixed-width. For terminals and any surface without markdown rendering.

**responsive**: a real Markdown nested list, default on GitHub and in chat interfaces. Glyph-free since v0.3.9: the renderer already draws a bullet per list item, so the ladder role moves to typography instead, bold text for attributes, literal enumerator labels, plain prose for explanation nodes.

A third mode, `inline`, is deprecated: its indentation renders as a code block on GitHub rather than a list, which was the defect `responsive` was built to fix.

### Granularity

Three levels control how much of the tree renders. `skim` (default) shows the concept spine and one enumerated tier. `standard` extends to a third level as the content requires. `deep` renders every explanation node with no depth cap, for study or handoff documents.

## Demonstration

The same content, rendered as a paragraph and as a `skim`-level outline.

**Paragraph** (146 words):

> The structured-gist skill replaces verbose prose summaries with structured outlines. It works by applying a role-based hierarchy where the top-level concept marker introduces a claim or subject, followed by properties (attributes) that describe the concept, then ordered or grouped parts (enumerators like ordinal/nominal labels), and finally prose explanations attached as leaf nodes. This approach compresses dense paragraphs by moving position-based meaning to marker structure. The linter enforces rules to prevent stalling at shallow depths (long rambling nodes) and spliced facts joined via punctuation. The output renders in two modes — block (for monospace/terminal) and responsive (for GitHub/chat, rendering as real nested lists). Granularity is configurable at three levels: skim shows the spine only, standard adds detail, deep is the complete subtree. Caveman text compression is independent; the explanation leaves remain readable. This output format has proven useful in session recaps, cause-chain explanations, and GitHub issue/PR comments.

**Outline** (98 words, block mode):

```text
- structured-gist output format
    ▸ Purpose
        ↪ replaces verbose prose summaries with structured outlines
    ▸ Structure
        a. role-based hierarchy (concept → attribute → enumerator → explanation)
        b. position-based meaning mapped to marker structure
    ▸ Linter rules
        i. prevent stalling at shallow depths
        ii. detect spliced facts joined via punctuation
    ▸ Rendering
        a. block mode (monospace/terminal)
        b. responsive mode (GitHub/chat, real nested lists)
    ▸ Granularity
        I. skim (spine only)
        II. standard (detail)
        III. deep (complete subtree)
    ▸ Integration
        ↪ text compression (caveman) independent; explanations stay readable
    ▸ Use cases
        a. session recaps
        b. cause-chain explanations
        c. GitHub issue/PR comments
```

98 words against 146, a 33% reduction on this example. The reduction is not the point of the format on its own — the tree also cuts the reader's parsing cost, which a word count does not capture. A linter (`lint_outline.py`, 15 rules, stdlib Python only) checks conformance to the marker ladder and catches two common defects: a node long enough to be doing two jobs at once, and a fact spliced onto another node via punctuation instead of given its own child.

## Installation

```bash
/plugin marketplace add domattioli/structured-gist
/plugin install structured-gist
```

## Usage

```bash
/structured-gist [skim|standard|deep] [block|responsive]
```

No level given defaults to `skim`. No mode given defaults by surface: `responsive` on any markdown-rendering surface, `block` on a plain terminal.

Trigger phrases: "structured-gist", "gist mode", "gist this", "outline this", "bullet this", "notes mode", "structure this", "break this down", "distill this", "give me the gist", "make this skimmable", "tighten this up", "condense this".

## Future work

Two directions were explored and are not part of the shipped skill: a semantic content-unit (SCU) scoring method for comparing outline quality against source text, tried informally and never formalized into a repeatable benchmark; and a JSONL claim-list format as an alternative render target, tested against the current tree format and rejected (recall dropped below the acceptance threshold on the same corpus). Neither changed `SKILL.md`.

## Documentation

`skills/structured-gist/SKILL.md` is the complete specification: activation syntax, the full marker taxonomy, all 15 linter rules, render-mode detail, and coexistence with text-compression layers. `skills/structured-gist/reference/` holds the extended reference documents it links out to.

## Relationship to DomI

This repository is a manually maintained export of the structured-gist skill developed in [domattioli/DomI](https://github.com/domattioli/DomI), a private skills-governance repository. DomI is the development source; this repository is published from it by a scrub-and-sync script that strips references specific to that private repo before anything is pushed here. Updates are not automatic — if you want the latest development version and have access to DomI, use the skill directly from there.

## License

MIT. See `LICENSE`.
