# Decision gate log

Records for opus/terra-adjudicated decision gates (T017, T023a, T027a, T033, T054, T062). Each entry: gate id, ruling, reasoning.

## T033 — D4 cache-key tuple completeness (ruled by terra, supervisor)

**Ruling**: The plan.md D4 tuple — `(case_id, rendering_level, rendering_content, gold_content, prompt_content, model_id)` — is COMPLETE as specified, on the explicit condition that every `*_content` field is defined as the full literal text/JSON bytes hashed into the key, never an id, version pointer, or filename. Pinning that meaning now, in writing, so it cannot silently narrow later.

**Gaps raised by sol's prep analysis, resolved**:
1. Judge/scorer prompt template version — covered: `prompt_content` means the fully-rendered prompt text sent to the model, not a template id. A template edit changes the hashed bytes → correct cache miss.
2. Judge decoding params (temperature/top_p/max_tokens/seed) — NOT added to the tuple. Rationale: the harness's judged lane runs a single fixed decoding config today (no run-to-run param variation exercised anywhere in suite.json or run.py as scoped in this backlog). Adding unused key dimensions is speculative complexity plan.md doesn't call for. Documented here as a KNOWN LIMITATION: if a future change makes decoding params vary per run, the cache key must be extended before that lands, or results will silently conflate different decoding conditions under one hash.
3. Scoring/aggregation logic version (combine.py's interpretation of raw judge output) — NOT part of the cache key. Rationale: this is downstream of the model call; a combine.py code change is an ordinary code deploy, not a cache-invalidation concern — the cached judged verdict (the model's raw output) stays valid, only its downstream interpretation changes, and re-running combine.py's own tests covers that, not a cache miss. Out of scope by design, not a gap.
4. Gold schema version drift (T025 adds `epistemic`/`attaches_to` later) — covered: `gold_content` hashes the full `gold.json` file content, not a schema-version field, so any T025 schema change automatically changes the hash and busts the cache. No action needed.
5. Provider-side model drift (same `model_id`, provider silently updates server-side weights) — unfixable by any cache key. Documented as a KNOWN LIMITATION, not solved: `model_id` is the best available proxy; true immutability would require provider-side version pinning, which most providers don't expose.

**Action for T036 (run.py)**: implement the cache key over full literal content for all four `*_content`/`case_id`/`model_id` fields per the tuple above. Proceed — cleared.

## T054 — modality/polarity vocabulary for claim_list (ruled by terra, supervisor)

**Ruling**: APPROVED as proposed by sol, unmodified.

- `polarity`: `["affirmative", "negative"]` — binary, mirrors the existing `negation` gold-fact category (pre-dates this backlog). No third state.
- `modality`: `["assertion", "epistemic_hedge", "deontic_hedge"]` — `assertion` is the unqualified default; `epistemic_hedge` maps to US3's `epistemic` gold category (likelihood/certainty qualification); `deontic_hedge` maps to US3 Test Case 3 (obligation/permission — MUST/SHOULD/MAY), which this backlog's own issue-hedge-axis.md draft already treats as conceptually distinct from epistemic-likelihood even though both currently share one gold category. No "neutral"/"unknown" bucket — a claim with no detected hedge language defaults to `assertion`; FR-018b requires the renderer reject any value outside the enumeration, so every claim must resolve to one of the three.

**Reasoning**: fully grounded in artifacts this backlog and the pre-existing repo already wrote down — no invented category, no new design surface. Fits the escalation predicate (task's output determined by what's already on record) rather than requiring operator input.

**Action for T051**: wire this exact enumeration into `claim_list.schema.json`. Cleared to proceed.

## Gap-1 — hedge_survival_rate rendering-side match (ruled by operator via terra)

**Ruling**: Option A — full-document search, no localization. Drop "node(s) containing the bound fact" language from issue-hedge-axis.md entirely. Rendering-side survival check searches the WHOLE rendered output text for that case+rendering-level (not any node/section subset) for either the exact lexicon term or any term from the same lexicon category as the source hedge, case-insensitive substring match — the match logic itself (exact-or-same-category) was already correct and unchanged, only the search scope changes.

**Reasoning**: matches this metric's own documented division of labor (issue-hedge-axis.md line 179 — locality/migration-detection is explicitly `caveat_attach_accuracy`'s job, not `hedge_survival_rate`'s). No new mechanism invented; reuses the existing verdict-file-supplies-retained-status convention already used elsewhere in the harness. Known accepted tradeoff: full-doc search can false-positive "survived" if the hedge/category term appears elsewhere in a small rendering unrelated to the bound fact — accepted as low-risk given renderings are single test-case documents, and documented here rather than silently present.

**Action**: revise issue-hedge-axis.md to remove "node(s)" language, re-run a fresh third cold-read check per T023a, then proceed to T024 (file the issue) once that cold-read passes.

## T027a — hedge_lexicon.json citation review (ruled by operator via terra)

**Ruling**: Option 3 — dispatch a web-search-capable agent to verify all 6 distinct citations in hedge_lexicon.json (Hyland 2005, Lakoff 1973, Kilicoglu & Bergler 2011, Vincze et al. 2008, Hyland 1998, Salager-Meyer 1994, Marín 2010) before final operator sign-off. Bring findings (does each citation resolve/exist, does it roughly match the claim it's cited for) back for the operator's final approve/edit/drop call — this is NOT a rubber stamp on file existence, a real verification pass is required first.

**Action**: run the web-search verification pass, then route the findings back to the operator (via terra) for the actual T027a sign-off — the sign-off itself is still the operator's, this ruling only fixes HOW it gets prepared, not that it's needed. The lexicon stays DRAFT/unused until that sign-off lands (FR-007a unchanged), which still blocks T028-T030.
