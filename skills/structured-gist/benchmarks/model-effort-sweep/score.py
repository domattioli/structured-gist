#!/usr/bin/env python3
"""
Scoring step of the model-effort sweep. Makes no model calls.

Per (case, generator-effort cell, judge):
    semantic metrics from ../semantic-compression/scoring/combine.py
    `score_semantic(gold, verdict)` and deterministic metrics from
    ../semantic-compression/scoring/deterministic.py
    `score_case_tier_level(rendering_path, source_text)` (reduction %, lint
    violations, word counts), plus token/cost data from the run's meta.json.

Judge disagreement, per item:
    fact status, relation status, question verdict, and `source_supported`
    for a hallucination claim both judges flagged (matched on normalised
    claim text). Every disagreement is listed in results/DISAGREEMENTS.md.
    tiebreaks.json (in this folder, written as a template of nulls when
    absent) is where the operator records a verdict:
        {case: {cell: {item_id: verdict}}}
    where verdict is a fact/relation status, a question verdict, or
    true/false for a hallucination item.

Resolution, per item:
    agreed value; else the operator tiebreak when given; else the mean of
    the two judges' item scores, flagged unresolved. Implemented without
    re-deriving combine.py's arithmetic: build verdict A (judge 1) and B
    (judge 2), overwrite tiebroken items in both with the tiebreak, then
    average score_semantic(A) and score_semantic(B). Every metric is linear
    in its item scores, so that average equals the per-item mean exactly.
    Hallucination claims flagged by only one judge are not item
    disagreements; their counts enter the resolved value as the mean of
    the two judges' counts.

Writes:
    results/sweep.json        per judge, resolved, a judge-independent
                              `deterministic` table (every run with an
                              outline), and per (generator, effort)
                              mean/min/max/n over cases, with unresolved
                              counts. Deterministic metrics (reduction,
                              lint, words, tokens, cost, duration) are
                              aggregated over every run in every view;
                              judge metrics over that view's judged runs.
    results/SWEEP_SCORES.md   generated tables
    results/DISAGREEMENTS.md  one row per disagreeing item
    tiebreaks.json            only when absent
"""
import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

from generate import (CONFIG_PATH, HERE, cell_name, load_cases, load_config, load_json,
                      read, run_dir, write_json)
from judge import FACT_STATUSES, Q_VERDICTS, REL_STATUSES, judged_path

SCORING_DIR = HERE.parent / "semantic-compression" / "scoring"
sys.path.insert(0, str(SCORING_DIR))
import combine  # noqa: E402
import deterministic  # noqa: E402

# kind -> (verdict field, default when the judge left the item out, allowed values)
# Defaults mirror combine.score_semantic's own defaults.
KINDS = {
    "facts": ("status", "omitted", FACT_STATUSES),
    "relations": ("status", "lost", REL_STATUSES),
    "questions": ("verdict", "unanswerable", Q_VERDICTS),
}
GOLD_TEXT_FIELD = {"facts": "text", "relations": "text", "questions": "question"}

SEMANTIC_METRICS = [
    "task_weighted_fact_retention", "unweighted_retention", "relation_retention",
    "recoverability", "omission_rate", "mutation_rate", "unsupported_claim_count",
    "unverified_claim_count", "flagged_vs_gold_count",
]
DET_FIELDS = {"source_words": "source_words", "output_words": "output_words",
              "reduction_pct": "reduction_pct", "conformance_violation_count": "lint_violations",
              "is_block_mode": "is_block_mode"}
META_FIELDS = ["input_tokens", "output_tokens", "total_tokens", "cost_usd", "duration_s"]
# Judge-independent metrics: taken from every run with an outline in every view.
DET_METRICS = {"source_words", "output_words", "reduction_pct", "lint_violations", "is_block_mode",
               "input_tokens", "output_tokens", "total_tokens", "cost_usd", "duration_s"}
AGG_METRICS = [
    "task_weighted_fact_retention", "relation_retention", "recoverability", "reduction_pct",
    "lint_violations", "unsupported_claim_count", "unverified_claim_count", "output_tokens",
    "total_tokens", "input_tokens", "cost_usd", "duration_s", "output_words",
]
TIEBREAKS_NAME = "tiebreaks.json"


def claim_key(claim: str) -> str:
    norm = re.sub(r"\s+", " ", claim.strip().lower()).rstrip(" .;:")
    return "h:" + hashlib.sha1(norm.encode("utf-8")).hexdigest()[:10]


def _value(verdict: dict, kind: str, item_id: str) -> tuple:
    field, default, _ = KINDS[kind]
    item = verdict.get(kind, {}).get(item_id, {})
    return item.get(field, default), item.get("evidence", item.get("answer_given", ""))


def _halluc_map(verdict: dict) -> dict:
    out = {}
    for h in verdict.get("hallucinations", []):
        out.setdefault(claim_key(h.get("claim", "")), h)
    return out


def find_disagreements(gold: dict, va: dict, vb: dict) -> list:
    """Items on which two judges' verdicts differ."""
    out = []
    for kind in KINDS:
        for g in gold.get(kind, []):
            a, ea = _value(va, kind, g["id"])
            b, eb = _value(vb, kind, g["id"])
            if a != b:
                out.append({"kind": kind, "item_id": g["id"], "gold_text": g[GOLD_TEXT_FIELD[kind]],
                            "a": a, "a_evidence": ea, "b": b, "b_evidence": eb})
    ha, hb = _halluc_map(va), _halluc_map(vb)
    for key in sorted(set(ha) & set(hb)):
        sa, sb = ha[key].get("source_supported"), hb[key].get("source_supported")
        if isinstance(sa, bool) and isinstance(sb, bool) and sa != sb:
            out.append({"kind": "hallucinations", "item_id": key, "gold_text": ha[key]["claim"],
                        "a": sa, "a_evidence": ha[key].get("source_quote", ""),
                        "b": sb, "b_evidence": hb[key].get("source_quote", "")})
    return out


def _parse_tiebreak(kind: str, value):
    if value is None:
        return None
    if kind == "hallucinations":
        if isinstance(value, bool):
            return value
        v = str(value).strip().lower()
        if v in ("true", "supported", "yes"):
            return True
        if v in ("false", "unsupported", "no"):
            return False
        raise ValueError(f"tiebreak {value!r} for a hallucination item must be true/false")
    allowed = KINDS[kind][2]
    if value not in allowed:
        raise ValueError(f"tiebreak {value!r} for a {kind} item must be one of {sorted(allowed)}")
    return value


def _set(verdict: dict, kind: str, item_id: str, value) -> None:
    if kind == "hallucinations":
        for h in verdict.get("hallucinations", []):
            if claim_key(h.get("claim", "")) == item_id:
                h["source_supported"] = value
        return
    field = KINDS[kind][0]
    verdict.setdefault(kind, {}).setdefault(item_id, {})[field] = value


def _mean2(a, b):
    if a is None or b is None:
        return None
    return round((a + b) / 2, 4)


def resolve(gold: dict, va: dict, vb: dict, tiebreaks: dict) -> tuple:
    """(resolved semantic metrics, disagreements) for one cell. See the module docstring."""
    disagreements = find_disagreements(gold, va, vb)
    A, B = copy.deepcopy(va), copy.deepcopy(vb)
    unresolved, tiebroken = [], []
    for d in disagreements:
        tb = _parse_tiebreak(d["kind"], (tiebreaks or {}).get(d["item_id"]))
        if tb is None:
            unresolved.append(d["item_id"])
            continue
        _set(A, d["kind"], d["item_id"], tb)
        _set(B, d["kind"], d["item_id"], tb)
        tiebroken.append(d["item_id"])
    sa, sb = combine.score_semantic(gold, A), combine.score_semantic(gold, B)
    out = {m: _mean2(sa[m], sb[m]) for m in SEMANTIC_METRICS}
    out["disagreement_count"] = len(disagreements)
    out["tiebroken_items"] = tiebroken
    out["unresolved_items"] = unresolved
    out["unresolved_count"] = len(unresolved)
    return out, disagreements


def _agg(values: list) -> dict:
    vals = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if not vals:
        return {"mean": None, "min": None, "max": None, "n": 0}
    return {"mean": round(sum(vals) / len(vals), 4), "min": round(min(vals), 4),
            "max": round(max(vals), 4), "n": len(vals)}


def collect(cfg: dict, cases: list, root: Path, tiebreaks: dict) -> tuple:
    judges = [j["name"] for j in cfg["judges"]]
    per_judge = {j: {} for j in judges}
    resolved = {}
    det_table = {}
    disagreements = []
    for case in cases:
        cid = case["id"]
        gold = load_json(case["dir"] / "gold.json")
        source_text = read(case["dir"] / "source.md")
        for gen in cfg["generators"]:
            for effort in cfg["efforts"]:
                cell = cell_name(gen["name"], effort)
                d = run_dir(root, cid, gen["name"], effort)
                if not (d / "standard.md").exists() or not (d / "meta.json").exists():
                    continue
                meta = load_json(d / "meta.json")
                if meta.get("exit_code") != 0:
                    continue
                det = deterministic.score_case_tier_level(d / "standard.md", source_text)
                base = {out: det.get(src) for src, out in DET_FIELDS.items()}
                base.update({k: meta.get(k) for k in META_FIELDS})
                if base.get("total_tokens") is None and all(
                        isinstance(base.get(k), int) for k in ("input_tokens", "output_tokens")):
                    # Claude reports input and output separately; total = input + output
                    # (input already includes cache creation and cache reads).
                    base["total_tokens"] = base["input_tokens"] + base["output_tokens"]
                # Judge-independent: recorded for every run with an outline.
                det_table.setdefault(cid, {})[cell] = dict(base)
                verdicts = {}
                for j in judges:
                    p = judged_path(root, j, cid, cell)
                    if not p.exists():
                        continue
                    v = load_json(p)
                    verdicts[j] = v
                    sem = combine.score_semantic(gold, v)
                    per_judge[j].setdefault(cid, {})[cell] = {
                        **base, **{m: sem[m] for m in SEMANTIC_METRICS},
                        "pass2": v.get("_meta", {}).get("pass2")}
                if len(judges) >= 2 and all(j in verdicts for j in judges[:2]):
                    tb = tiebreaks.get(cid, {}).get(cell, {})
                    res, dis = resolve(gold, verdicts[judges[0]], verdicts[judges[1]], tb)
                    resolved.setdefault(cid, {})[cell] = {**base, **res}
                    for x in dis:
                        disagreements.append({"case": cid, "cell": cell, **x,
                                              "tiebreak": tb.get(x["item_id"])})
    return per_judge, resolved, det_table, disagreements


def aggregate(table: dict, det_table: dict, cfg: dict) -> dict:
    """Mean/min/max/n over cases per (generator, effort). Deterministic
    metrics come from det_table (every run with an outline, judged or not);
    judge metrics come from the view's own table."""
    out = {}
    for gen in cfg["generators"]:
        for effort in cfg["efforts"]:
            cell = cell_name(gen["name"], effort)
            rows = [c[cell] for c in table.values() if cell in c]
            det_rows = [c[cell] for c in det_table.values() if cell in c]
            judged = [m for m in AGG_METRICS if m not in DET_METRICS]
            if rows and "unresolved_count" in rows[0]:
                judged.append("unresolved_count")
            agg = {"n_cases": len(det_rows), "n_judged": len(rows)}
            agg.update({m: _agg([r.get(m) for r in det_rows]) for m in AGG_METRICS if m in DET_METRICS})
            agg.update({m: _agg([r.get(m) for r in rows]) for m in judged})
            out.setdefault(gen["name"], {})[effort] = agg
    return out


def _fmt(a: dict) -> str:
    if not a or a.get("mean") is None:
        return "n/a"
    if a["min"] == a["max"]:
        return f"{a['mean']:g} (n={a['n']})"
    return f"{a['mean']:g} [{a['min']:g}, {a['max']:g}] (n={a['n']})"


def _esc(s) -> str:
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def write_disagreements(path: Path, disagreements: list, judges: list) -> None:
    ja, jb = (judges + ["judge-b"])[:2]
    lines = ["# Judge disagreements (generated, do not hand-edit)", "",
             "Each row is one item on which the two judges disagree. Record your verdict in "
             f"`{TIEBREAKS_NAME}` as `{{case: {{cell: {{item_id: verdict}}}}}}`, then rerun "
             "`python3 score.py`. The tiebreak column echoes what that file holds.", "",
             f"Disagreeing items: {len(disagreements)}; with a tiebreak: "
             f"{sum(1 for d in disagreements if d['tiebreak'] is not None)}.", "",
             f"| case | cell | item id | gold text | {ja} verdict + evidence | {jb} verdict + evidence | tiebreak |",
             "|---|---|---|---|---|---|---|"]
    for d in disagreements:
        lines.append(
            f"| {_esc(d['case'])} | {_esc(d['cell'])} | {_esc(d['item_id'])} | {_esc(d['gold_text'])} | "
            f"**{_esc(d['a'])}**: {_esc(d['a_evidence'])} | **{_esc(d['b'])}**: {_esc(d['b_evidence'])} | "
            f"{_esc(d['tiebreak'])} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


TABLE_METRICS = [
    ("task_weighted_fact_retention", "Task-weighted fact retention"),
    ("relation_retention", "Relation retention"),
    ("recoverability", "Recoverability"),
    ("unsupported_claim_count", "Unsupported claims (confirmed)"),
    ("unverified_claim_count", "Unverified claims"),
    ("reduction_pct", "Reduction %"),
    ("lint_violations", "Lint violations"),
    ("output_tokens", "Output tokens"),
    ("total_tokens", "Total tokens (Claude: input + output)"),
    ("cost_usd", "Cost (USD)"),
]


def write_scores(path: Path, sweep: dict, cfg: dict) -> None:
    efforts = cfg["efforts"]
    lines = ["# Model-effort sweep scores (generated, do not hand-edit)", "",
             "Regenerate with `python3 score.py`. Cells show mean over cases "
             "[min, max] (n = cases contributing); n/a means no scored run yet. "
             "Reduction, lint, token, and cost tables cover every generated run, "
             "judged or not.", "",
             f"Granularity `{cfg['granularity']}`, mode `{cfg['mode']}`, condition "
             f"`{json.dumps(cfg['condition'], sort_keys=True)}`, cases: {sweep['n_cases']}, "
             f"judges: {', '.join(sweep['judges'])} (judge effort `{cfg['judge_effort']}`).", "",
             f"Unresolved judge disagreements: {sweep['unresolved']['total']} of "
             f"{sweep['unresolved']['disagreements']} disagreeing items "
             "(unresolved items are scored as the mean of the two judges).", ""]
    sections = [("resolved", "Resolved (agreed, tiebreak, or two-judge mean)")] + \
               [(j, f"Judge: {j}") for j in sweep["judges"]]
    for key, title in sections:
        agg = sweep["aggregate"].get(key, {})
        lines += [f"## {title}", ""]
        for metric, label in TABLE_METRICS:
            lines += [f"### {label}", "", "| generator | " + " | ".join(efforts) + " |",
                      "|---" * (len(efforts) + 1) + "|"]
            for gen in cfg["generators"]:
                row = [_fmt(agg.get(gen["name"], {}).get(e, {}).get(metric)) for e in efforts]
                lines.append(f"| {gen['name']} | " + " | ".join(row) + " |")
            lines.append("")
    lines += ["## Unresolved items per cell", "", "| generator | " + " | ".join(efforts) + " |",
              "|---" * (len(efforts) + 1) + "|"]
    for gen in cfg["generators"]:
        row = [str(sweep["unresolved"]["by_cell"].get(cell_name(gen["name"], e), 0)) for e in efforts]
        lines.append(f"| {gen['name']} | " + " | ".join(row) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(cfg: dict, cases: list, root: Path) -> dict:
    root = Path(root)
    tb_path = root / TIEBREAKS_NAME
    tiebreaks = load_json(tb_path) if tb_path.exists() else {}
    per_judge, resolved, det_table, disagreements = collect(cfg, cases, root, tiebreaks)
    judges = [j["name"] for j in cfg["judges"]]
    by_cell = {}
    for d in disagreements:
        if d["tiebreak"] is None:
            by_cell[d["cell"]] = by_cell.get(d["cell"], 0) + 1
    sweep = {
        "generators": [g["name"] for g in cfg["generators"]],
        "generator_models": {g["name"]: g["model"] for g in cfg["generators"]},
        "efforts": cfg["efforts"],
        "judges": judges,
        "judge_effort": cfg["judge_effort"],
        "granularity": cfg["granularity"],
        "mode": cfg["mode"],
        "condition": cfg["condition"],
        "n_cases": len(cases),
        "per_judge": per_judge,
        "resolved": resolved,
        "deterministic": det_table,
        "aggregate": {"resolved": aggregate(resolved, det_table, cfg),
                      **{j: aggregate(per_judge[j], det_table, cfg) for j in judges}},
        "unresolved": {"total": sum(by_cell.values()), "disagreements": len(disagreements),
                       "tiebroken": sum(1 for d in disagreements if d["tiebreak"] is not None),
                       "by_cell": dict(sorted(by_cell.items()))},
    }
    results = root / "results"
    results.mkdir(parents=True, exist_ok=True)
    write_json(results / "sweep.json", sweep)
    write_scores(results / "SWEEP_SCORES.md", sweep, cfg)
    write_disagreements(results / "DISAGREEMENTS.md", disagreements, judges)
    if not tb_path.exists():
        template = {}
        for d in disagreements:
            template.setdefault(d["case"], {}).setdefault(d["cell"], {})[d["item_id"]] = None
        write_json(tb_path, template)
    return sweep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config", type=Path, default=CONFIG_PATH)
    ap.add_argument("--root", type=Path, default=HERE)
    args = ap.parse_args(argv)
    cfg = load_config(args.config)
    sweep = build(cfg, load_cases(cfg), args.root)
    n = sum(len(c) for c in sweep["resolved"].values())
    print(f"scored {n} resolved cells; {sweep['unresolved']['disagreements']} disagreements, "
          f"{sweep['unresolved']['total']} unresolved")
    print(f"wrote {Path(args.root) / 'results'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
