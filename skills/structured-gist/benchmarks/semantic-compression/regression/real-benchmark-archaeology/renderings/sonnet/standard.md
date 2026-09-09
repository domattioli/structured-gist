```text
- Original metric
    ▸ Definition
        ↪ wall-clock time to locate one fact:
        outline scan vs prose read
    ▸ Track record
        ↪ never measured across six version bumps
        — retired 2026-07-03

- Replacement metric
    ▸ Why adopted
        ↪ only metric ever recorded with a real
        number
    ▸ v0.2.9 evidence
        ↪ 147-word paragraph → 88-word outline,
        40.1% reduction, literal count

- Composite benchmark
    ▸ Composition
        ↪ v0.4.0's outline_quality_composite
        (spec-023): retention, robustness, brevity
    ▸ Results
        a. direct-prompt composite 0.5488
        b. KG composite 0.7604, robustness 1.0
        c. KG retention 0.7608 vs 0.8285
            ↪ lower — stricter word budgets
            dropped real content
    ▸ Verdict
        ↪ "iterate" — KG never became default;
        excluded under spec-026 FR-006

- Missing scoring code
    ▸ What's absent
        ↪ compare_corpus.py, score_outline.py,
        the 20-source corpus
    ▸ Cause
        ↪ lived in a private upstream repo;
        stripped by sync commits into this scaffold

- Earlier approaches
    A. SCU scoring
        ↪ unit-by-unit comparison, never
        formalized into a repeatable benchmark
    B. JSONL claim-list format
        ↪ rejected — recall fell below the
        acceptance threshold

- Open question
    ↪ revisit KG mode now that retention
    scoring exists, or is its retention gap a
    dead end regardless of robustness?
```
