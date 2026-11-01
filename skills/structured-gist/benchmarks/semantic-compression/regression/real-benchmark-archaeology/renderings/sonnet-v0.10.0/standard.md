```text
- Retired metric
    ▸ Definition
        ↪ `seconds_to_locate_fact` was wall-clock time for a
        reader to find a single fact by scanning an outline
        versus reading prose end to end.
    ▸ Track record
        ↪ Across six version bumps it was never once measured;
        every historical row citing it reads "not-measured" or
        "n/a."
    ▸ Retirement
        ↪ Formally retired on 2026-07-03.
- Replacement metric
    ▸ Name
        ↪ `word_count_reduction_pct` became the declared primary
        benchmark, as the only metric the project's history had
        ever recorded a real number for.
    ▸ Evidence
        ↪ The v0.2.9 row: a 147-word dense paragraph became an
        88-word outline over the same matched scope, a 40.1%
        reduction computed with a literal word count rather than
        estimated.
- Composite benchmark
    ▸ Origin
        ↪ v0.4.0 introduced `outline_quality_composite` under
        spec-023, combining retention, robustness, and brevity.
    ▸ Comparison
        ↪ Direct-prompt outline mode versus experimental KG
        mode, across a 20-source corpus.
    ▸ Composite scores
        a. direct-prompt 0.5488
        b. KG mode 0.7604
    ▸ Robustness
        ↪ KG mode scored a perfect 1.0 by construction, since it
        enforces structure mechanically.
    ▸ Retention scores
        a. direct-prompt 0.8285
        b. KG mode 0.7608
    ▸ Retention gap
        ↪ KG mode's stricter word budgets ended up dropping real
        content.
    ▸ Verdict
        ↪ Recorded as "iterate," not "ship": KG mode never
        became the default rendering path, and was later
        explicitly excluded from this repository's public-facing
        scaffold under spec-026's FR-006.
- Missing machinery
    ▸ Scripts
        a. `compare_corpus.py`
        b. `score_outline.py`
        c. 20-source corpus
    ▸ Status
        ↪ None of it exists anywhere in this checkout; it lived
        in a private upstream repository.
    ▸ Cause
        ↪ A series of "sync from DomI structured-gist skill"
        commits stripped it out when this public scaffold was
        built.
    ▸ Surviving evidence
        ↪ Only tiny non-functional placeholder stub files and
        the historical benchmark.md row.
- Abandoned approaches
    A. SCU scoring
    ↪ Semantic content-unit scoring compared outline quality
    against source text unit by unit, but was never formalized
    into a repeatable benchmark anyone could rerun.
    B. JSONL claim list
    ↪ Tested as a possible replacement for the tree-shaped
    outline; rejected outright because its recall dropped below
    the team's acceptance threshold.
- Open question
    ▸ Proposition
        ↪ Now that a real retention-scoring approach exists,
        should KG mode be revisited, or does its retention gap
        make that a dead end regardless of how good its
        structural robustness is?
```
