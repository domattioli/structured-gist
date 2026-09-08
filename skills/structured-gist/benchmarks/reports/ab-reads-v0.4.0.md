# A/B blind reads — v0.4.0 corpus (user session, 2026-08-07) Protocol: 6 divergent pairs selected from the v0.4.0 comparison (largest
composite-excl gaps + both ld-* craters + one near-tie), blind-labeled A/B
with per-pair randomized assignment, read by the user in the Claude Code
chat surface. User stated preference + reasons. Assignment map was
recorded before presentation and un-blinded after all six verdicts. ## Results | pair | source | A | B | metric favors (excl) | user picked | agree? |
|---|---|---|---|---|---|---|
| 1 | ff-metric-glossary | kg | direct | direct (+0.2552) | direct — "can't tell the difference but I guess B" | weak yes |
| 2 | ld-migration-guide | direct | kg | direct (+0.1541) | **kg** | **no** |
| 3 | mx-postmortem-actions | kg | direct | direct (+0.1058) | direct | yes |
| 4 | mx-tooling-survey | direct | kg | kg (+0.0704) | **direct** | **no** |
| 5 | trade-off-model-tiering | kg | direct | kg (+0.0198) | **direct** | **no** |
| 6 | ld-incident-timeline | direct | kg | direct (+0.0267) | direct | yes | Tally: direct 5, kg 1. Metric–human agreement: 3/6 (one of the three a
coin-flip "can't tell"). The benchmark's composite-excl is a weak proxy for
user preference at current formula. ## User-stated reasons (verbatim intent, paraphrase-compressed) 1. Pair 1: no perceptible difference despite the corpus's LARGEST metric gap (0.2552) — retention deltas driven by dropped `↪` leaves read as near-invisible to a human skimming a glossary.
2. Pair 5: "the Risk bullet is too long on both" — overlong `↪` leaves are a defect in the user's eyes regardless of mode.
3. Pair 6: "both have bullets that use semicolons and/or clause-ending commas that violate the global rule of pushing those clauses to a new potentially further nested bullet" — the user applies the R9 delimiter-split expectation TO `↪` LEAVES, which R9 currently exempts as "the prose home."
4. Global: "the width of the code block seems to consume only half of the width of the claude code window, making me need to scroll more" — the R11 64-char hard cap under-fills the desktop chat viewport (same complaint class that produced `responsive` mode in v0.3.7, now aimed at block mode inside chat). ## Candidate deterministic features derived (for scorer/linter iteration) - **F1 leaf-length term**: per-`↪` word count cap or penalty (both modes offend; user names it unprompted). Candidate: penalty above N words per leaf, N calibrated from the pairs (pair-5 Risk leaves ≈ 20–24 words).
- **F2 R9-for-leaves**: extend delimiter-split scanning into `↪` leaf text (currently exempt). A leaf with `;` or a >2-word clause after a comma/colon is two facts wearing one leaf — split to sibling/nested leaves. Spec change to SKILL.md + lint rule, then flows into robustness axis for free.
- **F3 width utilization**: R11's 64-char cap wastes desktop width. Options: raise cap, make cap surface-parameterized, or route in-chat outlines to `responsive` (block reserved for committed `.md`/terminal). Needs user ratification — touches v0.3.6's phone-first rationale.
- **F4 metric recalibration**: retention recall over-weights dropped leaf detail the user cannot perceive (pair 1); composite-excl disagrees with the human 3/6. Any scorer v2 should validate against these six labeled pairs as a held-out preference set. ## Standing decisions this session (user-ratified) - Exit criteria for promote/shelve: composite delta threshold (mechanical).
- Next comparison adds a **direct+retry** third arm (lint-fix loop parity).
- KG word budgets negotiable — relax to recover retention.
- Responsive-mode KG render = hard prerequisite for promotion.
- Cost becomes a scored 4th axis (KG currently emits ~5× direct's bytes; see `cost_report.py`).
- Long documents stay in scope; fix both modes on ld-*.
- Composite weights: sweep shows verdict nearly weight-invariant (`weight_sweep.py`: 0 promote / 144 iterate / 27 shelve of 171 triples on excl composite) — no weighting makes KG win content quality.
- Graph is a means to determinism, not a first-class artifact; must not significantly degrade cost.
- v0.5 metric re-declaration + hybrid mode: deferred pending this data.
