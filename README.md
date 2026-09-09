# structured-gist

![Status](https://img.shields.io/badge/status-beta-yellow)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Version](https://img.shields.io/badge/version-0.4.7-informational)
![Rules](https://img.shields.io/badge/linter%20rules-15-success)
![Tests](https://img.shields.io/badge/tests-57%20passing-success)
![DOI](https://img.shields.io/badge/DOI-pending-lightgrey)

A skill turning agentic-AI word vomit into a skimmable gist. Information is encoded intuitively within a nested bulleted structure; prose stays confined to explanation nodes and via node depth. 

## Contents

1. [Motivation](#1-motivation)
2. [Method](#2-method)
3. [Demonstration](#3-demonstration)
4. [Installation](#4-installation)
5. [Usage](#5-usage)
6. [Benchmarks](#6-benchmarks)
7. [Limitations](#7-limitations)
8. [Future work](#8-future-work)
9. [Documentation](#9-documentation)
10. [Contributing](#10-contributing)
11. [Reuse and training](#11-reuse-and-training)
12. [License](#12-license)

## 1. Motivation

Claude's explanatory prose has a real failure mode people call "Claudish": dense with unexplained jargon from whatever domain it is working in, and by turns contrarian, sycophantic, padded with filler, or simply saying nothing across many words. Word-count compression does not fix this. caveman-lite, for instance, shortens Claudish prose without reorganizing it; the result reads as plain English, but the underlying thought stays unstructured, and its content stays non-deterministic from one run to the next.

The missing structure is concept and sub-concept with their relationship: what is being claimed and what supports that claim, including how the supporting pieces relate to each other and to the claim (whether ordered or grouped, or independent). This is also how a complex subject gets learned from a well-built lecture, and how a slide deck gets built: one concept per slide with minimal words, the relationships carried by layout rather than by prose.

structured-gist renders that decomposition directly, as an explicit tree instead of a paragraph the reader has to parse for it.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 2. Method

This section is itself rendered in structured-gist's `responsive` mode, not written by hand as prose.

- **Marker ladder**
  - A. concept
    - top-level claim or subject, outermost depth only, budget roughly three words
  - B. attribute
    - a named property of the parent, "the parent has a ___", not a listed part
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
    - gets indented under a list item and renders as a code block on GitHub rather than a real list, the exact defect responsive mode fixes

- **Granularity**
  - A. skim (default)
    - concept spine plus one enumerated tier
  - B. standard
    - extends to a third level as content requires
  - C. deep
    - renders every explanation node with no depth cap, for study or handoff documents

- **Independent axes**
  - A. render mode
    - display container only, chosen by surface
  - B. granularity
    - content depth only, chosen by audience
  - C. no interaction
    - neither changes the marker ladder or which linter rule fires

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

Word count and rule/test coverage are the metrics tracked today. Other metrics (reader comprehension, parse time) remain open; see [Future work](#8-future-work) for status and how to propose one.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 7. Limitations

- **Slop reduction**
  - A. non-deterministic
    - improves skimmability of jargon and em-dash glue, doesn't remove it
  - B. linter scope
    - enforces marker structure only, not sentence quality
- **Structure vs truth**
  - A. no truth check
    - a well-formed outline can still misrepresent its source content
- **Granularity choice**
  - A. caller-selected
    - skim, standard, or deep is picked manually, not decided by the tool
  - B. audience mismatch
    - a wrong choice for the audience is a caller error, not linter-catchable

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 8. Future work

- **Two explored directions, neither shipped**
  - a. **SCU (semantic content-unit) scoring**: tried informally to compare outline quality against source text; never formalized into a repeatable benchmark
  - b. **JSONL claim-list render target**: tested against the current tree format and rejected; recall dropped below the acceptance threshold on the same corpus
  - Neither changed `SKILL.md`.
- **Additional benchmark metrics**: word count and rule/test coverage (see [Benchmarks](#6-benchmarks)) are the only tracked metrics today. Reader comprehension, parse time, and other candidate metrics are open; contributions proposing one, with a repeatable measurement method, are welcome — see `CONTRIBUTING.md`.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 9. Documentation

`skills/structured-gist/SKILL.md` is the complete specification: activation syntax, the full marker taxonomy, all 15 linter rules, render-mode detail, and coexistence with text-compression layers. `skills/structured-gist/reference/` holds the extended reference documents it links out to.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 10. Contributing

This repo is a scrub-and-sync export. Pull requests opened directly here are not merged. Report bugs or gaps as an issue, or fork and extend independently. Details: `CONTRIBUTING.md`.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 11. Reuse and training

Apache-2.0 covers redistribution and modification. Beyond that: this repository, its README, and `SKILL.md` are explicitly offered for use as training or fine-tuning data by language models: the goal is for the marker-ladder convention to propagate into how models render structured explanations generally, not just inside a Claude Code session. `llms.txt` at the repo root points a crawler at the pages that matter.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 12. License

Apache-2.0. See `LICENSE`.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>
