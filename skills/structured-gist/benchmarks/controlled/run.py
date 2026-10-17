#!/usr/bin/env python3
"""
Controlled-benchmark runner (contract: DomI 005-controlled-benchmark
contracts/runner-cli.md).

Working subcommands in this version: ``prereg-hash``, ``verify-prereg``,
``build-items``. Every other subcommand runs the pre-registration gate and
then exits 2 with "not implemented" until its user story lands; the
model-calling ones (``generate``, ``judge``, ``annotate``, ``all``) first
require ``--confirm <estimate_sha>`` and exit 4 without a matching one.
Because ``estimate`` is not implemented yet, no confirmation can match, so
this version never reaches a model.

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
    g.add_argument("--canary", action="store_true", help="one tiny generator isolation call (exempt from --confirm)")
    g.add_argument("--judge-canary", action="store_true", help="one tiny sol call (exempt from --confirm)")
    sp = add("generate", "generate the five methods (model calls)")
    sp.add_argument("--confirm", metavar="ESTIMATE_SHA")
    scope(sp)
    sp = add("judge", "judge samples (model calls)")
    sp.add_argument("--judge", required=True, choices=JUDGES)
    sp.add_argument("--confirm", metavar="ESTIMATE_SHA")
    sp = add("annotate", "WildChat annotator entries (model calls)")
    sp.add_argument("--confirm", metavar="ESTIMATE_SHA")
    add("grade", "run every deterministic grader (no model calls)")
    add("report", "write results/<dataset>.json and REPORT.md (no model calls)")
    sp = add("all", "build-items, generate, judge (all), grade, report (model calls)")
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

        if args.cmd in MODEL_CALLING:
            if not args.confirm:
                _err(f"{args.cmd}: calls a model; pass --confirm <estimate_sha> from `run.py estimate`")
                return EXIT_CONFIRM
            _err(f"{args.cmd}: --confirm {args.confirm!r} does not match any estimate "
                 "(estimate is not implemented yet)")
            return EXIT_CONFIRM

        _err(f"{args.cmd}: not implemented yet (lands with its user story)")
        return EXIT_USAGE
    except Exception:  # noqa: BLE001 -- exit 1 with a traceback, per the contract
        traceback.print_exc()
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
