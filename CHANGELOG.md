# Changelog

Release notes for tagged versions. The release workflow publishes the section that matches the tag. The full per-version history, including releases before 0.9.0, is in [skills/structured-gist/CHANGELOG.md](skills/structured-gist/CHANGELOG.md).

## [Unreleased]

## [0.9.1] — 2026-10-23

### Fixed

- `structured-gist-claims --help` no longer crashes with `FileNotFoundError`. The command now parses its arguments with argparse: an optional `file` argument (stdin when omitted), `-h/--help` and `--version`. Output and exit codes for file and stdin input are unchanged.

## [0.9.0] — 2026-10-19

First release on PyPI. It covers the unreleased 0.7.0 and 0.8.0 work and the changes below.

### Added

- Python package `structured-gist` on PyPI. It installs the stdlib-only outline linter as the `structured-gist-lint` command and the `structured_gist` import package.
- Linter rule R17, advisory only: `structured-gist-lint --advisory` flags a `↪` explanation leaf that holds 2 or more commas outside code, quotes and parentheses. Advisories never change the exit code. R17 stays advisory until hedge detection exists ([#9](https://github.com/domattioli/structured-gist/issues/9)).
- `SKILL.md` pre-emit check: a six-step pass over word caps, enumerator case, delimiter tails, arrow rarity, sibling families and line width, run before an outline is sent ([#22](https://github.com/domattioli/structured-gist/issues/22)).
- Smoke-test ratchet on the benchmark renderings: `tests/renderings_lint_baseline.json` holds per-rule violation counts, and smoke fails when any rule's count rises ([#22](https://github.com/domattioli/structured-gist/issues/22)).
- Tag-push release workflow: tests, version gate, PyPI publish and GitHub release. Zenodo archives each GitHub release under the concept DOI.

### Changed

- Benchmark metric is `fact_retention_delta`, replacing `word_count_reduction_pct` (0.7.0). Output length is no longer the headline number ([#28](https://github.com/domattioli/structured-gist/issues/28)).
- The `block` line budget follows the terminal: `width auto` resolves to the terminal width minus 8, clamped to 32-120, and 64 when no width is known (0.8.0).
- Citation metadata names Dominik O. Mattioli with ORCID 0000-0002-7327-6337.
