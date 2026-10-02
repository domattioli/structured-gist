# Archived granularity levels: skim and deep

Archived in v0.6.0 (2026-10-02). The skill now ships one granularity level, `standard`.

## Why

The controlled benchmark (DomI spec 005) scores the skill at `standard` only, so `skim` and `deep` have no current evidence behind them. Earlier in-repo measurements put weighted retention at 0.37 for `skim`, 0.89 for `standard` and 0.99 for `deep` (see the README Benchmarks section).

## What was archived

- `skim.md`: the request-cache example at `skim`.
- `deep.md`: the same example at `deep`.
- `self-explain-three-levels.md`: `examples/self-explain.md` as it was at v0.5.0, with all three levels.

The KG renderer (`skills/structured-gist/scripts/kg_render.py --level`) still carries all three prunes as part of the experimental KG mode.

## Spec text removed from SKILL.md (v0.5.0)

```text
## Granularity levels

- `skim` (**default**) → L1 concepts + one enumerated tier (L2). Concept spine only; low-priority detail collapsed.
- `standard` → through L3 as the content needs.
- `deep` → exhaustive. Every `↪` elaboration surfaced, nothing collapsed. **No depth cap.** Study / handoff.

Distinctness: same content → `skim` shallower than `standard` shallower-or-equal `deep`.
```

Activation was `/structured-gist [skim|standard|deep] [block [width N|auto]|responsive]`, with `skim` as the default.

## Return condition

A level comes back only with a controlled benchmark run at that level. Restoring a level means restoring its section in SKILL.md, its example under `skills/structured-gist/examples/`, its smoke and pytest checks, and bumping the version.
