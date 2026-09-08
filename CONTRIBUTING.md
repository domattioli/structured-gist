# Contributing

This repository is a one-way, scrub-and-sync export of a skill developed in a private governance repo. Nobody edits files here directly and merges nothing back upstream — so a normal "open a PR, get it merged" flow does not apply. Two real paths exist instead.

## Report an issue or suggest a change

Open a GitHub issue: a linter false positive/negative, a render-mode defect, a trigger phrase that should activate the skill and doesn't, unclear docs. Include a minimal repro (the input outline or prompt, expected vs. actual). Issues are read and may inform the next scrub-sync from the private repo, but there is no SLA and no guarantee a given request lands.

## Fork and extend independently

If you want to change behavior yourself rather than wait, fork the repo. It works standalone:

- `skills/structured-gist/SKILL.md` is the complete specification — read it before changing anything.
- `skills/structured-gist/tests/lint_outline.py` is the conformance linter (15 rules, stdlib Python only, zero dependencies). Run it against your own fixtures: `python3 skills/structured-gist/tests/lint_outline.py < your_output.md`.
- `skills/structured-gist/tests/` has the pytest suite (`pytest skills/structured-gist/tests/`) — extend it alongside any linter-rule change; an unfollowed rule with no test is a rule that silently rots.
- Bump `version:` in `SKILL.md` frontmatter and add a row to `skills/structured-gist/tests/benchmark.md` for any behavior change — every version there justifies itself with a measured number, not a description. See existing rows for the format.
- A fork's changes never sync back here automatically; if you want to propose them for the upstream skill, open an issue describing the change and link the fork.

## What won't be accepted upstream

Pull requests opened directly against this repo. Since nothing here is hand-edited, a merged PR would be silently overwritten on the next scrub-sync — worse than no contribution at all. Use one of the two paths above instead.
