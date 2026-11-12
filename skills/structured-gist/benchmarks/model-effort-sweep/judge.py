#!/usr/bin/env python3
"""
Judging step of the model-effort sweep.

For every run with a standard.md and every judge in config.json:

Pass 1 (source-blind, model-blind)
    judge_prompt(gold, rendering) asks for fact/relation/question verdicts
    with evidence quotes and a list of outline claims not covered by gold.
    The judge never sees source.md and never learns which model wrote the
    outline: the prompt does not name it and the call runs in an empty
    temporary directory.

Pass 2 (source access, same judge)
    support_prompt(source, claims) checks each flagged claim against
    source.md and merges `source_supported` into the matching hallucination
    entry. Pass 2 is the only step that sees the source (see
    ../semantic-compression/README.md "Hallucination / unsupported-claim
    correction").

Output: judged/<judge>/<case>/<generator>-<effort>.json, in the judged
schema used by ../semantic-compression (facts, relations, questions,
hallucinations) plus a `_meta` block. A reply that is not valid JSON is
retried once; a second failure writes <cell>.error.json and no verdict.
If pass 2 fails twice, the pass-1 verdict is kept, its hallucinations stay
without `source_supported` (counted as unverified, never as unsupported),
and the error file records why.

Resume: a judged file whose `_meta.pass2` is "done" or "not_needed" is
skipped. A file stuck after pass 1 reruns pass 2 only.

Usage:
    python3 judge.py --dry-run
    python3 judge.py [--only-judge J] [--only-model M] [--only-effort E] [--only-case C] [--limit N]
"""
import argparse
import json
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import backends
import prompts
from generate import (add_filter_args, cell_name, check_filters, load_cases, load_config,
                      load_json, read, run_dir, sha256_text, utc_now, write_json)

FACT_STATUSES = {"retained", "partial", "omitted", "mutated"}
REL_STATUSES = {"retained", "partial", "lost"}
Q_VERDICTS = {"correct", "partial", "wrong", "unanswerable"}


def judged_path(root: Path, judge_name: str, case_id: str, cell: str) -> Path:
    return Path(root) / "judged" / judge_name / case_id / f"{cell}.json"


def validate_verdict(v, gold=None) -> list:
    """Shape check, plus (when gold is given) every gold id must have a
    verdict, so a skipped item is never silently scored as omitted.
    Returns a list of problems (empty when valid)."""
    problems = []
    if not isinstance(v, dict):
        return ["top level is not an object"]
    for key, field, allowed in (("facts", "status", FACT_STATUSES),
                                ("relations", "status", REL_STATUSES),
                                ("questions", "verdict", Q_VERDICTS)):
        block = v.get(key)
        if not isinstance(block, dict):
            problems.append(f"{key} is not an object")
            continue
        for item_id, item in block.items():
            if not isinstance(item, dict) or item.get(field) not in allowed:
                problems.append(f"{key}.{item_id}.{field} not in {sorted(allowed)}")
        if gold is not None:
            missing = [x["id"] for x in gold.get(key, []) if x["id"] not in block]
            if missing:
                problems.append(f"{key} missing ids {missing}")
    h = v.get("hallucinations")
    if not isinstance(h, list) or not all(isinstance(x, dict) and isinstance(x.get("claim"), str) for x in h):
        problems.append("hallucinations is not a list of {claim, note}")
    return problems


def validate_support(v, n_claims: int) -> list:
    if not isinstance(v, list):
        return ["top level is not a list"]
    if len(v) != n_claims:
        return [f"expected {n_claims} entries, got {len(v)}"]
    problems = []
    for i, x in enumerate(v):
        if not isinstance(x, dict) or not isinstance(x.get("source_supported"), bool):
            problems.append(f"entry {i} lacks a boolean source_supported")
    return problems


def ask_json(call_fn, judge: dict, effort: str, prompt: str, cfg: dict, validate) -> tuple:
    """Call the judge, parse JSON, retry once on invalid output.
    Returns (parsed or None, attempts list)."""
    attempts = []
    for attempt in (1, 2):
        try:
            with tempfile.TemporaryDirectory(prefix="sg-sweep-judge-") as cwd:
                res = call_fn(judge["backend"], judge["model"], effort, prompt, cwd,
                              codex_home=cfg["codex_home"], timeout_s=cfg["timeout_s"])
        except Exception as e:
            res = {"text": "", "exit_code": -1, "stderr_tail": f"{type(e).__name__}: {e}"}
        record = {k: res.get(k) for k in ("exit_code", "input_tokens", "cache_creation_input_tokens",
                                          "cache_read_input_tokens", "output_tokens",
                                          "total_tokens", "cost_usd", "duration_s")}
        if res.get("exit_code") != 0:
            record["error"] = f"exit code {res.get('exit_code')}"
            record["stderr_tail"] = res.get("stderr_tail")
            attempts.append(record)
            if isinstance(res.get("exit_code"), int) and res["exit_code"] == -1:
                break  # refused before any process ran; retrying cannot help
            continue
        try:
            parsed = prompts.extract_json(res.get("text") or "")
        except ValueError as e:
            record["error"] = str(e)
            record["reply_tail"] = (res.get("text") or "")[-1000:]
            attempts.append(record)
            continue
        problems = validate(parsed)
        if problems:
            record["error"] = "; ".join(problems[:10])
            record["reply_tail"] = (res.get("text") or "")[-1000:]
            attempts.append(record)
            continue
        attempts.append(record)
        return parsed, attempts
    return None, attempts


def merge_support(halluc: list, support: list) -> list:
    """Attach source_supported/source_quote to each hallucination entry, by
    position (the support prompt numbers the claims in the same order)."""
    out = []
    for h, s in zip(halluc, support):
        h = dict(h)
        h["source_supported"] = s["source_supported"]
        h["source_quote"] = s.get("quote", "")
        out.append(h)
    return out


def needs_work(p: Path) -> str:
    """'pass1', 'pass2', or '' (done)."""
    if not p.exists():
        return "pass1"
    try:
        data = load_json(p)
    except (json.JSONDecodeError, OSError):
        return "pass1"
    return "" if data.get("_meta", {}).get("pass2") in ("done", "not_needed") else "pass2"


def judge_cell(item: dict, cfg: dict, root: Path, call_fn) -> dict:
    judge, case, cell = item["judge"], item["case"], item["cell"]
    out_path = judged_path(root, judge["name"], case["id"], cell)
    err_path = out_path.with_name(f"{cell}.error.json")
    effort = cfg["judge_effort"]
    rendering = read(run_dir(root, case["id"], *item["gen_effort"]) / "standard.md")
    gold = load_json(case["dir"] / "gold.json")
    source = read(case["dir"] / "source.md")
    errors = {}

    if item["stage"] == "pass1":
        jp = prompts.judge_prompt(gold, rendering)
        verdict, attempts = ask_json(call_fn, judge, effort, jp, cfg,
                                     lambda v: validate_verdict(v, gold))
        if verdict is None:
            write_json(err_path, {"pass": 1, "judge": judge["name"], "model": judge["model"],
                                  "case": case["id"], "cell": cell, "attempts": attempts,
                                  "utc": utc_now()})
            return {"item": item, "status": "pass1_failed"}
        verdict = {k: verdict[k] for k in ("facts", "relations", "questions", "hallucinations")}
        verdict["_meta"] = {
            "judge": judge["name"], "model": judge["model"], "backend": judge["backend"],
            "effort": effort, "case": case["id"], "cell": cell,
            "rendering_sha256": sha256_text(rendering),
            "judge_prompt_sha256": sha256_text(jp),
            "pass1_attempts": attempts, "pass1_utc": utc_now(), "pass2": "pending",
        }
        write_json(out_path, verdict)
    else:
        verdict = load_json(out_path)

    halluc = verdict.get("hallucinations", [])
    if not halluc:
        verdict["_meta"]["pass2"] = "not_needed"
    else:
        claims = [h["claim"] for h in halluc]
        sp = prompts.support_prompt(source, claims)
        support, attempts = ask_json(call_fn, judge, effort, sp, cfg,
                                     lambda v: validate_support(v, len(claims)))
        verdict["_meta"]["pass2_attempts"] = attempts
        verdict["_meta"]["support_prompt_sha256"] = sha256_text(sp)
        if support is None:
            verdict["_meta"]["pass2"] = "failed"
            errors = {"pass": 2, "judge": judge["name"], "model": judge["model"],
                      "case": case["id"], "cell": cell, "attempts": attempts, "utc": utc_now()}
        else:
            verdict["hallucinations"] = merge_support(halluc, support)
            verdict["_meta"]["pass2"] = "done"
        verdict["_meta"]["pass2_utc"] = utc_now()
    write_json(out_path, verdict)
    if errors:
        write_json(err_path, errors)
        return {"item": item, "status": "pass2_failed"}
    if err_path.exists():
        err_path.unlink()
    return {"item": item, "status": "ok"}


def plan(cfg: dict, cases: list, root: Path, args) -> list:
    items = []
    for case in cases:
        if args.only_case and case["id"] not in args.only_case:
            continue
        for gen in cfg["generators"]:
            if args.only_model and gen["name"] not in args.only_model:
                continue
            for effort in cfg["efforts"]:
                if args.only_effort and effort not in args.only_effort:
                    continue
                d = run_dir(root, case["id"], gen["name"], effort)
                if not (d / "standard.md").exists():
                    continue
                meta = d / "meta.json"
                if not meta.exists() or load_json(meta).get("exit_code") != 0:
                    continue
                cell = cell_name(gen["name"], effort)
                for judge in cfg["judges"]:
                    if args.only_judge and judge["name"] not in args.only_judge:
                        continue
                    stage = needs_work(judged_path(root, judge["name"], case["id"], cell))
                    items.append({"judge": judge, "case": case, "cell": cell,
                                  "gen_effort": (gen["name"], effort), "stage": stage})
    return items


def main(argv=None, call_fn=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    add_filter_args(ap)
    ap.add_argument("--only-judge", action="append", help="judge name (repeatable)")
    args = ap.parse_args(argv)
    call_fn = call_fn or backends.call

    cfg = load_config(args.config)
    cases = load_cases(cfg)
    check_filters(args, cfg, cases)
    for j in args.only_judge or []:
        if j not in {x["name"] for x in cfg["judges"]}:
            raise SystemExit(f"--only-judge {j!r} is not in config")
    root = Path(args.root)
    items = plan(cfg, cases, root, args)
    pending = [i for i in items if i["stage"]]
    selected = pending[: args.limit] if args.limit is not None else pending

    if args.dry_run:
        for i in items:
            argv_preview = backends.build_argv(i["judge"]["backend"], i["judge"]["model"],
                                               cfg["judge_effort"], "<tmpdir>")
            state = i["stage"] or "done"
            print(f"[{state}] {i['judge']['name']} {i['case']['id']} {i['cell']} :: {json.dumps(argv_preview)}")
        if any(i["judge"]["backend"] == "codex" for i in selected) and not backends.codex_auth_present(cfg["codex_home"]):
            print(f"warning: {backends.expand_codex_home(cfg['codex_home'])}/auth.json is missing; codex judge calls would be refused")
        print(f"judge items: {len(items)} (runs with standard.md x judges)")
        print(f"done: {len(items) - len(pending)}, pending: {len(pending)}, selected for this run: {len(selected)}")
        print("dry run: no model calls made")
        return 0

    if any(i["judge"]["backend"] == "codex" for i in selected) and not backends.codex_auth_present(cfg["codex_home"]):
        print(f"error: {backends.expand_codex_home(cfg['codex_home'])}/auth.json does not exist; "
              "log in to the benchmark Codex home or pass --only-judge for claude judges.", file=sys.stderr)
        return 2

    failures = 0
    with ThreadPoolExecutor(max_workers=max(1, int(cfg["concurrency"]))) as pool:
        futures = [pool.submit(judge_cell, i, cfg, root, call_fn) for i in selected]
        for f in futures:
            r = f.result()
            i = r["item"]
            failures += 0 if r["status"] == "ok" else 1
            print(f"{r['status']:<12} {i['judge']['name']} {i['case']['id']} {i['cell']}")
    print(f"judged {len(selected) - failures}/{len(selected)} items; {failures} with errors")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
