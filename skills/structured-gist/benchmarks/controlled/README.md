# Controlled benchmark

A pre-registered, length-matched comparison of the structured-gist skill
against four controls (plain prose, plain bullets, lead-N, TextRank) on the
42 frozen external-validation cases. The design lives in DomI
`specs/consumers/structured-gist/specs/005-controlled-benchmark/`. The rules
that bind this run are in `PREREGISTRATION.md` and `prereg.json` in this
directory.

Status: User Story 1 (pre-registration) is built. It is **not committed**
yet. The judges are sol and the free judges.
Nothing here has called a model.

## Layout

| Path | Contents |
|---|---|
| `PREREGISTRATION.md`, `prereg.json` | The pre-registration record. |
| `run.py` | The runner. `prereg-hash`, `verify-prereg`, and `build-items` work. Every other subcommand runs the gate and then exits 2 ("not implemented"). The model-calling ones exit 4 first unless `--confirm` matches an estimate, and no estimate exists yet. |
| `bench/words.py` | Word counter `alnum-token-v2`. |
| `bench/records.py` | Canonical JSON and JSONL IO, atomic writes, and a stdlib JSON Schema check. |
| `bench/cache.py` | Content-addressed, resumable call cache. |
| `bench/items.py` | The 42 items, built through `EV/adapters/common.py` (read-only). |
| `bench/prereg.py` | Hash, gate, and the SC-001 check. |
| `bench/stopwords.txt` | Frozen English stopword list for TextRank. |
| `prompts/` | Generation and judge prompts, and the outside-provider notice. |
| `schemas/` | Copies of the DomI contract schemas. |
| `runs/` | Run outputs. Only `.gitkeep` is committed before the gate. |
| `tests/` | `pytest` suite. No test calls a model or opens a socket. |

Paths below use: EV = `../semantic-compression/external-validation/`
(frozen, never edited), SC = `../semantic-compression/`.

## Run the tests

```bash
python3 -m pytest skills/structured-gist/benchmarks/controlled/tests -q
```

CI runs the same suite on Python 3.11 in
`.github/workflows/benchmark-deterministic.yml`.

## Pinned inputs covered by the pre-registration hash

`prereg_sha256 = sha256(canonical_json_bytes(prereg.json) + raw_bytes(PREREGISTRATION.md))`.

The hash covers the two files directly. Through the SHA-256 values pinned in
`prereg.json` it also covers these files. The gate recomputes each one and
refuses (exit 3) on any difference:

| `prereg.json` key | Live file |
|---|---|
| `generator.prompt_sha256.shared_user` | `prompts/shared_user.md` |
| `generator.prompt_sha256.skill_instruction` | `prompts/skill_instruction.md` |
| `generator.prompt_sha256.plain_system` | `prompts/plain_system.md` |
| `generator.prompt_sha256.prose_instruction` | `prompts/prose_instruction.md` |
| `generator.prompt_sha256.bullets_instruction` | `prompts/bullets_instruction.md` |
| `judges.judge_prompt_sha256` | `prompts/judge.md` |
| `judges.notice_sha256` | `prompts/provider_notice.txt` |
| `generator.skill_md_sha256` | `skills/structured-gist/SKILL.md` |
| `generator.render_modes_md_sha256` | `skills/structured-gist/reference/render-modes.md` |
| `scores.combine_py_sha256` | `SC/scoring/combine.py` |
| `textrank.stopwords_sha256` | `bench/stopwords.txt` |
| `corpus.corpus_manifest_sha256` | `EV/MANIFEST.json` |
| `corpus.derived_manifest_sha256` | `EV/DERIVED_MANIFEST.json` |

The gate also checks:

- `generator.skill_version` against the `version:` line of `SKILL.md`.
- `corpus.datasets` and `corpus.gold_relation_counts` against what
  `bench/items.py` computes from the frozen gold.
- The section-12 notice block in `PREREGISTRATION.md` byte for byte against
  `prompts/provider_notice.txt`.
- The 14 FR-001 headings, in order.
- Every 64-hex hash quoted in `PREREGISTRATION.md`, which must be one of the
  pinned values.

The runner code itself (`run.py`, `bench/*.py`) is not pinned by hash. It is
fixed by the commit that the SC-001 check ties runs to.

### Amendment rule

Any change to a pinned input or to either pre-registration file after the
commit means a **new version**:

- a new file version;
- a new `prereg_sha256`;
- a new run id (the default run id is `pr-<prereg_sha256[:12]>`, so it
  changes by itself);
- a dated entry under "Deviations" in `PREREGISTRATION.md`, giving the
  change and the reason.

Never edit in place. The gate refuses a working copy that differs from the
commit. It also refuses a run whose `manifest.json` records another hash.
`verify-prereg` lists older `pr-`/`dryrun-` run dirs as superseded and
ignores them. The dry run may change plumbing only (see
`PREREGISTRATION.md` section 14).

## Corpus hashes: what is checked

`EV/MANIFEST.json` records `source_sha256` per case. That value is the hash
of the **upstream** payload, not of `source.md`, and it cannot be recomputed
offline. It is copied into each item unchanged. The per-case integrity check
uses `transformed_case_sha256 = sha256(source.md bytes + external_gold.json
bytes)`, which matches for 42 of 42 cases. It also uses
`derived_gold_sha256` and `blind_weights_sha256` from
`EV/DERIVED_MANIFEST.json`, which match 42 of 42. The SHA-256 values of the
two manifest files themselves are pinned in `prereg.json`.

## CLI assumptions (T005)

Probed 2026-09-27 with `--help` and `--version` only. No prompt was sent.
The captured text is in `tests/fixtures/cli/`.

- `claude` 2.1.283. `--help` lists `-p/--print`, `--model`, `--effort`
  (low, medium, high, xhigh, max), `--tools` (`""` disables all tools),
  `--disable-slash-commands`, `--strict-mcp-config`,
  `--no-session-persistence`, `--setting-sources`, `--output-format`
  (text, json, stream-json), `--verbose`, `--bare`, `--system-prompt`, and
  `--append-system-prompt`.
- `--system-prompt-file` is **not** listed as its own option. It appears
  only inside the `--bare` description (`--system-prompt[-file]`). The
  generator adapter must not rely on it. Fallback: pass the skill text with
  `--system-prompt <contents>`. `SKILL.md` plus `render-modes.md` is about
  39 KB, well under `ARG_MAX`. A canary must confirm this before the run.
- `agents-inc` is an argparse launcher. `agents-inc run` takes `--model`
  (required), `--effort` (default `medium`), and `--cwd` (required).
- The codex-bridge wrappers `mask.sh`, `gask.sh`, and `oask.sh` have **no**
  `--help`: an unknown argument is sent to the provider as a prompt. They
  were **not executed**. Their usage was read from the script source, and
  the source SHA-256 is in each fixture.
- `mask.sh` sets `MODEL=$(tier_to_model "$TIER")` and has no flag or
  environment override for the model.
- `oask.sh` honours the `MODEL` environment variable and allows only `:free`
  models.
- All three wrappers refuse to run while `WORKERBEES_GOVERNANCE` is set. The
  runner must unset it for the subprocess only.

## Pre-commit review (T024), 2026-09-27

- `python3 run.py prereg-hash` exited 0.
- `python3 run.py build-items --run-id prereg-check` exited 0. It wrote 42
  items (QMSum 24, Qasper 10, HotpotQA 8), gold relation counts QMSum 50,
  Qasper 5, HotpotQA 7, and zero-relation cases QMSum 3, Qasper 6,
  HotpotQA 1. These match `prereg.json`.
- `pytest` on `tests/` was green.
- No file under `runs/` except `.gitkeep` and `prereg-check`, and no
  `calls/` directory anywhere.
- `runs/prereg-check/` was deleted afterwards. It must not be committed
  ahead of the gate.
- `verify-prereg` and every gated subcommand exit 3 on the live files, as
  expected. The files were not committed at that time.

## Open before the commit gate (T027)

- **T023**: the operator confirms the OpenRouter free daily limit (the
  default is 50; gemini is 200) and the generator backend
  (`claude-isolated-config` or `claude-bare`).
- After both, recompute nothing by hand. The only pinned hashes are file
  hashes, which do not change. The new `prereg_sha256` comes from
  `run.py prereg-hash`.
