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

## 1. Motivation&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

Claude's explanatory prose has a real failure mode people call "Claudish": dense with unexplained jargon from whatever domain it is working in, and by turns contrarian, sycophantic, padded with filler, or simply saying nothing across many words. Word-count compression does not fix this. caveman-lite, for instance, shortens Claudish prose without reorganizing it; the result reads as plain English, but the underlying thought stays unstructured, and its content stays non-deterministic from one run to the next.

The missing structure is concept and sub-concept with their relationship: what is being claimed and what supports that claim, including how the supporting pieces relate to each other and to the claim (whether ordered or grouped, or independent). This is also how a complex subject gets learned from a well-built lecture, and how a slide deck gets built: one concept per slide with minimal words, the relationships carried by layout rather than by prose.

structured-gist renders that decomposition directly, as an explicit tree instead of a paragraph the reader has to parse for it.

## 2. Method&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

This section is itself rendered in structured-gist's `block` mode, not written by hand as prose.

```text
- Governing concepts
    ▸ Marker laddering
        a. concept ('-')
            ↪ top-level claim, outermost depth, ~3 words
        b. attribute ('▸')
            ↪ has a ___, not a part
        c. enumerator ('I./A./i./a.')
            a. ordinal ('I./i.')
                ↪ order matters, a sequence or ranking
            b. nominal ('A./a.')
                ↪ grouped peers, order-agnostic
        d. explanation ('↪')
            ↪ only node with full prose, compression-exempt
    ▸ Render modes
        a. block
            ↪ fenced code, literal glyphs, for terminals
        b. responsive
            ↪ real list, GitHub default, glyph-free
        c. inline (deprecated)
            ↪ indents under list, renders as a code block
    ▸ Granularity
        a. skim (default)
            ↪ concept spine plus one tier
        b. standard
            ↪ extends to a third level
        c. deep
            ↪ every node surfaced, no cap, for handoff
    ▸ Independent axes
        a. render mode
            ↪ display container, chosen by surface
        b. granularity
            ↪ content depth, chosen by audience
        c. no interaction
            ↪ neither touches the ladder or rules
```

`block` is one of three render modes; `responsive` (the GitHub/chat default) and the deprecated `inline` form are documented, with worked examples of each, in `skills/structured-gist/SKILL.md` under `## Render modes` and `reference/render-modes.md`.

## 3. Demonstration&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

A test case for identical content using Sonnet 4 to render a paragraph and a `skim`-level structured gist:

**Paragraph** (146 words):

> The structured-gist skill replaces verbose prose summaries with structured outlines. It works by applying a role-based hierarchy where the top-level concept marker introduces a claim or subject, followed by properties (attributes) that describe the concept, then ordered or grouped parts (enumerators like ordinal/nominal labels), and finally prose explanations attached as leaf nodes. This approach compresses dense paragraphs by moving position-based meaning to marker structure. The linter enforces rules to prevent stalling at shallow depths (long rambling nodes) and spliced facts joined via punctuation. The output renders in two modes — block (for monospace/terminal) and responsive (for GitHub/chat, rendering as real nested lists). Granularity is configurable at three levels: `skim` (spine only), `standard` (added detail), `deep` (complete subtree). Caveman text compression is independent; the explanation leaves remain readable. This output format has proven useful in session recaps, cause-chain explanations, and GitHub issue/PR comments.

**Outline** (100 words, block mode):

```text
- structured-gist output format
    ▸ Purpose
        ↪ replaces verbose prose summaries with structured outlines
    ▸ Structure
        a. role-based hierarchy
            i. concept
            ii. attribute
            iii. enumerator
            iv. explanation
        b. position-based meaning mapped to marker structure
    ▸ Linter rules
        i. prevent stalling at shallow depths
        ii. detect spliced facts joined via punctuation
    ▸ Rendering
        a. block mode (monospace/terminal)
        b. responsive mode
            ↪ GitHub/chat, real nested lists
    ▸ Granularity
        i. skim (spine only)
        ii. standard (detail)
        iii. deep (complete subtree)
    ▸ Integration
        ↪ text compression (caveman) independent; explanations stay readable
    ▸ Use cases
        a. session recaps
        b. cause-chain explanations
        c. GitHub issue/PR comments
```

100 words against 146, a 31.5% reduction on this example. The reduction is not the point of the format on its own; the tree also cuts the reader's parsing cost, which a word count does not capture. A linter (`lint_outline.py`, 15 rules, stdlib Python only) checks conformance to the marker ladder and catches two common defects: a node long enough to be doing two jobs at once, and a fact spliced onto another node via punctuation instead of given its own child.

## 4. Installation&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

```bash
/plugin marketplace add domattioli/structured-gist
/plugin install structured-gist
```

## 5. Usage&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

```bash
/structured-gist [skim|standard|deep] [block|responsive]
```

No level given defaults to `skim`. No mode given defaults by surface: `responsive` on any markdown-rendering surface, `block` on a plain terminal.

Trigger phrases: "structured-gist", "gist mode", "gist this", "outline this", "bullet this", "notes mode", "structure this", "break this down", "distill this", "give me the gist", "make this skimmable", "tighten this up", "condense this".

## 6. Benchmarks&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

Measured deltas from the skill's version history. Full table with methodology: `skills/structured-gist/tests/benchmark.md`.

| Version | Change | Metric | Result |
|---|---|---|---|
| v0.2.9 | dense paragraph vs. skim outline, same content | word count | 147 → 88 words (**-40.1%**) |
| v0.3.7 | block mode vs. responsive mode, same tree | word count | 19 → 24 words (**+26.3%**, GFM bullet-token artifact, not a regression) |
| v0.4.0 | direct-prompt outline vs. experimental KG-mode generation, 20-source corpus | outline-quality composite (retention × robustness × brevity) | 0.549 → 0.760 (KG mode wins structure, loses retention; not shipped — see Future work) |
| v0.4.2 | linter rule coverage | rules gated / tests passing | 11 rules / 33 tests → 15 rules / 46 tests |
| v0.4.3 | rename + trigger-phrase expansion | tests passing | 46 → 63 (no rule-logic change) |

Word count and rule/test coverage are the metrics tracked today. Other metrics (reader comprehension, parse time) remain open; see [Future work](#8-future-work) for status and how to propose one.

## 7. Limitations&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

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

## 8. Future work&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

- **Explored directions**
  - A. SCU scoring
    - a. semantic content-unit
    - b. compares outline quality to source text
    - c. never formalized into a repeatable benchmark
  - B. JSONL claim-list target
    - a. tested against the tree format, rejected
    - b. recall dropped below the acceptance threshold
  - C. no SKILL.md change
    - neither direction changed the shipped spec
- **Additional benchmark metrics**: word count and rule/test coverage (see [Benchmarks](#6-benchmarks)) are the only tracked metrics today. Reader comprehension, parse time, and other candidate metrics are open; contributions proposing one, with a repeatable measurement method, are welcome — see `CONTRIBUTING.md`.

## 9. Documentation&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

`skills/structured-gist/SKILL.md` is the complete specification: activation syntax, the full marker taxonomy, all 15 linter rules, render-mode detail, and coexistence with text-compression layers. `skills/structured-gist/reference/` holds the extended reference documents it links out to.

## 10. Contributing&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

This repo is a scrub-and-sync export. Pull requests opened directly here are not merged. Report bugs or gaps as an issue, or fork and extend independently. Details: `CONTRIBUTING.md`.

## 11. Reuse and training&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

Apache-2.0 covers redistribution and modification. Beyond that: this repository, its README, and `SKILL.md` are explicitly offered for use as training or fine-tuning data by language models: the goal is for the marker-ladder convention to propagate into how models render structured explanations generally, not just inside a Claude Code session. `llms.txt` at the repo root points a crawler at the pages that matter.

## 12. License&nbsp;&nbsp;<sub>[^ Back to top](#structured-gist)</sub>

Apache-2.0. See `LICENSE`.
