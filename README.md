# structured-gist

![Status](https://img.shields.io/badge/status-alpha-orange)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Version](https://img.shields.io/badge/version-0.4.7-informational)
![Rules](https://img.shields.io/badge/linter%20rules-15-success)
![Tests](https://img.shields.io/badge/tests-57%20passing-success)
![DOI](https://img.shields.io/badge/DOI-pending-lightgrey)

A skill turning agentic-AI word vomit into a skimmable gist. Information is encoded intuitively within a nested bulleted structure and via node depth; prose stays confined to explanation nodes. 

## Contents

1. [Motivation](#1-motivation)
2. [Method](#2-method)
3. [Installation](#3-installation)
4. [Usage](#4-usage)
5. [Benchmarks](#5-benchmarks)
6. [Limitations](#6-limitations)
7. [Future work](#7-future-work)
8. [Documentation](#8-documentation)
9. [Contributing](#9-contributing)
10. [Reuse and training](#10-reuse-and-training)
11. [License](#11-license)

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 1. Motivation

Claude's explanatory prose has a real failure mode people call "Claudish": dense with unexplained jargon from whatever domain it is working in, and by turns contrarian, sycophantic, padded with filler, or simply saying nothing across many words. Word-count compression does not fix this. caveman-lite, for instance, shortens Claudish prose without reorganizing it; the result reads as plain English, but the underlying thought stays unstructured, and its content stays non-deterministic from one run to the next.

The missing structure is concept and sub-concept with their relationship: what is being claimed and what supports that claim, including how the supporting pieces relate to each other and to the claim (whether ordered or grouped, or independent). This is also how a complex subject gets learned from a well-built lecture, and how a slide deck gets built: one concept per slide with minimal words, the relationships carried by layout rather than by prose.

structured-gist renders that decomposition directly, as an explicit tree instead of a paragraph the reader has to parse for it.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 2. Method

This section is itself rendered in structured-gist's `block` mode, not written by hand as prose. It covers the marker taxonomy and a worked example (a real word-count comparison) in one outline.

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
- Worked example
    ▸ Test case
        ↪ Sonnet 4 rendered the same content two ways
    ▸ Word count
        a. paragraph
            ↪ 146 words
        b. outline
            ↪ 100 words, skim, block mode
        c. reduction
            ↪ 31.5%, tree also cuts parsing cost
    ▸ Outline content
        a. purpose
            ↪ replaces verbose summaries with outlines
        b. structure
            ↪ role hierarchy, position over sentence structure
        c. linter rules
            i. flags shallow-depth stalling
            ii. detects punctuation-spliced facts
        d. use cases
            i. session recaps
            ii. cause-chain explanations
            iii. GitHub issue/PR comments
    ▸ Linter
        ↪ lint_outline.py, 15 rules, stdlib only
```

`block` is one of three render modes; `responsive` (the GitHub/chat default) and the deprecated `inline` form are documented, with worked examples of each, in `skills/structured-gist/SKILL.md` under `## Render modes` and `reference/render-modes.md`.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 3. Installation

```bash
/plugin marketplace add domattioli/structured-gist
/plugin install structured-gist
```

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 4. Usage

```bash
/structured-gist [skim|standard|deep] [block|responsive]
```

No level given defaults to `skim`. No mode given defaults by surface: `responsive` on any markdown-rendering surface, `block` on a plain terminal.

Trigger phrases: "structured-gist", "gist mode", "gist this", "outline this", "bullet this", "notes mode", "structure this", "break this down", "distill this", "give me the gist", "make this skimmable", "tighten this up", "condense this".

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 5. Benchmarks

Measured deltas from the skill's version history. Full table with methodology: `skills/structured-gist/tests/benchmark.md`.

| Version | Change | Metric | Result |
|---|---|---|---|
| v0.2.9 | dense paragraph vs. skim outline, same content | word count | 147 → 88 words (**-40.1%**) |
| v0.3.7 | block mode vs. responsive mode, same tree | word count | 19 → 24 words (**+26.3%**, GFM bullet-token artifact, not a regression) |
| v0.4.0 | direct-prompt outline vs. experimental KG-mode generation, 20-source corpus | outline-quality composite (retention × robustness × brevity) | 0.549 → 0.760 (KG mode wins structure, loses retention; not shipped — see Future work) |
| v0.4.2 | linter rule coverage | rules gated / tests passing | 11 rules / 33 tests → 15 rules / 46 tests |
| v0.4.3 | rename + trigger-phrase expansion | tests passing | 46 → 63 (no rule-logic change) |

Word count and rule/test coverage are the metrics tracked today. Other metrics (reader comprehension, parse time) remain open; see [Future work](#7-future-work) for status and how to propose one.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 6. Limitations

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

## 7. Future work

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
