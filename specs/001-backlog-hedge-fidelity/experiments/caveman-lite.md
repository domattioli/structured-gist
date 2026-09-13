# Experiment: sg-alone vs. sg-plus-caveman-lite (US7)

Pre-registered per FR-023 / T057. This file's prediction section is committed, standalone, before any run of either condition. Everything below the "Prediction" section is filled in later, as results land (T059-T063); the prediction itself is never edited retroactively.

## Conditions

- **sg-alone**: structured-gist rendering only (the existing condition already scored in `results/deterministic.json` / `results/combined.json`).
- **sg-plus-caveman-lite**: structured-gist rendering with caveman-lite compression rules applied on top, per DomI's `caveman` skill definition of the `lite` intensity level: "No filler/hedging. Keep articles + full sentences. Professional but tight." (source: `skills/caveman/SKILL.md`, Intensity table, `lite` row).

Both conditions are token-matched within ±5% per FR-021/T060 before the comparison is reported (T062 is the decision gate if they cannot be matched).

## Prediction (recorded before any run — FR-023)

**The paired condition (sg-plus-caveman-lite) retains hedging markedly worse than sg-alone, because compression rules delete hedging language by design.**

Rationale: caveman-lite's own operational definition explicitly instructs dropping "hedging" as one of its compression targets (alongside filler and pleasantries), while structured-gist alone has no such instruction and is the condition under which `hedge_survival_rate` was already measured favorably in the existing suite (see `results/deterministic.json` hedge fields for the deterministic-lane cases). The prediction is therefore that `hedge_survival_rate` for sg-plus-caveman-lite will be measurably lower than the corresponding sg-alone value(s) on the same cases, once both conditions are token-matched and run.

This prediction is falsifiable: T063 will mark it CONFIRMED or REFUTED against the measured `hedge_survival_rate` numbers once both conditions are run and scored.

## Token-matching log (T060)

_(to be filled in during T058-T060 — attempts and measured token deltas per case, until both conditions converge within ±5% or T062's decision gate fires)_

## Results (T061)

_(to be filled in after both conditions are run — hedge_survival_rate per condition, alongside existing retention metrics)_

## Conclusion (T063)

_(to be filled in last — prediction marked CONFIRMED or REFUTED against the measured numbers)_
