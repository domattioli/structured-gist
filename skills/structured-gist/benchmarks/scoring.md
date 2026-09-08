# Outline benchmark — scoring formulas, rationale, failure modes Spec of record: `/` (research.md D3–D8,
contracts/cli-contracts.md). This file is the FR-008 audit trail: every number
in a score record traces to a formula here. Constants here are echoed from
`score_outline.py` and checked by the final gate (M8): weights
`retention 0.5 / robustness 0.3 / brevity 0.2`, coverage threshold `θ = 0.5`,
tie threshold `ε = 1e-9`. ## Content units (retention denominator) Source and outline are normalized differently — they are different kinds of
text (D3): - **Source side**: NFC normalize → strip fenced-code content and inline code spans → lowercase → sentence-split on `[.!?]` + newline boundaries with abbreviation/decimal guards (`i.e.`, `etc.`, `Dr.`, `3.5` never split); markdown list lines are one unit each.
- **Outline side**: the outline is extracted via `lint_outline.extract_outline_from_text` (a block outline's fence is its *container*, never stripped as code — source-side stripping would zero the outline), then each node's content text via `lint_outline.parse_line` (drops markers and enumerator labels).
- **Shared token normalization**: split on non-alphanumeric → lowercase → drop stopwords (frozen ~120-word list in `content_units.py`) → 4-rule suffix stripper (`sses→ss`, `ies→i`, trailing-`s` drop, `ing`/`ed` drop with 3-char-stem guard).
- **Empty-unit rule (BL-2)**: a unit whose token set is empty after stopword removal is dropped from `units_total`; the count is reported as `units_dropped`. Never a 0/0, never silently counted covered. ## Retention `retention = recall = units_covered / units_total`, where a unit is covered
iff `|unit_tokens ∩ outline_tokens| / |unit_tokens| ≥ θ` (sets). **Precision** is reported separately (never blended — FR-003): fraction of
outline content tokens (set) present in the source vocabulary. Hallucinated
additions lower precision and can never raise recall. An outline with zero
content tokens: recall = 0.0, precision `ABSTAINED:no-outline-content`. Failure modes (accepted, documented): synonym paraphrase under-scores recall
(hits both compared modes equally — comparison-fair); the token bag ignores
negation ("not X" covers "X") — acceptable for mode-vs-mode deltas, wrong
tool for absolute quality certification. ## Brevity `brevity = clamp(1 − outline_content_words / source_content_words, 0, 1)`. **Multiset/set split (BL-1)**: brevity's numerator and denominator are
MULTISET token counts — every occurrence counts, so removing a duplicate word
moves the score (FR-004). Coverage and precision use token SETS. A verbatim
copy scores ≈0; the score improves monotonically as redundant wording drops.
A source with zero content words: `ABSTAINED:no-source-content` (abstains
retention + brevity; robustness still scores). ## Robustness `robustness = conformance = 1 / (1 + V)`, `V` = violation count from
`lint_outline.lint_text` (the skill's existing deterministic linter, imported
as the single oracle). Strictly lower for any violation; for a lint-clean
baseline, injected damage adds violations and cannot remove any, so a damaged
outline never outscores its intact original. **Perturbation-stability term: cut, twice, with proofs.** FR-005's
perturbation clause is formally waived on this record: 1. *Design 1* (4-perturbation recall-ratio mean — sibling-reverse, branch-delete, marker-corrupt, indent-corrupt): recall is an order-free token bag, so sibling-reverse, marker-corrupt, and indent-corrupt leave it byte-identical — 3 of 4 terms identically 1.0, a constant dressed as measurement.
2. *Design 2* (branch-delete recall ratio `recall(P2(o))/recall(o)`): (a) non-monotone — an outline with a redundant tail block scores HIGHER after deleting a content-bearing block (ratio denominator falls faster than the numerator); (b) its single-block fallback equals the clamped-1.0 reward it claimed to avoid; (c) it is a top-level-block-count proxy (evenly-covered N blocks score ≈(N−1)/N).
3. Any future stability term must ship with a counterexample-search test proving damage-monotonicity and block-count invariance. Prose proofs failed twice. Candidate for that future work: parse-tree edit distance. ## Composite `composite = 0.5·retention + 0.3·robustness + 0.2·brevity` (weights
configurable via `--weights <retention>,<robustness>,<brevity>` — positional
order explicit; must sum to 1.0 ± 1e-9). Ties declared at ε = 1e-9 on full
precision; serialized values rounded to 4 dp AFTER comparison. Any ABSTAINED
axis ⇒ composite ABSTAINED (no weight renormalization — one rule, stated). The comparison report also carries `composite_excl_conformance`
(retention/brevity renormalized 5/7, 2/7) because KG-mode conformance ≡ 1.0
by construction (self-lint gate) — tautological, so the headline verdict is
grounded in the conformance-excluded number first. ## Degenerate inputs (FR-007) | condition | result |
|---|---|
| empty/whitespace rendering | all axes `ABSTAINED:empty-rendering` |
| source < 2 units (after drops) | retention+brevity `ABSTAINED:single-fact-source` |
| `<mode>.SKIPPED` sentinel | all axes `ABSTAINED:mode-declined` |
| source content words = 0 | retention+brevity `ABSTAINED:no-source-content` |
| outline content tokens = 0 | recall 0.0; precision `ABSTAINED:no-outline-content` |
| all-stopword unit | dropped; `units_dropped` reported | Never a crash, never a misleading score; abstentions are named and counted in
the report's paired-aggregation tables.
