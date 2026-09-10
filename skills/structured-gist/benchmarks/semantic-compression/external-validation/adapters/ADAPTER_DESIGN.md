# External semantic-gold adapter — design

This document is written *before* any semantic decomposition happened
this session, per the task brief's "before implementation, summarize
which existing metrics require what." It is the ground-truth reference
for what `common.py` / `qmsum.py` / `qasper.py` / `hotpotqa.py` /
`validate_derived_gold.py` implement, and for `ANNOTATION_PROTOCOL.md`'s
instructions.

## 0. What existing metrics actually read (verified against source, not assumed)

Read in full this session: `../scoring/combine.py`, `../scoring/spr.py`,
`../gold.json` examples (e.g.
`../regression/real-hook-discovery/gold.json`),
`../scoring/blind_weights/*.json`. `../scoring/findability.py` and
`../scoring/wording_fidelity.py` (PR #18) do **not** exist on this branch
(branched from `main`, before #18 merged) — see "Dependency on #18" below.

| requirement | needed by | exact field(s) read |
|---|---|---|
| **1. semantic facts** | `combine.py::score_semantic` (`task_weighted_fact_retention`, `unweighted_retention`, `omission_rate`, `mutation_rate`); `spr.py::score_spr` (`blinded_task_weighted_fact_recall`, SPR, critical-unit diagnostics) | `gold["facts"]`: each needs `id`; `combine.py` additionally needs `weight` (a number) on every fact — see row 3 |
| **2. semantic relations** | `combine.py::score_semantic` (`relation_retention`); `spr.py::score_spr` (`task_weighted_relation_recall`, SPR, critical-unit diagnostics) | `gold["relations"]`: each needs `id` only for the arithmetic (no other field is read by either scorer) |
| **3. task weights** | `combine.py`'s `task_weighted_fact_retention`/`weighted_retention` reads `gold.json`'s per-fact `weight` (legacy, category-derived scale `{1, 2, 2.5, 3}`) directly off each fact dict; `spr.py` reads a **separate** file, `blind_weights/<case_id>.json` (`fact_weights`, `relation_weights`, both id -> `{1,2,3}`), and never touches a fact's `weight` field | see "Weight strategy" below — this corpus does **not** populate a category-derived `weight`; the adapter synthesizes one from the same blinded Stage-B annotation `spr.py` already uses |
| **4. questions/reference answers** | `combine.py::score_semantic` (`recoverability`) | `gold["questions"]`: each needs `id` only for the arithmetic (`fact_ids` is documentation, not read by either formula) |
| **5. source quotes** | not read by `combine.py`/`spr.py` arithmetic at all (they only read structured judge verdicts from `judged/*.json`, never `source.md`) — but required by (a) the future isolated judge that produces those verdicts, and (b) this session's own `validate_derived_gold.py` source-support check | `gold.json` facts/relations carry `source_quote` for judge/human reference; not a scorer input |
| **6. no adapter at all** | compression/reduction% (`deterministic.py`, reads only source/output word counts); structural conformance (`../../tests/lint_outline.py`, reads only rendered output syntax) | neither reads `gold.json` in any form |

**`recoverability`'s `fact_ids` field is documentation only in current
scorer code** — worth flagging since the task brief lists "recoverability
inputs" as something to inspect: the *arithmetic* needs nothing but a
question `id`; `fact_ids` exists so a human reading `gold.json` can see
which facts a question is testing. This corpus still populates it (see
"Questions" below) because it costs nothing and preserves that
readability, not because the scorer requires it.

### Dependency on #18

`findability.py` and `wording_fidelity.py` (PR #18) both operate on
*rendered output text vs. `source.md`*, not on `gold.json`'s fact/relation
schema at all (confirmed by reading `wording_fidelity.py`'s and
`findability.py`'s signatures during the corpus-freeze session, and by
their total absence of any `gold.json` field access). They therefore need
**no adapter work** once #18 merges — they should consume `source.md`
(native, untouched by this session) directly. This is flagged, not
verified against the actual merged code, since #18 has not merged as of
this session; the eval-running session should confirm this assumption
once it has.

## 1. Architecture

```
public benchmark annotation                (QMSum/Qasper/HotpotQA upstream)
        v
external_gold.json                         (frozen in PR #19 -- NEVER edited here)
        v
derived_gold.json                          (this session: facts + relations,
                                             lineage back to native_evidence)
        v
derived_blind_weights.json                 (this session: independent Stage-B
                                             1-3 task-importance annotation)
        v
adapters/common.py::to_gold_view()         (RUNTIME view: gold.json-compatible
adapters/common.py::to_blind_weights_view() dict, generated on demand -- never
                                             written to disk as a file literally
                                             named gold.json)
        v
future structured-gist evaluation          (combine.py / spr.py, next session)
```

`derived_gold.json` and `derived_blind_weights.json` are real committed
files (the frozen adapter output). The `gold.json`-shaped view is
deliberately **not** a third committed file — `to_gold_view(case_id)`
in `common.py` builds it in memory from the two committed files above,
so nothing on disk is ever named `gold.json` for external cases (the task
brief: "prefer generating it at runtime from derived_gold.json rather
than making the adapted artifact look indistinguishable from native
gold"). A future eval session that wants a literal `gold.json` file for
some tool that hard-requires that filename can call
`common.write_gold_view_file(case_id, dest)`, which still sources from
`derived_gold.json` + `derived_blind_weights.json` every time it's
called, and is never invoked by anything in this PR.

## 2. Weight strategy

`combine.py` and `spr.py` have historically used two *different* weight
sources for two different purposes (see `../README.md` "Weight
semantics" and `spr.py`'s module docstring): a category-derived legacy
weight baked into `gold.json`, and a separately-annotated blind
task-importance weight in `blind_weights/*.json`, kept apart specifically
so `spr.py::compare_weights()` could ask "was the old heuristic already a
good proxy?" — a question that presupposes the *existence* of an
un-blinded, category-derived weight to compare against.

This corpus has no such heuristic to compare against (the task brief is
explicit: "do not reuse historical category weights... any task weights
must be task-conditioned"), so there is nothing for `compare_weights()`
to meaningfully run against these cases, and this adapter does not try to
manufacture a second weight source just to keep that diagnostic company.
Instead:

- `derived_gold.json` facts/relations carry **no** `weight` field at all.
  A `category` field is preserved on facts for human interpretability
  only (per the "Field classification" table below) — the adapter never
  reads it as a weight.
- `derived_blind_weights.json` (Stage B, this corpus's only weight
  source) is schema-compatible with `../scoring/blind_weights/*.json`
  (`fact_weights`, `relation_weights`, both on the `{1,2,3}` scale,
  `rationale` per id) but carries `"annotation_protocol":
  "external-blinded-task-importance-v1"` — a distinct protocol id from
  the native corpus's `"blinded-task-importance-v1"`, since the
  annotation instructions differ (external benchmark task framing, not
  a hand-authored case's own README-defined intent) even though the
  scale and semantics are identical (1=supporting, 2=material,
  3=critical).
- `common.py::to_gold_view()` copies each fact's Stage-B `fact_weights[id]`
  into that fact's `weight` key in the generated view, so
  `combine.py`'s `task_weighted_fact_retention` is computed from the
  *task-conditioned* blind weight, not a fabricated category default —
  this is a deliberate improvement over how the native corpus's
  `weighted_retention` is currently computed, not a compatibility shim.
  `spr.py` reads `derived_blind_weights.json` directly (its native input
  shape), unchanged.

## 3. Field classification

Applied per dataset in `ANNOTATION_PROTOCOL.md`; summarized here.

| field | classification | notes |
|---|---|---|
| `question_or_query` / `reference_answer` | **Native** | copied verbatim from `external_gold.json`, never re-derived (task brief: "do not reinvent Q&A where the public benchmark already gives us one") |
| `intent.reader` / `intent.task` | **Native** | copied verbatim from `external_gold.json`'s `intent` (already a fixed template per dataset, set during corpus freeze) |
| fact/relation existence, text, `source_quote` | **Human/model-annotated** (isolated agent, Stage A) | requires semantic judgment over source + native evidence + question/answer |
| fact/relation `derived_from` (native evidence ids) | **Deterministically derived** | the annotator names which native evidence it drew from; `validate_derived_gold.py` mechanically checks the id exists in `external_gold.json.native_evidence` |
| fact `category` | **Human/model-annotated**, informational only | same category vocabulary as `gold.json` (`descriptive`/`constraint`/`decision`/... — see `ANNOTATION_PROTOCOL.md`); never consumed as a weight signal, per "Weight strategy" |
| relation `type` | **Human/model-annotated** | same vocabulary as `gold.json` (`causal`/`temporal_order`/`dependency`/...) plus the task brief's additions (`contrast`, `supersession`, `condition`, `decision_outcome`, `problem_resolution`) |
| relation `evidence_mode` | **Deterministically derived from the annotator's own claim** | the annotator states `"explicit"` (relationship stated in source text) or `"inferred"` (necessary composition, not literally stated); `validate_derived_gold.py` only checks the field is one of the two allowed values and is present — it cannot independently verify which is true, that judgment stays with the annotator/coverage-audit pass |
| `questions[0]` (single native Q&A, wrapped) | **Native** + **Deterministically derived** | the question/answer text is native; `fact_ids` (which derived facts the question draws on) is the annotator's own linkage, informational per the "recoverability" row above |
| fact/relation `weight` (Stage B, 1-3) | **Human/model-annotated** (isolated agent, Stage B, independent pass from Stage A) | never derived from `category`/`type` |
| corpus-defect flags (malformed native data discovered during annotation) | **Human/model-annotated**, recorded not silently fixed | see task brief "What NOT to do" — a genuinely malformed frozen case is documented as a defect, not swapped |
| per-case coverage-audit verdict | **Human/model-annotated** (isolated agent, separate pass) | "is any task-critical proposition/relationship missing" |
| anything not listed above (e.g. discourse structure, speaker intent beyond what's needed for the question, exhaustive entity lists) | **Unsupported** | left absent; a missing relation/fact is preferred over a fabricated one, per the task brief |

## 4. Semantic-unit granularity rule

**One independently meaningful proposition per fact; one task-relevant
relationship per relation.** Not maximal atomization, not lossy merging.
Concretely, `ANNOTATION_PROTOCOL.md` instructs annotators to reject:

- splitting one proposition across multiple facts to inflate weighted
  recall against a hypothetical scorer
- merging several independent propositions into one fact so a partial
  loss can't be detected
- a relation that only restates two facts already independently listed
  (i.e., "fact A and fact B coexist" is not a relation — a relation must
  state *how* they relate: causal, temporal, dependency, contrast,
  condition, supersession, decision->outcome, problem->resolution)
- copying `reference_answer` wording into a fact's `text` when the
  underlying source evidence actually supports a narrower or hedged
  claim (the fact must be traceable to `source_quote`, not to the
  benchmark's own answer string)
- a relation duplicated as a fact, or vice versa
- inflating relation count by adding edges between facts that don't need
  connecting to answer the question (task brief: "if the answer depends
  only on independent facts, relations may legitimately be empty")

`validate_derived_gold.py` cannot fully enforce this mechanically (it is
a judgment call), but it does mechanically flag two proxies for gaming:
a case whose fact count is far outside this corpus's observed
distribution for its dataset (reported, not blocked — see
`FINDINGS.md`), and any relation whose `text` is a near-duplicate of one
of its linked facts' `text` (Jaccard word overlap above a fixed
threshold, reported for human review).

## 5. Adapter code map

- `common.py` — shared dataclasses/schema validation, `to_gold_view()`,
  `to_blind_weights_view()`, `write_gold_view_file()`, native-evidence-id
  helpers shared by all three per-dataset modules.
- `qmsum.py` / `qasper.py` / `hotpotqa.py` — thin, dataset-specific:
  each exposes `native_evidence_id(entry) -> str` (the deterministic id
  scheme below) and `load_case(case_id)`. No scoring logic lives here.
- `validate_derived_gold.py` — fully offline integrity checker for the
  derived layer (mirrors `../scripts/verify_corpus.py`'s role for the
  native layer): lineage, id uniqueness, weight coverage, serialization
  determinism. Never modifies `../scripts/verify_corpus.py` itself, and
  never re-checks anything that script already covers (native hashes).

### Native-evidence-id scheme (used in every `derived_from` entry)

| dataset | id format | example |
|---|---|---|
| qmsum | `span:{span_index}` | `span:0` |
| qasper | `para:{global_idx}` | `para:31` |
| hotpotqa | `{title}::sent{sent_id}` | `Neo-libertarianism::sent3` |

## 6. What this design deliberately does not do

- Does not touch `combine.py` or `spr.py`. Both already support exactly
  the inputs this adapter produces (a `gold.json`-shaped dict, a
  `blind_weights`-shaped dict); no scorer code changes are needed, so
  none are made.
- Does not pool QMSum/Qasper/HotpotQA gold into one shape beyond the
  shared `derived_gold.json` schema — each dataset's `native_metadata`
  (domain, cardinality, evidence distance, `pressure_only`, etc.) is
  copied through unchanged from `external_gold.json` into
  `derived_gold.json.native_metadata_ref` territory (a pointer, not a
  copy — see schema below) so nothing about dataset identity is lost or
  homogenized.
