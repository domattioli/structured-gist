# Investigation: does structured-gist's output STRUCTURE represent semantic linkage?

Status: PLAN v2 (post-Opus review), not yet built. v2 scopes to `standard`
granularity only — `skim` deferred entirely, `deep` deferred to a later
phase — per operator call, 2026-09-12. See "Revision (v2...)" section below
for what changed and why before treating any Decision above it as current.
Not part of `specs/001-backlog-hedge-fidelity/` — that spec's Scope Statement binds
it to its own eleven steps; this is a separate, newly-surfaced investigation.

## Question

structured-gist's benchmark already measures whether individual facts survive
compression (`weighted_retention`) and whether relationships between facts
survive *in the rendered prose* (`relation_retention`, judge-read). Neither
answers a different, structural question: does the outline's tree SHAPE
itself — nesting, depth, sibling order — represent semantic linkage between
facts on its own, independent of whether a reader/judge can piece the
relationship together from wording? This is not about adding a cross-
reference tag between nodes; it's about whether the structure the renderer
already produces incidentally or deliberately encodes relationships.

## Definitions (see repo `CONTEXT.md` for the canonical glossary entries)

- **Semantic linkage**: a relationship between two facts, scoped to the 6
  relation types already in ad hoc use across `gold.json` files: `causal`,
  `contrast_supersession`, `temporal_order`, `dependency`, `conditional`,
  `comparative_outcome`. No formal schema/enum enforces this list today.
- **Structural encoding**: the tree shape (not prose) conveying a linkage.
- **Node path**: the sequence of node labels from root to a node, capturing
  depth/ancestry/sibling position. Not currently captured anywhere in the
  pipeline (`judged/<tier>.json` fact verdicts carry only `{evidence, status}`).

## Decisions made during design interview (2026-09-12)

1. **Scope**: all 6 relation types, expecting `contrast_supersession` and
   `comparative_outcome` to be the hardest — they connect facts that are
   often narratively distant and have no fixed "correct order."
2. **Audit before design**: build a diagnostic that measures whether
   CURRENT renderings' tree shape already encodes each relation type,
   before writing any new grammar/`SKILL.md` rules. Don't design a fix for
   a problem we haven't confirmed exists, and don't skip fixing one that
   does.
3. **Node-path source**: judge-derived, additive pass (see ADR
   `docs/adr/0001-judge-derived-node-path.md`). A subagent per (case, tier)
   is given the rendering plus the ALREADY-RECORDED `evidence` quotes from
   existing `judged/<tier>.json` files, and asked only to locate which
   outline node contains each quote and record its node path. This does
   NOT re-litigate fact/relation/question status — those verdicts are
   reused as-is. Chosen over full re-judging (avoids re-churning trusted
   verdicts) and over mechanical text-matching against `source_quote`
   (fragile exactly where compression paraphrases most, i.e. `skim`).
4. **Two structural criteria, not one**:
   - **Order**: for `temporal_order`, `dependency`, `conditional`, and
     `causal` when the source narrative itself is order-preserving — do
     the related facts' node paths appear in the same relative order
     (sibling/enumerator/traversal order) as the relation's stated
     sequence?
   - **Proximity/grouping**: for `contrast_supersession`,
     `comparative_outcome`, and `causal` always (in addition to order when
     applicable) — are the related facts closer together in the tree
     (smaller tree-distance via LCA) than an unrelated pair would be?
   - `causal` is checked on BOTH criteria, not bucketed into one, because
     `cause-chain-reversal` is a named pressure-test specifically built to
     defy order (the real cause is revealed structurally later than its
     effect) — this diagnostic should be able to surface that as a
     genuine order-criterion failure while still checking proximity.
5. **Order-direction ground truth**: `gold.json` relations' `fact_ids`
   array order already conveys before/after direction as an informal,
   unenforced authoring convention (verified across ~30 existing relation
   entries — held consistently). Decision: DOCUMENT this convention
   explicitly (in this investigation doc and, if the diagnostic is later
   built, as a comment near wherever it's consumed) rather than build
   automated enforcement now — enforcement would require cross-referencing
   `source_quote` character offsets against `source.md`, which isn't
   captured today either, and isn't blocking this diagnostic.
   For chained relations (`fact_ids` with 3+ entries, e.g. a causal chain
   A→B→C), the order check validates each CONSECUTIVE pair, not just
   first-vs-last.
6. **Statistical design**: NOT a per-case significance test (individual
   cases are too small — as few as 4-12 relations per case — for a
   permutation test to have real power). Also not naive corpus-wide
   pooling (relation-instances are clustered by case, not i.i.d., since
   the same relation recurs across a case's 3 levels × up to 2 tiers).
   Decision: pool across tier × level for a much larger dataset than
   per-case counting suggests — 231 relation-instances across 33
   renderings, from the 8 of 9 cases with judged data (`registrar-hedge`
   has none) — but run a STRATIFIED-BY-CASE permutation test: permute
   fact-pair assignment within each case's own tree only (never across
   cases), then aggregate the resulting effect sizes/p-values across
   cases. This respects the clustering while using the full available
   dataset, and was chosen only after confirming a larger dataset was
   available for free (pooling tier×level) rather than requiring new
   test-case authoring.
7. **Dataset scope for v1**: the existing tier/level judged corpus
   (haiku/sonnet renderings, 8 of 9 cases), NOT the `sg-alone`/
   `sg-plus-caveman-lite` conditions corpus. The conditions corpus has NO
   judged data at all — that is T061's separate, currently-held blocker
   (see `specs/001-backlog-hedge-fidelity/decisions.md` "T060/T062 —
   CLOSED" entry's "Open gap surfaced" note). This investigation is
   deliberately decoupled from T061; if this investigation's findings are
   interesting, extending it to the conditions axis becomes a later
   argument for un-holding T061, not a prerequisite for this work.
8. **Artifact location**: this standalone doc under `docs/investigations/`,
   not a new numbered `specs/NNN-.../` scaffold — promoting this to a real
   spec (with tasks, a build order, etc.) is a decision to make only AFTER
   Opus's review confirms the plan holds up, not before.

## What this diagnostic does NOT do (explicitly out of scope for v1)

- Does not touch `SKILL.md`, the grammar, or the linter (matches this
  benchmark suite's existing stated convention in its own `README.md`:
  "Nothing here changes SKILL.md, the grammar, or the linter").
- Does not build or extend the `sg-alone`/`sg-plus-caveman-lite` judging
  pipeline (that's T061, held separately).
- Does not attempt automated enforcement of the `fact_ids`-order authoring
  convention (documented only, per decision 5).
- Does not propose any new grammar mechanism (e.g. a cross-reference
  marker) — per the operator's clarification, the question is whether
  EXISTING tree shape already encodes linkage, not whether to add a new
  linking mechanism.

## Opus review findings (2026-09-12) — verdict: NEEDS REVISION, not fundamentally flawed

Independently verified the corpus claims (231/33/8-of-9 all confirmed exact,
no node-path data anywhere confirmed) but found 4 BLOCKING issues in the
measurement design itself:

1. **BLOCKING** — Decision 5's "`fact_ids` order encodes direction
   consistently" is false corpus-wide. ~14 of 53 relations use `fact_ids`
   as an unordered membership set or a singleton, not a directional
   sequence (e.g. `negation-and-true-peers` r2 explicitly asserts NO
   dependency exists between its listed facts). Scoring these against an
   "order" criterion manufactures failures for exactly the relation types
   (`contrast_supersession`, `comparative_outcome`) already predicted to
   look worst — a self-fulfilling result. Fix: `gold.json` needs an
   explicit `ordered: true|false` (or `endpoints`-vs-`members`)
   annotation per relation before the order criterion is computable. This
   is a real prerequisite, not documentation-only as originally written.
2. **BLOCKING** — proximity is degenerate at `skim` (every skim rendering
   is exactly 2 levels deep per SKILL.md spec, so LCA-distance collapses
   to a binary same-parent/not indicator) and only 156 of 231
   relation-instances have all endpoints actually rendered (14/89 at
   skim) — informative missingness correlated with retention, not random.
3. **BLOCKING** — the order criterion ignores SKILL.md's own explicit
   ordinal-vs-nominal enumerator-family rule (roman = order matters,
   letter/attribute = order-agnostic by design). Scoring sibling order
   inside a nominal (letter/`▸`) sibling set is a category error — the
   grammar already declares order carries no meaning there. Must condition
   the order check on marker family.
4. **BLOCKING** — the additive judging pass's premise (locate nodes via
   existing `evidence` quotes) fails on real data: only 339/789 (43%)
   `evidence` values are literal substrings of their rendering; 272 are
   paraphrased, "evidence of absence" (unlocatable in principle), or
   multi-node composites (one fact spanning a node + its `↪` child, per
   SKILL.md's own R9/non-leaf-`↪` rules — a structural guarantee that some
   facts have no single node). Also: there is no live judge pass to ride
   on (re-judging is manual/agent-driven per the benchmark README) — this
   is a new 33-subagent run, not "negligible extra cost" as ADR-0001 claims.

Plus 3 WORTH-FIXING (stratification model incomplete — shared endpoints
within a rendering, level-nesting skim⊂standard⊂deep, ambiguous
permutation unit, effective-n really ~8 not 231; corpus itself is 56%
non-conformant to its own grammar, confounding a null result; several
cases are organized by source topic, so proximity may just restate
topical sectioning, not linkage) and 3 MINOR (7th relation type
`cause_rationale` exists in-corpus, contradicting the "6 types" framing;
Decision 1 and Decision 5 directly contradict each other on whether
`fact_ids` order is meaningful — same defect as #1 above; `claim_list.
schema.json`'s `source_span{start,end,text}` is unused prior art for the
node-path schema).

One point noted IN THE PLAN'S FAVOR: Decision 7 (defer conditions axis)
is defensible but under-argued — SKILL.md's stated caveman/structure
independence gives an a priori, falsifiable reason tree shape shouldn't
move under caveman-lite, stronger than "no judged data exists yet."

**Verdict**: investigation is worth running, not abandoned. As originally
scoped it would produce a low-power result confounded with tree topology,
source sectioning, and pre-existing corpus non-conformance — largely
evidence about `gold.json`'s authoring conventions, not about
structured-gist. Required before implementation: (1) add `ordered`/
`endpoints`-vs-`members` to gold relations, (2) condition order-checking
on enumerator family, (3) restrict v1 proximity analysis to
`standard`/`deep` (n=143) or add topology/topic controls, (4) pilot the
additive judging pass on ONE case before committing to all 33 renderings,
with a schema admitting multi-node/not-locatable outcomes, (5) restate
the permutation design with rendering as the unit and effective-n stated
honestly.

## Revision (v2, post-Opus review + operator's skim-deferral call, 2026-09-12)

Supersedes the conflicting parts of Decisions 1/4/5/6/7 above. Kept for
history; v2 is the plan actually going forward.

**Granularity scope narrowed to `standard` only, skim excluded entirely.**
Operator call: defer `skim` altogether (not just down-weight it) and focus
on one default modality — `standard` — until the method is well-established
there; `deep` deferred to a later phase, not v1. This also resolves Opus
Finding 2 (skim's 2-level tree makes proximity degenerate) by construction,
without needing a topology-normalization fix yet.

Dataset at `standard` only: 77 relation-instances across 11 renderings (8
cases; 3 of them — `cause-chain-reversal`, `migration-tristate`,
`synthetic-scale-verylarge` — have both haiku and sonnet tiers, contributing
2 renderings each), 67 of which have both endpoints actually locatable
(recomputed from Opus's per-level table). `registrar-hedge` stays excluded
(no judged data). Effective-n for the stratified test is still ~8 (one per
case), not 67 or 77 — state this honestly in any write-up, per Opus Finding
5, rather than implying more independent power than exists.

**Fix for Finding 1 (order not computable without ground truth) —
prerequisite task added:** before any order-criterion scoring, every
`standard`-relevant relation in the 8 judged cases' `gold.json` needs an
explicit `ordered: true` (genuine before/after sequence) or `ordered:
false` (unordered membership set) field added by hand-review — do NOT
infer it from `fact_ids` array position. Membership relations get
proximity-only scoring; only `ordered: true` relations get the order
check. This is now a real, scoped, small task (annotate ~53 relations
once, corpus-wide — cheap to do even though standard-only is today's
scope, since it's needed the moment deep/skim are revisited later).

**Fix for Finding 3 (enumerator-family category error) — order check
conditioned on marker family:** the order criterion only applies when
BOTH related facts sit under ordinal (roman `I./i.`) enumerator families.
If either fact sits under a nominal (letter `A./a.`) family or a `▸`
attribute, the relation is scored on proximity only — per SKILL.md's own
stated rule that nominal/attribute siblings are order-agnostic by design,
scoring their order would be a category error, not a finding.

**Fix for Finding 4 (additive judging pass premise fails on real data) —
pilot-first, schema widened:** before committing to all 11 `standard`
renderings, pilot the additive judging pass on ONE case first
(`cause-chain-reversal` — relation-rich, has both tiers, already used as
the worked example throughout this doc). The node-path schema must admit
three outcomes per fact, not just a path: `located` (path found),
`multi_node` (evidence spans 2+ nodes — record both paths), `not_locatable`
(evidence describes an absence or is too paraphrased to place). Do not
assume this is free/riding on an existing pass — ADR-0001's "negligible
extra cost" framing is corrected: this is a new, separately-costed
subagent dispatch per rendering.

**Fix for Finding 5 (permutation design underspecified) — restated:**
permutation unit is one rendering's own tree (not "a case," which spans
multiple renderings). For each rendering, permute which fact-pairs are
"related" vs "random" WITHIN that rendering's own relation set and fact
set only. Aggregate the resulting per-rendering effect size up to one
effect size per case (mean or median across that case's renderings), then
report the across-case distribution (~8 points) descriptively — no
corpus-wide p-value implying 67-77 independent samples. Within-rendering
shared-endpoint dependence (Opus's chained-relation point) is accepted as
a known limitation for v1, not solved — flag it in the eventual write-up
rather than attempting a fix now.

**Explicitly retained as stated limitations, not fixed in v1** (per Opus
Findings 6, 7 — accepted, not solved): the corpus is 56% non-conformant to
its own grammar corpus-wide (state this as a confound on any null result);
several cases are organized by source topic, so a proximity finding may
partly restate topical sectioning rather than linkage — no topic-control
added in v1, flag as an open confound in the write-up.

**Decision 7 (defer conditions axis) — strengthened, not changed:** adopt
Opus's better argument as the stated rationale — SKILL.md declares
structured-gist "independent of caveman (structure vs wording)," so
`sg-plus-caveman-lite` is predicted, a priori, not to move tree shape at
all. This is now a stated, falsifiable prediction to check later, not just
"no data exists yet."

## Pilot result + second Opus check (2026-09-12) — GO, with 3 fixes applied before scaling

Pilot ran on `cause-chain-reversal` (Sonnet subagent). Independently verified
by the orchestrating session (diffs confirmed additive-only, 5+ node paths
hand-checked against renderings) AND a second, targeted Opus pass (checked
all 6 `ordered` calls against `source.md`, spot-checked 15 more previously-
unverified node paths). Verdict: **GO** — no error found that invalidates
the method — but 3 cheap fixes required before scaling to the other 7 cases:

1. **`ordered` discriminator rule, now explicit** (previously implicit/
   per-judgment, causing the pilot's own least-confident call, r3 vs r5,
   both typed `contrast_supersession` but scored oppositely): `ordered:
   true` **iff** the fact set traces a single sequence where EVERY
   adjacent pair in `fact_ids` has a real, source-confirmed before/after
   relationship. A relation whose members include parallel elaborations,
   or that is fundamentally a belief-revision (old-view-superseded-by-new)
   rather than an event sequence, is `ordered: false` even if some
   sub-chain within it happens to be ordered elsewhere (that sub-chain is
   likely already covered by its own separate `ordered: true` relation —
   check for double-counting before scoring).
2. **4th node-path outcome added: `omitted`.** The original 3-outcome
   schema (`located`/`multi_node`/`not_locatable`) conflated two different
   things: a fact the rendering never recalled at all (status `omitted`
   in the existing, untouched fact verdict) vs. a fact that WAS recalled
   but couldn't be confidently placed in one node. These are different
   findings and must not share `not_locatable`. Every fact/relation-
   endpoint key must now be present in `node_paths` — no silently-missing
   keys (found in the pilot's haiku output: 6 omitted facts had no key at
   all; retrofitted with `{"omitted": true}` directly, verified against
   git history to touch nothing else).
3. **Path-string normalization specified.** Node paths strip leading
   markers (`-`/`▸`/enumerator prefixes like `i.`/`a.`) and re-join
   wrapped `↪` leaf text with single spaces — this was applied silently
   by the pilot; it must be a stated convention so all 8 cases normalize
   the same way and paths are comparable for the eventual tree-distance
   computation.

Also applied: pilot's `sonnet` output under-called `multi_node` once
(fact f15's two clauses split across two sibling nodes, `▸ Symptom
reduced` / `▸ Not fixed`, originally recorded as single `located`) —
corrected directly, verified against the rendering.

**Next**: scale the same process (relation `ordered` annotation + additive
node-path pass, `standard` level only) to the remaining 7 judged cases,
using the corrected 3-fix schema/rule above.

## Open implementation details (deferred to build time, not blocking Opus review)

- Exact node-path capture prompt/schema for the additive judging pass.
- Exact tree-distance formula and permutation-test parameters (sample
  count, effect-size metric).
- How order-criterion partial credit is scored for chains with 3+ facts
  (e.g. 2-of-3 consecutive pairs correctly ordered).
- Report format for findings (a metrics table analogous to
  `relation_retention`, or a narrative writeup, or both).

## Results (2026-09-12)

The diagnostic is implemented in
`skills/structured-gist/benchmarks/semantic-compression/scoring/structural_linkage.py`;
its generated JSON and Markdown reports live beside it. Across the eight case
rollups, relative proximity advantage ranged from **0.184 to 0.723** (Q1
0.350, median 0.485, mean 0.455, Q3 0.572; n=8). Thus, in every case,
gold-linked facts were closer in the judged outline tree than random locatable
fact pairs, with the median case showing about a 48.5% distance reduction.
This is descriptive evidence of structural grouping, not a corpus-wide
significance claim: the effective independent sample remains about eight
cases, shared endpoints remain dependent, and topical sectioning may explain
part of the advantage.

Order encoding is rarer than proximity encoding, though the first pass of
this scorer undercounted it: the eligibility check originally tested a
resolved fact's own marker family, but most facts are judged into `↪`
explanation leaves nested *under* an ordinal (`I./II.`) sibling rather than
sitting on the ordinal marker line itself, so almost no pair qualified
(three instances, all typed 1.0, cave-chain-reversal only). Fixed by lifting
each resolved node to its nearest self-or-ancestor node with
`marker_family == "ordinal"` before comparing sibling position
(`nearest_ordinal_ancestor`, `structural_linkage.py`) — a fact nested three
levels under `II.` now correctly resolves to that `II.` sibling for the
order check. After the fix: four ordered relation-rendering instances across
two cases (`causality-heavy-explain`, `cause-chain-reversal`) have at least
one eligible adjacent pair, six eligible pairs total, all scoring 1.0. The
`cause-chain-reversal` spot check still confirms its hand-reviewed
discriminator (r1/r2/r4/r5/r6 ordered, r3 membership): haiku r4 remains
eligible and passes, and the fix now also surfaces sonnet-side eligible
pairs that the pre-fix leaf-only check missed. Order-encoding evidence is
still much thinner than proximity-encoding evidence (6 eligible pairs vs. 67
locatable proximity pairs across the corpus) — most relations still have no
eligible ordinal pair at all — but the result is no longer an artifact of
under-detection. A large share of the proximity advantage is driven by
same-node co-location rather than sibling adjacency (e.g. `real-hook-discovery`,
the highest-scoring case, has half its real pairs at distance 0 because
several gold facts were judged into one shared node) — this is grouping
evidence, not fine-grained sequence evidence, and should be read that way.

Implementation exposed two read-only data inconsistencies. Some finalized
judgments wrap `located` as `[[path]]` rather than the documented `[path]`, and
some paths retain an enumerator prefix or use a slightly different ancestor
label (“Mobile app release train” versus rendered “Mobile release train”). The
scorer handles these conservatively by unwrapping a single path, stripping
residual markers, and using a longest-unique-suffix match only for marker-family
recovery. One rendering also uses a hanging indent on a wrapped continuation;
the parser rejoins that unmarked continuation without changing source data.
