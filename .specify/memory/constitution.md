# structured-gist Constitution

**Version**: 1.0.0 | **Ratified**: 2026-09-09

## Principles

### P1 — Zero runtime dependencies
The skill and its linter run on the Python standard library alone. No new binary or
third-party runtime dependency may be added to ship a feature. Test-only and
CI-only tooling is exempt only when it is not required to use the skill.

### P2 — Every claim is falsifiable
A render target, rule, or metric enters the repo only with a stated success
criterion that can fail. Features whose success cannot be measured are deferred,
not built.

### P3 — No self-graded evidence
A component may not be the sole judge of its own output. Judged metrics must be
produced by a pinned, separately-recorded judge; deterministic metrics are
preferred wherever the property is mechanically checkable.

### P4 — Deterministic checks stay free
Anything mechanically checkable runs in CI at no model cost. Model-judged
evaluation is manually invoked and cached, never a CI gate.

### P5 — Structure is the invariant
Changes preserve the role ladder (concept → attribute → enumerator → explanation)
and the existing lint contract. New rules extend the ladder; they do not
reinterpret it.

### P6 — No personal data in the repo
Any excerpt sourced from conversation corpora passes an explicit redaction review
before it is written to any file, issue, comment, or fixture. Unredactable
material is dropped, not paraphrased into the repo.
