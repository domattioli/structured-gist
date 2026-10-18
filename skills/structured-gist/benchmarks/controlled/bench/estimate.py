#!/usr/bin/env python3
"""
Token estimate (T026, FR-017): a pure function of prereg.json, the files it
pins, and the frozen corpus. No timestamps, no model calls, no generated text.

Per case, N = alnum-token-v2 word count of
``EV/evaluation/<dataset>/renderings/<case>/standard.md``.

- anthropic: 3 calls (skill, plain_prose, plain_bullets).
  input = ceil(chars(system + user) / 4) + overhead.anthropic;
  output = ceil(output_tokens_per_word * N * (1 + thinking_ratio)).
- openai: 5 calls (one per method sample).
  input = ceil(chars(notice + judge.md + checklist) / 4) + ceil(output_tokens_per_word * N)
          + overhead.openai; output as above.

Free judges are unpaid and not estimated.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from bench import generate, items as items_mod, judge, prereg as prereg_mod, records, words

REQUIRED_PARAMS = ("chars_per_token", "output_tokens_per_word", "thinking_ratio", "safety_margin",
                   "per_call_overhead_tokens", "overhead_measured")
BACKENDS = ("anthropic", "openai")
ANTHROPIC_CALLS = 3
OPENAI_CALLS = 5


class EstimateKeysMissing(Exception):
    pass


def check_keys(prereg_obj: dict) -> None:
    cost = prereg_obj.get("cost") or {}
    params = cost.get("estimate_params")
    missing = []
    if not isinstance(params, dict):
        missing.append("cost.estimate_params")
    else:
        missing += [f"cost.estimate_params.{k}" for k in REQUIRED_PARAMS if k not in params]
        ov = params.get("per_call_overhead_tokens")
        if isinstance(ov, dict):
            missing += [f"cost.estimate_params.per_call_overhead_tokens.{b}" for b in BACKENDS if b not in ov]
    wb = cost.get("window_budget")
    if not isinstance(wb, dict):
        missing.append("cost.window_budget")
    else:
        missing += [f"cost.window_budget.{k}" for k in ("tokens_per_backend", "window_hours", "applies_to") if k not in wb]
    if "ceiling_paid_tokens" not in cost:
        missing.append("cost.ceiling_paid_tokens")
    if missing:
        raise EstimateKeysMissing("estimate: prereg.json is missing " + ", ".join(missing))


def projected_n(item: dict) -> int:
    p = items_mod.EV / "evaluation" / item["dataset"] / "renderings" / item["case_id"] / "standard.md"
    return words.count_words(p.read_text(encoding="utf-8"))


def _ceil(x: float) -> int:
    return math.ceil(round(x, 9))


def compute(root: Path, prereg_obj: dict, case_items: list[dict]) -> dict:
    """The estimate body (no estimate_sha, no run_id)."""
    check_keys(prereg_obj)
    P = prereg_obj["cost"]["estimate_params"]
    cpt, opw, tr, margin = P["chars_per_token"], P["output_tokens_per_word"], P["thinking_ratio"], P["safety_margin"]
    ov = P["per_call_overhead_tokens"]
    root = Path(root)
    notice = judge.read_notice(root)
    judge_md = (root / "prompts" / "judge.md").read_text(encoding="utf-8")
    sys_skill = generate.system_prompt("skill", root)
    sys_plain = generate.system_prompt("plain_prose", root)

    per_case = []
    tot = {b: {"calls": 0, "input_tokens": 0, "output_tokens": 0} for b in BACKENDS}
    for it in sorted(case_items, key=lambda i: i["item_id"]):
        n = projected_n(it)
        out_tok = _ceil(opw * n * (1 + tr))
        a_in = 0
        for arm, sysp in (("skill", sys_skill), ("plain_prose", sys_plain), ("plain_bullets", sys_plain)):
            um = generate.user_message(arm, it, root, None if arm == "skill" else n)
            a_in += _ceil((len(sysp) + len(um)) / cpt) + ov["anthropic"]
        a_out = ANTHROPIC_CALLS * out_tok
        checklist = json.dumps(items_mod.judge_view(it), indent=2, sort_keys=True, ensure_ascii=False)
        o_in = OPENAI_CALLS * (_ceil((len(notice) + len(judge_md) + len(checklist)) / cpt)
                               + _ceil(opw * n) + ov["openai"])
        o_out = OPENAI_CALLS * out_tok
        tot["anthropic"]["calls"] += ANTHROPIC_CALLS
        tot["anthropic"]["input_tokens"] += a_in
        tot["anthropic"]["output_tokens"] += a_out
        tot["openai"]["calls"] += OPENAI_CALLS
        tot["openai"]["input_tokens"] += o_in
        tot["openai"]["output_tokens"] += o_out
        per_case.append({"item_id": it["item_id"], "n": n, "anthropic_tokens": a_in + a_out,
                         "openai_tokens": o_in + o_out})
    per_backend = {}
    for b in BACKENDS:
        t = tot[b]
        total = _ceil((t["input_tokens"] + t["output_tokens"]) * (1 + margin))
        per_backend[b] = {"calls": t["calls"], "input_tokens": t["input_tokens"],
                          "output_tokens": t["output_tokens"], "total_tokens": total}
    total_paid = sum(per_backend[b]["total_tokens"] for b in BACKENDS)
    ceiling = prereg_obj["cost"]["ceiling_paid_tokens"]
    return {
        "prereg_sha256": prereg_mod.prereg_sha256(root),
        "scope": {"cases": sorted(i["item_id"] for i in case_items)},
        "params": json.loads(json.dumps(P)),
        "per_backend": per_backend,
        "total_paid_tokens": total_paid,
        "ceiling_paid_tokens": ceiling,
        "within_ceiling": total_paid <= ceiling,
        "per_case": per_case,
    }


def sha_of(body: dict) -> str:
    return hashlib.sha256(records.canonical_json_bytes(body)).hexdigest()


def with_sha(body: dict, run_id: str) -> dict:
    return {**body, "estimate_sha": sha_of(body), "run_id": run_id}


def body_of(file_obj: dict) -> dict:
    return {k: v for k, v in file_obj.items() if k not in ("estimate_sha", "run_id")}
