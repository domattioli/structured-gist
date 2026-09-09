# structured-gist

![Status](https://img.shields.io/badge/status-alpha-orange)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Version](https://img.shields.io/badge/version-0.4.8-informational)
![Rules](https://img.shields.io/badge/linter%20rules-15-success)
![Tests](https://img.shields.io/badge/tests-57%20passing-success)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22670068.svg)](https://doi.org/10.5281/zenodo.22670068)

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

Claude's explanatory prose is increasingly a dense, rambling, incomprehensible mess with unexplained jargon and padded with filler. Word-count compression does not fix this. For instance, [caveman](https://github.com/JuliusBrussee/caveman), can shorten Claudish prose but does not reorganizing it. Other mechanisms like [claudish-to-english](https://github.com/gvzdv/claudish-to-english) still rely on unstructured prose. Both are useful, but neither deterministically cuts through the noise.

What's missing is structure: concept, sub-concept, and the relationship between them. This is also how a well-built lecture teaches a complex subject, and how a good slide deck gets built: one concept per slide, minimal words, relationships carried by layout instead of prose.
 
`structured-gist` renders that decomposition as an explicit tree instead of a paragraph the reader has to parse for it. We can't get rid of the AI slop, but we can push it to the peripheries and help you get to the gist faster.

<div align="right"><a href="#structured-gist"><sub>^ Back to top</sub></a></div>

## 2. Method

The example below compares Opus 5's unadulterated description of how this skill works vs. the dogfood-ed skill output. It covers the marker taxonomy and overall gist of how `structured-gist` works.

As a paragraph, it reads:

> structured-gist is a documentation tool that replaces verbose prose summaries with compact outlines, trading paragraphs a reader has to work through for a structure they can take in at a glance. Rather than relying on sentence grammar to carry relationships, it uses a role hierarchy in which each node's position in the tree encodes its meaning: a concept sits at the root, named attributes hang beneath it, ordinal or nominal enumerators sequence the branches, and prose explanations appear only as leaves. Because a format like that decays quickly when written by hand, a linter enforces it with fifteen rules in total. Two representative examples: one flags shallow-depth stalling, where a node occupies a level without contributing any real structure beneath it, and another detects punctuation-spliced facts, where two distinct claims are welded together with a comma or semicolon instead of being split into separate sibling nodes. The linter lives at lint_outline.py, depends only on the standard library, and applies all fifteen rules automatically. It fits session recaps, cause-chain explanations, and GitHub issue and PR comments — anywhere a reader needs to skim a structure rather than parse a paragraph for it.

Rendered as an outline in `skim` granularity and `block` mode (the default modal combination), the same content drops down 64% from 191 to 68 words. The tree also cuts parsing cost for the reader, but [Future work](#7-future-work) needs to quantify | qualify this.

```text
-- structured-gist
    ▸ Purpose
        ↪ replaces verbose prose summaries with compact
          outlines a reader takes in at a glance
    ▸ Mechanism
        ↪ role hierarchy, not sentence grammar, carries
          relationships: node position encodes meaning
    ▸ Role ladder
        i. concept
        ii. attribute
        iii. enumerator
        iv. explanation
- Linter
    ▸ Rationale
        ↪ the format decays quickly when hand-written
    ▸ Rules
        a. shallow-depth stalling
        b. punctuation-spliced facts
    ▸ Implementation
        a. lint_outline.py
        b. stdlib-only
- Fit
    a. session recaps
    b. cause-chain explanations
    c. GitHub issue + PR comments
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

No level given defaults to `skim`. No mode given defaults to `block` on all surfaces; pick `responsive` explicitly for a real GFM nested list on a markdown-rendering surface.

Trigger phrases: "structured-gist", "sg", "gist mode", "gist this", "outline this", "bullet this", "notes mode", "cliff notes", "spark notes", "structure this", "break this down", "distill this", "give me the gist", "make this skimmable", "tighten this up", "condense this".

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
| eval-only (#10) | semantic-compression suite curated: 8 regression/pressure-test cases, weighted retention scored against gold fact lists (sonnet run on all 8; haiku run on 3 of 8 — full-suite Opus 5 run planned this weekend) | weighted retention (skim → standard → deep) | 0.37 → 0.89 → 0.99; compression itself correlates *negatively* with usefulness (r = -0.75) — kept as a separate reported cost, never blended into a quality score |

Word count, rule/test coverage, and semantic retention (`skills/structured-gist/benchmarks/semantic-compression/`) are the metrics tracked today. Other metrics (reader comprehension, parse time) remain open; see [Future work](#7-future-work) for status and how to propose one.

<!-- README-EXAMPLE:START -->
## registrar-hedge (Before / After)

### Before (source)

```
Task: migrate the domain mindmatterbh.com from the old Squarespace site to an
already-deployed Cloudflare Pages site. Guide me click-by-click; I'll be
logged into the relevant dashboards and can screen-share tabs.

Context:
- New site: Cloudflare Pages project "mindmatter-bh", live at
  https://mindmatter-bh.pages.dev (direct wrangler uploads, not git-connected).
  Cloudflare account name: [account name redacted].
- CRITICAL: the same Cloudflare account also hosts my personal site (project
  [name redacted] / [redacted]). Do not touch that project or its DNS.
- Old site: Squarespace, still live at mindmatterbh.com. It must remain
  intact as a rollback target for ~2 weeks after cutover. Prefer a DNS-record
  cutover I can revert in minutes; avoid destructive steps (do not cancel the
  Squarespace subscription, do not delete the Squarespace site, do not
  transfer the domain registration itself right now).
- Registrar is unconfirmed - likely Squarespace Domains (site was built
  there), possibly Google Domains legacy or another registrar. Step 1 is
  identifying it with me (whois + what the Squarespace/Domains dashboard shows).

What I need from you, in order:
1. Identify registrar + current DNS host for mindmatterbh.com; list current
   DNS records so we have a written rollback snapshot before changing anything.
2. Decide the cleanest path for pointing apex + www at the Pages project.
   Constraint check: if the DNS stays at Squarespace, confirm whether its DNS
   supports what the apex needs (CNAME flattening/ALIAS); if not, walk me
   through moving just DNS hosting to Cloudflare (add site as a free zone,
   import records, switch nameservers) while keeping registration where it is,
   and note that this weakens the "instant rollback" property - tell me the
   actual rollback procedure and time for whichever path we take.
3. Lower TTLs first if the current host allows it.
4. In Cloudflare Pages > mindmatter-bh > Custom domains: add mindmatterbh.com
   and www.mindmatterbh.com, then make the DNS changes it prescribes.
5. Verify: apex + www resolve to the new site over HTTPS, cert issued,
   http->https and www/apex canonicalization work, and
   https://mindmatterbh.com/about (extensionless) returns 200.
6. Give me the exact rollback steps as a saved note, and remind me to submit
   the sitemap in Google Search Console after cutover.

Known open issue, for your awareness: the site's contact form backend is not
functional yet (being fixed separately). If we complete DNS today, that's
accepted - launch decision is mine.

```

### After (structured-gist rendering)

```text
- Domain migration
    ▸ Scope
        ↪ move mindmatterbh.com from Squarespace to
          Cloudflare Pages; Squarespace stays as rollback
          for ~2 weeks
    ▸ Registrar for mindmatterbh.com
        ↪ unconfirmed — likely Squarespace Domains,
          possibly Google Domains legacy, or another
          registrar
        a. Squarespace Domains
        b. Google Domains legacy
        c. Another registrar
    ▸ Step 1
        ↪ identify which registrar + current DNS host,
          snapshot all current DNS records before any changes
    ▸ DNS hosting decision
        I. if Squarespace hosts DNS: confirm it supports
           CNAME flattening/ALIAS for apex
        II. if not: move DNS to Cloudflare (free zone,
            import records, switch nameservers)
    ▸ Tradeoff
        ↪ DNS move weakens instant-rollback property;
          requires documented procedure instead
    ▸ Preference
        ↪ record-level cutover that reverts in minutes;
          no destructive steps (keep Squarespace site + subscription intact,
          do not transfer domain registration yet)
    ▸ Steps
        I. lower TTLs
        II. add custom domains (apex + www) in Cloudflare
            Pages UI
        III. apply DNS changes it prescribes
        IV. verify HTTPS, certs, canonicalization,
            extensionless paths
        V. save exact rollback procedure
        VI. submit sitemap to Google Search Console
    ▸ Open issue
        ↪ contact form backend is broken (being fixed
          separately) but user accepts the risk and will
          proceed

```

**Metrics:**
- Source: 384 words
- Rendering: 192 words
- Compression: 50.0%

**Key structure:**
- The registrar hedge is encoded as an attribute node (`▸`) with the uncertainty hedge on the node itself
- Three qualified candidates appear as enumerated children (a./b./c.) beneath the attribute
- This structure preserves the epistemic qualifier and its alternatives without flattening them into prose

<!-- README-EXAMPLE:END -->

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
- **Additional benchmark metrics**: word count, rule/test coverage, and semantic retention (see [Benchmarks](#5-benchmarks)) are the tracked metrics today. Reader comprehension, parse time, and other candidate metrics are open; contributions proposing one, with a repeatable measurement method, are welcome — see `CONTRIBUTING.md`.

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
