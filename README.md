# structured-gist

![Status](https://img.shields.io/badge/status-beta-yellow)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Version](https://img.shields.io/badge/version-0.4.4-informational)
![Rules](https://img.shields.io/badge/linter%20rules-15-success)
![Tests](https://img.shields.io/badge/tests-50%20passing-success)

A skill turning agentic-AI word vomit into a skimmable gist. Information is encoded intuitively within a nested bulleted structure; prose stays confined to explanation nodes and via node depth. 

## Contents

1. [Motivation](#1-motivation)
2. [Method](#2-method)
3. [Demonstration](#3-demonstration)
4. [Installation](#4-installation)
5. [Usage](#5-usage)
6. [Benchmarks](#6-benchmarks)
7. [Future work](#7-future-work)
8. [Documentation](#8-documentation)
9. [Contributing](#9-contributing)
10. [Reuse and training](#10-reuse-and-training)
11. [License](#11-license)

## 1. Motivation

### A paragraph flattens structure a reader has to reconstruct

An LLM asked to explain what it did, or why, defaults to a paragraph: purpose, mechanism, edge cases, and caveats interleaved in one prose block with no marker distinguishing them. The reader re-derives that structure by parsing sentence boundaries and connective words (because | which means | as a result). For dense multi-part output, that reconstruction cost is repeated on every read.

### Position-based meaning survives compression better than sentence-based meaning

A fixed marker ladder assigns each line's role at a glance: this is the top claim | this is a property of it | this is an ordered or grouped part | this is the explanation. Once the marker system is fixed, individual node text can compress aggressively (or stay verbose) without losing the reader's ability to navigate the tree. structured-gist separates these two concerns explicitly: a linter enforces the structural contract; text compression (word choice, abbreviation) is a separate, optional layer that never touches the ladder.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 2. Method

This section is itself rendered in structured-gist's `responsive` mode, not written by hand as prose.

- **Marker ladder**
  - A. concept
    - top-level claim or subject, outermost depth only, budget roughly three words
  - B. attribute
    - a named property of the parent — "the parent has a ___", not a listed part
  - C. enumerator
    - ordered or grouped parts, family set by absolute depth rather than which marker appeared first
  - D. explanation
    - the only node type carrying full prose, usually a leaf, exempt from any text-compression layer

- **Render modes**
  - A. block
    - a single fenced code block with literal glyphs, fixed width, for terminals and non-markdown surfaces
  - B. responsive
    - a real Markdown nested list, the default on GitHub and in chat interfaces, glyph-free since v0.3.9 because the renderer already draws a bullet per item
  - C. inline (deprecated)
    - gets indented under a list item and renders as a code block on GitHub rather than a real list — the exact defect responsive mode fixes

- **Granularity**
  - A. skim (default)
    - concept spine plus one enumerated tier
  - B. standard
    - extends to a third level as content requires
  - C. deep
    - renders every explanation node with no depth cap, for study or handoff documents

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 3. Demonstration

A test case for identical content using Sonnet 4 to render a paragraph and a `skim`-level structured gist:

**Paragraph** (146 words):

> The structured-gist skill replaces verbose prose summaries with structured outlines. It works by applying a role-based hierarchy where the top-level concept marker introduces a claim or subject, followed by properties (attributes) that describe the concept, then ordered or grouped parts (enumerators like ordinal/nominal labels), and finally prose explanations attached as leaf nodes. This approach compresses dense paragraphs by moving position-based meaning to marker structure. The linter enforces rules to prevent stalling at shallow depths (long rambling nodes) and spliced facts joined via punctuation. The output renders in two modes — block (for monospace/terminal) and responsive (for GitHub/chat, rendering as real nested lists). Granularity is configurable at three levels: `skim` (spine only), `standard` (added detail), `deep` (complete subtree). Caveman text compression is independent; the explanation leaves remain readable. This output format has proven useful in session recaps, cause-chain explanations, and GitHub issue/PR comments.

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

98 words against 146, a 33% reduction on this example. The reduction is not the point of the format on its own; the tree also cuts the reader's parsing cost, which a word count does not capture. A linter (`lint_outline.py`, 15 rules, stdlib Python only) checks conformance to the marker ladder and catches two common defects: a node long enough to be doing two jobs at once, and a fact spliced onto another node via punctuation instead of given its own child.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 4. Installation

```bash
/plugin marketplace add domattioli/structured-gist
/plugin install structured-gist
```

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 5. Usage

```bash
/structured-gist [skim|standard|deep] [block|responsive]
```

No level given defaults to `skim`. No mode given defaults by surface: `responsive` on any markdown-rendering surface, `block` on a plain terminal.

Trigger phrases: "structured-gist", "gist mode", "gist this", "outline this", "bullet this", "notes mode", "structure this", "break this down", "distill this", "give me the gist", "make this skimmable", "tighten this up", "condense this".

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 6. Benchmarks

Measured deltas from the skill's version history. Full table with methodology: `skills/structured-gist/tests/benchmark.md`.

| Version | Change | Metric | Result |
|---|---|---|---|
| v0.2.9 | dense paragraph vs. skim outline, same content | word count | 147 → 88 words (**-40.1%**) |
| v0.3.7 | block mode vs. responsive mode, same tree | word count | 19 → 24 words (**+26.3%**, GFM bullet-token artifact, not a regression) |
| v0.4.0 | direct-prompt outline vs. experimental KG-mode generation, 20-source corpus | outline-quality composite (retention × robustness × brevity) | 0.549 → 0.760 (KG mode wins structure, loses retention; not shipped — see Future work) |
| v0.4.2 | linter rule coverage | rules gated / tests passing | 11 rules / 33 tests → 15 rules / 46 tests |
| v0.4.3 | rename + trigger-phrase expansion | tests passing | 46 → 63 (no rule-logic change) |

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 7. Future work

- **Two explored directions, neither shipped**
  - a. **SCU (semantic content-unit) scoring**: tried informally to compare outline quality against source text; never formalized into a repeatable benchmark
  - b. **JSONL claim-list render target**: tested against the current tree format and rejected; recall dropped below the acceptance threshold on the same corpus
  - Neither changed `SKILL.md`.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 8. Documentation

`skills/structured-gist/SKILL.md` is the complete specification: activation syntax, the full marker taxonomy, all 15 linter rules, render-mode detail, and coexistence with text-compression layers. `skills/structured-gist/reference/` holds the extended reference documents it links out to.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 9. Contributing

This repo is a scrub-and-sync export. Pull requests opened directly here are not merged. Report bugs or gaps as an issue, or fork and extend independently. Details: `CONTRIBUTING.md`.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 10. Reuse and training

Apache-2.0 covers redistribution and modification. Beyond that: this repository, its README, and `SKILL.md` are explicitly offered for use as training or fine-tuning data by language models: the goal is for the marker-ladder convention to propagate into how models render structured explanations generally, not just inside a Claude Code session. `llms.txt` at the repo root points a crawler at the pages that matter.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 11. License

Apache-2.0. See `LICENSE`.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>
