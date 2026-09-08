# structured-gist — deterministic test results (v0.3.2)

**Date**: 2026-07-04 · **Mechanism**: `lint_outline.py` (Python stdlib, no LLM, no RNG, no clock → byte-reproducible). v0.3: 17 pytest cases + 44 smoke checks green; attribute marker `▸`, non-leaf `↪`, R8 no-self-nest. v0.3.1 added every-fenced-block coverage for SKILL.md + example files (the linter auto-extracts only the first block). v0.3.2 added R9 delimiter-split (19 pytest cases; new `good_r9.md`/`bad_r9.md` fixtures).

## Test subject

"How does this skill work?" — rendered by structured-gist itself, covering every
current rule (marker ladder, ordinal-vs-nominal, length gradient +
connective-clause test, granularity, render modes, spacing, emphasis, leaf
preservation, carve-outs, caveman independence): full content lives in
`examples/self-explain.md` (not re-quoted here — a prior version of this file
inlined the outline verbatim and drifted stale against the actual example
after the v0.2.5 taxonomy redesign; single source of truth now). GitHub
authoring is no longer a structured-gist rule as of v0.2.11/ — it moved to
``  since it's this repo
comment-discipline policy, not a rule of this skill.

## Verdict

```
structured-gist-lint skim.md: PASS (0 violations)
structured-gist-lint standard.md: PASS (0 violations)
structured-gist-lint deep.md: PASS (0 violations)
structured-gist-lint caveman-combo.md: PASS (0 violations)
structured-gist-lint self-explain.md: PASS (0 violations)
exit=0
DETERMINISTIC ✓ (identical output across repeated runs)
```

## What the linter checks (deterministic rules, v0.3 taxonomy)

- **R1** ladder-by-depth — L1 `-` only · L2 `I.`/`A.`/`▸` (or `↪`) · L3+ `i.`/`a.`/`▸` (or `↪`) · plain `•` bullet banned at every depth. The attribute marker `▸` (family `attr`) is valid at any depth ≥1.
- **R2** no skipped rungs (depth ≤ prev+1)
- **R4** (v0.3, revised) a `↪` MAY have children; a **non-leaf** `↪` must be the **first child** of its parent (summary-before-detail). A leaf `↪` is valid anywhere. (Pre-v0.3 this rule was "`↪` is a leaf, no children" — relaxed per .)
- **R5** arrow rarity — per top-level block, `↪` count ≤ depth-1 non-arrow node count (attributes count toward the denominator)
- **R6** sibling-family consistency (non-arrow siblings under one parent share one family; `↪` exempt; `▸` is its own family — an all-attr sibling set is consistent)
- **R7** word caps (L1 dash ≤3 words, L3+ ordinal/nominal ≤6, **`▸` attribute ≤4**; L2 enumerator and `↪` exempt)
- **R8** (v0.3, new) no-self-nest — a `▸` may not be the direct child of a `▸` (user directive; interpose a `↪` hook or an enumerator to nest deeper)
- **R9** (v0.3.2, new) delimiter-split — a structural (non-`↪`) node that appends **>2 words** after a space-flanked dash (` - `/` — `), colon, semicolon, arrow (`→`), or inside a parenthetical is two nodes wearing one marker → split the tail to a nested child. Tails of ≤2 words stay inline. Exempt: the `↪` leaf (prose home), intra-word hyphens (`lecture-note` is one word), inline code (`file:line`). Generalizes the connective-clause test (words → punctuation).

(R3 — the old "bold every L1 top" check — was removed in the v0.2.5 taxonomy
redesign along with the `•` bullet and the `→`-as-leaf marker; bold tops are
now an `inline`-mode-only style choice, not a lint-gated rule.)

## Negative controls

Bad fixtures (`tests/fixtures/bad_*.md`) each break exactly one rule → linter flags each. `test_lint.py` (pytest) asserts examples + good fixtures clean and bad fixtures dirty. v0.3 additions: `bad_attr_self_nest.md` → R8, `bad_nonleaf_arrow_not_first.md` → R4; `good_attribute.md` + `good_nonleaf_arrow.md` lint clean. v0.3.2 additions: `bad_r9.md` (5-word semicolon tail) → R9, `good_r9.md` (≤2-word delimiter tails) lint clean. The pre-v0.3 `bad_arrow_child.md` was retired — the rule it guarded ("`↪` is always a leaf") was the exact rule R4 relaxed, so that outline is now valid by design; its role as the R4 negative control passed to `bad_nonleaf_arrow_not_first.md`.

## Note — the gate has teeth

During authoring, the linter caught a genuine violation: `standard.md` had a 6-word L2 bullet ("all 77 skills load at start") exceeding the R7 cap of 5 → reworded to "77 skills load at start". An LLM-judge would not have flagged that reproducibly; the deterministic linter did.
