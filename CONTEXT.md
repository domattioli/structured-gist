# structured-gist

structured-gist renders explanatory/process-recap prose as a nested lecture-note outline (concept → attribute → enumerator → explanation). This context covers its output grammar and the semantic-compression benchmark that scores its fidelity.

## Language

**Semantic linkage**:
A relationship between two facts that a faithful rendering must preserve, beyond each fact's own content surviving individually. Encompasses the relation types already in informal use across `gold.json` test-case files (no formal schema yet) — at least 7 confirmed in-corpus: `causal`, `contrast_supersession`, `temporal_order`, `dependency`, `conditional`, `comparative_outcome`, `cause_rationale` (found in `registrar-hedge`, corrected from an earlier undercount of 6 — Opus review, 2026-09-12). Distinguished from mere fact retention (`hedge_survival_rate`, `weighted_retention`) — a rendering can retain every individual fact and still fail to preserve the linkage between them (e.g. losing that fact B superseded fact A, even though both facts are individually present).
_Avoid_: "relation" alone (ambiguous with the pre-existing `relations` array/`relation_retention` metric, which scores linkage via judge-read prose, not via structure)

**Structural encoding** (of a linkage):
The outline's tree shape/position itself — nesting depth, sibling order, enumerator family — conveying that two facts are linked, without an added cross-reference tag or id. Distinguished from *prose-carried* linkage, where the connection is only recoverable by a reader (or judge) parsing sentence content, with the tree shape itself indifferent to it. Current state: structured-gist has structural encoding only for the tree-shaped subset of linkage (parent/attribute-of via nesting, `temporal_order`/`dependency`-like sequence via enumerator order); `contrast_supersession`/`comparative_outcome` have no structural encoding today — they survive, if at all, purely as prose repetition, indifferent to tree shape.
_Avoid_: "linking the nodes" (implies an added tag/id mechanism — explicitly ruled out; the question is whether tree *shape* itself can represent the linkage)

**Node path**:
The sequence of node labels from an outline's root down to a given node (e.g. `["Checkout-service reliability", "Six alerts", "b. Critical incident", "iv. root cause"]`), capturing depth, parent chain, and sibling position. Not currently recorded anywhere in the pipeline — `judged/<tier>.json` fact verdicts carry only `{evidence, status}`, no positional data. Required as a prerequisite for any structural-linkage diagnostic (you can't check whether tree shape reflects a relation between two facts without knowing where each fact landed in the tree).
_Avoid_: "location" (too generic), "position" alone (ambiguous with sibling-order-only meaning; node path also captures depth/ancestry)

**Ordered relation** (vs. **membership relation**):
A `gold.json` relation whose `fact_ids` array conveys a genuine before/after or cause/effect sequence (e.g. `cause-chain-reversal` r1's causal chain). Distinguished from a **membership relation**, where `fact_ids` lists co-equal/unordered group members and no sequence is asserted — confirmed present in ~14 of 53 in-corpus relations (Opus review, 2026-09-12), including relations that explicitly assert NO ordering/dependency exists between the listed facts. `gold.json` does not currently distinguish these two cases structurally (no `ordered` field) — an initial design assumption that fact_ids order always encodes direction was checked against the full corpus and found false; a per-relation `ordered: true|false` (or `endpoints`-vs-`members`) field is a real prerequisite for any order-based structural check, not an optional refinement.
_Avoid_: assuming `fact_ids` order is always meaningful — verify per relation via the `ordered` field once it exists, never infer it from array position alone

## Flagged ambiguities

- "Relation" is heavily overloaded in this codebase: `gold.json`'s `relations` array + `combine.py`'s `relation_retention` metric already measure linkage *survival in rendered prose*, which is a different question from whether the *structural grammar* has a way to represent linkage on purpose. Investigation in progress is about the latter.
