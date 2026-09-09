#!/usr/bin/env python3
"""
Deterministic layer of the semantic-compression eval suite.

Computes, per (test-class, case, model-tier, granularity level), the things
that need no judgment call at all:
  - source word count / output word count / compression ratio
  - structural conformance (reuses the REAL skill linter, unmodified) as a
    pass/fail gate, never blended into a semantic score

This script never calls a model and never guesses at meaning. Anything
requiring semantic judgment (retention, relations, unsupported-claim
checking, recoverability) lives in each case's judged/<tier>.json, produced
separately by an isolated judge, and is only *combined* here (see
combine.py), not computed here.

No compression-adjusted "density" composite is computed anywhere in this
file — round-1 evidence showed every such formula is negatively correlated
with actual usefulness (see ../RESULTS.md). Compression is reported as its
own number, never folded into a meaning score.

Usage:
    python3 deterministic.py     # scan regression/ + pressure-tests/, write results/deterministic.json
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # .../semantic-compression
RESULTS = ROOT / "results"
TEST_CLASSES = ["regression", "pressure-tests"]

# Reuse the real, shipped linter — do not reimplement structural rules here.
LINTER_PATH = ROOT.parent.parent / "tests"
sys.path.insert(0, str(LINTER_PATH))
import lint_outline  # noqa: E402

LEVELS = ["skim", "standard", "deep"]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def score_case_tier_level(rendering_path: Path, source_text: str) -> dict:
    if not rendering_path.exists():
        return {"status": "missing", "path": str(rendering_path)}

    text = read(rendering_path)
    outline_lines, is_block = lint_outline.extract_outline_from_text(text)
    output_words = lint_outline.count_words("\n".join(outline_lines))
    source_words = lint_outline.count_words(source_text)
    violations = lint_outline.lint_text(text)

    compression_ratio = (output_words / source_words) if source_words else None
    reduction_pct = (1 - compression_ratio) * 100 if compression_ratio is not None else None

    return {
        "status": "scored",
        "is_block_mode": is_block,
        "source_words": source_words,
        "output_words": output_words,
        "compression_ratio": round(compression_ratio, 4) if compression_ratio is not None else None,
        "reduction_pct": round(reduction_pct, 2) if reduction_pct is not None else None,
        "conformance_violation_count": len(violations),
        "conformance_violations": [
            {"line": v[0], "rule": v[1], "message": v[2]} for v in violations
        ],
        "conformance_clean": len(violations) == 0,
    }


def main():
    results = {}

    for test_class in TEST_CLASSES:
        class_dir = ROOT / test_class
        if not class_dir.exists():
            continue
        for case_dir in sorted(class_dir.iterdir()):
            if not case_dir.is_dir():
                continue
            case_id = case_dir.name
            source_path = case_dir / "source.md"
            if not source_path.exists():
                continue
            source_text = read(source_path)

            rendering_root = case_dir / "renderings"
            if not rendering_root.exists():
                continue

            results[case_id] = {"test_class": test_class}
            for tier_dir in sorted(rendering_root.iterdir()):
                if not tier_dir.is_dir():
                    continue
                tier = tier_dir.name
                results[case_id][tier] = {}
                for level in LEVELS:
                    results[case_id][tier][level] = score_case_tier_level(
                        tier_dir / f"{level}.md", source_text
                    )

    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / "deterministic.json"
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {out_path}")

    n_cases = len(results)
    n_scored = sum(
        1
        for tiers in results.values()
        for tier, levels in tiers.items()
        if tier != "test_class"
        for r in levels.values()
        if r.get("status") == "scored"
    )
    print(f"{n_cases} cases, {n_scored} (case,tier,level) renderings scored")


if __name__ == "__main__":
    main()
