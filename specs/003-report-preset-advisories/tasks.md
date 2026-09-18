# Tasks: Report preset + interrogative/hedge advisories

**Spec**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md) · **Branch**: `development` (spec dir `003-report-preset-advisories`)

## Conventions

- **Executor model for every task below: `sonnet`** (one implementor subagent; the supervisor plans, re-runs every check itself, and integrates — the supervisor writes no deliverable edits).
- **Check polarity — read this before running anything.** A **Success check** states a command and the output that means the task is DONE. A **Failure check** states a command and the output that means the task is BROKEN: if the command produces that output, the task has FAILED and must be fixed. Never read a Failure check as a target to hit.
- Every speckit helper script is invoked with `SPECIFY_FEATURE=003-report-preset-advisories` (the repo's `check-prerequisites.sh` rejects the `development` branch; the override is honored — see plan D6). No branch rename.
- Edits are surgical. No whole-file rewrite of `SKILL.md`.
- `skills/structured-gist/tests/lint_outline.py` MUST NOT be modified by any task. No pre-existing test may be modified; additions only.
- All commands run from the repo root `/Users/domattioli/Projects/structured-gist`. Every baseline value quoted below was measured by running the command against the untouched tree on 2026-09-18.
- **Progress check vs guard.** A check marked **(guard)** already reads OK before any work — its job is to catch a regression, not to show progress. Every other check reads not-yet-done on the untouched tree, so a passing read is real evidence.
- **Checks on files a task creates** (T009–T011) error loudly before that file exists — `FileNotFoundError`, `awk: can't open file`, a `grep` warning — rather than silently printing a passing value. Run them only after the file is created; an error before then is expected, not a result.
- Shared helper used by several checks — define it once per shell:

  ```bash
  sec() { awk -v s="## $1" 'index($0,s)==1{f=1;next} /^## /{f=0} f' skills/structured-gist/SKILL.md; }
  ```

- Terminology is fixed by spec Key Entities: **summary preset**, **report preset**, **hedge**, **certainty branch**, **finding**, **fidelity check**. Do not introduce synonyms.

## Phase 1 — Skill document advisories

### T001 — Taxonomy "answers" extension + interrogative rule (C1)

**Model**: sonnet
**File**: `skills/structured-gist/SKILL.md`, `## Marker taxonomy`
**Do**: In the role table, make the attribute and explanation rows state the question each answers about its parent, in the style of the concept and enumerator rows. Below the table add at most 3 lines stating that who/what/where/when/why/how/whether are prompts for content and do not select a marker, redirecting to the existing role criteria (top claim → concept, named property → attribute, ordered or grouped part → enumerator, explanation → `↪`).
**Success check**: `sec "Marker taxonomy" | grep -c "content prompts"` → `1`; and `sec "Marker taxonomy" | grep -E '^\| \*\*(attribute|explanation)\*\*' | grep -c '?'` → `2` (baseline `0` — neither row poses a question today; counting quotes instead would read `2` before any edit and prove nothing).
**Failure check**: `sec "Marker taxonomy" | grep -c '^| '` → anything **other than `5`** means FAIL (pre-edit baseline `5` = header + 4 role rows; the `|---|` separator has no trailing space and is not matched — a different number means a row was added or lost). `sec "Marker taxonomy" | grep -c 'MUST'` → anything **other than `2`** means FAIL (pre-edit baseline `2`, both from the no-self-nesting rule; a higher number means the advisory was written as a mandate).

### T002 — Advisory attribute-name lexicon (C2)

**Model**: sonnet
**File**: `skills/structured-gist/SKILL.md`, `## Marker taxonomy`, immediately after the attribute-vs-enumerator paragraph
**Do**: Add one advisory paragraph naming commonly source-supported attribute names — Purpose, Mechanism, Actor, Location, Timing, Certainty. State that Scope names a boundary and Trigger names an initiating condition and neither is a catch-all for every "where" or "when"; that "whether" names a proposition to resolve, not a degree of confidence; that source-specific names are preferred and absent properties omitted; and that this vocabulary is advisory and not checked by the linter.
**Success check**: `for w in Purpose Mechanism Actor Location Timing Certainty Scope Trigger whether advisory; do printf '%s ' "$(sec "Marker taxonomy" | grep -c "$w")"; done` → every number ≥ `1`.
**Failure check**: `sec "Marker taxonomy" | grep -ciE "linter (requires|enforces|checks) (this|the) (lexicon|vocabulary)"` → any value **≥ 1** means FAIL. `python3 -m pytest skills/structured-gist/tests/test_lint.py -q -k skill_md` → any result other than `1 passed` means FAIL. `grep -c "Encoding" skills/structured-gist/examples/attribute.md` → anything **other than `3`** means FAIL (pre-edit baseline `3`; the lexicon must not invalidate existing example names).

### T003 — Preset-omission contract (M1)

**Model**: sonnet
**File**: `skills/structured-gist/SKILL.md`, immediately after the summary preset's fenced block and its depth note
**Do**: Add one or two sentences: presets supply optional branch names, not required slots; omit any branch the source does not support, the summary preset included; a preset never changes the marker ladder or adds a role.
**Success check**: `grep -c "optional branch names" skills/structured-gist/SKILL.md` → `1`; and `a=$(grep -n "Enumerators under a" skills/structured-gist/SKILL.md | cut -d: -f1); b=$(grep -n "optional branch names" skills/structured-gist/SKILL.md | cut -d: -f1); c=$(grep -n "^\*\*Report preset" skills/structured-gist/SKILL.md | cut -d: -f1); [ "$a" -lt "$b" ] && [ "$b" -lt "$c" ] && echo ORDER_OK` → `ORDER_OK`. **Corrected post-implement (2026-09-18):** the `c` anchor was originally `grep -n "structured-gist report" … | head -1`, which after T014 matches the frontmatter `description:` line (line 5) instead of the preset heading, making the order read `ORDER_BAD` for a correctly-ordered file. Anchor on the preset's own bold heading.
**Failure check**: `git diff -U0 -- skills/structured-gist/SKILL.md | grep -c '^-.*▸ Open questions'` → any value **≥ 1** means FAIL (the summary preset's canonical block was edited). `grep "optional branch names" skills/structured-gist/SKILL.md | grep -ci summary` → `0` means FAIL (the contract sentence itself must name the summary preset; baseline `0`). Note a plain `grep -c "summary preset"` is useless here — it already reads `1` on the untouched tree, matching `**Session-summary preset (v0.3)…**` at SKILL.md:21.

### T004 — Report preset block (C4)

**Model**: sonnet
**File**: `skills/structured-gist/SKILL.md`, immediately after T003's contract
**Do**: Add the preset in the shape of the summary preset. The bold lead line must carry the exact version label `(v0.5.0b1)` — mirroring the summary preset's `(v0.3)` convention — and name `/structured-gist report` with alias `findings`. Prose: finding-first, one top concept per supported finding, multiple findings allowed as peers; **a finding is never invented when the source establishes none**; optional branches Question, Method, Observed, Inferred, Next, included only when source-supported; under Method, ordered steps take the lowercase ordinal family (`i.`/`ii.`) and unordered components the lowercase nominal family (`a.`/`b.`), while Method itself stays a named `▸` branch and is never an ordinal node; no generic Intro/Background/Conclusion headings, with context kept under the finding it belongs to; granularity and render mode apply unchanged and no new roles are introduced. Follow with a fenced ` ```text ` skeleton of at most 12 lines: one finding concept, two or three `▸` branches, at least one `↪` leaf.
**Success check**: `python3 -m pytest skills/structured-gist/tests/test_lint.py -q -k skill_md` → `1 passed`; `grep -c "(v0.5.0b1)" skills/structured-gist/SKILL.md` → ≥ `1`; `grep -ciE "never invent|not invent" skills/structured-gist/SKILL.md` → ≥ `1`.
**Failure check**: `awk '/```text/{f=1;next} /```/{f=0} f' skills/structured-gist/SKILL.md | grep -cE '^ {8,}(I|V|X)+\. |^ {8,}[A-Z]\. '` → any value **≥ 1** means FAIL (an uppercase enumerator at depth ≥2, i.e. beneath a `▸`). Baseline `0`. The obvious-looking `^\s+(I|II|III|A|B)\. ` form must NOT be used: it reads `3` on the untouched tree because the existing worked example at SKILL.md:177-181 legitimately uses depth-1 `I.`–`IV.` under a concept, so the task could never pass. `grep -cE "^\s*(I|i)+\. *Method" skills/structured-gist/SKILL.md` → any value **≥ 1** means FAIL (Method rendered as an ordinal node).

### T005 — Relation-wording preservation (M2)

**Model**: sonnet
**File**: `skills/structured-gist/SKILL.md`, at the `↪`-versus-`→` glyph rule
**Do**: Add one or two sentences: keep the source's relation wording and keep its endpoints identifiable; an association, correlation, or uncertain link is not rewritten as a causal `→`.
**Success check**: `a=$(grep -n "Leaf marker is" skills/structured-gist/SKILL.md | cut -d: -f1); b=$(grep -n "association" skills/structured-gist/SKILL.md | head -1 | cut -d: -f1); if [ -z "$b" ]; then echo NOT_PRESENT; else echo $((b-a)); fi` → a value in `0..3`. Baseline prints `NOT_PRESENT` (the word does not occur in the file yet); the `-z` guard is required because bare `$((b-a))` with an empty `b` raises a shell arithmetic error instead of a readable result.
**Failure check**: `grep -cF 'The plain `→` is reserved for inline cause-effect' skills/structured-gist/SKILL.md` → anything **other than `1`** means FAIL (the existing distinction was reworded). `grep -cE "^\*\*R[0-9]+" skills/structured-gist/SKILL.md` → anything **other than `0`** means FAIL (pre-edit baseline `0`; a new numbered rule was introduced).

### T006 — Observed-versus-inferred advisory (C5)

**Model**: sonnet
**File**: `skills/structured-gist/SKILL.md`, `## Nest by dependency`
**Do**: Append a softened advisory: when the source distinguishes observation from inference, preserve that distinction; use separate branches only when grouping would blur status, otherwise keep the attribution explicit inside the `↪`; never infer evidential status from wording alone and never manufacture missing evidence.
**Success check**: `sec "Nest by dependency" | grep -ciE "only when|when the source"` → ≥ `1`.
**Failure check**: `sec "Nest by dependency" | grep -ciE "never share a node|must always split|always use separate"` → any value **≥ 1** means FAIL (the advisory hardened into an absolute rule).

### T007 — New `## Hedge preservation` section (C3)

**Model**: sonnet
**File**: `skills/structured-gist/SKILL.md`, new section immediately after `## Leaf preservation`
**Do**: Add a section titled exactly `## Hedge preservation`: preserve source hedges with the claim they govern, including in collapsed output; keep the hedge in the claim text or in an immediately attached `↪`; use a certainty branch only when the hedge's scope is unambiguous; never turn a hedged source claim into an unhedged heading.
**Success check**: `grep '^## ' skills/structured-gist/SKILL.md | grep -A1 'Leaf preservation' | tail -1` → `## Hedge preservation`.
**Failure check**: `grep -c '^## Leaf preservation$' skills/structured-gist/SKILL.md` → anything **other than `1`** means FAIL (the section was renamed or removed). `sec "Hedge preservation" | grep -c .` → any value **> 6** means FAIL (section too long). `sec "Hedge preservation" | grep -cE "^\*\*R[0-9]+|linter (enforces|checks)"` → any value **≥ 1** means FAIL (written as an enforced rule).

### T008 — Limitations entries (C3 enforcement + M2)

**Model**: sonnet
**File**: `skills/structured-gist/SKILL.md`, `## Limitations`
**Do**: Add exactly two bullets: (a) accepting the hedge rule in general requires comparing source against output for both hedge retention and claim attachment — structural linting alone establishes neither, so general enforcement is deferred to the held hedge-fidelity backlog item, and the shipped fidelity check covers only declared statements in this repo's own example and fixtures; (b) relation-wording preservation is enforced only over those same declared statements, not over arbitrary sources.
**Success check**: `sec "Limitations" | grep -c '^- '` → `5` (pre-edit baseline `3`, plus 2); and `sec "Limitations" | grep -c "deferred"` → ≥ `1`.
**Failure check**: `git diff -U0 -- skills/structured-gist/SKILL.md | grep -c '^-.*robustness axis'` → any value **≥ 1** means FAIL (a pre-existing limitation was edited or removed).

## Phase 2 — Example, fidelity check, coverage

### T009 — `examples/report.md`

**Model**: sonnet
**File**: `skills/structured-gist/examples/report.md` (new)
**Do**: Create the example in the style of `examples/attribute.md`: a short framing paragraph; a machine-readable declaration as an **HTML comment** (no extra fence — see plan D5) with the fields `source:`, `hedge:`, `claim-key:`, `relation:`, `endpoint-a:`, `endpoint-b:`; one fenced ` ```text ` outline applying the report preset to that synthetic source, with **two findings whose branch sets differ**; two or three closing lines naming what it demonstrates. The declared source must contain both a hedge and an association phrase; the declared hedge token must NOT occur inside the declared claim key; the outline must keep the hedge attached to its claim and keep the association wording. Content is synthetic — no real name, host, URL, or corpus excerpt (constitution P6).
**Success check**: `cd skills/structured-gist && python3 tests/lint_outline.py examples/report.md` → `PASS (0 violations)`; and `python3 -c "import sys;sys.path.insert(0,'skills/structured-gist/tests');from test_lint import _lint_all_blocks;print(_lint_all_blocks('skills/structured-gist/examples/report.md'))"` → every value in the printed mapping is `[]`; and `awk '/```text/{f=1;next} /```/{f=0} f' skills/structured-gist/examples/report.md | grep -c '^- '` → ≥ `2`.
**Corrected post-implement (2026-09-18):** the text-mode check alone is BLIND to the line-wrap rule — `lint_text` skips it because the continuation-merge step discards physical-line widths (`lint_outline.py:308-318`), while `lint_file` enforces it. The first implementation of this example read clean in text mode and `line 3 [R11]: line exceeds 64 chars (94)` in file mode. File mode is now the primary check here and in T011.
**Failure check**: `grep -cE 'https?://|@[a-z]+\.' skills/structured-gist/examples/report.md` → any value **≥ 1** means FAIL (a real identifier leaked). `awk '/```text/{f=1;next} /```/{f=0} f' skills/structured-gist/examples/report.md | grep -c '^- '` → `1` or `0` means FAIL (the findings were packaged under one root, or none were emitted).

### T010 — Fidelity-check helper (D5, FR-022/FR-024)

**Model**: sonnet
**File**: `skills/structured-gist/tests/fidelity_check.py` (new, stdlib only)
**Do**: Implement `check_fidelity(path) -> list[str]` — empty list means clean. Parse the HTML-comment declaration block, extract the file's first ` ```text ` fenced outline, and return violation strings for three failure modes:
1. **Declaration validity** — any of the six fields missing or empty, OR the `hedge` token occurring inside the `claim-key` string (that combination would make check 2 pass unconditionally).
2. **Hedge attachment** — locate the outline line containing `claim-key`; violation unless the `hedge` matches as a **whole word** (`re.search(rf"\b{re.escape(hedge)}\b", line, re.I)`) in that line, or in a subsequent line that is indented deeper, carries the `↪` marker, and is reached without first passing a line at or above the claim line's indent.
3. **Relation preservation** — violation if the `relation` phrase appears in no outline line, or if any single line contains the declared endpoints joined by `→` in **either** order (`a → b` or `b → a`).

Before running any of the three checks, **merge wrapped continuation lines into their owning node** — a line whose stripped content does not begin with a ladder marker glyph is a continuation and joins the previous node's text with a single space — so a declared phrase split across a hard wrap is neither missed nor falsely flagged. No import of `lint_outline`; no third-party import.
**Success check**: `python3 -c "import sys;sys.path.insert(0,'skills/structured-gist/tests');from fidelity_check import check_fidelity;print(check_fidelity('skills/structured-gist/examples/report.md'))"` → `[]`.
**Failure check**: `grep -E "^(import|from) " skills/structured-gist/tests/fidelity_check.py | grep -vcE "^(import|from) (re|sys|pathlib|typing)\b"` → any value **≥ 1** means FAIL (a non-stdlib or unapproved import). `grep -c "lint_outline" skills/structured-gist/tests/fidelity_check.py` → any value **≥ 1** means FAIL (the linter was imported or re-implemented). `python3 -c "import sys;sys.path.insert(0,'skills/structured-gist/tests');from fidelity_check import check_fidelity as c;print(c('skills/structured-gist/examples/report.md'))"` → any non-empty list means FAIL.

### T011 — Negative fixtures (FR-023, N1)

**Model**: sonnet
**Files** (new): `skills/structured-gist/tests/fixtures/fidelity/hedge_dropped.md`, `.../relation_upgraded.md`, `.../declaration_malformed.md`
**Do**: Each carries a declaration block plus an outline. `hedge_dropped.md` — the hedge is absent from both the claim node and any attached `↪`. `relation_upgraded.md` — the declared association is rendered as the two endpoints joined by `→` on one line (use the reversed order `b → a`, so the bidirectional check is exercised). `declaration_malformed.md` — the `hedge` token occurs inside `claim-key`, the declaration form that would otherwise produce a vacuous pass. **Every one of the three must LINT CLEAN IN FILE MODE** (`python3 tests/lint_outline.py <fixture>` → `PASS (0 violations)`), not merely in text mode, so each proven failure is attributable to the fidelity property alone. Hard-wrap every line to ≤64 columns including indent, continuation indent identical to the marker line's, per SKILL.md `## Spacing`. They live in `tests/fixtures/fidelity/` and must NOT use the `bad_` prefix: in this repo `tests/fixtures/bad_*.md` means "must fail the linter" (`smoke.sh:248-268`), the opposite contract.
**Success check**: `python3 -c "
import sys;sys.path.insert(0,'skills/structured-gist/tests')
from fidelity_check import check_fidelity as c
from test_lint import _lint_all_blocks as L
import glob
for f in sorted(glob.glob('skills/structured-gist/tests/fixtures/fidelity/*.md')):
    print(f, len(c(f)), all(v==[] for v in L(f).values()))"` → three lines, each with a violation count ≥ `1` and `True`.
**Failure check**: in that output, a violation count of `0` on any fixture means FAIL (the check cannot fail — the P2 proof is void); `False` on any fixture means FAIL (the fixture trips the linter, so its failure is not attributable to the fidelity property). `find skills/structured-gist/tests/fixtures/fidelity -name 'bad_*.md' 2>/dev/null | wc -l` → any value **≥ 1** means FAIL (reserved prefix reused). Use `find`, not `ls` with a glob: under zsh an unmatched glob aborts the command before `ls` runs.

### T012 — New test cases (FR-021/FR-022/FR-023)

**Model**: sonnet
**File**: `skills/structured-gist/tests/test_lint.py` (additions only)
**Do**: Add `test_report_example_clean` in `TestNormativeBlocks`, mirroring `test_attribute_example_clean` but targeting `examples/report.md`. Add a new class `TestFidelity` with five cases: (1) the example is fidelity-clean; (2)–(4) each negative fixture yields ≥1 violation; (5) all three fixtures lint clean.
**Success check**: `python3 -m pytest skills/structured-gist/tests/test_lint.py -q -k "report or Fidelity"` → `6 passed` (5 in `TestFidelity` + `test_report_example_clean`; verified that `-k "report or Fidelity"` collects `0` tests today, so there is no pre-existing name collision inflating the count).
**Failure check**: `git diff -U0 -- skills/structured-gist/tests/test_lint.py | grep -c '^-[^-]'` → any value **≥ 1** means FAIL (a pre-existing line was removed or changed; additions only). A collected count other than `6` means FAIL.

## Phase 3 — Version, discoverability, bookkeeping

### T013 — Version bump to `0.5.0b1` (three code surfaces)

**Model**: sonnet
**Files**: `skills/structured-gist/SKILL.md` frontmatter; `plugins/structured-gist/.claude-plugin/plugin.json`; `README.md` badge
**Do**: Replace the version at all three with exactly `0.5.0b1`. Do not normalize the string to satisfy any validator; a rejection is reported in the task output.
**Success check**: `grep -c '^version: "0.5.0b1"$' skills/structured-gist/SKILL.md` → `1`; `grep -c '"version": "0.5.0b1"' plugins/structured-gist/.claude-plugin/plugin.json` → `1`; `grep -c 'version-0.5.0b1' README.md` → `1` (each baseline `0`). **Corrected post-implement (2026-09-18):** the original single command `grep -rn … | wc -l` → `3` is wrong once T004 lands, because T004's in-prose label `**Report preset (v0.5.0b1)…**` is a fourth occurrence inside `SKILL.md`; the literal command reads `4` on a correct tree. Check each surface separately instead. And **(guard)** `python3 -m json.tool plugins/structured-gist/.claude-plugin/plugin.json > /dev/null; echo $?` → `0`.
**Failure check**: `grep -rn "0\.4\.12" --exclude-dir=.git --exclude-dir=specs --exclude=CHANGELOG.md --exclude=benchmark.md . | wc -l` → any value **≥ 1** means FAIL (a surface was missed; pre-edit baseline is `3`). `python3 -m json.tool … ; echo $?` → any value **≠ 0** means FAIL. `grep -c "0\.5\.0-b1\|version: \"0\.5\.0\"$" skills/structured-gist/SKILL.md` → any value **≥ 1** means FAIL (the string was normalized). Use `grep -c`, not `grep -rc`: the recursive form prefixes the count with the filename (`skills/…/SKILL.md:0`) instead of printing a bare number.

### T014 — Frontmatter description + qualified triggers (FR-019, A2)

**Model**: sonnet
**File**: `skills/structured-gist/SKILL.md` frontmatter `description:`
**Do**: Surgically insert a brief mention of the report preset and its `findings` alias. Any trigger phrase added must be a **qualified** form containing the skill's own lexicon — for example `"sg report"`, `"gist report"`, `"structured-gist report"`, `"findings outline"`. The bare words `report` and `findings` must NOT be added as standalone triggers.
**Success check**: **(guard)** `bash skills/structured-gist/tests/smoke.sh 2>&1 | grep -c '^FAIL'` → `0` (baseline `0`, smoke is green today); and `python3 -c "d=open('skills/structured-gist/SKILL.md').read().split('---')[1];print('report' in d and 'findings' in d)"` → `True` (baseline `False`).
**Failure check**: `git diff -U0 -- skills/structured-gist/SKILL.md | grep '^+description:' | grep -cE '"report"|"findings"'` → any value **≥ 1** means FAIL (a bare standalone trigger was added). `python3 -c "print(sum(1 for l in open('skills/structured-gist/SKILL.md') if l.startswith('description:')))"` → anything **other than `1`** means FAIL (the description split across lines or broke YAML).

### T015 — Changelog entry (C1, FR-019a)

**Model**: sonnet
**File**: `skills/structured-gist/CHANGELOG.md`
**Do**: Add a `**v0.5.0b1**` entry as the new first bullet, matching the existing entry format (`- **vX** (date, one-line headline): body…`), summarizing the advisories, the report preset, the fidelity check, and stating explicitly that no rule logic changed.
**Success check**: `head -3 skills/structured-gist/CHANGELOG.md | grep -c '\*\*v0.5.0b1\*\*'` → `1`.
**Failure check**: `grep -c '\*\*v0.4.12\*\*' skills/structured-gist/CHANGELOG.md` → anything **other than `1`** means FAIL (prior entry lost or duplicated). `git diff -U0 -- skills/structured-gist/CHANGELOG.md | grep -c '^-[^-]'` → any value **≥ 1** means FAIL (history rewritten rather than appended).

### T016 — Benchmark row (FR-020, U5)

**Model**: sonnet
**File**: `skills/structured-gist/tests/benchmark.md`
**Do**: Append one row for `v0.5.0b1` dated 2026-09-18, mirroring the **conventions of the `v0.4.12` row** (line 70), which uses the metric cell form `n/a (plugin packaging fix)` rather than the token `not-measured`. Use the analogous form `n/a (advisory guidance + preset)`, keep the same column count, and cite as evidence the added guidance, the lint-covered example, and the fidelity check with its negative fixtures. Fabricate no measurement.
**Success check**: `grep -c "v0.5.0b1" skills/structured-gist/tests/benchmark.md` → `1` (baseline `0`); and **(guard)** `python3 -c "ls=[l for l in open('skills/structured-gist/tests/benchmark.md') if l.startswith('| v0.')];print(len(set(l.count('|') for l in ls)))"` → `1` (baseline `1` — column counts already agree, so this only detects a malformed new row).
**Failure check**: that first command printing any value **> 1** means FAIL (the new row's column count differs). `git diff -U0 -- skills/structured-gist/tests/benchmark.md | grep -c '^-[^-]'` → any value **≥ 1** means FAIL (an existing row was edited).

### T017 — Discoverability surfaces (C2, FR-025)

**Model**: sonnet
**Files**: `llms.txt` (Examples list), `skills/structured-gist/SKILL.md` ("More examples:" pointer), `README.md` (activation section, line ~94)
**Do**: Add `examples/report.md` to the `llms.txt` Examples list in the existing entry style; extend the skill document's `More examples: examples/{skim,standard,deep,attribute}.md` pointer to include `report`; in the README activation section, add one line noting that two opt-in presets exist — the summary preset and the report preset — with their invocations.
**Success check**: `grep -c "examples/report.md" llms.txt` → `1`; `grep "More examples" skills/structured-gist/SKILL.md | grep -c report` → `1`; `grep -c "structured-gist report" README.md` → ≥ `1`.
**Failure check**: `grep -c "examples/attribute.md" llms.txt` → anything **other than `1`** means FAIL (an existing index entry was dropped or duplicated). `grep -cF "/structured-gist [skim|standard|deep]" README.md` → anything **other than `1`** means FAIL (pre-edit baseline `1`; the existing activation line was replaced instead of supplemented).

### T018 — Plugin-manifest validation, report-only (C3, FR-026)

**Model**: sonnet
**Do**: Re-run, read-only, the validation path the `v0.4.12` changelog entry cites, against the bumped version. Do NOT re-run `claude plugin marketplace add`. Run only the non-mutating inspection: `claude plugin details structured-gist@structured-gist`; if the CLI is unavailable, run `python3 -m json.tool plugins/structured-gist/.claude-plugin/plugin.json` instead and state explicitly that the CLI path could not be exercised. `command -v claude` returns a path in this environment, so the CLI path is expected to be exercisable. Quote the command and its full output verbatim in the task report. Do NOT alter the version string on rejection — escalate it.
**Success check**: the task report contains the command and its verbatim output; and `grep -c '"version": "0.5.0b1"' plugins/structured-gist/.claude-plugin/plugin.json` → `1`.
**Closed 2026-09-18.** This session's read-only run returned `Plugin "structured-gist@structured-gist" not found` — no marketplace was registered here, so the loader path could not be exercised from inside the feature. The orchestrator subsequently ran the full validation under operator direction and reported: `claude plugin validate` clean from the repo root and from an unrelated directory; the plugin directory clean with a symlink-not-read warning; a dereferenced copy clean with no warnings; a local marketplace add + install + `claude plugin details` reporting `structured-gist 0.5.0b1`, Skills (1), with the test install and marketplace removed afterwards. `0.5.0b1` is validated against the real loader. No operator decision outstanding.
**Failure check**: `git diff -U0 -- plugins/structured-gist/.claude-plugin/plugin.json | grep -c '^[+-][^+-]'` → anything **other than `2`** means FAIL (something beyond the single version line changed). A reported rejection that was resolved locally — by editing the version string or the manifest schema — instead of being raised as a NEEDS-OPERATOR item means FAIL.

## Phase 4 — Gate (supervisor re-runs every command independently)

### T019 — Full suite + budget verification

**Model**: sonnet runs it first; the supervisor re-runs each command itself and quotes the output.
**Do**: Run and report verbatim:
1. `python3 -m pytest skills/structured-gist/tests/ -q`
2. `bash skills/structured-gist/tests/smoke.sh 2>&1 | tail -5`
3. `git status --short`
4. `git diff --numstat`
5. `git diff --name-only | grep -c lint_outline.py`
6. `SPECIFY_FEATURE=003-report-preset-advisories bash .specify/scripts/bash/check-prerequisites.sh --json`

**Success check**: (1) exits `0`, no failures; (2) reports `0` FAIL; (5) prints `0`; (4) shows `skills/structured-gist/SKILL.md` insertions between `25` and `45` after subtracting the version and description lines; (6) prints the feature-dir JSON.
**Failure check**: (1) reporting any `failed`/`error` means FAIL. (2) reporting any `FAIL` line means FAIL. (5) printing any value **≥ 1** means FAIL (`lint_outline.py` was modified). (4) showing a `SKILL.md` insertion count **< 25 or > 45** (net of the version and description lines) means FAIL. Any modified path outside this repository means FAIL. Note: `skills/structured-gist/scripts/validate_plugin.sh` is an **expected untracked path** — an operator-directed, orchestrator-authored plugin-validation harness that belongs to no task in this feature. Leave it in place, do not delete it, and do not count it as a scope breach. `git diff -U0 -- skills/structured-gist/tests/test_lint.py skills/structured-gist/CHANGELOG.md skills/structured-gist/tests/benchmark.md | grep -c '^-[^-]'` → any value **≥ 1** means FAIL (a pre-existing line was removed).

## Dependencies

- T001–T008 all touch `SKILL.md` → apply sequentially.
- T009 → T010 → T011 → T012 (helper needs the example's declaration format; fixtures need the helper; tests need both).
- T013 precedes T015, T016, T018 (they cite the new version).
- T014 and T017 are independent of Phase 2.
- T019 runs last.

## Traceability

| Requirement | Task(s) |
|---|---|
| FR-001, FR-002 | T001 |
| FR-003, FR-004, FR-005 | T002 |
| FR-006, FR-007 | T007 |
| FR-008 | T008 |
| FR-009, FR-010, FR-011, FR-012 | T004 |
| FR-013 | T003 |
| FR-014 | T006 |
| FR-015 | T005, T008 |
| FR-016 | T019 (gate) |
| FR-017 | T004, T009, T012 |
| FR-018 | T013, T015, T016 |
| FR-019 | T014 |
| FR-019a | T015 |
| FR-020 | T016 |
| FR-021 | T012, T019 |
| FR-022, FR-023, FR-024 | T010, T011, T012 |
| FR-025 | T017 |
| FR-026 | T018 |
| SC-001 | T009 |
| SC-002 | T001 |
| SC-003 | T010, T011, T012 |
| SC-004 | T004, T009, T012 |
| SC-005 | T019 |
| SC-006 | T019 |
