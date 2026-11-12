#!/usr/bin/env python3
"""
Generation step of the model-effort sweep.

For every (case, generator, effort) cell, render the case's source.md as a
structured-gist outline (standard granularity, block mode) and write

    runs/<case>/<generator>-<effort>/standard.md   extracted outline
    runs/<case>/<generator>-<effort>/raw.txt       the unparsed reply
    runs/<case>/<generator>-<effort>/meta.json     model, backend, effort,
        condition, tokens, cost, duration, exit code, SHA-256 of SKILL.md
        and of the prompt, UTC timestamp

A cell whose meta.json records exit_code 0 and whose standard.md exists is
skipped (resume). A failed call is recorded in meta.json with its exit code
and stderr tail; no outline is written for it, and nothing is fabricated.

Usage:
    python3 generate.py --dry-run
    python3 generate.py [--only-model M] [--only-effort E] [--only-case C] [--limit N]

Also holds the config/case helpers that judge.py and score.py import.
"""
import argparse
import datetime
import hashlib
import json
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import backends
import prompts

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"
TEST_CLASSES = ["regression", "pressure-tests"]


# ---------------------------------------------------------------- helpers

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(p: Path, data) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(p)


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_config(path: Path = CONFIG_PATH) -> dict:
    cfg = load_json(path)
    base = path.resolve().parent
    cfg["suite_dir"] = str((base / cfg["suite_dir"]).resolve())
    cfg["skill_path"] = str((base / cfg["skill_path"]).resolve())
    return cfg


def load_cases(cfg: dict) -> list:
    """Case ids from suite.json, each resolved to its case directory."""
    suite_dir = Path(cfg["suite_dir"])
    suite = load_json(suite_dir / "suite.json")
    out = []
    for c in suite["cases"]:
        cid = c["id"]
        for tc in TEST_CLASSES:
            d = suite_dir / tc / cid
            if (d / "source.md").exists():
                out.append({"id": cid, "dir": d})
                break
        else:
            raise SystemExit(f"case {cid!r} has no source.md under {suite_dir}")
    return out


def cell_name(model_name: str, effort: str) -> str:
    return f"{model_name}-{effort}"


def add_filter_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--dry-run", action="store_true", help="print the plan; make no model calls")
    ap.add_argument("--only-model", action="append", help="generator name (repeatable)")
    ap.add_argument("--only-effort", action="append", help="effort level (repeatable)")
    ap.add_argument("--only-case", action="append", help="case id (repeatable)")
    ap.add_argument("--limit", type=int, default=None, help="run at most N pending items")
    ap.add_argument("--config", type=Path, default=CONFIG_PATH)
    ap.add_argument("--root", type=Path, default=HERE,
                    help="directory holding runs/, judged/, results/ (default: this folder)")


def check_filters(args, cfg: dict, cases: list) -> None:
    known = {
        "--only-model": {g["name"] for g in cfg["generators"]},
        "--only-effort": set(cfg["efforts"]),
        "--only-case": {c["id"] for c in cases},
    }
    for flag, values in (("--only-model", args.only_model), ("--only-effort", args.only_effort),
                         ("--only-case", args.only_case)):
        for v in values or []:
            if v not in known[flag]:
                raise SystemExit(f"{flag} {v!r} is not in config/suite: {sorted(known[flag])}")


def matrix(cfg: dict, cases: list, args) -> list:
    """All cells in case x generator x effort order, after --only-* filters."""
    cells = []
    for case in cases:
        if args.only_case and case["id"] not in args.only_case:
            continue
        for gen in cfg["generators"]:
            if args.only_model and gen["name"] not in args.only_model:
                continue
            for effort in cfg["efforts"]:
                if args.only_effort and effort not in args.only_effort:
                    continue
                cells.append({"case": case, "gen": gen, "effort": effort})
    return cells


# ---------------------------------------------------------------- generation

def run_dir(root: Path, case_id: str, gen_name: str, effort: str) -> Path:
    return Path(root) / "runs" / case_id / cell_name(gen_name, effort)


def is_done(d: Path) -> bool:
    meta = d / "meta.json"
    if not meta.exists() or not (d / "standard.md").exists():
        return False
    try:
        return load_json(meta).get("exit_code") == 0
    except (json.JSONDecodeError, OSError):
        return False


def run_cell(cell: dict, cfg: dict, root: Path, skill_text: str, call_fn) -> dict:
    case, gen, effort = cell["case"], cell["gen"], cell["effort"]
    d = run_dir(root, case["id"], gen["name"], effort)
    d.mkdir(parents=True, exist_ok=True)
    source_text = read(case["dir"] / "source.md")
    prompt = prompts.generation_prompt(skill_text, source_text)
    meta = {
        "case": case["id"],
        "generator": gen["name"],
        "model": gen["model"],
        "backend": gen["backend"],
        "effort": effort,
        "granularity": cfg["granularity"],
        "mode": cfg["mode"],
        "condition": cfg["condition"],
        "skill_sha256": sha256_text(skill_text),
        "prompt_sha256": sha256_text(prompt),
        "started_utc": utc_now(),
    }
    try:
        with tempfile.TemporaryDirectory(prefix="sg-sweep-gen-") as cwd:
            res = call_fn(gen["backend"], gen["model"], effort, prompt, cwd,
                          codex_home=cfg["codex_home"], timeout_s=cfg["timeout_s"])
    except Exception as e:  # recorded, never papered over
        res = {"text": "", "input_tokens": None, "output_tokens": None, "cost_usd": None,
               "duration_s": None, "exit_code": -1, "stderr_tail": f"{type(e).__name__}: {e}"}

    text = res.get("text") or ""
    (d / "raw.txt").write_text(res.get("raw_stdout", text) or "", encoding="utf-8")
    outline_path = d / "standard.md"
    if res.get("exit_code") == 0 and text.strip():
        outline_path.write_text(prompts.extract_outline(text), encoding="utf-8")
    elif outline_path.exists():
        outline_path.unlink()
    if res.get("exit_code") == 0 and not text.strip():
        meta["note"] = "exit code 0 but empty reply; no outline written, cell will rerun"
    for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
              "output_tokens", "total_tokens", "cost_usd", "duration_s",
              "exit_code", "stderr_tail"):
        meta[k] = res.get(k)
    meta["finished_utc"] = utc_now()
    write_json(d / "meta.json", meta)
    return meta


def main(argv=None, call_fn=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    add_filter_args(ap)
    args = ap.parse_args(argv)
    call_fn = call_fn or backends.call

    cfg = load_config(args.config)
    cases = load_cases(cfg)
    check_filters(args, cfg, cases)
    root = Path(args.root)
    cells = matrix(cfg, cases, args)
    pending = [c for c in cells if not is_done(run_dir(root, c["case"]["id"], c["gen"]["name"], c["effort"]))]
    selected = pending[: args.limit] if args.limit is not None else pending

    if args.dry_run:
        for c in cells:
            d = run_dir(root, c["case"]["id"], c["gen"]["name"], c["effort"])
            state = "done" if c not in pending else ("run" if c in selected else "pending")
            argv_preview = backends.build_argv(c["gen"]["backend"], c["gen"]["model"], c["effort"], "<tmpdir>")
            print(f"[{state}] {c['case']['id']} {cell_name(c['gen']['name'], c['effort'])} "
                  f"-> {d.relative_to(root)} :: {json.dumps(argv_preview)}")
        n_cases = len({c["case"]["id"] for c in cells})
        n_gens = len({c["gen"]["name"] for c in cells})
        n_eff = len({c["effort"] for c in cells})
        if any(c["gen"]["backend"] == "codex" for c in selected) and not backends.codex_auth_present(cfg["codex_home"]):
            print(f"warning: {backends.expand_codex_home(cfg['codex_home'])}/auth.json is missing; codex cells would be refused")
        print(f"matrix: {n_cases} cases x {n_gens} generators x {n_eff} efforts = {len(cells)} cells")
        print(f"done: {len(cells) - len(pending)}, pending: {len(pending)}, selected for this run: {len(selected)}")
        print("dry run: no model calls made")
        return 0

    if any(c["gen"]["backend"] == "codex" for c in selected) and not backends.codex_auth_present(cfg["codex_home"]):
        print(f"error: {backends.expand_codex_home(cfg['codex_home'])}/auth.json does not exist; "
              "log in to the benchmark Codex home or pass --only-model for claude generators.", file=sys.stderr)
        return 2

    skill_text = read(Path(cfg["skill_path"]))
    failures = 0
    with ThreadPoolExecutor(max_workers=max(1, int(cfg["concurrency"]))) as pool:
        futures = [pool.submit(run_cell, c, cfg, root, skill_text, call_fn) for c in selected]
        for f in futures:
            meta = f.result()
            ok = meta["exit_code"] == 0 and "note" not in meta
            failures += 0 if ok else 1
            print(f"{'ok  ' if ok else 'FAIL'} {meta['case']} {cell_name(meta['generator'], meta['effort'])} "
                  f"exit={meta['exit_code']} out_tokens={meta.get('output_tokens')}")
    print(f"generated {len(selected) - failures}/{len(selected)} cells; {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
