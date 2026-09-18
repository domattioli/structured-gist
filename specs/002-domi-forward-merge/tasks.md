# Tasks — 002 forward-merge (plan folded in; single builder, sequential)

Paths: PUB=`/Users/domattioli/Projects/structured-gist-fwd`, DOMI=`/Users/domattioli/Projects/DomI`, SG=`skills/structured-gist`.

## A. Public worktree (PUB)

- [ ] T1 `git checkout -b chore/domi-forward-merge` in PUB (detached HEAD @ 9418a30).
- [ ] T2 Copy FR-1 paths DOMI/SG → PUB/SG (rsync, exclude `__pycache__`, `build_public_scaffold.sh`). Verify with `diff -rq` that only the 6 FR-2 files + public-only paths remain different.
- [ ] T3 3-way merge each FR-2 file. Method: `git merge-file -p PUB DomI-base DomI` is NOT available (no common ancestor in one repo) → do it by hand from `diff -u`; keep public hunks, import DomI hunks, apply D3 (block default) wording. Files: SKILL.md, reference/render-modes.md, tests/lint_outline.py, tests/smoke.sh, tests/test_lint.py, tests/benchmark.md.
- [ ] T4 Apply #484 hunks (patch at scratchpad `ba430dd.patch`) if T3 did not already carry them; reword any "responsive is the default" assertions inside those hunks to block-default.
- [ ] T5 FR-4 sweep: `grep -rn "nested-notes\|MANIFEST.md\|scripts/hooks" PUB/SG` → fix names/paths; smoke.sh MANIFEST check conditional.
- [ ] T6 FR-5 version bump (SKILL.md frontmatter, plugin.json, README badge), CHANGELOG + benchmark.md v0.4.11 rows.
- [ ] T7 FR-7 README/docs fixes (§5 row link, §7 KG line, §8 kg-mode.md).
- [ ] T8 Gates: pytest + smoke both green. Paste final counts.
- [ ] T9 `git add -A skills/structured-gist plugins README.md specs/002-domi-forward-merge` (+CHANGELOG if at root), commit per FR-8, `git tag v0.4.11`. NO push.

## B. DomI docs (DOMI, branch `development`, 18 unrelated dirty paths — stage ONLY the files below)

- [ ] T10 `MANIFEST.md` `### structured-gist` entry (lines ~538–571): heading version → `(v0.4.11 — canonical source now public repo domattioli/structured-gist, DomI copy pending removal; see scratchpad steps 4–6)`; line ~540 "responsive mode since v0.3.8" → "`block` default all surfaces since 0.4.8-public; `responsive` opt-in — DomI mandates responsive for GitHub via CLAUDE.md §Communication Style". Do NOT add `source:` pin field. Do NOT delete anything. Terse.
- [ ] T11 `specs/REGISTRY.md`: rows 014/018 keep their dir slugs (convention: one row per dir, unrenamed) but append ` (skill renamed structured-gist, 1224afc)` in the slug cell; ADD missing row `| 023 | nested-notes-kg-benchmark | Draft | - |` (dir exists, row absent). Keep table format.
- [ ] T12 Commit DomI: `docs: correct structured-gist MANIFEST entry + REGISTRY rows post forward-merge` — stage only MANIFEST.md + specs/REGISTRY.md. NO push.

## Deviations logged

- plan/tasks phases authored inline by orchestrator (Fable), not dispatched — cost; content is mechanical.
- clarify skipped: satisfied by grill-with-docs session (D1–D3).
- implement → Sonnet (operator override of Haiku default, explicit).
