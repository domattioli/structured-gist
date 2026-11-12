# Model-effort sweep

This harness measures how the generator model and its reasoning effort
affect structured-gist outlines. Six generator models each render the nine
cases of the semantic-compression suite at three effort levels, using the
`standard` granularity in `block` mode. Two judges from different vendors
then grade every outline against the suite's gold facts, relations, and
questions.

The harness reuses the semantic-compression suite and does not copy it. Case
ids come from `../semantic-compression/suite.json`, sources and gold files
from `../semantic-compression/{regression,pressure-tests}/<case>/`, semantic
arithmetic from `../semantic-compression/scoring/combine.py`
(`score_semantic`), and structure and size metrics from
`../semantic-compression/scoring/deterministic.py` (`score_case_tier_level`,
which runs the shipped linter).

## Matrix

| factor | levels |
|---|---|
| generator | haiku (`claude-haiku-4-5-20251001`), sonnet (`claude-sonnet-5-5`), opus (`claude-opus-5-5`) through the Claude CLI; luna, terra, sol through `agents-inc run` (Codex aliases) |
| effort | low, medium, high |
| case | the 9 cases in `suite.json` |
| granularity, mode | `standard`, `block` (fixed) |
| condition | `{"caveman": "off"}` (fixed in this sweep) |

That gives 6 x 3 x 9 = 162 generation cells. Each cell is judged by fable
(`claude-fable-5-1`) and astra (Codex alias), both at medium effort, so a
full run makes 324 judge items, each with up to two calls.

All settings live in `config.json`.

## Isolation

The sweep tries to measure the model and the skill text, not the
operator's environment.

- Claude calls run `claude -p` with `--tools ""` (no tools),
  `--strict-mcp-config` (no MCP servers), `--setting-sources ""` (no user,
  project, or local settings; the aim is that the operator's global
  instructions and any project AGENTS.md are not loaded), `--no-session-persistence`,
  and a fixed one-line system prompt. The prompt goes on stdin. Before the
  first real run, check with one probe call that no operator instruction
  leaks into a reply; the offline tests cannot verify this.
- Codex calls run `agents-inc run` with `CODEX_HOME` set to a dedicated
  benchmark home (default `~/.codex-bench`), so the operator's usual Codex
  configuration and instructions do not apply. The harness refuses to start
  a Codex call when `<codex_home>/auth.json` does not exist. It only checks
  that the file exists; it never opens or copies it.
- Every call runs in a fresh, empty temporary directory, never inside the
  repository.
- The generation prompt contains a fixed instruction, the full `SKILL.md`,
  and the case source, nothing else. Its SHA-256 and the SHA-256 of
  `SKILL.md` are recorded in each cell's `meta.json`.

The operator's sessions normally run with caveman compression on. This sweep
switches it off and records `condition: {"caveman": "off"}` in every
`meta.json` and in `results/sweep.json`. Caveman level is a candidate factor
for a future sweep; the condition field exists so those runs stay
comparable with this one.

## Judge protocol

The protocol follows `../semantic-compression/RESULTS.md` section 5 and the
README section "Hallucination / unsupported-claim correction".

1. Pass 1 is source-blind and model-blind. The judge receives the gold fact,
   relation, and question lists (ids and text, never gold's source quotes)
   and the outline. It never sees `source.md` and never learns which model
   wrote the outline. It returns a verdict with an evidence quote for every
   fact and relation, an answer for every question, and a list of outline
   claims that no gold fact covers.
2. Pass 2 gives the same judge `source.md` and the flagged claims, and asks
   whether the source supports each one. The answer is stored as
   `source_supported` on each flagged claim. This is the only step with
   source access. A claim that pass 2 could not check keeps no
   `source_supported` value and counts as unverified, never as unsupported.
3. A reply that is not valid JSON, or that leaves out a gold id, is retried
   once. A second failure writes `judged/<judge>/<case>/<cell>.error.json`
   and no verdict.
4. `score.py` compares the two judges item by item: fact status, relation
   status, question verdict, and `source_supported` for a claim both judges
   flagged. Every disagreement goes to `results/DISAGREEMENTS.md`. The
   operator records tiebreaks in `tiebreaks.json` as
   `{case: {cell: {item_id: verdict}}}`; `score.py` writes a template of
   nulls when the file does not exist yet and never overwrites it.
5. The resolved verdict for an item is the agreed value, otherwise the
   operator tiebreak, otherwise the mean of the two judges' item scores.
   Items in the last group are counted as unresolved in `sweep.json`,
   `SWEEP_SCORES.md`, and the plot captions.

## Run order

Run every step from this folder.

```bash
python3 generate.py --dry-run     # print the 162-cell matrix and planned commands
python3 generate.py               # write runs/<case>/<model>-<effort>/
python3 judge.py --dry-run
python3 judge.py                  # write judged/<judge>/<case>/<model>-<effort>.json
python3 score.py                  # write results/ and the tiebreaks.json template
# fill tiebreaks.json if you want to settle disagreements, then:
python3 score.py
python3 plot.py                   # write results/plots/*.svg
```

`generate.py` and `judge.py` accept `--only-model`, `--only-effort`,
`--only-case` (each repeatable), `--limit N`, and `--dry-run`; `judge.py`
also accepts `--only-judge`. Both resume: a cell with a successful
`meta.json` and a judge item whose second pass finished are skipped. A failed
call is recorded with its exit code and stderr tail and is retried on the
next run. Concurrency and the per-call timeout come from `config.json`.

The tests stub every backend and write only to temporary directories:

```bash
python3 -m pytest tests -q
```

## Outputs

- `runs/<case>/<model>-<effort>/standard.md`: the extracted outline.
- `runs/.../raw.txt`: the unparsed reply.
- `runs/.../meta.json`: model id, backend, effort, condition, tokens, cost,
  duration, exit code, hashes, UTC timestamps.
- `judged/<judge>/<case>/<model>-<effort>.json`: verdict in the
  semantic-compression judged schema plus a `_meta` block.
- `results/sweep.json`: per-judge and resolved metrics per cell, and the
  mean, min, and max over cases for each model and effort.
- `results/SWEEP_SCORES.md`, `results/DISAGREEMENTS.md`: generated tables.
- `results/plots/*.svg`: one chart per metric and an overview. The charts
  use CSS color variables with a dark-mode override and are byte-identical
  for the same `sweep.json`.

Codex calls report one total token count, stored as `total_tokens`; their
input and output token counts and cost stay empty rather than zero.

## Limitations

- Each cell runs once. Differences between neighbouring effort levels can be
  within run-to-run noise, and the harness does not estimate that noise.
- Nine small cases cannot represent every kind of source text. The min-max
  whiskers show spread across cases, not a confidence interval.
- Judges can favour outputs from their own model family. Using one judge
  from each vendor and showing both judges' scores next to the resolved score
  exposes this bias but does not remove it.
- Effort levels mean different things in different products. Claude's and
  Codex's `low`, `medium`, and `high` settings are not calibrated against
  each other, so compare effort trends within a vendor before comparing
  across vendors.
- Token counts are not comparable across backends: Claude reports input and
  output separately, while Codex reports a single total.
