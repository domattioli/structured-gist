---
status: accepted
---

# Judge-derived node path for structural-linkage diagnostic

To measure whether an outline's tree shape (not prose) encodes semantic linkage between facts, we need to know which node each fact landed in. We considered mechanical parsing + fuzzy text-matching against each fact's `source_quote` (no new judge work, but fragile — facts are paraphrased, not quoted verbatim, especially at `skim` level where compression rewords most). We chose instead to extend the existing judge pass to record each fact's node path (depth/parent chain/sibling position) alongside its `status`, since the judge already reads the full rendering to score `relation_retention` and this adds negligible extra cost while avoiding matching fragility exactly where it would be worst.
