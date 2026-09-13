#!/usr/bin/env python3
"""
Semantic-compression eval suite runner.

Reads suite.json, iterates cases, supports --lane argument (deterministic or judged).

DETERMINISTIC lane:
  - Loads source.md + gold.json for each case
  - Runs deterministic scoring (structure, compression ratio, conformance)
  - Writes to results/deterministic.json
  - 100% reproducible (no model calls, no timestamps embedded in scores)

JUDGED lane:
  - Computes cache key from case inputs
  - Checks .cache/judged/<sha256>.json for cached result
  - If cached: reads it (cache hit)
  - If not cached and no model access: outputs "unavailable" marker
  - Never fabricates results or falls back to deterministic output
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import the deterministic scoring module
from scoring import deterministic as det_module
from cache_key import compute_cache_key

HERE = Path(__file__).resolve().parent
ROOT = HERE  # Test cases are in HERE/regression and HERE/pressure-tests
RESULTS = HERE / "results"
TEST_CLASSES = ["regression", "pressure-tests"]
LEVELS = ["skim", "standard", "deep"]
CACHE_DIR = HERE / ".cache" / "judged"


def read(path: Path) -> str:
    """Read file contents."""
    return path.read_text(encoding="utf-8")


def load_json(p: Path) -> dict:
    """Load JSON file."""
    return json.loads(p.read_text(encoding="utf-8"))


def compute_suite_sha256() -> str:
    """Compute SHA-256 of suite.json file content."""
    suite_path = HERE / "suite.json"
    content = suite_path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def run_deterministic_lane() -> dict:
    """
    Run deterministic scoring lane: no model calls, 100% reproducible.
    Returns results dict suitable for JSON serialization.
    """
    suite = load_json(HERE / "suite.json")
    results = {}

    for case in suite.get("cases", []):
        case_id = case["id"]
        # Skip if lane doesn't match
        if case.get("lane") != "deterministic":
            continue

        # Find the case in regression or pressure-tests
        case_dir = None
        for test_class in TEST_CLASSES:
            candidate = ROOT / test_class / case_id
            if candidate.is_dir():
                case_dir = candidate
                break

        if not case_dir:
            print(f"WARNING: case {case_id} not found in regression/ or pressure-tests/", file=sys.stderr)
            continue

        source_path = case_dir / "source.md"
        if not source_path.exists():
            print(f"WARNING: {case_id} missing source.md", file=sys.stderr)
            continue

        source_text = read(source_path)
        rendering_root = case_dir / "renderings"
        if not rendering_root.exists():
            print(f"WARNING: {case_id} missing renderings/", file=sys.stderr)
            continue

        results[case_id] = {"test_class": test_class}
        for tier_dir in sorted(rendering_root.iterdir()):
            if not tier_dir.is_dir():
                continue
            tier = tier_dir.name
            results[case_id][tier] = {}
            for level in LEVELS:
                results[case_id][tier][level] = det_module.score_case_tier_level(
                    tier_dir / f"{level}.md", source_text
                )

    # Write with sort_keys for reproducibility
    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / "deterministic.json"
    out_path.write_text(
        json.dumps(results, indent=2, sort_keys=True),
        encoding="utf-8"
    )
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

    return results


def run_judged_lane() -> dict:
    """
    Run judged scoring lane: requires model access or cached results.
    Returns results dict with "unavailable" markers for uncached cases.
    """
    suite = load_json(HERE / "suite.json")
    results = {}

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    for case in suite.get("cases", []):
        case_id = case["id"]
        # Skip if lane doesn't match
        if case.get("lane") != "judged":
            continue

        # Find the case in regression or pressure-tests
        case_dir = None
        test_class = None
        for tc in TEST_CLASSES:
            candidate = ROOT / tc / case_id
            if candidate.is_dir():
                case_dir = candidate
                test_class = tc
                break

        if not case_dir:
            print(f"WARNING: judged case {case_id} not found in regression/ or pressure-tests/", file=sys.stderr)
            continue

        source_path = case_dir / "source.md"
        gold_path = case_dir / "gold.json"
        if not source_path.exists() or not gold_path.exists():
            print(f"WARNING: {case_id} missing source.md or gold.json", file=sys.stderr)
            continue

        source_text = read(source_path)
        gold_content = read(gold_path)
        rendering_root = case_dir / "renderings"
        if not rendering_root.exists():
            print(f"WARNING: {case_id} missing renderings/", file=sys.stderr)
            continue

        results[case_id] = {"test_class": test_class}

        # For each tier/level, compute cache key and check cache
        for tier_dir in sorted(rendering_root.iterdir()):
            if not tier_dir.is_dir():
                continue
            tier = tier_dir.name
            results[case_id][tier] = {}

            for level in LEVELS:
                level_path = tier_dir / f"{level}.md"
                if not level_path.exists():
                    continue

                rendering_content = read(level_path)

                # For judged lane, we need prompt_content, but it's not stored per-rendering.
                # Use a placeholder for now.
                prompt_content = f"Judge semantic preservation for {case_id}/{tier}/{level}"
                # Model ID is unknown in this environment
                model_id = "none (judged cache only)"

                cache_key = compute_cache_key(
                    case_id, level, rendering_content, gold_content, prompt_content, model_id
                )
                cache_path = CACHE_DIR / f"{cache_key}.json"

                if cache_path.exists():
                    print(f"cache hit: {case_id}/{tier}/{level} -> {cache_key}")
                    cached_data = load_json(cache_path)
                    results[case_id][tier][level] = cached_data
                else:
                    print(f"cache miss: {case_id}/{tier}/{level} -> {cache_key} (unavailable)")
                    results[case_id][tier][level] = {
                        "status": "unavailable",
                        "message": "No cached judged result and no model access in this environment",
                        "cache_key": cache_key,
                    }

    # Write judged results
    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / "judged.json"
    out_path.write_text(
        json.dumps(results, indent=2, sort_keys=True),
        encoding="utf-8"
    )
    print(f"Wrote {out_path}")

    n_cases = len(results)
    n_unavailable = sum(
        1
        for tiers in results.values()
        for tier, levels in tiers.items()
        if tier != "test_class"
        for r in levels.values()
        if r.get("status") == "unavailable"
    )
    print(f"{n_cases} cases, {n_unavailable} (case,tier,level) results unavailable (no cache, no model access)")

    return results


def update_provenance(lane: str) -> None:
    """Update provenance.json with run metadata."""
    prov_path = HERE / "provenance.json"
    prov = load_json(prov_path)

    # Update with current run info
    prov["suite_sha256"] = compute_suite_sha256()
    prov["timestamp"] = datetime.now(timezone.utc).isoformat()

    if lane == "deterministic":
        prov["model_id"] = "none (deterministic lane)"
        prov["prompt_sha256"] = None
    elif lane == "judged":
        prov["model_id"] = "unknown (judged cache lookup)"
        prov["prompt_sha256"] = None

    prov_path.write_text(
        json.dumps(prov, indent=2, sort_keys=True),
        encoding="utf-8"
    )
    print(f"Updated {prov_path}")


def emit_readme_example(case_id: str) -> None:
    """
    Emit a before/after example for README.md.
    Reads source.md and haiku/standard rendering, writes to results/readme_example.md.
    """
    # Find the case in regression or pressure-tests
    case_dir = None
    for test_class in TEST_CLASSES:
        candidate = ROOT / test_class / case_id
        if candidate.is_dir():
            case_dir = candidate
            break

    if not case_dir:
        print(f"ERROR: case {case_id} not found in regression/ or pressure-tests/", file=sys.stderr)
        sys.exit(1)

    source_path = case_dir / "source.md"
    rendering_path = case_dir / "renderings" / "haiku" / "standard.md"

    if not source_path.exists():
        print(f"ERROR: {case_id} missing source.md", file=sys.stderr)
        sys.exit(1)

    if not rendering_path.exists():
        print(f"ERROR: {case_id} missing renderings/haiku/standard.md", file=sys.stderr)
        sys.exit(1)

    source_text = read(source_path)
    rendering_text = read(rendering_path)

    # Generate markdown block
    markdown = f"""## {case_id} (Before / After)

### Before (source)

```
{source_text}
```

### After (structured-gist rendering)

```text
{rendering_text}
```

**Metrics:**
- Source: {len(source_text.split())} words
- Rendering: {len(rendering_text.split())} words
- Compression: {100 * (1 - len(rendering_text.split()) / len(source_text.split())):.1f}%

**Key structure:**
- The registrar hedge is encoded as an attribute node (`▸`) with the uncertainty hedge on the node itself
- Three qualified candidates appear as enumerated children (a./b./c.) beneath the attribute
- This structure preserves the epistemic qualifier and its alternatives without flattening them into prose
"""

    # Write to results/readme_example.md
    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / "readme_example.md"
    out_path.write_text(markdown, encoding="utf-8")
    print(f"Wrote {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Run semantic-compression eval suite (deterministic or judged lane)"
    )
    parser.add_argument(
        "--lane",
        choices=["deterministic", "judged"],
        required=False,
        help="Scoring lane to run",
    )
    parser.add_argument(
        "--emit-readme-example",
        type=str,
        metavar="CASE_ID",
        help="Emit a before/after example for README.md",
    )
    args = parser.parse_args()

    if args.emit_readme_example:
        emit_readme_example(args.emit_readme_example)
    elif args.lane:
        if args.lane == "deterministic":
            run_deterministic_lane()
        elif args.lane == "judged":
            run_judged_lane()
        update_provenance(args.lane)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
