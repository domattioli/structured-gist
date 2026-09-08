base_source.md → test_benchmark.py axis isolates → ~10-sentence prose, no lists, ≥2 content words per sentence
base_outline.md → test_benchmark.py axis isolates → 2+ top-level concept blocks, valid fenced, lint-clean, covers most source sentences
brevity_padded.md → test_benchmark.py brevity isolate (fixture a) → token_set(outline_content_text) == token_set(base_outline), len(tokens) > base, lines ≤64 chars, identical-indent continuations
robustness_violated.md → test_benchmark.py robustness isolate → base_outline + exactly 2 injected structural violations (not content words), lint ≥2 violations
damage_series_1.md → test_benchmark.py damage-monotonicity → base_outline + 1 violation
damage_series_2.md → test_benchmark.py damage-monotonicity → base_outline + 2 violations
damage_series_3.md → test_benchmark.py damage-monotonicity → base_outline + 3 violations, strictly decreasing robustness
retention_swapped.md → test_benchmark.py retention isolate (fixture c) → base_outline + 1 branch's content replaced by equal-count NON-STOPWORD gibberish, token_set differs, len(tokens) equal, lines ≤64 chars, structure identical
degenerate/empty.md → test_benchmark.py degenerate suite → empty file, zero crashes
degenerate/single_fact_source.md → test_benchmark.py degenerate suite → single sentence source, handles edge case
degenerate/hallucinated_outline.md → test_benchmark.py degenerate suite → valid fenced outline, half base_source tokens + half invented
degenerate/unrelated_outline.md → test_benchmark.py degenerate suite → valid fenced outline, zero token overlap with base_source
degenerate/allstop_source.md → test_benchmark.py degenerate suite → all-stopword source ('It is what it is. So it goes.'), zero content words
degenerate/allstop_unit_source.md → test_benchmark.py degenerate suite → normal source + one all-stopword sentence → units_dropped count
degenerate/allstop_outline.md → test_benchmark.py degenerate suite → fenced outline, all node texts are stopwords only, precision ABSTAINED:no-outline-content
