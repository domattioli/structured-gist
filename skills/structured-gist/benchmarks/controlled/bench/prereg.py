#!/usr/bin/env python3
"""
Pre-registration hash, gate, and SC-001 check (FR-001, FR-002, SC-001).

    prereg_sha256 = sha256(canonical_json_bytes(prereg.json)
                           + raw_bytes(PREREGISTRATION.md))

``canonical_json_bytes`` is the frozen corpus serializer (sorted keys,
indent 2, trailing newline), so the JSON file's own formatting does not change
the hash; the Markdown file is hashed byte for byte.

The gate (``gate``) refuses (the runner exits 3) when:
- either file is missing, was never committed, or has uncommitted (staged or
  unstaged) changes;
- a required key is missing or holds a placeholder (a string containing
  ``TODO``, the string ``...``, a string that is only ``<...>``, an empty
  string, or ``null`` outside the two pre-registered null slots);
- the 14 FR-001 headings are not present in order;
- a consistency check fails: the section-12 notice block differs from
  ``prompts/provider_notice.txt``; a pinned hash differs from its live file;
  the corpus counts or gold relation counts differ from what ``items.py``
  computes; ``generator.skill_version`` differs from ``SKILL.md``; or a
  64-hex hash quoted in PREREGISTRATION.md is not one of the pinned values;
- ``runs/<run_id>/manifest.json`` exists and records a different hash.

``verify`` adds SC-001: the pre-registration commit must be a strict
ancestor of the earliest commit touching ``runs/`` (``runs/.gitkeep`` and
superseded run dirs excluded), and every checked run's manifest must carry
the committed hash. A superseded run dir is one whose id has the default form
``pr-<12 hex>`` or ``dryrun-<12 hex>`` for an older pre-registration hash.
A run with WildChat items also needs the committed slop addendum hash
(FR-020).

Only read-only git commands are used (status, log, show, ls-tree, diff
--cached --name-only, merge-base, rev-parse). No network. No model calls.
"""
from __future__ import annotations

import functools
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bench import items as items_mod
from bench.records import canonical_json_bytes

CB = Path(__file__).resolve().parent.parent
SG = CB.parent.parent
SC = SG / "benchmarks" / "semantic-compression"
EV = SC / "external-validation"

PREREG_JSON = "prereg.json"
PREREG_MD = "PREREGISTRATION.md"
PREREG_FILES = (PREREG_JSON, PREREG_MD)

REQUIRED_HEADINGS = [
    (1, "Question"),
    (2, "Cases and datasets"),
    (3, "Methods"),
    (4, "Length rule and tolerance"),
    (5, "Main scores"),
    (6, "Win rule"),
    (7, "Main judge and effort"),
    (8, "Judge panel, subset rule, retry policy, agreement statistics"),
    (9, "Secondary scores"),
    (10, "Uncertainty method"),
    (11, "Report shape"),
    (12, "Outside-provider notice"),
    (13, "Known limits"),
    (14, "Amendment and deviation rule"),
]

_DS3 = {"qmsum": None, "qasper": None, "hotpotqa": None}

# Required keys: a dict maps key -> sub-spec (None for a leaf). A list spec
# ``[keys]`` means "a non-empty list whose entries each have these keys".
REQUIRED: dict = {
    "version": None,
    "question": None,
    "master_seed": None,
    "corpus": {
        "datasets": dict(_DS3),
        "corpus_manifest_sha256": None,
        "derived_manifest_sha256": None,
        "gold_relation_counts": dict(_DS3),
        "relation_check_threshold": None,
    },
    "methods": None,
    "generator": {
        "model": None, "effort": None, "backend": None,
        "skill_md_sha256": None, "render_modes_md_sha256": None, "skill_version": None,
        "prompt_sha256": {k: None for k in ("shared_user", "skill_instruction", "plain_system",
                                            "prose_instruction", "bullets_instruction")},
        "max_regenerations": None,
        "failure_retries": None,
    },
    "length": {
        "tolerance": None, "word_counter": None, "strip_list_labels": None,
        "strip_html_comments": None, "flags": None, "n_fallback": None,
    },
    "textrank": {"damping": None, "tol": None, "max_iter": None, "stopwords_sha256": None},
    "scores": {"main": None, "combine_py_sha256": None},
    "win_rule": {k: None for k in ("test", "alpha", "exact_max_n", "monte_carlo_draws", "holm_families",
                                   "unadjusted", "tie_tolerance", "verdict_labels", "controls")},
    "bootstrap": {k: None for k in ("resamples", "type", "level", "seed_mean", "seed_diff", "seed_permutation")},
    "judges": {
        "main": {k: None for k in ("id", "model", "effort", "max_attempts", "check_resolved_model")},
        "panel": ["id", "model", "coverage"],
        "subset_rule": {"per_dataset": dict(_DS3), "order": None},
        "judge_prompt_sha256": None,
        "notice_sha256": None,
        "call_timeout_seconds": None,
        "free_judge_id_change": None,
        "retry_queue": {k: None for k in ("base_minutes", "cap_hours", "jitter", "attempt_limit", "tick_seconds",
                                          "retries_paid_judges", "paid_ceiling_check", "creates_entries")},
    },
    "agreement": {k: None for k in ("scale", "kappa", "alpha", "raw_percent", "threshold")},
    "secondary": {k: None for k in ("qmsum", "qasper", "hotpotqa", "normalization")},
    "report": {k: None for k in ("pooled", "early_signal", "first_row_control", "freeze_days_after_main_run")},
    "testing_criteria": ["name", "type", "pass_threshold"],
    "dry_run": {k: None for k in ("cases", "run_id", "reported", "scores_inspected", "reads", "may_change")},
    "slop": {
        "addendum_path": None, "secondary_scores": None, "run_id_from": None,
        "annotator": {k: None for k in ("model", "fallback", "via", "queue")},
    },
    "cost": {k: None for k in ("estimate_paid_tokens", "paid_vendors", "ceiling_paid_tokens", "ceiling_counts_reasoning",
                               "canary_calls_exempt_from_confirm", "confirmed_by_operator", "estimate_inputs")},
}

# Paths where null is the pre-registered value (no threshold is applied).
NULL_ALLOWED = (re.compile(r"^agreement\.threshold$"), re.compile(r"^testing_criteria\[\d+\]\.pass_threshold$"))

_HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
_SUPERSEDABLE = re.compile(r"^(?:pr|dryrun)-([0-9a-f]{12})$")


def pinned_sources(root: Path) -> dict[str, Path]:
    """Every pinned hash key in prereg.json and the live file it must match."""
    root = Path(root)
    out = {f"generator.prompt_sha256.{k}": root / "prompts" / f"{k}.md"
           for k in ("shared_user", "skill_instruction", "plain_system", "prose_instruction", "bullets_instruction")}
    out.update({
        "judges.judge_prompt_sha256": root / "prompts" / "judge.md",
        "judges.notice_sha256": root / "prompts" / "provider_notice.txt",
        "generator.skill_md_sha256": SG / "SKILL.md",
        "generator.render_modes_md_sha256": SG / "reference" / "render-modes.md",
        "scores.combine_py_sha256": SC / "scoring" / "combine.py",
        "textrank.stopwords_sha256": root / "bench" / "stopwords.txt",
        "corpus.corpus_manifest_sha256": EV / "MANIFEST.json",
        "corpus.derived_manifest_sha256": EV / "DERIVED_MANIFEST.json",
    })
    return out


def pinned_hash_keys() -> list[str]:
    return list(pinned_sources(CB))


# ---------------------------------------------------------------------------
# hashing
# ---------------------------------------------------------------------------

def compute_sha256(prereg_obj: Any, md_bytes: bytes) -> str:
    return hashlib.sha256(canonical_json_bytes(prereg_obj) + md_bytes).hexdigest()


def _sha_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prereg_sha256(root: Path) -> str:
    """The hash of the working-copy files. Raises FileNotFoundError when one
    is missing."""
    root = Path(root)
    obj = json.loads((root / PREREG_JSON).read_text(encoding="utf-8"))
    return compute_sha256(obj, (root / PREREG_MD).read_bytes())


def committed_prereg_sha256(root: Path, rev: str = "HEAD") -> str | None:
    """The hash of the two files as committed at `rev`, or None."""
    j = _git_show(root, f"{rev}:./{PREREG_JSON}")
    m = _git_show(root, f"{rev}:./{PREREG_MD}")
    if j is None or m is None:
        return None
    try:
        obj = json.loads(j.decode("utf-8"))
    except ValueError:
        return None
    return compute_sha256(obj, m)


def default_run_id(root: Path) -> str:
    return "pr-" + prereg_sha256(root)[:12]


# ---------------------------------------------------------------------------
# git (read-only)
# ---------------------------------------------------------------------------

def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def _git_show(root: Path, spec: str) -> bytes | None:
    res = subprocess.run(["git", "-C", str(root), "show", spec], capture_output=True)
    return res.stdout if res.returncode == 0 else None


def _in_git(root: Path) -> bool:
    return _git(root, "rev-parse", "--is-inside-work-tree").stdout.strip() == "true"


def last_commit(root: Path, *paths: str) -> str | None:
    """``git log -1 --format=%H -- <paths>``: the latest commit touching any
    of `paths`, or None."""
    out = _git(root, "log", "-1", "--format=%H", "--", *paths).stdout.strip()
    return out or None


def prereg_commit(root: Path) -> str | None:
    return last_commit(root, *PREREG_FILES)


def _is_dirty(root: Path, rel: str) -> bool:
    return bool(_git(root, "status", "--porcelain", "--untracked-files=all", "--", rel).stdout.strip())


def git_state_problems(root: Path) -> list[str]:
    root = Path(root)
    problems: list[str] = []
    if not _in_git(root):
        return [f"{root}: not inside a git work tree; the pre-registration must be committed"]
    for name in PREREG_FILES:
        if not (root / name).is_file():
            problems.append(f"{name}: missing")
            continue
        if last_commit(root, name) is None:
            problems.append(f"{name}: never committed")
        elif _is_dirty(root, name):
            problems.append(f"{name}: uncommitted changes (commit a new pre-registration version)")
    return problems


# ---------------------------------------------------------------------------
# keys and placeholders
# ---------------------------------------------------------------------------

def _required_problems(obj: Any, spec: Any, where: str, out: list[str]) -> None:
    if spec is None:
        return
    if isinstance(spec, list):
        if not isinstance(obj, list) or not obj:
            out.append(f"required key {where} must be a non-empty list")
            return
        for i, entry in enumerate(obj):
            if not isinstance(entry, dict):
                out.append(f"required key {where}[{i}] must be an object")
                continue
            for k in spec:
                if k not in entry:
                    out.append(f"missing required key {where}[{i}].{k}")
        return
    if not isinstance(obj, dict):
        out.append(f"required key {where} must be an object")
        return
    for k, sub in spec.items():
        path = f"{where}.{k}" if where else k
        if k not in obj:
            out.append(f"missing required key {path}")
        else:
            _required_problems(obj[k], sub, path, out)


def required_key_problems(obj: Any) -> list[str]:
    out: list[str] = []
    _required_problems(obj, REQUIRED, "", out)
    return out


def _is_placeholder_str(s: str) -> bool:
    t = s.strip()
    return t == "" or "TODO" in s or t == "..." or re.fullmatch(r"<[^<>]*>", t) is not None


def _walk(obj: Any, where: str = ""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{where}.{k}" if where else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{where}[{i}]")
    else:
        yield where, obj


def placeholder_problems(obj: Any) -> list[str]:
    out = []
    for path, v in _walk(obj):
        if v is None and not any(rx.match(path) for rx in NULL_ALLOWED):
            out.append(f"{path}: placeholder null where a value is required")
        elif isinstance(v, str) and _is_placeholder_str(v):
            out.append(f"{path}: placeholder value {v!r}")
    return out


def _get(obj: Any, dotted: str) -> Any:
    node = obj
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


# ---------------------------------------------------------------------------
# PREREGISTRATION.md structure
# ---------------------------------------------------------------------------

def heading_problems(md: str) -> list[str]:
    found = [ln[3:].strip() for ln in md.split("\n") if ln.startswith("## ")]
    want = [f"{n}. {t}" for n, t in REQUIRED_HEADINGS]
    if found == want:
        return []
    for i, w in enumerate(want):
        if i >= len(found):
            return [f"PREREGISTRATION.md: heading '## {w}' missing (found {len(found)} of 14 '## ' headings)"]
        if found[i] != w:
            return [f"PREREGISTRATION.md: heading {i + 1} is '## {found[i]}', expected '## {w}'"]
    return [f"PREREGISTRATION.md: extra '## ' heading '## {found[len(want)]}' after the 14 required ones"]


def extract_notice(md: str) -> str:
    """The section-12 notice: the contents of the first ```text fence after
    the '## 12.' heading, fence lines removed, the fence indent (4 spaces in
    PREREGISTRATION.md) removed from every line, plus one trailing newline.
    Raises ValueError when there is no such block."""
    lines = md.split("\n")
    try:
        start = next(i for i, ln in enumerate(lines) if ln.startswith("## 12."))
    except StopIteration:
        raise ValueError("no '## 12.' section")
    i = start + 1
    while i < len(lines) and not lines[i].startswith("## "):
        m = re.match(r"^( *)```text\s*$", lines[i])
        if m:
            indent = m.group(1)
            body: list[str] = []
            i += 1
            while i < len(lines) and not re.match(rf"^{indent}```\s*$", lines[i]):
                ln = lines[i]
                if ln.strip() == "":
                    body.append("")
                elif ln.startswith(indent):
                    body.append(ln[len(indent):])
                else:
                    raise ValueError(f"notice line not indented by the fence indent: {ln!r}")
                i += 1
            if i >= len(lines):
                raise ValueError("unterminated notice fence")
            return "\n".join(body) + "\n"
        i += 1
    raise ValueError("no ```text block in section 12")


def skill_version(skill_md: Path = SG / "SKILL.md") -> str | None:
    m = re.search(r'^version:\s*"?([^"\n]+?)"?\s*$', Path(skill_md).read_text(encoding="utf-8"), re.MULTILINE)
    return m.group(1) if m else None


@functools.lru_cache(maxsize=1)
def _live_corpus() -> tuple[dict, dict, tuple]:
    built = items_mod.build_items()
    counts: dict[str, int] = {}
    for it in built:
        counts[it["dataset"]] = counts.get(it["dataset"], 0) + 1
    return counts, items_mod.relation_totals(built), tuple(items_mod.manifest_problems())


def consistency_problems(root: Path, obj: dict, md: str) -> list[str]:
    root = Path(root)
    problems: list[str] = []

    notice_file = root / "prompts" / "provider_notice.txt"
    try:
        block = extract_notice(md)
        if not notice_file.is_file():
            problems.append("prompts/provider_notice.txt: missing")
        elif block.encode("utf-8") != notice_file.read_bytes():
            problems.append("PREREGISTRATION.md section 12 notice block differs from prompts/provider_notice.txt")
    except ValueError as e:
        problems.append(f"PREREGISTRATION.md section 12 notice: {e}")

    for key, path in pinned_sources(root).items():
        want = _get(obj, key)
        if want is None:
            continue  # reported by required_key_problems / placeholder_problems
        if not path.is_file():
            problems.append(f"{key}: pinned file {path} is missing")
        elif _sha_file(path) != want:
            problems.append(f"{key}: pinned {str(want)[:12]}... but {path.name} is {_sha_file(path)[:12]}...")

    counts, relations, manifest_issues = _live_corpus()
    problems.extend(f"corpus integrity: {p}" for p in manifest_issues)
    if _get(obj, "corpus.datasets") != counts:
        problems.append(f"corpus.datasets: pre-registered {_get(obj, 'corpus.datasets')} != items {counts}")
    if _get(obj, "corpus.gold_relation_counts") != relations:
        problems.append(f"corpus.gold_relation_counts: pre-registered {_get(obj, 'corpus.gold_relation_counts')} "
                        f"!= items {relations}")

    live_version = skill_version()
    if _get(obj, "generator.skill_version") != live_version:
        problems.append(f"generator.skill_version: pre-registered {_get(obj, 'generator.skill_version')!r} "
                        f"!= SKILL.md {live_version!r}")
    live_skill_sha = _sha_file(SG / "SKILL.md")
    if _get(obj, "generator.skill_md_sha256") != live_skill_sha:
        problems.append(f"generator.skill_md_sha256: pre-registered {str(_get(obj, 'generator.skill_md_sha256'))[:12]}... "
                        f"!= SKILL.md {live_skill_sha[:12]}...")

    pinned_values = {v for _, v in _walk(obj) if isinstance(v, str) and _HEX64.fullmatch(v)}
    for h in sorted(set(_HEX64.findall(md)) - pinned_values):
        problems.append(f"PREREGISTRATION.md quotes hash {h[:12]}... that is not a pinned value in prereg.json")
    return problems


# ---------------------------------------------------------------------------
# gate
# ---------------------------------------------------------------------------

def manifest_problem(root: Path, run_id: str, expected_sha: str) -> str | None:
    p = Path(root) / "runs" / run_id / "manifest.json"
    if not p.is_file():
        return None
    try:
        got = json.loads(p.read_text(encoding="utf-8")).get("prereg_sha256")
    except (ValueError, AttributeError):
        return f"run {run_id}: manifest.json is not valid JSON"
    if got != expected_sha:
        return f"run {run_id}: manifest.json records prereg_sha256 {str(got)[:12]}..., pre-registration is {expected_sha[:12]}..."
    return None


def gate(root: Path, run_id: str | None = None) -> list[str]:
    """Every reason the pre-registration gate refuses; empty means pass."""
    root = Path(root)
    problems = git_state_problems(root)
    if any(p.endswith(": missing") for p in problems) or not all((root / f).is_file() for f in PREREG_FILES):
        return problems
    try:
        obj = json.loads((root / PREREG_JSON).read_text(encoding="utf-8"))
    except ValueError as e:
        return problems + [f"{PREREG_JSON}: not valid JSON ({e})"]
    md = (root / PREREG_MD).read_text(encoding="utf-8")
    problems += required_key_problems(obj)
    problems += placeholder_problems(obj)
    problems += heading_problems(md)
    problems += consistency_problems(root, obj, md) if isinstance(obj, dict) else []
    if run_id:
        mp = manifest_problem(root, run_id, compute_sha256(obj, (root / PREREG_MD).read_bytes()))
        if mp:
            problems.append(mp)
    return problems


# ---------------------------------------------------------------------------
# verify-prereg (SC-001)
# ---------------------------------------------------------------------------

@dataclass
class VerifyResult:
    problems: list[str] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)
    superseded: list[str] = field(default_factory=list)


def _run_ids_in_git(root: Path) -> set[str]:
    committed = _git(root, "ls-tree", "-r", "--name-only", "HEAD", "--", "runs/").stdout.split("\n")
    staged = _git(root, "diff", "--cached", "--name-only", "--relative", "--", "runs/").stdout.split("\n")
    ids = set()
    for rel in committed + staged:
        parts = rel.strip().split("/")
        if len(parts) >= 3 and parts[0] == "runs":
            ids.add(parts[1])
    return ids


def _read_run_file(root: Path, run_id: str, name: str) -> bytes | None:
    rel = f"runs/{run_id}/{name}"
    data = _git_show(root, f":./{rel}")
    if data is None and (Path(root) / rel).is_file():
        data = (Path(root) / rel).read_bytes()
    return data


def _has_wildchat(root: Path, run_id: str) -> bool:
    if run_id.startswith("slop-"):
        return True
    data = _read_run_file(root, run_id, "items.jsonl")
    if not data:
        return False
    for line in data.decode("utf-8").splitlines():
        try:
            if json.loads(line).get("item", {}).get("dataset") == "wildchat":
                return True
        except (ValueError, AttributeError):
            continue
    return False


def verify(root: Path, run_ids: list[str] | None = None) -> VerifyResult:
    root = Path(root)
    res = VerifyResult(problems=gate(root))
    current = committed_prereg_sha256(root)
    commit = prereg_commit(root)
    if current is None or commit is None:
        if not any("never committed" in p or "missing" in p for p in res.problems):
            res.problems.append("pre-registration is not committed at HEAD")
        return res

    in_git = _run_ids_in_git(root)
    superseded = sorted(r for r in in_git
                        if (m := _SUPERSEDABLE.match(r)) and m.group(1) != current[:12])
    if run_ids:
        res.checked = list(run_ids)
        res.superseded = [r for r in superseded if r not in run_ids]
    else:
        res.checked = sorted(in_git - set(superseded))
        res.superseded = superseded

    excludes = [":(exclude)runs/.gitkeep"] + [f":(exclude)runs/{r}" for r in res.superseded]
    first = _git(root, "log", "--reverse", "--format=%H", "--", "runs/", *excludes).stdout.split()
    if first:
        earliest = first[0]
        is_anc = _git(root, "merge-base", "--is-ancestor", commit, earliest).returncode == 0
        if earliest == commit or not is_anc:
            res.problems.append(
                f"pre-registration commit {commit[:12]} is not a strict ancestor of the earliest runs/ "
                f"commit {earliest[:12]} (SC-001)")

    slop_path = None
    committed_json = _git_show(root, f"HEAD:./{PREREG_JSON}")
    if committed_json is not None:
        try:
            slop_path = json.loads(committed_json.decode("utf-8")).get("slop", {}).get("addendum_path")
        except (ValueError, AttributeError):
            slop_path = None
    slop_path = slop_path or "slop/PREREGISTRATION.md"

    for rid in res.checked:
        raw = _read_run_file(root, rid, "manifest.json")
        if raw is None:
            res.problems.append(f"run {rid}: manifest.json missing, so the committed hash is not recorded")
            continue
        try:
            manifest = json.loads(raw.decode("utf-8"))
        except ValueError:
            res.problems.append(f"run {rid}: manifest.json is not valid JSON")
            continue
        if manifest.get("prereg_sha256") != current:
            res.problems.append(f"run {rid}: manifest.json prereg_sha256 {str(manifest.get('prereg_sha256'))[:12]}... "
                                f"is not the committed hash {current[:12]}...")
        if _has_wildchat(root, rid):
            blob = _git_show(root, f"HEAD:./{slop_path}")
            if blob is None:
                res.problems.append(f"run {rid}: WildChat items but the slop addendum {slop_path} is not committed")
            elif _is_dirty(root, slop_path):
                res.problems.append(f"run {rid}: slop addendum {slop_path} has uncommitted changes")
            elif manifest.get("slop_addendum_sha256") != hashlib.sha256(blob).hexdigest():
                res.problems.append(f"run {rid}: manifest slop_addendum_sha256 does not match the committed "
                                    f"slop addendum {slop_path}")
    return res
