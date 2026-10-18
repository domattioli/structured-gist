# Install

Add this repo as a plugin marketplace, then install:

```
/plugin marketplace add domattioli/structured-gist
/plugin install structured-gist
```

After installation, invoke the skill with:

```
/structured-gist [block [width N|auto]|responsive]
```

Where:
- `block` (default) renders a fenced outline. Its line budget is 64 columns unless you pass `width N` (exact, no cap) or `width auto` (terminal width minus 8, clamped to 32-120).
- `responsive` renders a real nested list for Markdown surfaces.

Output uses one granularity level, `standard`. `skim` and `deep` are archived.

See `SKILL.md` for the complete rule set and render-mode details.
