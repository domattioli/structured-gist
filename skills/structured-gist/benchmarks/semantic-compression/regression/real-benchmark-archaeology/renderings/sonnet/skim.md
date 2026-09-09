```text
- Original metric
    I. seconds_to_locate_fact, never measured
    II. retired 2026-07-03

- Replacement metric
    A. word_count_reduction_pct now primary
    B. 40.1% cut (v0.2.9 test)

- Composite benchmark
    I. outline_quality_composite, v0.4.0
    II. KG mode scored higher, weaker retention
    III. iterate, not shipped

- Missing scoring code
    A. compare_corpus.py, score_outline.py gone
    B. stripped from public scaffold

- Earlier approaches
    A. SCU scoring, never formalized
    B. JSONL claim-list, rejected

- Open question
    I. revisit KG mode or dead end?
```
