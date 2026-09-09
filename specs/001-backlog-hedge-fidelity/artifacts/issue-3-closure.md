# Issue #3 Closure: Slide-Deck (.pptx) Render Target

Closing as **not planned**.

## Decision

The slide-deck render mode (mapping structured-gist outlines to PowerPoint via python-pptx) does not meet the bar for implementation given three convergent reasons.

## Explicit Reasons for Closure

### 1. Lossy Ladder-to-Slide Remapping

The proposed mapping encodes an arbitrary-depth outline tree onto flat PowerPoint slides. This mapping is fundamentally lossy—there is no clean lossless transformation of nested hierarchies to slide boundaries the way inline/block/responsive text render modes preserve structure. Concretely: arbitrary-depth nesting collapses to speaker notes or overflow; concepts with many attributes exceed slide real estate; deep-granularity trees with too much content per concept force design compromises (truncation, hiding, pagination) that degrade fidelity. There is no principled solution to "how deep is too deep?" or "when does a slide overflow?" that works across all input structures.

### 2. Absence of Falsifiable Success Metric

Unlike the linter (deterministic pass/fail rules) or the retention/compression benchmarks (quantified degradation), there is no stated way to test whether a given ladder-to-slide mapping is "correct." The issue requests "a prototype + accepted mapping" with no acceptance criteria, no target audience definition, and no way to validate that the mapping meets a user's needs. Success is unmeasurable, making it impossible to iterate or know when the implementation is complete.

### 3. Added Binary Dependency (python-pptx)

The skill currently has zero external runtime dependencies—pure Python standard library. Adding python-pptx introduces a new third-party binary dependency. This is a non-trivial cost: additional maintenance surface, platform-specific build issues, version conflicts, and cognitive load for users. Justifying this cost requires clear demand and a falsifiable success criterion (both absent here).

## Reopening Condition

This issue should be reopened if **demonstrated demand** emerges:
- Multiple users or downstream consumer repos explicitly requesting this render target, or
- A concrete use case with users who have validated they would actually use a deck render mode in their workflow.

Such demand would justify re-evaluating against the three criteria above and potentially reconsidering the tradeoffs.
