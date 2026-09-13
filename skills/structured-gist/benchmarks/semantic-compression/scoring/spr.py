#!/usr/bin/env python3
"""
Semantic Preservation Recall (SPR) -- an EXPERIMENTAL measurement, additive
to and never replacing this suite's canonical scoring in `combine.py`. See
`../SPR_FINDINGS.md` for what this experiment found and whether it should be
kept.

What this module answers: when task importance is annotated independently
(blinded to the existing category-derived weights, model renderings,
skim/standard/deep labels, judge verdicts, and scores) and relations are
promoted from a side diagnostic to a first-class weighted semantic unit
alongside facts, does the resulting weighted recall number explain this
suite's known successes and failures better than task-weighted fact
retention alone (`combine.py`'s `task_weighted_fact_retention`)?

Three numbers, each over a case's ANNOTATED semantic units (facts, then
relations, then both together), all built from the SAME blinded 1-3
task-importance scale recorded in `blind_weights/<case_id>.json`:

    blinded_task_weighted_fact_recall =
        sum(blind_weight_v * retention_v for fact v) / sum(blind_weight_v)

    task_weighted_relation_recall =
        sum(blind_weight_e * retention_e for relation e) / sum(blind_weight_e)

    semantic_preservation_recall (SPR) =
        (sum(blind_weight_v * retention_v for fact v) +
         sum(blind_weight_e * retention_e for relation e))
        / (sum(blind_weight_v for fact v) + sum(blind_weight_e for relation e))

retention is 1.0 retained, 0.5 partial, 0.0 omitted/mutated/lost -- the same
STATUS_SCORE encoding `combine.py` uses. No lambda/coefficient is applied
between facts and relations, and facts/relations are never separately
normalized and averaged 50/50 -- each annotated unit contributes to SPR in
proportion to its own blinded importance weight, nothing more. This is a
deliberate test of whether that's actually valid, not an assumption -- see
`SPR_FINDINGS.md` "Do facts and relations legitimately share one scale?".

CRITICAL: this module NEVER reads a fact's legacy `weight` field from
gold.json for any of the three formulas above. Only `blind_weights/*.json`
(annotation_protocol: blinded-task-importance-v1) feeds SPR's arithmetic.
The legacy weight is used in exactly one place in this file --
`compare_weights()`, a side-by-side descriptive comparison of the two weight
sources, never blended into a score. Mixing an unvalidated legacy weight
into a "task-weighted" score is exactly the mistake this experiment exists
to avoid (see `README.md` "Critical requirement: do not combine incomparable
weights").

Nothing here calls a model or re-judges anything. All semantic verdicts
(was fact X retained? is relation Y intact?) were already decided by the
same isolated judges `combine.py` reads from `judged/<tier>.json`; this
module only adds a second, independently-sourced weight to the same
preservation judgments.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = ROOT / "results"
BLIND_WEIGHTS_DIR = HERE / "blind_weights"
TEST_CLASSES = ["regression", "pressure-tests"]

STATUS_SCORE = {"retained": 1.0, "partial": 0.5, "omitted": 0.0, "mutated": 0.0}
REL_STATUS_SCORE = {"retained": 1.0, "partial": 0.5, "lost": 0.0}
LEVELS = ["skim", "standard", "deep"]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _round_half_up(x: float) -> int:
    return math.floor(x + 0.5)


def _rank(values):
    """Average ranks (1-indexed), ties get the mean of their tied positions.
    No scipy dependency -- this suite's verification runs in a disposable
    venv without it (see README.md "Re-running")."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def spearman_rho(xs, ys):
    """Spearman rank correlation, pure Python. Returns None if undefined
    (fewer than 2 points, or one side has zero variance -- e.g. every legacy
    weight in a tiny case is identical)."""
    n = len(xs)
    if n < 2:
        return None
    rx, ry = _rank(xs), _rank(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    varx = sum((a - mx) ** 2 for a in rx)
    vary = sum((b - my) ** 2 for b in ry)
    if varx == 0 or vary == 0:
        return None
    return cov / math.sqrt(varx * vary)


def compare_weights(gold_facts: list, blind_fact_weights: dict) -> dict:
    """Descriptive comparison of legacy category-derived fact weights
    (gold.json's `weight`, scale {1, 2, 2.5, 3}) against blinded
    task-importance fact weights (`blind_weights/<case>.json`, scale
    {1, 2, 3}). This is NOT part of any score -- it answers "was the old
    category heuristic already a good proxy for task importance, or does
    blinded task-aware weighting materially change what the corpus values?"
    (README.md "Next experiment").

    The two scales are not natively comparable (2.5 has no integer
    counterpart), so exact-agreement uses round-half-up on the legacy value
    (2.5 -> 3) -- a documented modeling choice, not a neutral fact. Mean
    absolute difference is reported on the legacy scale's own units (i.e.
    unrounded), so it is not directly interpretable as "number of ordinal
    steps" -- treat it as a relative-magnitude signal, not an exact count.
    """
    pairs = [(f["id"], f["weight"], blind_fact_weights[f["id"]]) for f in gold_facts]
    n = len(pairs)
    if n == 0:
        return {
            "n_facts": 0,
            "exact_agreement_rate": None,
            "mean_abs_diff_legacy_scale": None,
            "spearman_rho": None,
            "largest_disagreements": [],
        }
    legacy_rounded = [_round_half_up(l) for _, l, _ in pairs]
    blind_vals = [b for _, _, b in pairs]
    exact_agree = sum(1 for lr, b in zip(legacy_rounded, blind_vals) if lr == b)
    abs_diffs = [abs(l - b) for _, l, b in pairs]
    largest = sorted(
        ((fid, l, b, abs(l - b)) for fid, l, b in pairs), key=lambda t: -t[3]
    )[:3]
    return {
        "n_facts": n,
        "exact_agreement_rate": round(exact_agree / n, 4),
        "mean_abs_diff_legacy_scale": round(sum(abs_diffs) / n, 4),
        "spearman_rho": (
            round(r, 4) if (r := spearman_rho([l for _, l, _ in pairs], blind_vals)) is not None else None
        ),
        "largest_disagreements": [
            {"fact_id": fid, "legacy_weight": l, "blind_weight": b, "abs_diff": d}
            for fid, l, b, d in largest
            if d > 0
        ],
    }


def score_spr(gold: dict, verdict: dict, blind: dict) -> dict:
    """Compute blinded_task_weighted_fact_recall, task_weighted_relation_recall,
    and semantic_preservation_recall for one (case, tier, level). See module
    docstring for the formulas. `blind` must carry `fact_weights` covering
    every gold fact id and `relation_weights` covering every gold relation
    id -- a missing id is a hard KeyError (annotation coverage is a
    precondition here, not a runtime fallback -- see test_missing_blind_weight
    coverage note in test_spr.py for why this is deliberate)."""
    facts = gold.get("facts", [])
    relations = gold.get("relations", [])
    fv = verdict.get("facts", {})
    rv = verdict.get("relations", {})
    fw = blind["fact_weights"]
    rw = blind["relation_weights"]

    fact_terms = []
    for f in facts:
        fid = f["id"]
        st = fv.get(fid, {}).get("status", "omitted")
        fact_terms.append((fw[fid], STATUS_SCORE.get(st, 0.0), st))

    rel_terms = []
    for r in relations:
        rid = r["id"]
        st = rv.get(rid, {}).get("status", "lost")
        rel_terms.append((rw[rid], REL_STATUS_SCORE.get(st, 0.0), st))

    fact_weight_sum = sum(w for w, _, _ in fact_terms)
    fact_weighted_sum = sum(w * s for w, s, _ in fact_terms)
    blinded_task_weighted_fact_recall = (
        round(fact_weighted_sum / fact_weight_sum, 4) if fact_weight_sum else None
    )

    rel_weight_sum = sum(w for w, _, _ in rel_terms)
    rel_weighted_sum = sum(w * s for w, s, _ in rel_terms)
    task_weighted_relation_recall = (
        round(rel_weighted_sum / rel_weight_sum, 4) if rel_weight_sum else None
    )

    combined_weight_sum = fact_weight_sum + rel_weight_sum
    combined_weighted_sum = fact_weighted_sum + rel_weighted_sum
    spr = (
        round(combined_weighted_sum / combined_weight_sum, 4)
        if combined_weight_sum
        else None
    )

    # Critical-loss diagnostic: never a scalar, never blended into SPR --
    # guards against a healthy-looking average concealing one task-breaking
    # omission at blind weight 3 ("critical"). See README.md "Critical
    # semantic-loss diagnostic".
    critical_fact_terms = [(w, s, st) for w, s, st in fact_terms if w == 3]
    critical_rel_terms = [(w, s, st) for w, s, st in rel_terms if w == 3]
    critical_total = len(critical_fact_terms) + len(critical_rel_terms)
    critical_lost = (
        sum(1 for _, _, st in critical_fact_terms if st in ("omitted", "mutated"))
        + sum(1 for _, _, st in critical_rel_terms if st == "lost")
    )
    critical_partial = sum(
        1 for _, _, st in critical_fact_terms if st == "partial"
    ) + sum(1 for _, _, st in critical_rel_terms if st == "partial")

    return {
        "blinded_task_weighted_fact_recall": blinded_task_weighted_fact_recall,
        "task_weighted_relation_recall": task_weighted_relation_recall,
        "semantic_preservation_recall": spr,
        "critical_units_total": critical_total,
        "critical_units_lost": critical_lost,
        "critical_units_partial": critical_partial,
    }


def main():
    combined_path = RESULTS / "combined.json"
    if not combined_path.exists():
        raise SystemExit(
            "results/combined.json not found -- run scoring/deterministic.py "
            "and scoring/combine.py first (spr.py reuses their legacy "
            "columns for the comparison table rather than recomputing them)."
        )
    legacy = load_json(combined_path)

    spr_results = {}
    weight_comparison = {}

    for test_class in TEST_CLASSES:
        class_dir = ROOT / test_class
        if not class_dir.exists():
            continue
        for case_dir in sorted(class_dir.iterdir()):
            if not case_dir.is_dir():
                continue
            case_id = case_dir.name
            gold_path = case_dir / "gold.json"
            judged_dir = case_dir / "judged"
            blind_path = BLIND_WEIGHTS_DIR / f"{case_id}.json"
            if not gold_path.exists() or not judged_dir.exists():
                continue
            if not blind_path.exists():
                # No blinded annotation for this case -- excluded from SPR,
                # never silently scored 0 or skipped without a trace.
                continue
            gold = load_json(gold_path)
            blind = load_json(blind_path)
            assert blind["annotation_protocol"] == "blinded-task-importance-v1"
            assert blind["case_id"] == case_id

            weight_comparison[case_id] = compare_weights(
                gold.get("facts", []), blind["fact_weights"]
            )

            spr_results[case_id] = {"test_class": test_class}
            for judged_path in sorted(judged_dir.glob("*.json")):
                tier = judged_path.stem
                judged = load_json(judged_path)
                spr_results[case_id][tier] = {}
                for level in LEVELS:
                    if level not in judged:
                        continue
                    new = score_spr(gold, judged[level], blind)
                    old = legacy.get(case_id, {}).get(tier, {}).get(level, {})
                    spr_results[case_id][tier][level] = {
                        **new,
                        "legacy_task_weighted_fact_retention": old.get("task_weighted_fact_retention"),
                        "unweighted_relation_retention": old.get("relation_retention"),
                        "recoverability": old.get("recoverability"),
                        "compression_ratio": old.get("compression_ratio"),
                        "reduction_pct": old.get("reduction_pct"),
                        "conformance_violation_count": old.get("conformance_violation_count"),
                    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "spr.json").write_text(
        json.dumps(spr_results, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"Wrote {RESULTS / 'spr.json'}")
    (RESULTS / "weight_comparison.json").write_text(
        json.dumps(weight_comparison, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"Wrote {RESULTS / 'weight_comparison.json'}")

    write_spr_table(spr_results, weight_comparison)


def write_spr_table(spr_results: dict, weight_comparison: dict):
    lines = []
    lines.append("# Semantic Preservation Recall (SPR): experimental results (generated, do not hand-edit)\n")
    lines.append(
        "**Experimental, not canonical.** This table is produced by "
        "`scoring/spr.py`, a measurement additive to `scoring/combine.py` -- "
        "see `../SPR_FINDINGS.md` for the full write-up and whether this "
        "metric should be kept. Regenerate with "
        "`python3 scoring/deterministic.py && python3 scoring/combine.py && "
        "python3 scoring/spr.py`.\n"
    )

    lines.append("## Blinded weight comparison (legacy category-derived vs. blinded task-derived, facts only)\n")
    lines.append("| case | n facts | exact agreement | mean abs diff (legacy scale) | Spearman rho |")
    lines.append("|---|---|---|---|---|")
    for case_id, c in sorted(weight_comparison.items()):
        lines.append(
            f"| {case_id} | {c['n_facts']} | {c['exact_agreement_rate']} | "
            f"{c['mean_abs_diff_legacy_scale']} | {c['spearman_rho']} |"
        )
    lines.append("")

    lines.append("## SPR and component metrics per (case, tier, level)\n")
    header = (
        "| case | tier | level | compression | legacy fact retention | "
        "blinded fact recall | weighted relation recall | SPR | recoverability | "
        "critical lost/partial/total | conform_viol |"
    )
    lines.append(header)
    lines.append("|---" * 10 + "|")
    for case_id, tiers in sorted(spr_results.items()):
        for tier, levels in tiers.items():
            if tier == "test_class":
                continue
            for level in LEVELS:
                r = levels.get(level)
                if not r:
                    continue
                lines.append(
                    f"| {case_id} | {tier} | {level} | {r.get('reduction_pct')} | "
                    f"{r.get('legacy_task_weighted_fact_retention')} | "
                    f"{r.get('blinded_task_weighted_fact_recall')} | "
                    f"{r.get('task_weighted_relation_recall')} | "
                    f"{r.get('semantic_preservation_recall')} | "
                    f"{r.get('recoverability')} | "
                    f"{r.get('critical_units_lost')}/{r.get('critical_units_partial')}/{r.get('critical_units_total')} | "
                    f"{r.get('conformance_violation_count')} |"
                )
    lines.append("")

    out = RESULTS / "SPR_SCORES.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
