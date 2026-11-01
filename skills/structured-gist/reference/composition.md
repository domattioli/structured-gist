# Composition with a public-prose wording skill and caveman — full spec

Pointer target from `SKILL.md` `## Caveman coexistence`. The load-bearing
independence rule stays in `SKILL.md` itself (smoke-gated); this file holds
the per-mode table and the surrounding rationale.

## Public wording belongs to a separate wording skill

On public reader-facing prose surfaces specifically, a separate public-prose
wording skill, if you use one, owns the wording inside nodes and `↪` leaves —
not caveman. caveman stays out of those surfaces entirely, so the compatibility
table below applies only where caveman is the active wording layer
(non-public, computer-facing surfaces). structured-gist itself never changes
wording on any surface.

## Compose per node

Only when caveman is separately active:
1. place by marker — structured-gist
2. enumerator wording compressed — **caveman, not structured-gist**
3. `↪` leaf text left readable — structured-gist

## Caveman modes

Invariants across ALL 6 caveman modes:
- structure (markers + indent + `↪`) unchanged — markers stay **Latin even under wenyan** (localizing to 一/甲 would break the taxonomy + cross-surface scan)
- the structural leaf marker is `↪`; the plain `→` in the wording column below is the inline cause-effect glyph (`X → Y`), a DIFFERENT role — they never swap
- enumerator wording delegated to caveman; the `↪` leaf is exempt from compression

| caveman mode | enumerator wording | markers | ↪ leaf |
|---|---|---|---|
| (none) | normal EN | Latin | readable |
| lite | tight EN | Latin | readable |
| full | fragments | Latin | readable |
| ultra | abbrev + `→` | Latin | readable |
| wenyan-lite | semi-文言 | Latin | readable |
| wenyan-full | 文言文 | Latin | readable |
| wenyan-ultra | extreme 文言 | Latin | readable |
