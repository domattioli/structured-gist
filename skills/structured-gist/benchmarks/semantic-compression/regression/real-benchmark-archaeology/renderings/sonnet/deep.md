```text
- Original metric
    ▸ Definition
        ↪ wall-clock time for a reader to locate one
        fact scanning an outline vs reading prose
        end-to-end
    ▸ Track record
        ↪ across six version bumps, never once
        measured — every row cites "not-measured" or
        "n/a"
    ▸ Fate
        ↪ retired 2026-07-03, due to that unmeasured
        track record

- Replacement metric
    ▸ Adoption reason
        ↪ declared primary benchmark because it was
        the only metric ever recorded with a real
        number
    ▸ v0.2.9 evidence
        a. 147-word paragraph → 88-word outline
        (matched scope)
        b. 40.1% reduction
            ↪ a literal word count, not an estimate

- Composite benchmark
    ▸ Composition
        ↪ v0.4.0 introduced outline_quality_composite
        (spec-023): three axes — retention,
        robustness, brevity
    ▸ Comparison setup
        ↪ direct-prompt outline mode vs experimental
        KG (knowledge-graph) mode, across a
        20-source corpus
    ▸ Results
        a. direct-prompt composite 0.5488
        b. KG composite 0.7604 (higher overall)
        c. KG robustness 1.0
            ↪ perfect by construction — KG mode
            enforces structure mechanically
        d. KG retention 0.7608 vs 0.8285
        (direct-prompt)
            ↪ lower because KG's stricter word
            budgets dropped real content
    ▸ Verdict
        ↪ "iterate," not "ship" — KG mode never
        became the default rendering path; later
        excluded from the public scaffold under
        spec-026 FR-006

- Missing scoring code
    ▸ What's absent
        ↪ compare_corpus.py, score_outline.py, and
        the 20-source corpus behind the v0.4.0 row —
        none exist in this checkout
    ▸ Cause
        ↪ scripts lived in a private upstream repo;
        "sync from DomI structured-gist skill"
        commits stripped them when this public
        scaffold was built
    ▸ Surviving evidence
        ↪ only tiny, non-functional placeholder stub files and
        the historical benchmark.md row remain — the sole
        evidence the measurement ever happened

- Earlier approaches
    A. SCU scoring
        ↪ semantic content-unit scoring, compared
        outline vs source text unit by unit; never
        formalized into a repeatable benchmark
    B. JSONL claim-list format
        ↪ tested as a replacement for the
        tree-shaped outline; rejected — recall fell
        below the acceptance threshold

- Open question
    ▸ Trade-off
        ↪ now that a real retention-scoring approach
        exists, should KG mode be revisited — or
        does its retention gap make that a dead end
        regardless of structural robustness?
```
