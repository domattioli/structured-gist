# 002 — Forward-merge DomI structured-gist into public repo (v0.4.11)

**Status**: Accepted (clarify satisfied via grill-with-docs, 2026-09-18; decisions D1–D3 below)
**Base**: worktree `structured-gist-fwd` @ `9418a30` (feature `001-backlog-hedge-fidelity` committed HEAD; WIP excluded)
**Source**: `DomI/skills/structured-gist` @ DomI `development` (v0.4.8, incl. #484 `ba430dd`)

## Decisions (operator-confirmed)

- D1 target = worktree from `9418a30` (not `main`: block-default flip `439307a` lives only on the feature branch).
- D2 scope = carry entire spec-023 lineage (kg-mode + corpus benchmark). DomI retains nothing.
- D3 default = `block` (public 0.4.8 flip stands). DomI keeps `responsive` via its CLAUDE.md elevation hook. No ADR.

## Requirements

- FR-1 DomI-only paths copied verbatim: `CHANGELOG.md`, `reference/kg-mode.md`, `scripts/{kg.py,kg_render.py}` (NOT `build_public_scaffold.sh`, NOT `__pycache__`), `benchmarks/{compare_corpus,content_units,cost_report,score_outline,weight_sweep}.py`, `benchmarks/{prompts.json,requirements.txt,scoring.md}`, `benchmarks/{corpus,renderings,reports,results}/`, `tests/{test_benchmark.py,test_kg.py}`, `tests/fixtures/{bench,kg}/`.
- FR-2 Shared files 3-way merged (public = base branch, DomI = incoming): `SKILL.md`, `reference/render-modes.md`, `tests/lint_outline.py`, `tests/smoke.sh`, `tests/test_lint.py`, `tests/benchmark.md`. Rule: keep every public-side change; add every DomI-side change that is not the render-mode default; where DomI text says responsive-is-default, public block-default wording wins.
- FR-3 #484 hunks (`ba430dd`: SKILL.md worked-example reorder + "do not mix" callout; render-modes.md WRONG/RIGHT repro block) present in merged files, re-worded onto block-default framing where they assert responsive-default.
- FR-4 Any DomI copied text referencing `nested-notes` skill name, DomI-only paths (`MANIFEST.md`, `scripts/hooks/*`), or DomI issue numbers without context: rename to `structured-gist`; DomI-repo checks in `smoke.sh` become conditional (skip when `MANIFEST.md` absent) — pre-merge baseline already fails that one check outside DomI.
- FR-5 Version 0.4.11 in `SKILL.md` frontmatter, `plugins/structured-gist/plugin.json`, README badge; `CHANGELOG.md` + `tests/benchmark.md` gain a v0.4.11 row (`not-measured`, evidence = this merge).
- FR-6 Gates: `python3 -m pytest skills/structured-gist/tests -q` all pass (expect ≥ 61 public + DomI kg/bench tests); `bash skills/structured-gist/tests/smoke.sh` 0 fail.
- FR-7 Docs: README §5 v0.4.0 row links to real `skills/structured-gist/benchmarks/reports/comparison-v0.4.0.md`; §7 Future work gains a one-line KG-mode entry (experimental, opt-in, verdict iterate) so the row's "see Future work" resolves; README §8 Documentation lists `reference/kg-mode.md`. `CONTEXT.md`: no change unless a term conflicts.
- FR-8 One commit on the worktree (detached HEAD → create branch `chore/domi-forward-merge` first), message `chore: forward-merge DomI structured-gist v0.4.8 → v0.4.11`, tag `v0.4.11`. NO push.

## Out of scope

DomI steps 4–6 (delete DomI copy, MANIFEST external pin, `install_skills.sh`, `vendored_skills.txt`, hardcoded-path grep). Public WIP on `001-backlog-hedge-fidelity`.
