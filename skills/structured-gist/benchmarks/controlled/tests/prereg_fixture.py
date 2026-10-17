"""Temporary pre-registration repositories for tests (tasks T017, T018).

Everything here writes only under a pytest ``tmp_path``. The real repository
is never touched: every git command runs with ``-C <tmp root>``, and commits
use explicit identity and ``core.hooksPath=/dev/null`` so no user hook runs.

The fixture computes every pinned hash itself with ``hashlib`` from the live
files, independently of ``bench/prereg.py``, so the tests check the module
against a second implementation.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

CB = Path(__file__).resolve().parent.parent
SG = CB.parent.parent
SC = SG / "benchmarks" / "semantic-compression"
EV = SC / "external-validation"


def _live_skill_version() -> str:
    m = re.search(r'^version:\s*"?([^"\n]+?)"?\s*$', (SG / "SKILL.md").read_text(encoding="utf-8"), re.MULTILINE)
    return m.group(1)

NOTICE_SHA256 = "463711420fb2e97f84b8ffc5ddde82ba5f116e65e8ec69e07621252fa48d6c82"
RELATION_COUNTS = {"qmsum": 50, "qasper": 5, "hotpotqa": 7}

HEADINGS = [
    "Question",
    "Cases and datasets",
    "Methods",
    "Length rule and tolerance",
    "Main scores",
    "Win rule",
    "Main judge and effort",
    "Judge panel, subset rule, retry policy, agreement statistics",
    "Secondary scores",
    "Uncertainty method",
    "Report shape",
    "Outside-provider notice",
    "Known limits",
    "Amendment and deviation rule",
]

JUDGE_IDS = ["sol", "gemini_flash", "nemotron_ultra", "qwen_fallback"]

GIT_ID = [
    "-c", "user.name=bench-test",
    "-c", "user.email=bench-test@example.invalid",
    "-c", "commit.gpgsign=false",
    "-c", "core.hooksPath=/dev/null",
]


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def expected_prereg_sha256(root: Path) -> str:
    obj = json.loads((root / "prereg.json").read_text(encoding="utf-8"))
    return hashlib.sha256(canonical(obj) + (root / "PREREGISTRATION.md").read_bytes()).hexdigest()


def testing_criteria() -> list[dict]:
    out = []
    for j in JUDGE_IDS:
        out.append({"name": f"judge_labels.{j}", "type": "label_model", "judge": j, "pass_threshold": None})
        out.append({"name": f"fact_retention.{j}", "type": "python", "judge": j, "pass_threshold": None})
        out.append({"name": f"relation_retention.{j}", "type": "python", "judge": j, "pass_threshold": None})
    out += [
        {"name": "rouge_l_recall", "type": "text_similarity", "evaluation_metric": "rouge_l", "dataset": "qmsum", "pass_threshold": None},
        {"name": "answer_token_recall", "type": "python", "dataset": "qasper", "pass_threshold": None},
        {"name": "answer_containment", "type": "python", "dataset": "hotpotqa", "pass_threshold": None},
        {"name": "words", "type": "python", "pass_threshold": None},
        {"name": "lint", "type": "python", "pass_threshold": None},
    ]
    return out


def make_prereg(root: Path) -> dict:
    """A complete, placeholder-free prereg.json for the tmp root, with every
    pinned hash computed from the live files."""
    prompts = root / "prompts"
    return {
        "version": 1,
        "question": "Does a structured-gist outline keep more of a source's facts and relations than other short versions of the same length?",
        "master_seed": "test-seed-0001",
        "corpus": {
            "datasets": {"qmsum": 24, "qasper": 10, "hotpotqa": 8},
            "corpus_manifest_sha256": sha(EV / "MANIFEST.json"),
            "derived_manifest_sha256": sha(EV / "DERIVED_MANIFEST.json"),
            "gold_relation_counts": dict(RELATION_COUNTS),
            "relation_check_threshold": 20,
        },
        "methods": ["skill", "plain_prose", "plain_bullets", "lead_n", "textrank"],
        "generator": {
            "model": "claude-opus-5-5", "effort": "medium", "backend": "claude-isolated-config",
            "skill_md_sha256": sha(SG / "SKILL.md"),
            "render_modes_md_sha256": sha(SG / "reference" / "render-modes.md"),
            "skill_version": _live_skill_version(),
            "prompt_sha256": {
                k: sha(prompts / f"{k}.md")
                for k in ("shared_user", "skill_instruction", "plain_system", "prose_instruction", "bullets_instruction")
            },
            "max_regenerations": 2,
            "failure_retries": 2,
        },
        "length": {
            "tolerance": 0.10, "word_counter": "alnum-token-v2", "strip_list_labels": True, "strip_html_comments": True,
            "flags": ["source_shorter_than_band", "length_violation"],
            "n_fallback": {"rule": "round(source_words * median(N / source_words))", "marker": "n_source: fallback_median_ratio"},
        },
        "textrank": {"damping": 0.85, "tol": 1e-6, "max_iter": 200, "stopwords_sha256": sha(root / "bench" / "stopwords.txt")},
        "scores": {"main": ["fact_retention", "relation_retention"], "combine_py_sha256": sha(SC / "scoring" / "combine.py")},
        "win_rule": {
            "test": "sign_flip_permutation_one_sided", "alpha": 0.05, "exact_max_n": 20, "monte_carlo_draws": 100000,
            "holm_families": ["fact_greater", "fact_less"], "unadjusted": ["relation_less"], "tie_tolerance": 1e-12,
            "verdict_labels": ["skill ahead", "mixed: facts ahead, relations behind", "no difference shown", "skill behind"],
            "controls": ["plain_bullets", "plain_prose", "lead_n", "textrank"],
        },
        "bootstrap": {
            "resamples": 10000, "type": "paired_percentile", "level": 0.95,
            "seed_mean": "master_seed:dataset:method", "seed_diff": "master_seed:dataset:control",
            "seed_permutation": "master_seed:perm:dataset:control:score",
        },
        "judges": {
            "main": {"id": "sol", "model": "gpt-5.6-sol", "effort": "medium", "max_attempts": 3, "check_resolved_model": True},
            "panel": [
                {"id": "gemini_flash", "model": "gemini-3.8-flash", "coverage": "all_best_effort", "daily_cap": 200},
                {"id": "nemotron_ultra", "model": "nvidia/nemotron-3-ultra-550b-a55b:free", "coverage": "all_best_effort", "daily_cap": 50,
                 "fallback": {"id": "qwen_fallback", "model": "qwen/qwen3.8-27b:free", "after_hours_without_success": 24}},
            ],
            "subset_rule": {"per_dataset": {"qmsum": 5, "qasper": 2, "hotpotqa": 2}, "order": "sha256(master_seed + ':subset:' + case_id) ascending"},
            "judge_prompt_sha256": sha(prompts / "judge.md"),
            "notice_sha256": sha(prompts / "provider_notice.txt"),
            "call_timeout_seconds": 600,
            "free_judge_id_change": "stop_judge_keep_scores",
            "retry_queue": {"base_minutes": 15, "cap_hours": 24, "jitter": 0.10, "attempt_limit": 8, "tick_seconds": 1800,
                            "retries_paid_judges": True, "paid_ceiling_check": True, "creates_entries": False},
        },
        "agreement": {"scale": ["lost", "partial", "retained"], "kappa": "quadratic_weighted_pairwise", "alpha": "krippendorff_ordinal", "raw_percent": True, "threshold": None},
        "secondary": {"qmsum": "rouge_l_recall", "qasper": "answer_token_recall", "hotpotqa": "answer_containment", "normalization": "squad_v1"},
        "report": {"pooled": False, "early_signal": ["qasper", "hotpotqa"], "first_row_control": "plain_bullets", "freeze_days_after_main_run": 7},
        "testing_criteria": testing_criteria(),
        "dry_run": {"cases": "first_case_id_per_dataset_ascending", "run_id": "dryrun-{prereg_sha256[:12]}",
                    "reported": False, "scores_inspected": False, "reads": ["exit_codes", "record_validity", "cost"],
                    "may_change": ["adapters", "parsing", "retries", "timeouts"]},
        "slop": {"addendum_path": "slop/PREREGISTRATION.md", "secondary_scores": "n/a", "run_id_from": "addendum_v1_sha256",
                 "annotator": {"model": "qwen/qwen3.8-27b:free", "fallback": "dots-studio/dots-3-note-preview:free", "via": "oask.sh", "queue": "retry_queue"}},
        "cost": {"estimate_paid_tokens": 3050000, "paid_vendors": ["anthropic", "openai"], "ceiling_paid_tokens": 5000000,
                 "ceiling_counts_reasoning": True, "canary_calls_exempt_from_confirm": True, "confirmed_by_operator": "2026-09-27",
                 "estimate_inputs": "pinned and frozen inputs only"},
    }


def make_md(root: Path, prereg: dict | None = None) -> str:
    """A PREREGISTRATION.md with the 14 headings in order, the notice block
    in section 12 (a 4-space-indented fence inside a list item, contents
    copied from the file), and two pinned hashes quoted in the prose."""
    notice = (root / "prompts" / "provider_notice.txt").read_text(encoding="utf-8")
    prereg = prereg or json.loads((root / "prereg.json").read_text(encoding="utf-8"))
    parts = ["# Test pre-registration\n"]
    for i, h in enumerate(HEADINGS, 1):
        parts.append(f"\n## {i}. {h}\n\n")
        if i == 2:
            parts.append(f"Corpus manifest: `{prereg['corpus']['corpus_manifest_sha256']}`.\n")
        elif i == 12:
            parts.append(f"Notice SHA-256: `{prereg['judges']['notice_sha256']}`.\n\n")
            parts.append("- The notice, verbatim:\n\n    ```text\n")
            parts.extend(f"    {ln}\n" if ln else "\n" for ln in notice.rstrip("\n").split("\n"))
            parts.append("    ```\n")
        else:
            parts.append("Text.\n")
    return "".join(parts)


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *GIT_ID, *args], capture_output=True, text=True, check=check)


def commit(root: Path, message: str, *paths: str) -> str:
    git(root, "add", "--", *(paths or (".",)))
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD").stdout.strip()


def write_prereg(root: Path, prereg: dict, md: str | None = None) -> None:
    (root / "prereg.json").write_bytes(canonical(prereg))
    (root / "PREREGISTRATION.md").write_text(md if md is not None else make_md(root, prereg), encoding="utf-8")


def make_root(tmp_path: Path, *, with_prereg: bool = True, commit_all: bool = True) -> Path:
    """A tmp git repo shaped like the controlled-benchmark directory:
    ``prompts/``, ``bench/stopwords.txt``, ``runs/.gitkeep``, and (by default)
    committed ``prereg.json`` and ``PREREGISTRATION.md``. It is nested one
    level down (``repo/controlled``) so path-prefix handling is exercised."""
    repo = tmp_path / "repo"
    root = repo / "controlled"
    (root / "bench").mkdir(parents=True)
    shutil.copytree(CB / "prompts", root / "prompts")
    shutil.copy2(CB / "bench" / "stopwords.txt", root / "bench" / "stopwords.txt")
    (root / "runs").mkdir()
    (root / "runs" / ".gitkeep").write_bytes(b"")
    git(repo, "init", "-q")
    commit(repo, "setup")
    if with_prereg:
        write_prereg(root, make_prereg(root))
        if commit_all:
            commit(repo, "pre-registration")
    return root


def write_manifest(root: Path, run_id: str, prereg_sha256: str, **extra) -> Path:
    d = root / "runs" / run_id
    d.mkdir(parents=True, exist_ok=True)
    p = d / "manifest.json"
    p.write_bytes(canonical({"run_id": run_id, "prereg_sha256": prereg_sha256, **extra}))
    return p


def mutate(prereg: dict, dotted: str, value) -> dict:
    """A deep copy of `prereg` with the dotted key set to `value`."""
    out = copy.deepcopy(prereg)
    node = out
    parts = dotted.split(".")
    for part in parts[:-1]:
        node = node[int(part)] if isinstance(node, list) else node[part]
    last = parts[-1]
    if isinstance(node, list):
        node[int(last)] = value
    else:
        node[last] = value
    return out


def delete(prereg: dict, dotted: str) -> dict:
    out = copy.deepcopy(prereg)
    node = out
    parts = dotted.split(".")
    for part in parts[:-1]:
        node = node[int(part)] if isinstance(node, list) else node[part]
    del node[parts[-1]]
    return out
