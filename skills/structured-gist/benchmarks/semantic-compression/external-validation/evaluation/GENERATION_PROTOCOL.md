# Rendering generation protocol

You are generating `structured-gist` renderings of a source document, cold
— the same way the skill would be invoked on real content. You are NOT
evaluating anything, NOT told what "should" be preserved, and have no
information about how these renderings will later be scored.

## What you may read

- `skills/structured-gist/SKILL.md` (the skill definition — the grammar,
  the ladder, the render modes, the granularity levels)
- The one `source.md` you are given for each case

## What you must NOT read or know

- `external_gold.json`, `derived_gold.json`, `derived_blind_weights.json`,
  `provenance.json`, `coverage_audit.json` — none of these
- Any other case's source or rendering
- Anything under `pressure-tests/`, `regression/`, `scoring/`, `results/`
- The native question/query or reference answer for the case

## What to produce, per case

Three renderings: `skim`, `standard`, `deep`. Use `responsive` render mode
(markdown surface — these sources are `.md` files, and per `SKILL.md`
"markdown surface (GitHub, chat) → responsive"). Follow `SKILL.md`
exactly: the four-role ladder, the render-mode rules, the granularity
definitions. Do not invent your own compression heuristics beyond what
`SKILL.md` specifies.

Treat the case's `source.md` as the raw content to render — this is a
recap/explain-shaped document (a meeting transcript, a technical paper,
or a multi-paragraph QA context), which is exactly what `structured-gist`
targets. Apply the skill as you would to any long recap/explanation
input; do not special-case it because it came from an external dataset.

## Output

Write each rendering to the exact path given (three files per case:
`skim.md`, `standard.md`, `deep.md`), as plain markdown — the direct
`structured-gist` output for that source, nothing else prepended or
appended (no "Here is the outline:" preamble, no meta-commentary).

## What NOT to do

- Do not generate a rendering, judge whether it looks good, and
  regenerate. Whatever `structured-gist` produces on the first cold pass
  is what gets frozen — this is a measurement of the skill's actual
  behavior, not its best-case behavior.
- Do not look at another case's source or rendering while working on this
  one, even within the same batch — treat each case independently.
- Do not adjust your approach based on case difficulty, length, or
  content type beyond what `SKILL.md` itself directs.
