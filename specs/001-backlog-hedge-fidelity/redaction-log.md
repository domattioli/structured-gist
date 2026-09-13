# Redaction log — T004 decision gate

Per FR-010b: reviewing authority is the supervising operator session. Not delegated.

## Candidate 1 — registrar hedge chain

- **Source**: session `9ecc2fa7-e73a-43f0-ab1d-5f45d0516db9`, project `-Users-domattioli-Downloads`, 2026-07-28.
- **Verdict**: APPROVED (usable verbatim).
- **Text**: "Registrar is unconfirmed - likely Squarespace Domains (site was built there), possibly Google Domains legacy or another registrar."
- **Reasoning**: Real domain name (`mindmatterbh.com`) and business context, but no personal data under FR-010c's enumerated categories (no personal name, handle, phone, address, or identifier tied to an individual). Approved as-is.

## Candidate 2 — "Kiran"/phone conditional hedge

- **Source**: session `9ecc2fa7-e73a-43f0-ab1d-5f45d0516db9`, project `-Users-domattioli-Downloads`, 2026-07-31.
- **Verdict**: DROPPED. Not usable anywhere, in whole or paraphrased.
- **Text (for the record only, not for reuse)**: "...it could be Kiran's personal cell. If you confirm it's the practice line, I'll put it on th[e site]..."
- **Reasoning**: Names a real third-party individual and links them to a personal-cell-phone question — squarely within FR-010c's enumerated personal-data categories. Highest-sensitivity excerpt in the batch.
- **Consequence**: Per the clarify answer on file (spec.md `## Clarifications`), no fallback candidate is sought. Issue #3's step-3 new-issue filing (US3) proceeds with two test cases (registrar, deontic) instead of three, and the new issue's text must record that a second corpus case was attempted and dropped, and why.
