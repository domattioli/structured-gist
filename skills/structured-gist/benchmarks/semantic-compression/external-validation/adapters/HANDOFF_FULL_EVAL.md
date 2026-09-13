# Handoff to the full-eval-execution session

This session built and froze the **semantic-gold adapter layer** only —
`derived_gold.json` / `derived_blind_weights.json` / `coverage_audit.json`
per case, plus `adapters/common.py`'s runtime views. It did **not**:

- render structured-gist output (skim/standard/deep) against any case
- call a judge model or compute any retention/relation/recoverability/
  SPR/wording-fidelity/findability/compression/conformance number
- inspect how structured-gist performs on any of these cases

See `../HANDOFF.md` (from the corpus-freeze session) for the original
mechanical-integration-surface notes; this document supersedes it now
that the adapter exists — read this one first.

## What the next session can now do that it couldn't before

`adapters/common.py::to_gold_view(dataset, case_id)` returns a
`gold.json`-compatible dict (facts with `weight`, relations, a single
native-Q&A-wrapped `questions[0]`, `intent`) for every case that has both
a `derived_gold.json` and a `derived_blind_weights.json`.
`to_blind_weights_view(dataset, case_id)` returns a
`blind_weights/<case_id>.json`-compatible dict. Neither `combine.py` nor
`spr.py` needs to change to consume these — feed
`to_gold_view(...)` wherever those scripts currently do
`load_json(case_dir / "gold.json")`, and `to_blind_weights_view(...)`
wherever they do `load_json(BLIND_WEIGHTS_DIR / f"{case_id}.json")`.
`common.write_gold_view_file()` exists if some tool hard-requires a
literal `gold.json` path on disk.

**Which cases actually have both files** (and are therefore ready for
`combine.py`/`spr.py`-shaped scoring) is reported in `DERIVED_MANIFEST.json`
(`cases[].weighted == true`) — check this before assuming full coverage;
see `FINDINGS.md`'s per-dataset classification for which datasets/cases
are recommended for full semantic scoring vs. native-metrics-only.

## Metric-by-metric: what's native-gold-driven vs. derived-gold-driven vs. deterministic vs. judge/model-dependent

| metric | driven by | deterministic once inputs exist? | datasets it can run on |
|---|---|---|---|
| compression / reduction% | `source.md` + rendered output word counts | yes (pure arithmetic) | all three, no adapter needed |
| structural conformance (linter) | rendered output syntax only | yes | all three, no adapter needed |
| wording fidelity (PR #18, if merged) | rendered output + `source.md` | yes, given a rendering | all three, no adapter needed — **unverified assumption, confirm against #18's actual merged code** (see `ADAPTER_DESIGN.md` "Dependency on #18") |
| corrected retained-unit findability (PR #18, if merged) | rendered output + `source.md` | yes, given a rendering | all three, same caveat as above |
| native-task recoverability | `to_gold_view()`'s single `questions[0]` (native question/answer) + a judge's verdict on whether the rendering answers it | needs one judge call per (case, tier, level) to produce the verdict; arithmetic after that is deterministic | all cases with a `derived_gold.json` (recoverability only needs the native Q&A, which every native case already has — but `to_gold_view()` currently requires `derived_gold.json` too, since it's the single code path; a case with only native gold and no derived layer can still be recoverability-scored by reading `external_gold.json.question_or_query`/`reference_answer` directly, bypassing the adapter) |
| source support (hallucination/unsupported-claim check) | rendered output + `source.md`, judged | needs a judge; arithmetic after is deterministic | all three, no adapter needed (operates on source.md directly) |
| task-weighted fact retention (`combine.py`) | `to_gold_view()`'s facts (with Stage-B-derived `weight`) + a judge's per-fact verdict | needs a judge; arithmetic deterministic | only cases with both `derived_gold.json` and `derived_blind_weights.json` |
| relation retention (`combine.py`) | `to_gold_view()`'s relations + judge verdict | needs a judge; arithmetic deterministic | only cases with `derived_gold.json` (weights not required — `combine.py`'s relation_retention doesn't read a weight) |
| blinded task-weighted fact/relation recall, SPR, critical-unit diagnostics (`spr.py`) | `to_gold_view()` + `to_blind_weights_view()` + judge verdict | needs a judge; arithmetic deterministic | only cases with both files |

**No metric in this corpus should ever be pooled across QMSum/Qasper/
HotpotQA into one combined number** — report three separate profiles, the
same convention `../README.md`'s "Intended roles" table already
established for the native corpus. HotpotQA stays `pressure_only: true`
throughout — never include it in a headline "external validation"
average.

## Practical notes

- `DERIVED_MANIFEST.json` is the index — one row per annotated case, with
  hashes, protocol versions, fact/relation/critical-unit counts, coverage-
  audit status, and adjudication status (calibration cases only).
- `adapters/validate_derived_gold.py` should pass before and after any
  future change to the derived layer; it also proves the native layer
  (`external_gold.json`, `source.md`, `provenance.json`, `MANIFEST.json`,
  each dataset's `selection.json`) was never touched, via
  `NATIVE_SNAPSHOT.json`.
- A case without a `derived_gold.json` is not a defect — see
  `FINDINGS.md` for which cases/datasets were intentionally left
  unannotated and why (reliability concerns, corpus defects found during
  annotation, or scope decisions this session made and documented rather
  than silently working around).
- `coverage_audit.json` per case records what a separate blind pass found
  missing/redundant/unsupported in that case's inventory, and what was
  (or wasn't) corrected as a result — read it before trusting a case's
  fact/relation completeness for anything load-bearing.
