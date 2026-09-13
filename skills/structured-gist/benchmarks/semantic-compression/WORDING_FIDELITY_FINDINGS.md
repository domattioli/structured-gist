# Wording fidelity: findings (measurement only)

`scoring/wording_fidelity.py` tests SKILL.md's own claim, quoted verbatim
from `SKILL.md` line 10: **"structure only, wording untouched."** This is
Eval A of a two-eval measurement-only PR (Eval B: `FINDABILITY_FINDINGS.md`).
Neither eval changes `SKILL.md`, the grammar, the linter, or any existing
rendering, judge verdict, or gold semantic judgment. Nothing here calls a
model, embeds, stems, or fuzzy-matches anything — every number below is
exact token-sequence containment after a small, documented, auditable
normalization pass (`scoring/text_norm.py`).

**This is a lexical provenance test, not a semantic-faithfulness test.** A
paraphrase can be semantically perfect and still fail this eval; that is
the point. `combine.py`'s `task_weighted_fact_retention` already answers
"did the meaning survive" — this answers a different, narrower question:
"is the *wording* that survived actually copied from the source, or
rewritten?"

## Metric definitions

Computed per (case, tier, level) over each rendering's **semantic nodes**
(`scoring/outline_nodes.py`: every marker-bearing line — concept `-`,
attribute `▸`, enumerator `I./A./i./a.`, explanation `↪` — with the marker
glyph stripped and any R11 hard-wrap continuation lines rejoined, exactly
as `tests/lint_outline.py` itself merges them before linting).

1. **Verbatim node rate (VNR)** — per node, binary: does the node's whole
   normalized text appear as ONE contiguous token span anywhere in
   `source.md`? `VNR = verbatim_nodes / semantic_nodes`.
2. **Extractive token coverage** — output-wide: concatenate every semantic
   node's tokens in on-page reading order, then run a greedy
   longest-contiguous-match tiling against source (global reordering
   allowed — a fragment can be found anywhere in source, not just where an
   equivalent sentence sat originally). Reported at three minimum-fragment
   thresholds from the *same* tiling pass: `coverage@1`, `coverage@2`,
   `coverage@3` (`min_len` filters, not three separate algorithms).
3. **Novel phrase diagnostic** — a "novel span" is a maximal run of
   consecutive output tokens with no length-≥2 matched fragment covering
   them (the same ≥2 threshold as coverage@2). Diagnostic only, never a
   score: every span is listed individually, longest-first, so a single
   novel word inside an otherwise-verbatim sentence cannot disappear into
   an average.

## Normalization (`scoring/text_norm.py`)

Two representations of the same text, built one on top of the other:

- `normalize()` — strips presentation-only markup: backtick code spans
  (`` `x` `` → `x`), `**bold**`/`*italic*`/`~~strike~~`/`<u>`, markdown
  backslash-escapes, curly quotes → straight, whitespace runs → one space,
  and a stray space before sentence-final punctuation from line-wrap
  rejoining (`"session ."` → `"session."`) — with a **word-boundary
  lookahead** so it never eats the space before an unrelated token that
  starts with punctuation (see "bug caught" below). Case and word choice
  are untouched; this is the string shown in diagnostics.
- `tokenize()` — `normalize()` + whitespace-split + strip **edge**
  punctuation from each token + casefold. Casefolding is the one lossy
  step, applied only here, for one documented reason: turning a
  mid-sentence clause into a standalone node/line routinely
  re-capitalizes its first letter with zero wording change (source
  `"...but this repo actually keeps..."` → node `"Repo keeps skills
  top-level..."`). Every other letter-for-letter difference still counts
  as a mismatch.

**Deliberately excluded from the punctuation-strip set:** hyphens/dashes
and slashes. A token's edges are never stripped of `-` (would corrupt a
leading negative number or a hyphenated compound like `top-level`) or `/`
(often load-bearing in a path like `skills/<name>/SKILL.md`). Inline code
identifiers, paths, and versions pass through structurally intact.

**Structural allowlist.** SKILL.md defines exactly one piece of literal,
skill-mandated fixed vocabulary that could leak into node text: the
`/structured-gist summary` preset's section headers ("Session summary",
"Changed", "Decisions", "Next", "State", "Open questions" —
`SKILL.md` "## Activation"). A node whose whole normalized text exactly
equals one of these (case-insensitive) is excluded from both the VNR
numerator and denominator — it is skill-format vocabulary, not source
wording or model paraphrase, and scoring it either way would misrepresent
what this eval measures. This is a closed 6-phrase allowlist, not a
broad stopword list (README.md explicitly warns against building one that
could hide paraphrasing). **Measured result: 0 of 8 cases use the summary
preset, so this allowlist matched 0 nodes across the entire corpus** —
reported explicitly rather than assumed irrelevant.

### Normalization was inspected against real renderings, not designed in the abstract

Before finalizing the normalizer, its output was checked against actual
corpus renderings (`regression/real-hook-discovery/renderings/sonnet/{skim,
standard,deep}.md` first, then spot-checked across cases), per the PR
brief's instruction to inspect real renderings before deciding exact
normalization. All 8 cases render in `block` mode only (fenced ` ```text `,
no `responsive`/`inline` variants present in this corpus) — confirmed by
scanning every rendering file for its opening fence and for `▸`/`↪`/`→`/`•`
glyph counts. `outline_nodes.py` still calls the general
`lint_outline.extract_outline_from_text`, so it would handle `responsive`
mode correctly if a future case added one; this corpus does not exercise
that path.

### Normalization bug caught before scoring: space-before-punctuation over-match

The first version of the wrap-rejoin fix (`\s+([.,;:!?])` → drop the
space) fired unconditionally on ANY space before a period, not just a
sentence-final one. Real corpus text such as
`` load_local_skills assumed `.claude/` layout `` (backtick-stripped to
`assumed .claude/ layout`) was corrupted to `assumed.claude/ layout` —
gluing two real words together and silently changing the token sequence.
Caught immediately by running the scorer against
`real-hook-discovery/renderings/sonnet/standard.md` and inspecting a
novel-span diagnostic that showed the impossible token `assumed.claude/`.
Fixed by requiring the punctuation to be followed by whitespace-or-end
(`(?=\s|$)`), which a path-initial period never is. Grep confirmed the
literal artifact this rule exists for (an orphaned punctuation mark at the
start of a hard-wrapped continuation line) **does not occur anywhere in
the current corpus** — the rule is a documented defensive normalization
for a shape not yet seen, not a fix for an observed case, and is covered
by `test_one_novel_word_inside_otherwise_copied_text` and the punctuation
test in `test_wording_fidelity.py`.

## Results

Full machine-readable output: `results/wording_fidelity.json`. Generated
table: `results/WORDING_FIDELITY_SCORES.md`. Regenerate with
`python3 scoring/wording_fidelity.py` (deterministic, byte-for-byte
reproducible — no model, network, or randomness at scoring time).

### By granularity level (averaged across all 11 case/tier renderings at each level)

| level | n | avg VNR | avg coverage@1 | avg coverage@2 | avg coverage@3 |
|---|---|---|---|---|---|
| skim | 11 | 0.2087 | 0.7630 | 0.3208 | 0.0590 |
| standard | 11 | 0.1836 | 0.8522 | 0.5688 | 0.3487 |
| deep | 11 | 0.1806 | 0.8734 | 0.6784 | 0.4936 |

### By model tier (all scored case/level renderings)

| tier | n | avg VNR | avg coverage@2 |
|---|---|---|---|
| sonnet | 24 | 0.2109 | 0.5499 |
| haiku | 9 | 0.1378 | 0.4501 |

### By node role, aggregated across the whole corpus

| role | nodes | verbatim | verbatim-node rate |
|---|---|---|---|
| concept (`-`, L1 only) | 126 | 66 | 0.5238 |
| attribute (`▸`) | 211 | 38 | 0.1801 |
| enumerator (`I./A./i./a.`) | 307 | 44 | 0.1433 |
| explanation (`↪`) | 325 | 32 | 0.0985 |

## Corpus conclusions

**1. Does current structured-gist actually preserve wording?** At the
**token level**, mostly yes and it strengthens with depth: coverage@2 (a
genuine 2+-word copied run) rises monotonically 0.32 → 0.57 → 0.68 from
skim to deep, and coverage@1 is 0.76–0.87 throughout. At the **node
level**, no: VNR stays low (0.18–0.21) at every granularity — most
individual nodes are not, as a whole, one contiguous verbatim span, even
at `deep`. Both are true at once because structured-gist's own grammar
(SKILL.md "Connective-clause test", "Delimiter-split test") *requires*
splitting a source sentence's clause and its reasoning across a
parent node and a child `↪` — each resulting node is typically an edited
clip (words dropped, a connective removed, a component reworded to fit)
rather than a lifted sentence, even when nearly every individual word in
it still traces back to source vocabulary.

**2. Where does it mutate wording?** Concept labels (`-`) are copied most
often (VNR 0.52) — sample size here is modest (126 nodes, ~1–4 per
case/tier/level) but plausible: a top concept is often close to a short
source noun phrase. Explanation leaves (`↪`) mutate wording the *most*
(VNR 0.099) — see Q5. Non-verbatim nodes and novel spans are dumped in
full in `results/wording_fidelity.json` (`non_verbatim_nodes`,
`representative_novel_spans` per rendering) for direct inspection; the
most common shape observed by hand-reading several cases is a
multi-fact node compressed into one clause (e.g. `f1`+`f2` → "assumed
`.claude/` layout") and top-level section labels invented outright
("Discovery gap", "Root cause", "Result" — none of these three strings
appear anywhere in `real-hook-discovery/source.md`).

**3. Is the violation rare enough that "wording untouched" is empirically
credible?** **Not at the node level, as literally worded.** A ~18–21%
whole-node verbatim rate means roughly 4 in 5 nodes are, by this
definition, not "untouched." Read charitably — "structure only, wording
untouched" most plausibly means *the skill introduces no wording of its
own beyond restructuring*, not *every node is a lifted quote* — and
token-level coverage@2/3 supports that weaker, more plausible reading
reasonably well, especially at `standard`/`deep` (0.57–0.68 at
coverage@2). The literal claim, read as "each node is a verbatim
fragment," is contradicted by the node-level data; the weaker,
almost-certainly-intended reading is empirically credible at
`standard`/`deep` and materially weaker at `skim` (coverage@2 only 0.32 —
`skim`'s aggressive compression budget does force real paraphrase, not
just excerpting).

**4. Does mutation vary by level/model?** By level: token-level
extractiveness rises with depth (see table); node-level VNR does **not**
show the same monotone rise (0.2087 → 0.1836 → 0.1806 — flat to slightly
*declining* with depth, the opposite direction from coverage). This
divergence is itself a finding, not noise: `deep` renders substantially
more nodes (see per-case node counts in `results/WORDING_FIDELITY_SCORES.md`
— e.g. `synthetic-scale-verylarge`/haiku goes from 12 nodes at skim to 114
at deep), and the additional nodes are apparently not disproportionately
more likely to be exact single-span quotes even though the surviving text
overall traces more of its tokens to source. By model tier, on the 3
cases with both renderings (`cause-chain-reversal`, `migration-tristate`,
`synthetic-scale-verylarge`): sonnet is more extractive than haiku on
both measures (VNR 0.211 vs 0.138; coverage@2 0.550 vs 0.450) — a
plausible, modest signal, not a large one, from a 9-vs-24-rendering
sample.

**5. Are explanations (`↪`) more likely to mutate wording than terse
structural nodes?** Yes, clearly, and in fact more than every other role:
explanation VNR (0.099) is the *lowest* of the four roles, below even
enumerators (0.143) and attributes (0.180). This is not a defect relative
to SKILL.md's own contract for `↪` — "the ONLY place prose explanation
lives," "not caveman-compressed... stays a readable explanation" — that
contract is about *not compressing* the leaf, not about *quoting* it
verbatim. An explanation leaf is exactly where a model is expected to
synthesize a connective sentence ("...so a broken link fails loudly
instead of silently") joining ideas that may not sit adjacent in the
source at all. The finding: SKILL.md never claims `↪` content is
extracted, only that it is not truncated — and the data is consistent
with that narrower, correct reading, not with "wording untouched" applied
uniformly to every marker type.

**6. Is "structure only, wording untouched" empirically accurate, mostly
accurate, or contradicted?** **Mostly accurate at the token level,
contradicted at the node level, as literally worded.** See Q3. The
practically useful takeaway for anyone relying on this claim: expect most
individual *words* surviving into a `standard`/`deep` outline to be
traceable to the source, and expect most individual *nodes* to be edited
clips rather than lifted sentences — especially explanation (`↪`) nodes
and especially at `skim`.

## Pressure checks (actively tried to falsify this metric)

- **Common words inflating extractive coverage** — real and demonstrated:
  coverage@1 (0.76–0.87 throughout) is uniformly much higher than
  coverage@2 (0.32–0.68) and coverage@3 (0.06–0.49) precisely because
  short common words ("the", "a", "and") coincidentally exist in
  isolation elsewhere in source even inside a genuine paraphrase — this
  is why coverage@1 alone is reported only as one of three thresholds,
  never as *the* number, and why the novel-span diagnostic is built on
  the ≥2 threshold rather than ≥1.
- **Structural labels mistaken for paraphrases** — checked directly: the
  6-phrase allowlist matched 0 nodes in this corpus (no case uses the
  summary preset), so no structural label was silently exempted from
  scoring, and none was needed to be for the current corpus. If a future
  case uses `/structured-gist summary`, those exact 6 phrases (and only
  those) are excluded.
- **Reordered verbatim spans incorrectly penalized** — checked directly
  by `test_reordered_exact_nodes_each_stay_verbatim`: each node is
  checked against the whole source independently, with no requirement
  that node order match source order, so reordering costs nothing.
- **Punctuation/markdown normalization hiding real wording changes** —
  the normalizer strips markup and collapses whitespace/punctuation
  spacing only; it never merges two different *words*. A paraphrase
  still fails to match after normalization by construction
  (`test_genuine_paraphrase_is_not_verbatim_and_has_low_coverage`).
  Conversely, the space-before-punctuation rule initially over-matched
  and corrupted real words (see "bug caught" above) — found and fixed
  before this corpus run was finalized, not after.
- **One novel word disappearing inside a good average** — checked
  directly: novel spans are listed individually
  (`representative_novel_spans`, longest-first), and
  `test_one_novel_word_inside_otherwise_copied_text` proves a single
  substituted word inside an 8/9-token verbatim sentence surfaces as its
  own length-1 entry rather than being absorbed into a 0.89 coverage
  average.

## Interaction with findability (Eval B)

`FINDABILITY_FINDINGS.md`'s evidence-access measures locate a fact's
evidence inside a rendering using the judge's recorded `evidence` text
(from `judged/<tier>.json`), matched against the rendering with the SAME
`text_norm.py` normalizer used here. Where this eval's own data shows a
node's wording was mutated enough to break contiguous-span containment,
that is a real, causally connected risk to findability's alignment step —
Eval B reports any resulting alignment failures directly rather than
falling back to fuzzy matching (see `FINDABILITY_FINDINGS.md` "Alignment
failures").

## Promotion classification

**A — durable deterministic regression metric.** Cheap (pure Python,
milliseconds, no fixtures beyond files already in the repo), stable
(byte-for-byte reproducible), and it tests SKILL.md's own stated contract
directly rather than a proxy for it. Recommended durable regression use:
watch **coverage@2 by level** (skim/standard/deep) and **VNR by role**
(explanation vs. the rest) for a large negative shift on `standard`/`deep`
renderings — that would mean the skill started inventing wording rather
than restructuring it, which is exactly the failure mode "structure only,
wording untouched" promises does not happen. VNR's absolute level (~0.18)
is a descriptive baseline, not a threshold to gate on: a *drop* in it is
more informative than any single value, since the claim being protected
is "keeps restructuring, doesn't rewrite," not "every node is a literal
quote."

This confirms the PR brief's stated prior for this eval.
