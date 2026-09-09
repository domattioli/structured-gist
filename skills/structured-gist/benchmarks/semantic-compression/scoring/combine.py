#!/usr/bin/env python3
"""
Combines deterministic.json (structure/size, no judgment) with each case's
judged/<tier>.json (semantic verdicts from an isolated judge) into one
per-(case,tier,level) metrics table, and emits both a machine-readable
results/combined.json and a human-readable results/SCORES.md.

Nothing here calls a model. All semantic content (was fact X retained? is
relation Y intact? is a claim genuinely unsupported by the source? is
question Q answerable?) was already decided by a judge and is only
*arithmetic* here.

Score encoding for a fact/relation status, used throughout:
    retained -> 1.0   partial -> 0.5   omitted -> 0.0   mutated -> 0.0
(mutated counts as 0 for retention -- it is a DIFFERENT failure mode from
omission, tracked separately, never averaged into "the fact came through OK".)

Semantic sufficiency: sum(weight_i * retention_i) / sum(weight_i) over a
case's gold facts -- "how much of the information that matters to the
case's intended reader/task survived the transformation." This is the same
arithmetic this suite has always run under the name `weighted_retention`;
`semantic_sufficiency` is the formal name for that number going forward.
Both keys are emitted with an identical value -- `weighted_retention` is
kept only because README.md/RESULTS.md quote baselines like "wRetention >=
0.95" and this suite doesn't want two independently-computed metrics that
mean the same thing. See README.md "Semantic sufficiency" and "Weight
semantics" for what a fact's `weight` means now (importance to the case's
stated `intent.reader`/`intent.task`, with category as a default heuristic,
not a universal importance ranking) and why baselines are observed
reference points, not a formal definition of sufficiency.

Scoring dimensions reported (decomposable, no master scalar):
    semantic_sufficiency (= weighted_retention), unweighted_retention,
    relation_retention, recoverability, unsupported_claim_count,
    conformance_violation_count, reduction_pct / compression_ratio

No compression-adjusted "density" composite is computed. Round-1 evidence
(see ../RESULTS.md) showed every meaning-per-word formula tried is
NEGATIVELY correlated with actual usefulness (recoverability) — do not
resurrect one here.

Hallucination / unsupported-claim correction: a judge here never sees
source.md, so "no matching gold fact" is not proof a claim is unsupported —
gold's fact list is a curated subset of the source, not an exhaustive one.
Every hallucination entry in judged/*.json therefore carries a
`source_supported` boolean, set by checking the claim directly against
source.md (see RESULTS.md "Hallucination correction" for how the current
values were verified). Only entries with source_supported=false count
toward `unsupported_claim_count`, the canonical metric. The raw judge-flagged
count is preserved as `flagged_vs_gold_count` for transparency but is NOT
the metric to gate on -- round 1 found it overcounts by roughly 20-to-0 on
this corpus.
"""
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = ROOT / "results"
TEST_CLASSES = ["regression", "pressure-tests"]

STATUS_SCORE = {"retained": 1.0, "partial": 0.5, "omitted": 0.0, "mutated": 0.0}
Q_SCORE = {"correct": 1.0, "partial": 0.5, "wrong": 0.0, "unanswerable": 0.0}
LEVELS = ["skim", "standard", "deep"]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def score_semantic(gold: dict, verdict: dict) -> dict:
    facts = gold.get("facts", [])
    relations = gold.get("relations", [])
    questions = gold.get("questions", [])

    fv = verdict.get("facts", {})
    rv = verdict.get("relations", {})
    qv = verdict.get("questions", {})
    halluc = verdict.get("hallucinations", [])

    total_weight = sum(f["weight"] for f in facts) or 1.0
    weighted_units = 0.0
    unweighted_units = 0.0
    n_omitted = 0
    n_mutated = 0

    for f in facts:
        st = fv.get(f["id"], {}).get("status", "omitted")
        s = STATUS_SCORE.get(st, 0.0)
        weighted_units += f["weight"] * s
        unweighted_units += s
        if st == "omitted":
            n_omitted += 1
        if st == "mutated":
            n_mutated += 1

    semantic_sufficiency = weighted_units / total_weight
    unweighted_retention = unweighted_units / len(facts) if facts else None

    rel_scores = [
        {"retained": 1.0, "partial": 0.5, "lost": 0.0}.get(
            rv.get(r["id"], {}).get("status", "lost"), 0.0
        )
        for r in relations
    ]
    relation_retention = (sum(rel_scores) / len(rel_scores)) if rel_scores else None

    q_scores = [
        Q_SCORE.get(qv.get(q["id"], {}).get("verdict", "unanswerable"), 0.0)
        for q in questions
    ]
    recoverability = (sum(q_scores) / len(q_scores)) if q_scores else None

    unsupported = [h for h in halluc if not h.get("source_supported", False)]

    sem_sufficiency_rounded = round(semantic_sufficiency, 4)

    return {
        "semantic_sufficiency": sem_sufficiency_rounded,
        # Historical alias, NOT independently computed -- always equal to
        # semantic_sufficiency above. Kept for continuity with baselines
        # already written down in README.md/RESULTS.md ("wRetention >= ...").
        "weighted_retention": sem_sufficiency_rounded,
        "unweighted_retention": round(unweighted_retention, 4) if unweighted_retention is not None else None,
        "relation_retention": round(relation_retention, 4) if relation_retention is not None else None,
        "recoverability": round(recoverability, 4) if recoverability is not None else None,
        "omission_rate": round(n_omitted / len(facts), 4) if facts else 0.0,
        "mutation_rate": round(n_mutated / len(facts), 4) if facts else 0.0,
        "unsupported_claim_count": len(unsupported),
        "unsupported_claims": unsupported,
        "flagged_vs_gold_count": len(halluc),
    }


def main():
    det = load_json(RESULTS / "deterministic.json")
    combined = {}

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
            if not gold_path.exists() or not judged_dir.exists():
                continue
            gold = load_json(gold_path)

            combined[case_id] = {
                "test_class": test_class,
                "pressure_tags": gold.get("pressure_tags", []),
                "size_bucket": gold.get("size_bucket"),
                # What the weights in this case's facts encode importance
                # for -- see README.md "Intended reader/task". Absent on a
                # case that hasn't been annotated yet; combine.py does not
                # require it.
                "intent": gold.get("intent"),
            }

            det_case = det.get(case_id, {})
            for judged_path in sorted(judged_dir.glob("*.json")):
                tier = judged_path.stem
                judged = load_json(judged_path)
                det_tier = det_case.get(tier, {})
                combined[case_id][tier] = {}
                for level in LEVELS:
                    if level not in judged:
                        continue
                    sem = score_semantic(gold, judged[level])
                    d = det_tier.get(level, {})
                    combined[case_id][tier][level] = {**d, **sem}

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "combined.json").write_text(json.dumps(combined, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {RESULTS / 'combined.json'}")

    write_scores_table(combined)


def write_scores_table(combined: dict):
    lines = []
    lines.append("# Semantic-compression eval suite: canonical scores (generated, do not hand-edit)\n")
    lines.append("Regenerate with `python3 scoring/deterministic.py && python3 scoring/combine.py`.\n")

    for test_class in TEST_CLASSES:
        cases = {k: v for k, v in combined.items() if v.get("test_class") == test_class}
        if not cases:
            continue
        lines.append(f"## {test_class}\n")

        lines.append("**Case intent** (what each case's fact weights are importance-*for* -- see README.md \"Intended reader/task\"; cases without one predate this schema field):\n")
        for case_id, c in sorted(cases.items()):
            intent = c.get("intent")
            if intent:
                rationale = f" _{intent['rationale']}_" if intent.get("rationale") else ""
                lines.append(f"- `{case_id}` -- reader: {intent.get('reader', '?')}; task: {intent.get('task', '?')}.{rationale}")
            else:
                lines.append(f"- `{case_id}` -- (no `intent` recorded yet)")
        lines.append("")

        header = (
            "| case | tier | level | src_w | out_w | reduction% | conform_viol | "
            "semSufficiency | relRetention | omission% | unsupported_claims | recoverability |"
        )
        lines.append(header)
        lines.append("|---" * 12 + "|")
        for case_id, tiers in sorted(cases.items()):
            for tier, levels in tiers.items():
                if tier in ("test_class", "pressure_tags", "size_bucket", "intent"):
                    continue
                for level in LEVELS:
                    r = levels.get(level)
                    if not r:
                        continue
                    lines.append(
                        f"| {case_id} | {tier} | {level} | {r.get('source_words')} | {r.get('output_words')} | "
                        f"{r.get('reduction_pct')} | {r.get('conformance_violation_count')} | "
                        f"{r.get('semantic_sufficiency')} | {r.get('relation_retention')} | "
                        f"{round((r.get('omission_rate') or 0)*100,1)} | {r.get('unsupported_claim_count')} | "
                        f"{r.get('recoverability')} |"
                    )
        lines.append("")

    out = RESULTS / "SCORES.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
