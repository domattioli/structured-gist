# structured-gist — self-explain example

Before (paragraph, 70 words): structured-gist replaces a paragraph with a depth-coded outline — a concept, its attributes (properties of the concept, marked `▸`), then ordered or grouped enumerators, then a hook-arrow leaf carrying the one long sentence. A marker never nests under the same marker; to go deeper a hook interposes. Terse at every rung, four spaces each. Its own properties — marker ladder, length gradient, spacing — are attributes of structured-gist, unfolded below.

Outline (standard granularity; attributes carry their enumerated content):

```text
- structured-gist
    ▸ Marker ladder
        a. roman for order
        b. letter for groups
        ↪ never mix roman and letter as siblings
    ▸ Length gradient
        a. enumerator stays terse
        b. connective clause to a leaf
            ↪ because/since inside a node means split it
    ▸ Spacing
        a. four spaces per rung
        b. blank line between siblings
```

Here `Marker ladder`, `Length gradient`, `Spacing` are attributes *of* structured-gist (`▸`), not peer concepts — the fix.

Before → after (framing paragraph vs. the standard block, arrows and list markers excluded), measured not asserted:

```text
$ wc -w <<< "$before"
70
$ wc -w <<< "$after"
28
```

-60%: naming the concept's attributes replaces the paragraph's connective prose.

Rule index for properties not self-demonstrated above, and the
consolidation call vs. `standard.md`/`caveman-combo.md`:
`reference/self-explain-notes.md`.
