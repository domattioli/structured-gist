#!/usr/bin/env python3
"""
Controlled-benchmark runner (contract: DomI 005-controlled-benchmark
contracts/runner-cli.md).

Subcommands: ``prereg-hash``, ``verify-prereg``, ``build-items`` (no gate);
``estimate``, ``preflight``, ``generate``, ``judge``, ``annotate``, ``grade``,
``report`` and ``all`` run the pre-registration gate first (exit 3 on
refusal). The model-calling ones (``generate``, ``judge``, ``annotate``,
``all``) need ``--confirm <estimate_sha>`` equal to the sha that
``estimate`` recomputes and wrote to ``runs/<id>/estimate.json`` (exit 4
otherwise, or when the estimate is over the ceiling). The canaries
(``generate --canary``, ``judge --judge-canary``, and the same flags on
``preflight``) are exempt from --confirm and never write under runs/.
``annotate`` is not implemented (exit 2).

Paths resolve relative to this file. ``SG_BENCH_ROOT`` overrides the
controlled-benchmark root (tests point it at a temporary git repository).

Exit codes: 0 ok, 1 unexpected error, 2 usage, 3 pre-registration gate,
4 cost not confirmed, 5 isolation, 6 model policy, 75 quota.

Python 3.11+ stdlib only. No network.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import traceback
from pathlib import Path

CB = Path(__file__).resolve().parent
if str(CB) not in sys.path:
    sys.path.insert(0, str(CB))

from bench import items as items_mod  # noqa: E402
from bench import prereg  # noqa: E402
from bench import estimate as est  # noqa: E402
from bench import generate as gen_mod  # noqa: E402
from bench import judge as judge_mod  # noqa: E402
from bench import pacing, pipeline, records, score  # noqa: E402

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_GATE = 3
EXIT_CONFIRM = 4
EXIT_ISOLATION = 5
EXIT_MODEL_POLICY = 6
EXIT_QUOTA = 75

UNGATED = frozenset({"prereg-hash", "build-items"})
MODEL_CALLING = frozenset({"generate", "judge", "annotate", "all"})
DATASETS = ("qmsum", "qasper", "hotpotqa")
JUDGES = ("sol", "gemini", "openrouter")
_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def bench_root() -> Path:
    return Path(os.environ.get("SG_BENCH_ROOT") or CB)


def _err(msg: str) -> None:
    print(msg, file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run.py",
        description="Controlled benchmark runner. Every subcommand except prereg-hash and "
                    "build-items runs the pre-registration gate first (exit 3 on refusal).",
    )
    sub = p.add_subparsers(dest="cmd", required=True, metavar="SUBCOMMAND")

    def add(name: str, help_text: str, *, run_id: bool = True) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, help=help_text, description=help_text)
        if run_id:
            sp.add_argument("--run-id", help="run id (default: pr-<prereg_sha256[:12]>)")
        return sp

    def scope(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--dataset", choices=DATASETS)
        sp.add_argument("--case", action="append", metavar="ID")

    add("prereg-hash", "print prereg_sha256 for the working copy (no gate)", run_id=False)
    sp = add("verify-prereg", "SC-001: pre-registration commit precedes every run; manifests carry its hash",
             run_id=False)
    sp.add_argument("--run-id", action="append", help="run id to check (repeatable; default: run ids in git)")
    add("build-items", "write runs/<id>/items.jsonl from the 42 frozen cases (no gate)")
    scope(add("estimate", "per-backend token estimate and estimate_sha (no model calls)"))
    sp = add("preflight", "tool, gate, and isolation checks")
    g = sp.add_mutually_exclusive_group()
    g.add_argument("--canary", action="store_true", help="alias of generate --canary")
    g.add_argument("--judge-canary", action="store_true", help="alias of judge --judge-canary")
    sp.add_argument("--canary-out", metavar="PATH")
    sp = add("generate", "generate the five methods (model calls)")
    sp.add_argument("--confirm", metavar="ESTIMATE_SHA")
    sp.add_argument("--canary", action="store_true", help="one tiny generator isolation call (exempt from --confirm)")
    sp.add_argument("--canary-out", metavar="PATH")
    scope(sp)
    sp = add("judge", "judge samples (model calls)")
    sp.add_argument("--judge", choices=JUDGES)
    sp.add_argument("--confirm", metavar="ESTIMATE_SHA")
    sp.add_argument("--judge-canary", action="store_true", help="one tiny sol call (exempt from --confirm)")
    sp.add_argument("--canary-out", metavar="PATH")
    sp = add("annotate", "WildChat annotator entries (model calls)")
    sp.add_argument("--confirm", metavar="ESTIMATE_SHA")
    add("grade", "run every deterministic grader (no model calls)")
    add("report", "write results/<dataset>.json and REPORT.md (no model calls)")
    sp = add("all", "build-items, generate, judge sol, grade, report (model calls)")
    sp.add_argument("--confirm", metavar="ESTIMATE_SHA")
    scope(sp)
    return p


def _default_run_id(root: Path) -> str | None:
    try:
        return prereg.default_run_id(root)
    except (FileNotFoundError, ValueError):
        return None


def cmd_prereg_hash(root: Path, args) -> int:
    try:
        print(prereg.prereg_sha256(root))
    except FileNotFoundError as e:
        _err(f"pre-registration file missing: {e.filename}")
        return EXIT_ERROR
    return EXIT_OK


def cmd_verify_prereg(root: Path, args) -> int:
    res = prereg.verify(root, args.run_id)
    for r in res.superseded:
        print(f"superseded (ignored): runs/{r}")
    for r in res.checked:
        print(f"checked: runs/{r}")
    if res.problems:
        for p in res.problems:
            _err(p)
        _err("verify-prereg: FAILED")
        return EXIT_GATE
    print(f"verify-prereg: ok ({len(res.checked)} run(s) checked, {len(res.superseded)} superseded)")
    return EXIT_OK


def cmd_build_items(root: Path, args) -> int:
    run_id = args.run_id or _default_run_id(root)
    if run_id is None:
        _err("build-items: no pre-registration found to derive the default run id; pass --run-id")
        return EXIT_USAGE

    prereg_obj = None
    pj = root / prereg.PREREG_JSON
    if pj.is_file():
        try:
            prereg_obj = json.loads(pj.read_text(encoding="utf-8"))
        except ValueError as e:
            _err(f"build-items: {prereg.PREREG_JSON} is not valid JSON ({e})")
            return EXIT_GATE

    problems = list(items_mod.manifest_problems())
    built = items_mod.build_items()
    relations = items_mod.relation_totals(built)
    if prereg_obj is not None:
        problems += items_mod.check_prereg_manifests(prereg_obj)
        want = (prereg_obj.get("corpus") or {}).get("gold_relation_counts")
        if want != relations:
            problems.append(f"corpus.gold_relation_counts: pre-registered {want} != computed {relations}")
    if problems:
        for p in problems:
            _err(p)
        _err("build-items: frozen corpus does not match the pre-registration; nothing written")
        return EXIT_GATE

    out = items_mod.write_items(root / "runs" / run_id, built)
    counts: dict[str, int] = {}
    for it in built:
        counts[it["dataset"]] = counts.get(it["dataset"], 0) + 1
    print(f"run id: {run_id}")
    print(f"wrote: {out} ({len(built)} items)")
    print(f"cases: {json.dumps(counts)}")
    print(f"gold relation counts: {json.dumps(relations)}")
    print(f"zero-relation cases: {json.dumps(items_mod.zero_relation_case_counts(built))}")
    for k, v in items_mod.manifest_sha256s().items():
        print(f"{k}: {v}")
    if prereg_obj is None:
        print("note: no prereg.json yet, so the corpus hashes were not checked against it")
    return EXIT_OK


class Stop(Exception):
    def __init__(self, code: int, msg: str):
        super().__init__(msg)
        self.code, self.msg = code, msg


def _load_prereg(root: Path) -> dict:
    return json.loads((root / prereg.PREREG_JSON).read_text(encoding="utf-8"))


def _rd(root: Path, rid: str) -> Path:
    return root / "runs" / rid


def cmd_estimate(root: Path, rid: str, args, pre: dict) -> int:
    all_items = items_mod.build_items()
    case_items = pipeline.scope_items(pre, rid, all_items, args.dataset, args.case)
    if not case_items:
        _err("estimate: no cases in scope")
        return EXIT_USAGE
    try:
        body = est.compute(root, pre, case_items)
    except est.EstimateKeysMissing as e:
        _err(str(e))
        return EXIT_GATE
    out = _rd(root, rid) / "estimate.json"
    records.write_json(out, est.with_sha(body, rid))
    sha = est.sha_of(body)
    print(f"run id: {rid}")
    print(f"estimate_sha: {sha}")
    print(f"cases: {len(case_items)}")
    for b, v in body["per_backend"].items():
        print(f"{b}: {v['calls']} calls, {v['total_tokens']} tokens")
    print(f"total paid tokens: {body['total_paid_tokens']} (ceiling {body['ceiling_paid_tokens']})")
    if not body["within_ceiling"]:
        print("WARNING: estimate is over the ceiling; --confirm will be refused")
    print(f"wrote: {out}")
    return EXIT_OK


def check_confirm(root: Path, rid: str, args, pre: dict, all_items: list[dict], *, args_scope: bool):
    """Returns (case_items, body, sha) or raises Stop."""
    f = _rd(root, rid) / "estimate.json"
    if not f.is_file():
        raise Stop(EXIT_CONFIRM, f"{args.cmd}: no estimate for run {rid}; run `run.py estimate` first")
    fobj = records.read_json(f)
    if args_scope:
        case_items = pipeline.scope_items(pre, rid, all_items, getattr(args, "dataset", None),
                                          getattr(args, "case", None))
    else:
        case_items = pipeline.items_of_ids(all_items, (fobj.get("scope") or {}).get("cases", []))
    try:
        body = est.compute(root, pre, case_items)
    except est.EstimateKeysMissing as e:
        raise Stop(EXIT_GATE, str(e))
    sha = est.sha_of(body)
    if not (args.confirm == sha == fobj.get("estimate_sha")):
        raise Stop(EXIT_CONFIRM, f"{args.cmd}: --confirm {args.confirm!r} does not match the recomputed "
                                 f"estimate {sha} (or the file on disk); rerun `run.py estimate`")
    if not body["within_ceiling"]:
        raise Stop(EXIT_CONFIRM, f"{args.cmd}: estimate {body['total_paid_tokens']} tokens is over the "
                                 f"ceiling {body['ceiling_paid_tokens']}")
    return case_items, body, sha


def _pacer(root: Path, rid: str, pre: dict) -> pacing.Pacer:
    cost = pre.get("cost") or {}
    full = (not pipeline.is_dry(rid)) and (cost.get("window_budget") or {}).get("applies_to") == "full_run_only"
    d = _rd(root, rid)
    d.mkdir(parents=True, exist_ok=True)
    return pacing.Pacer(d, cost, full_run=full)


def _guard(fn):
    """Maps stage exceptions to exit codes."""
    try:
        return fn()
    except pacing.PacedStop as e:
        print(str(e))
        return EXIT_QUOTA
    except pipeline.QuotaStop as e:
        _err(str(e))
        return EXIT_QUOTA
    except pipeline.PolicyStop as e:
        _err(f"model policy violation: {e}")
        return EXIT_MODEL_POLICY
    except gen_mod.BackendUnavailable as e:
        _err(str(e))
        return EXIT_ERROR
    except NotImplementedError as e:
        _err(str(e))
        return EXIT_USAGE
    except Stop as e:
        _err(e.msg)
        return e.code


def stage_generate(root, rid, pre, case_items, body, sha, pacer) -> int:
    rd = _rd(root, rid)
    rd.mkdir(parents=True, exist_ok=True)
    pipeline.write_manifest(root, rid, pre, sha, body)
    if not (rd / "items.jsonl").is_file():
        items_mod.write_items(rd, items_mod.build_items())
    pipeline.update_manifest(root, rid, state="generating")
    g = pipeline.Generator(root, pre, rid, pacer)
    samples = g.run(case_items)
    pipeline.write_samples(root, rid, samples)
    failed = sum(1 for s in samples if s["status"] == "failed")
    flags: dict = {}
    for s in samples:
        for fl in s["length_flags"]:
            flags[fl] = flags.get(fl, 0) + 1
    pipeline.update_manifest(root, rid, counts={"samples": len(samples), "failed_generations": failed,
                                                "length_flags": flags})
    print(f"generated: {len(samples)} samples ({failed} failed) -> {rd / 'samples.jsonl'}")
    return EXIT_OK


def stage_judge(root, rid, pre, pacer) -> int:
    rd = _rd(root, rid)
    if not (rd / "samples.jsonl").is_file():
        raise Stop(EXIT_USAGE, "judge: no samples.jsonl; run generate first")
    items = pipeline.load_items(root, rid)
    by_id = {i["item_id"]: i for i in items}
    samples = records.read_jsonl(rd / "samples.jsonl")
    pipeline.update_manifest(root, rid, state="judging")
    rows = pipeline.judge_samples(root, pre, rid, samples, by_id, pacer)
    inc = sum(1 for r in rows if r["status"] == "incomplete")
    pipeline.update_manifest(root, rid, counts={"judged": len(rows), "incomplete_sol": inc})
    print(f"judged: {len(rows)} samples ({inc} incomplete) -> {rd / pipeline.LABELS_FILE}")
    return EXIT_OK


def _read_graders(rd: Path) -> dict:
    out: dict[str, list[dict]] = {}
    g = rd / "graders"
    if g.is_dir():
        for p in sorted(g.glob("*.jsonl")):
            out[p.stem] = records.read_jsonl(p)
    return out


def stage_grade(root, rid, pre) -> int:
    if pipeline.is_dry(rid):
        raise Stop(EXIT_USAGE, "grade: a dry run's scores are never inspected (prereg dry_run.scores_inspected)")
    rd = _rd(root, rid)
    if not (rd / "samples.jsonl").is_file() or not (rd / pipeline.LABELS_FILE).is_file():
        raise Stop(EXIT_USAGE, "grade: needs samples.jsonl and graders/judge_labels.sol.jsonl")
    by_id = {i["item_id"]: i for i in pipeline.load_items(root, rid)}
    samples = records.read_jsonl(rd / "samples.jsonl")
    labels = {r["sample_id"]: r for r in records.read_jsonl(rd / pipeline.LABELS_FILE)}
    graded = score.grade(pre, samples, by_id, labels)
    for name, rows in graded.items():
        records.write_jsonl(rd / "graders" / f"{name}.jsonl", rows)
    pipeline.update_manifest(root, rid, state="grading")
    print(f"graded: {sum(len(v) for v in graded.values())} rows in {len(graded)} graders")
    return EXIT_OK


def stage_report(root, rid, pre) -> int:
    if pipeline.is_dry(rid):
        raise Stop(EXIT_USAGE, "report: a dry run is never reported (prereg dry_run.reported)")
    rd = _rd(root, rid)
    graded = _read_graders(rd)
    if score.FACT_GRADER not in graded:
        raise Stop(EXIT_USAGE, "report: run grade first")
    by_id = {i["item_id"]: i for i in pipeline.load_items(root, rid)}
    samples = records.read_jsonl(rd / "samples.jsonl")
    res = score.build_results(pre, samples, by_id, graded, pipeline.read_calls(root, rid))
    for ds, r in res.items():
        records.write_json(rd / "results" / f"{ds}.json", r)
    (rd / "REPORT.md").write_text(score.render_report(rid, pre, res), encoding="utf-8")
    pipeline.update_manifest(root, rid, state="reported")
    print(f"report: {rd / 'REPORT.md'}")
    for ds, r in res.items():
        print(f"{ds}: scored {len(r['cases_scored'])}, incomplete {len(r['incomplete_cases'])}")
    return EXIT_OK


def cmd_canary(root: Path, args, which: str, pre: dict) -> int:
    out = getattr(args, "canary_out", None)
    if out:
        target = Path(out).resolve()
        runs = (root / "runs").resolve()
        if target == runs or runs in target.parents:
            _err("canary: --canary-out must not be under runs/")
            return EXIT_USAGE
    try:
        res = gen_mod.canary(pre) if which == "gen" else judge_mod.judge_canary(pre)
    except (gen_mod.CanaryFailed, judge_mod.CanaryFailed) as e:
        _err(str(e))
        return {"model_policy_violation": EXIT_MODEL_POLICY, "quota_exhausted": EXIT_QUOTA}.get(e.outcome, EXIT_ERROR)
    except gen_mod.BackendUnavailable as e:
        _err(str(e))
        return EXIT_ERROR
    text = json.dumps(res, indent=2, sort_keys=True)
    print(text)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text + "\n", encoding="utf-8")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else EXIT_USAGE
    run_id = getattr(args, "run_id", None)
    if isinstance(run_id, str) and not _RUN_ID.match(run_id):
        _err(f"invalid --run-id {run_id!r}")
        return EXIT_USAGE
    if isinstance(run_id, list) and not all(_RUN_ID.match(r) for r in run_id):
        _err(f"invalid --run-id in {run_id!r}")
        return EXIT_USAGE

    root = bench_root()
    try:
        if args.cmd == "prereg-hash":
            return cmd_prereg_hash(root, args)
        if args.cmd == "build-items":
            return cmd_build_items(root, args)
        if args.cmd == "verify-prereg":
            return cmd_verify_prereg(root, args)

        # Gate first (FR-002).
        rid = run_id or _default_run_id(root)
        problems = prereg.gate(root, rid)
        if problems:
            for p in problems:
                _err(p)
            _err(f"{args.cmd}: pre-registration gate refused")
            return EXIT_GATE

        pre = _load_prereg(root)
        cmd = args.cmd
        if cmd == "estimate":
            return cmd_estimate(root, rid, args, pre)
        if cmd in ("generate", "preflight") and getattr(args, "canary", False):
            return cmd_canary(root, args, "gen", pre)
        if cmd in ("judge", "preflight") and getattr(args, "judge_canary", False):
            return cmd_canary(root, args, "judge", pre)
        if cmd == "judge" and not args.judge:
            _err("judge: --judge is required (unless --judge-canary)")
            return EXIT_USAGE
        if cmd == "grade":
            return _guard(lambda: stage_grade(root, rid, pre))
        if cmd == "report":
            return _guard(lambda: stage_report(root, rid, pre))
        if cmd in MODEL_CALLING:
            if not args.confirm:
                _err(f"{cmd}: calls a model; pass --confirm <estimate_sha> from `run.py estimate`")
                return EXIT_CONFIRM
            all_items = items_mod.build_items()

            def go() -> int:
                case_items, body, sha = check_confirm(root, rid, args, pre, all_items,
                                                      args_scope=cmd in ("generate", "all"))
                if cmd == "annotate":
                    raise Stop(EXIT_USAGE, "annotate: not implemented yet")
                if cmd == "judge" and args.judge != "sol":
                    judge_mod.free_judge()
                pacer = _pacer(root, rid, pre)
                if cmd == "generate":
                    return stage_generate(root, rid, pre, case_items, body, sha, pacer)
                if cmd == "judge":
                    return stage_judge(root, rid, pre, pacer)
                rc = stage_generate(root, rid, pre, case_items, body, sha, pacer)
                rc = rc or stage_judge(root, rid, pre, pacer)
                if pipeline.is_dry(rid):
                    print("dry run: grade and report skipped")
                    return rc
                return rc or stage_grade(root, rid, pre) or stage_report(root, rid, pre)

            return _guard(go)

        _err(f"{cmd}: not implemented yet")
        return EXIT_USAGE
    except Exception:  # noqa: BLE001 -- exit 1 with a traceback, per the contract
        traceback.print_exc()
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
