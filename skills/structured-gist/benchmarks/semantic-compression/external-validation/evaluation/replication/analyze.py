#!/usr/bin/env python3
"""
Computes the replication-analysis dataset (H1-H8 support numbers,
cross-metric case flags, and simple exploratory correlations that respect
case-level clustering -- one point per CASE, not per (case,level) row,
for any correlation across cases). Pure arithmetic over the already-frozen
deterministic_scores.json / scores.json files. No model calls.

Writes evaluation/replication/hypothesis_results.json.

Run: python3 analyze.py
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

EXTERNAL_VALIDATION = Path(__file__).resolve().parent.parent.parent
EVAL = EXTERNAL_VALIDATION / "evaluation"
LEVELS = ["skim", "standard", "deep"]
DATASETS = ("qmsum", "qasper", "hotpotqa")


def load(dataset: str, name: str) -> dict:
    return json.loads((EVAL / dataset / f"{name}.json").read_text("utf-8"))


def spearman(xs, ys):
    n = len(xs)
    if n < 2:
        return None

    def ranks(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        r = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    varx = sum((a - mx) ** 2 for a in rx)
    vary = sum((b - my) ** 2 for b in ry)
    if varx == 0 or vary == 0:
        return None
    return cov / (varx * vary) ** 0.5


def mean(vals):
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 4) if vals else None


def median(vals):
    vals = [v for v in vals if v is not None]
    return round(statistics.median(vals), 4) if vals else None


def collect_dataset(dataset: str) -> dict:
    det = load(dataset, "deterministic_scores")
    sco = load(dataset, "scores")

    per_level = {lvl: {
        "reduction_pct": [], "conformance_violations": [], "conformance_clean_count": 0, "n_conformance": 0,
        "verbatim_node_rate": [], "extractive_coverage_min2": [],
        "fact_retention": [], "unweighted_retention": [], "relation_retention": [],
        "recoverability": [], "spr": [], "critical_total": 0, "critical_lost": 0, "critical_partial": 0,
        "unsupported": 0, "unverified": 0,
    } for lvl in LEVELS}

    case_level_rows = []  # (case_id, level, reduction_pct, fact_ret, rel_ret, recov, spr, critical_lost_frac)

    for case_id in sorted(set(det) & set(sco)):
        for lvl in LEVELS:
            d = det[case_id].get(lvl, {})
            s = sco[case_id].get(lvl, {})
            if d.get("status") != "scored":
                continue
            per_level[lvl]["reduction_pct"].append(d["reduction_pct"])
            per_level[lvl]["conformance_violations"].append(d["conformance_violation_count"])
            per_level[lvl]["n_conformance"] += 1
            if d["conformance_clean"]:
                per_level[lvl]["conformance_clean_count"] += 1
            wf = d.get("wording_fidelity") or {}
            if wf.get("verbatim_node_rate") is not None:
                per_level[lvl]["verbatim_node_rate"].append(wf["verbatim_node_rate"])
            if wf.get("extractive_coverage_min2") is not None:
                per_level[lvl]["extractive_coverage_min2"].append(wf["extractive_coverage_min2"])

            if s.get("status") != "scored":
                continue
            sem = s["semantic"]
            spr_ = s["spr"]
            if sem["task_weighted_fact_retention"] is not None:
                per_level[lvl]["fact_retention"].append(sem["task_weighted_fact_retention"])
            if sem["unweighted_retention"] is not None:
                per_level[lvl]["unweighted_retention"].append(sem["unweighted_retention"])
            if sem["relation_retention"] is not None:
                per_level[lvl]["relation_retention"].append(sem["relation_retention"])
            if sem["recoverability"] is not None:
                per_level[lvl]["recoverability"].append(sem["recoverability"])
            if spr_["semantic_preservation_recall"] is not None:
                per_level[lvl]["spr"].append(spr_["semantic_preservation_recall"])
            per_level[lvl]["critical_total"] += spr_["critical_units_total"]
            per_level[lvl]["critical_lost"] += spr_["critical_units_lost"]
            per_level[lvl]["critical_partial"] += spr_["critical_units_partial"]
            per_level[lvl]["unsupported"] += sem["unsupported_claim_count"]
            per_level[lvl]["unverified"] += sem["unverified_claim_count"]

            crit_lost_frac = (spr_["critical_units_lost"] / spr_["critical_units_total"]) if spr_["critical_units_total"] else None
            case_level_rows.append({
                "case_id": case_id, "level": lvl,
                "reduction_pct": d["reduction_pct"],
                "fact_retention": sem["task_weighted_fact_retention"],
                "relation_retention": sem["relation_retention"],
                "recoverability": sem["recoverability"],
                "spr": spr_["semantic_preservation_recall"],
                "critical_lost_frac": crit_lost_frac,
                "conformance_violations": d["conformance_violation_count"],
            })

    summary = {}
    for lvl in LEVELS:
        p = per_level[lvl]
        summary[lvl] = {
            "reduction_pct_mean": mean(p["reduction_pct"]),
            "conformance_violation_mean": mean(p["conformance_violations"]),
            "conformance_clean_rate": round(p["conformance_clean_count"] / p["n_conformance"], 4) if p["n_conformance"] else None,
            "verbatim_node_rate_mean": mean(p["verbatim_node_rate"]),
            "extractive_coverage_min2_mean": mean(p["extractive_coverage_min2"]),
            "fact_retention_mean": mean(p["fact_retention"]),
            "unweighted_retention_mean": mean(p["unweighted_retention"]),
            "relation_retention_mean": mean(p["relation_retention"]),
            "recoverability_mean": mean(p["recoverability"]),
            "spr_mean": mean(p["spr"]),
            "critical_units_total": p["critical_total"],
            "critical_units_lost": p["critical_lost"],
            "critical_units_partial": p["critical_partial"],
            "critical_loss_rate": round(p["critical_lost"] / p["critical_total"], 4) if p["critical_total"] else None,
            "unsupported_claims": p["unsupported"],
            "unverified_claims": p["unverified"],
        }

    return {"summary_by_level": summary, "case_level_rows": case_level_rows}


def main() -> int:
    all_data = {ds: collect_dataset(ds) for ds in DATASETS}

    # H2: correlate reduction_pct vs {fact_retention, recoverability, critical_lost_frac}
    # within each dataset's case-level rows (case is the unit; level rows from the
    # SAME case are repeated measures, so this is reported per-dataset and flagged
    # as descriptive, not treated as N independent points across the whole corpus).
    correlations = {}
    for ds, data in all_data.items():
        rows = data["case_level_rows"]
        xs = [r["reduction_pct"] for r in rows]
        pairs = {
            "reduction_vs_fact_retention": [r["fact_retention"] for r in rows],
            "reduction_vs_recoverability": [r["recoverability"] for r in rows],
            "reduction_vs_critical_lost_frac": [r["critical_lost_frac"] for r in rows],
            "reduction_vs_spr": [r["spr"] for r in rows],
        }
        correlations[ds] = {}
        for name, ys in pairs.items():
            valid = [(x, y) for x, y in zip(xs, ys) if y is not None]
            if len(valid) >= 3:
                vx, vy = zip(*valid)
                rho = spearman(list(vx), list(vy))
                correlations[ds][name] = {"spearman_rho": round(rho, 3) if rho is not None else None, "n": len(valid)}
            else:
                correlations[ds][name] = {"spearman_rho": None, "n": len(valid)}

    # H4: does critical loss correlate with recoverability failure? Case-level,
    # deep level only (deep has the most retained content, least confounding by omission).
    h4 = {}
    for ds, data in all_data.items():
        rows = [r for r in data["case_level_rows"] if r["level"] == "deep"]
        crit_lost = [r["critical_lost_frac"] for r in rows if r["critical_lost_frac"] is not None]
        recov_when_crit_lost = [r["recoverability"] for r in rows if r["critical_lost_frac"] and r["critical_lost_frac"] > 0]
        recov_when_no_crit_lost = [r["recoverability"] for r in rows if r["critical_lost_frac"] == 0]
        h4[ds] = {
            "n_cases_with_any_critical_loss_at_deep": sum(1 for f in crit_lost if f > 0),
            "n_cases_total_at_deep": len(rows),
            "recoverability_mean_when_critical_loss_present": mean(recov_when_crit_lost),
            "recoverability_mean_when_no_critical_loss": mean(recov_when_no_crit_lost),
        }

    out = {
        "per_dataset": {ds: data["summary_by_level"] for ds, data in all_data.items()},
        "case_level_rows": {ds: data["case_level_rows"] for ds, data in all_data.items()},
        "h2_correlations_reduction_vs_quality": correlations,
        "h4_critical_loss_vs_recoverability": h4,
    }

    out_path = Path(__file__).parent / "hypothesis_results.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    for ds in DATASETS:
        print(f"=== {ds} ===")
        for lvl in LEVELS:
            s = out["per_dataset"][ds][lvl]
            print(f"  {lvl}: reduction={s['reduction_pct_mean']} fact={s['fact_retention_mean']} "
                  f"rel={s['relation_retention_mean']} recov={s['recoverability_mean']} spr={s['spr_mean']} "
                  f"critLossRate={s['critical_loss_rate']} conformClean={s['conformance_clean_rate']} "
                  f"verbatimNode={s['verbatim_node_rate_mean']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
