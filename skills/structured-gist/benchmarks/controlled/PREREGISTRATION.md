# Controlled benchmark: pre-registration

This file and `prereg.json` together are the pre-registration record for the
controlled benchmark (DomI feature 005). The runner reads the values from
`prereg.json`. This file explains them. The record is committed before any
benchmark output exists.

    prereg_sha256 = sha256(canonical_json_bytes(prereg.json) + raw_bytes(PREREGISTRATION.md))

`python3 run.py prereg-hash` prints it. Every run records it, and every
gated subcommand refuses to start (exit 3) when either file differs from its
committed version.

## 1. Question

Does a structured-gist outline keep more of a source's facts and relations
than other short versions of the same length?

The answer is given per dataset and per control. It is never pooled across
datasets.

## 2. Cases and datasets

- The 42 frozen external-validation cases, unchanged: QMSum 24, Qasper 10,
  HotpotQA 8. The gold facts, gold relations, and blind weights are the
  existing ones in `semantic-compression/external-validation/`.
- Frozen corpus manifest (`MANIFEST.json`) SHA-256:
  `d00987546e01da532b22de016dd2d8ade8132e095df3fea32ff0e791741691b7`.
- Frozen derived manifest (`DERIVED_MANIFEST.json`) SHA-256:
  `38460499d582012a8d7f5c15a19fee695057e703d55cd630ad94f0ec27e9c7b2`.
- `run.py build-items` recomputes every per-case hash that the two manifests
  record and refuses to continue if one differs.
- A fourth dataset, WildChat (the AI-slop set), has its own addendum,
  `slop/PREREGISTRATION.md`. It is reported separately and never pooled.

## 3. Methods

Five short versions per case:

1. **skill**: the structured-gist skill in `block` render mode, invoked as
   `/structured-gist block` with no granularity word.
2. **plain_prose**: the same generator, no skill, continuous prose.
3. **plain_bullets**: the same generator, no skill, a Markdown bulleted list.
4. **lead_n**: the first N words of the source. No model.
5. **textrank**: sentence-level TextRank over the source. No model.

Generator: `claude-opus-5-5` at `medium` effort, through the
`claude-isolated-config` backend. Every generation call records the resolved model
id; a resolved id that differs from the pinned id is refused and not scored
(FR-021).

Skill: `SKILL.md` version `0.5.0b2`, SHA-256
`ce2833d35e6b22ba0fdfabe53f9a97c08badfc012f81e1553157494a63829eac`. `reference/render-modes.md` SHA-256
`5c43291bd42a45dd56c250e028945b0d6b044858ab787e12d8bf22dfe4c73d31`.

Prompt files in `prompts/` (SHA-256 of the exact bytes):

| File | SHA-256 |
|---|---|
| `shared_user.md` | `c7b3cfe2594ac14f4479ab87d1cf443385e6ef93f9119eacde316a206fca23f2` |
| `skill_instruction.md` | `eeb45fcce3887b16ae22dd844a31c840da92b225d31ed9fef3515147b0e439f4` |
| `plain_system.md` | `f7b93e52a08bc1fefa3dc5524cc4989c1c7626eeea54ae13d29484c34dad8c08` |
| `prose_instruction.md` | `15c8dcd497846635e45265be194653b7abf17c21902e4614f9d7b7b2b75e90e5` |
| `bullets_instruction.md` | `c40dfc89790f97b481ae0f7c0192716213ae28140b6d3ddf1771183e57bc73f4` |

The plain prompts contain no skill rule, glyph, or wording (FR-005); a test
checks a frozen term list and 6-word overlap with the skill files.

TextRank: damping 0.85, tolerance 1e-6, at most 200 iterations, ties broken
by source position. Stopword list `bench/stopwords.txt`, SHA-256
`074d55c8652048903cc5d48bb7d932259d5a4ce49e613e48fb075da73473a280`.

## 4. Length rule and tolerance

- Word counter `alnum-token-v2`, the same for all five methods. HTML
  comments are removed. `**`, `__`, and backticks are removed. At the start
  of every line, list-label tokens are stripped, repeatedly while the first
  remaining token is a label: bullet markers `-` `*` `+`, enumerator labels
  matching `^([IVXLC]+|[ivxlc]+|[A-Z]|[a-z]|\d+)\.$`, and the block glyphs.
  So `- I. item` counts 1. Then every whitespace token with at least one
  alphanumeric character counts as one word.
- N is the word count of the case's skill outline. The band is
  `[ceil(0.9N), floor(1.1N)]` (tolerance ±10%).
- Over the band: the text is trimmed at the last whole word at or below
  `floor(1.1N)`, and the trim is recorded.
- Under the band (plain prose and plain bullets): up to 2 fresh
  regenerations with the identical prompt. The first in-band attempt is
  used. If none is in band, the last attempt is used with the flag
  `length_violation`.
- Lead-N: if the source has fewer than `ceil(0.9N)` words, the whole source
  is used and the sample is flagged `source_shorter_than_band`.
- N fallback: if the skill generation fails (empty or refused after 2
  retries), N is `round(source_words × median(N / source_words))` over that
  dataset's successful skill samples, and the sample is marked
  `n_source: fallback_median_ratio`.
- A failed generation (empty output or refusal) is scored as zero retention
  and counted separately in the report.
- Flag counts are reported per dataset and method.

## 5. Main scores

- **Fact retention**, weighted: retained 1, partial 0.5, omitted or changed
  0; fact weights 1 to 3 from the blind weights.
- **Relation retention**, unweighted: retained 1, partial 0.5, lost 0, as
  `scoring/combine.py:122-128` computes it. `combine.py` SHA-256
  `e3e7cea9b98b89ada16923848b97165ae4d19ed0510a2bcaeb6a101878ff67df`.
- Both come from the existing scoring code, unchanged. A judge result is
  checked for completeness (every gold id present) before scoring, because
  the scorer counts a missing id as lost.
- A case with zero gold relations has relation retention "not applicable".
  It is left out of that dataset's relation mean, and the count is reported
  (QMSum 3, Qasper
  6, HotpotQA
  1).
- A case still incomplete after retries is listed. It never drops silently
  from a mean.

## 6. Win rule

- Per dataset and per control. The controls are plain bullets, plain prose,
  lead-N, and TextRank.
- Test: one-sided paired sign-flip permutation test on the per-case
  differences (skill minus control), statistic = mean difference, α = 0.05.
  Exact enumeration when n ≤ 20; otherwise 100,000 seeded Monte Carlo draws
  with `p = (1 + #{T* ≥ T_obs − 1e-12}) / (1 + B)`. The same tie tolerance,
  1e-12, applies to the exact test.
- Fact tests: "skill higher" and "skill lower" are each a family of 4
  controls, Holm-corrected within the dataset.
- Relation guard: "skill relation retention lower", per control, α = 0.05,
  **without** Holm. Holm would raise the guard's p-values and so make the
  guard easier for the skill to pass.
- The guard applies only on a dataset with at least 20 gold relations. The
  frozen counts are QMSum 50, Qasper 5, HotpotQA
  7. Only QMSum reaches 20. On Qasper and HotpotQA the
  verdict uses fact retention alone.
- Verdict labels (FR-011):
  - `skill ahead`: the fact test is significant after Holm, and the relation
    guard passes or does not apply.
  - `mixed: facts ahead, relations behind`: the fact test is significant
    after Holm, and the relation guard fails.
  - `skill behind`: the control is significantly higher on facts (the
    opposite one-sided test, Holm-corrected).
  - `no difference shown`: otherwise.

## 7. Main judge and effort

- Main judge: sol, model `gpt-5.6-sol`, `medium`
  effort, through the `agents-inc` launcher. It is a different vendor from
  the generator.
- Every call records the resolved model id. A resolved id that differs from
  the pinned id is refused and not scored (FR-021).
- Blinding: the judge sees only the gold checklist (fact id, text, category;
  relation id, text, type, fact ids) and one short version. It never sees
  the source, the method name, the case id, weights, the question, or the
  reference answer. Samples carry an opaque id,
  `sha256(master_seed + ":" + sample_id)[:12]`. The call order is shuffled
  with the seed string `master_seed:order:judge_id`. The judge runs in an
  empty directory outside every git repository.
- Judge prompt `prompts/judge.md`, SHA-256
  `24d9cb0db8e99a4e698ab8d21a2316f66c14d82556ba0ebe0700159a6d6be956`.
- Up to 3 attempts per call in the main run, each with a 600 s timeout.

## 8. Judge panel, subset rule, retry policy, agreement statistics

- **Subset**: per dataset QMSum 5, Qasper 2, HotpotQA 2 cases (9 cases, 45
  samples), taken in ascending order of
  `sha256(master_seed + ":subset:" + case_id)`. The subset gives first
  priority in the free-judge queue. It is not a coverage requirement for any
  judge.
- **Free judges**: `gemini-3.8-flash` (daily cap 200) and
  `nvidia/nemotron-3-ultra-550b-a55b:free` (daily cap 50), on all 210
  samples, best effort. For them the subset is first priority in the queue,
  not a gate. If Nemotron Ultra has no successful call during 24 hours of
  attempts, it falls back to `qwen/qwen3.8-27b:free`, whose results are kept
  under a separate judge id (`qwen_fallback`) and never merged with
  Nemotron. Qwen wrote the WildChat gold, so it never judges a WildChat
  sample.
- A free judge whose resolved model id changes mid-run is stopped for the
  rest of the run. Its earlier scores are kept, and the stop is reported.
- **Retry policy**: a failed call (rate limit, overload, timeout, malformed
  output) goes to the retry queue. A sol call still failing after
  3 main-run attempts is enqueued as a paid entry and continues the same
  attempt count. Backoff is `min(24 h, 15 min × 2^(attempts − 1))` with ±10%
  deterministic jitter, up to 8 attempts in total. The scheduler ticks every
  1,800 s, retries only entries that already exist, and never creates one.
  Before each sol retry it checks the paid-token ceiling and holds
  the retry if the ceiling would be passed.
- The report freezes 7 days after the main run finishes. It gives each free
  judge's coverage at the freeze (scored / attempted / given up). If a free
  judge never succeeds, agreement uses the judges that scored, and a deviation
  is logged.
- **Agreement statistics**, per dataset, on the ordinal scale lost < partial
  < retained: quadratic-weighted Cohen's kappa for each judge pair, ordinal
  Krippendorff's alpha across the judges that scored (missing ratings allowed), and raw
  % agreement. No threshold is applied and no dataset is flagged.

## 9. Secondary scores

Computed without a judge, each against the dataset's human reference answer
(FR-014):

- QMSum: ROUGE-L **recall**.
- Qasper: answer-token **recall** after SQuAD v1 normalization.
- HotpotQA: normalized answer **containment** (1 if the normalized answer
  appears in the normalized sample as a whole-word sequence, else 0).

Recall-style scores are used because a summary is much longer than a
reference answer. Secondary scores never affect the win rule. WildChat has
no reference answer, so its secondary scores are `n/a`. Word counts and
linter status are diagnostics only.

## 10. Uncertainty method

- A paired percentile bootstrap with 10,000 seeded resamples over cases, at
  95%, for every per-dataset mean and every skill-minus-control difference.
- Seed strings: `master_seed:dataset:method` for method means,
  `master_seed:dataset:control` for differences, and
  `master_seed:perm:dataset:control:score` for the Monte Carlo permutation
  draws. A seed is `int(sha256(seed_string).hexdigest()[:16], 16)`.
- Raw and Holm-adjusted p-values are reported for every test.

## 11. Report shape

- One section per dataset: QMSum, Qasper, HotpotQA, and WildChat as a
  separate fourth section. No pooled cross-dataset number.
- In each dataset section the plain-bullets comparison is the first row.
- Qasper and HotpotQA are labelled early signals, because of their small
  case counts.
- Each of the 12 verdicts (4 controls × 3 datasets) carries its uncertainty
  range and says whether the relation guard was applied.
- If the skill does not get `skill ahead` against plain bullets on facts,
  or fails the relation guard against plain bullets, the dataset section
  prints this sentence, unmodified, and the result is not reframed:
  "Plain bullets were not significantly worse than the skill on this
  dataset, so any gain here may come from list format alone and not from
  the skill's rules."
- The report also lists incomplete cases, failed generations, length-flag
  counts, free-judge coverage, method-guess mentions, and every deviation.

## 12. Outside-provider notice

Every call to an outside model provider (OpenAI, Google,
OpenRouter) begins its runner-supplied prompt with this fixed block,
byte-identical in every call and part of the hashed prompt. Its SHA-256 is
`463711420fb2e97f84b8ffc5ddde82ba5f116e65e8ec69e07621252fa48d6c82`. Extraction rule: the notice is the
contents of the fenced block below, with the fence lines removed and the
4-space indent removed from every line, plus one trailing newline. It is
byte-equal to `prompts/provider_notice.txt`.

- The notice, verbatim:

    ```text
    === NOTICE (fixed text, identical in every request) ===
    The material in this request comes from structured-gist (https://github.com/domattioli/structured-gist).
    It is licensed under the Apache License 2.0 (https://github.com/domattioli/structured-gist/blob/main/LICENSE).
    Do not use this request or its data to train AI models.
    Any use or redistribution must keep the license and the NOTICE file (https://github.com/domattioli/structured-gist/blob/main/NOTICE) and cite https://doi.org/10.5281/zenodo.22670068 (see CITATION.cff: https://github.com/domattioli/structured-gist/blob/main/CITATION.cff).
    Dataset excerpts in this request remain under their own licenses; see the THIRD_PARTY_NOTICES.md files in the repository (https://github.com/domattioli/structured-gist).
    This notice is not part of the task input. The task follows.
    === END NOTICE ===
    ```

## 13. Known limits

- The notice names the project, so an outside judge can tell the material
  comes from structured-gist.
- `block` skill output keeps a format cue (a fenced `text` block with literal
  glyphs) that a judge may recognize.
- Codex loads the global `~/.codex/AGENTS.md` into sol. It cannot be turned
  off through the launcher; its SHA-256 is recorded in the run manifest.
- The generator is Opus, not the Sonnet of the earlier external-validation
  run, so results are not directly comparable to it.
- Lead-N and TextRank are verbatim source text. They may carry speaker
  labels or stop mid-sentence, so a judge may recognize them as extractive.
- The controls get a length target and the skill does not, because the
  skill's output defines N.
- The relation guard runs without Holm, and it applies only on QMSum.
- Qasper (10 cases) and HotpotQA (8 cases) are small; their results are
  early signals.

## 14. Amendment and deviation rule

Any change after the pre-registration commit is a new version of this record:
a new file version, a new `prereg_sha256`, a new run id, and a dated entry
under "Deviations" giving the change and the reason. There are no in-place
edits after the first run. The report lists every deviation.

### Dry-run rule

Before the full run, one case per dataset (the first `case_id` in ascending
order: `qmsum-01`, `qasper-01`, `hotpotqa-01`) runs under run id
`dryrun-<first 12 hex of prereg_sha256>`. Its outputs are never reported or
reused, and its scores are not inspected; only exit codes, record validity,
and cost are read. The dry run may lead to plumbing changes only (adapters,
parsing, retries, timeouts). It may not change methods, prompts, metrics,
tests, thresholds, the case set, or judge ids. Any change after the dry run
is a logged deviation.

### Deviations

None.
