## Hedge Detection Blocker for R17 Error-Promotion

This comment demonstrates why error-promotion for the comma-split rule (R17, issue #9) must be **blocked** pending hedge detection.

### Concrete Counterexample

From the redaction-log approval:

> Registrar is unconfirmed - likely Squarespace Domains (site was built there), possibly Google Domains legacy or another registrar.

This is an epistemic hedge — a carefully qualified claim that preserves uncertainty:
- "unconfirmed" signals the claim's status
- "likely X" and "possibly Y-or-Z" capture relative confidence in alternatives
- The comma-split structure (list of hedged possibilities) is structural

### The Silent Failure Mode

If naive compression were applied to this outline (the same failure mode that rule R17 addresses), a careless tool could collapse this to:

> Registrar is unconfirmed likely Squarespace Domains, possibly Google Domains legacy

Or worse, drop the hedges entirely in pursuit of brevity:

> Registrar: Squarespace Domains or Google Domains legacy

This silently **promotes** an unconfirmed claim to a bare fact — exactly the kind of epistemic loss that makes error-promotion dangerous.

### Rule-Promotion Dependency

The comma-split rule (R17) is a **structural rule** about outline formatting. Promoting it to a hard error means the linter would refuse outlines that break the rule. But structural rules and epistemic integrity are entangled: an outline that violates R17 might do so to preserve hedging language that compression would otherwise strip.

**We cannot promote R17 to a hard error until the linter can also detect/measure whether hedging language survives compression.** If we don't have hedge detection, we cannot confidently say that enforcing R17 won't accidentally enforce the loss of epistemic qualification.

### Decision

Error-promotion for R17 is **blocked** on a prior feature: hedge detection (FR-003b). Until then, R17 remains a linting warning, not an error gate.

---

## Rule Allocation (FR-003a)

Per the design framework (specs/001-backlog-hedge-fidelity/spec.md § Design):

- **R16** = depth-indent rule (issue #6)
- **R17** = comma-split rule (issue #9)

Posted: https://github.com/domattioli/structured-gist/issues/9#issuecomment-5609119079
