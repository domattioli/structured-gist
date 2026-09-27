#!/usr/bin/env python3
"""
Fast pyramid scoring (Nenkova & Passonneau 2004), after DomI's pyramid_report.py.

Pipeline (wall time is dominated by the model calls, all one-turn, no tools):
  1. extract  - one call per source, in parallel: atomic facts + verbatim quotes
  2. merge    - one call: cluster fact ids into SCUs; weight/evidence filled in Python
  3. judge    - in parallel: one presence call + one claim-check call per candidate chunk
  4. metrics  - raw, max_k, pyramid_score, weighted_recall, top_recall (in Python)

Usage:
  pyramid_fast.py score --source B1=spec.md --source B2=readme.md,results.json \
      --source B3=transcript.md --candidate message.md --out outdir
  pyramid_fast.py transcript --session S.jsonl --match "<text in the message>" \
      --out message.md [--slice-from "<text>" --slice-out B3.md]
"""

import argparse
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

EFFORT = "low"
SYSTEM = "You are a careful annotator. Output only the JSON requested, no prose, no code fences."


def call_model(prompt, model, retries=1):
    cmd = ["claude", "-p", "--model", model, "--tools", "", "--setting-sources", "",
           "--strict-mcp-config", "--no-session-persistence", "--effort", EFFORT, "--system-prompt", SYSTEM]
    for attempt in range(retries + 1):
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd="/tmp")
        try:
            return parse_json(r.stdout)
        except ValueError:
            if attempt == retries:
                raise RuntimeError(f"unparseable model output:\n{r.stdout[:2000]}\n{r.stderr[:500]}")


def parse_json(text):
    starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
    if not starts:
        raise ValueError("no JSON")
    s = min(starts)
    e = max(text.rfind("}"), text.rfind("]"))
    return json.loads(text[s:e + 1])


def read_source(spec):
    name, _, paths = spec.partition("=")
    parts = [f"--- file: {Path(p).name} ---\n{Path(p).read_text()}" for p in paths.split(",")]
    return name, "\n\n".join(parts)


def extract(name, text, model, cap):
    prompt = f"""Extract the {cap} most decisive atomic facts from the source below
(results, numbers, decisions, corrections, blockers, asks; skip procedure and boilerplate).
One fact = one atomic claim (who/what/why, one number or one relation), not a sentence.
Keep numbers exactly as written. Include facts stated in raw data (JSON, logs) when they are decisive.
Return a JSON array: [{{"fact": "...", "quote": "short verbatim clause from the source"}}]

SOURCE {name}:
{text}"""
    facts = call_model(prompt, model)
    return [{"id": f"{name}-{i + 1}", **f} for i, f in enumerate(facts)]


def merge(facts_by_source, model):
    listing = "\n".join(f"{f['id']}: {f['fact']}" for fs in facts_by_source.values() for f in fs)
    prompt = f"""Below are atomic facts extracted independently from {len(facts_by_source)} sources
(id prefix = source). Cluster facts that state the same claim (paraphrases, same number) into
Summary Content Units. List ONLY clusters whose members come from two or more different sources;
facts you leave out become single-source SCUs automatically. A fact id appears in at most one cluster.
If two sources give different values for the same quantity, output
{{"label": "...", "members": [ids from both], "conflict": true}} and do not merge them further.
Return a JSON array: [{{"label": "one-line atomic claim", "members": ["B1-3", "B2-7"], "conflict": false}}]

FACTS:
{listing}"""
    clusters = call_model(prompt, model)
    by_id = {f["id"]: f for fs in facts_by_source.values() for f in fs}
    used = {m for c in clusters if not c.get("conflict") for m in c.get("members", [])}
    conflicts = [c for c in clusters if c.get("conflict")]
    clusters = [c for c in clusters if not c.get("conflict")]
    for c in conflicts:  # one SCU per side of a disagreement
        for src in sorted({m.split("-")[0] for m in c.get("members", [])}):
            side = [m for m in c["members"] if m.startswith(src + "-")]
            used.update(side)
            clusters.append({"label": by_id[side[0]]["fact"] if side[0] in by_id else c["label"],
                             "members": side, "conflict": True})
    clusters += [{"label": f["fact"], "members": [i]} for i, f in by_id.items() if i not in used]
    scus = []
    for i, c in enumerate(clusters):
        evidence = {}
        for m in c.get("members", []):
            f = by_id.get(m)
            if f:
                evidence.setdefault(m.split("-")[0], f.get("quote", f["fact"]))
        if evidence:
            scu = {"scu": f"S{len(scus) + 1}", "label": c["label"], "weight": len(evidence),
                   "evidence": evidence}
            if c.get("conflict"):
                scu["conflict"] = True
            scus.append(scu)
    return scus


def scu_listing(scus):
    return "\n".join(f"{s['scu']} (w{s['weight']}): {s['label']}" for s in scus)


def judge_presence(scus, candidate, model):
    prompt = f"""Mark which SCUs the candidate states. Present only when the candidate states the
claim, not merely a related word. Return JSON: {{"present": {{"S3": "candidate phrase"}}}}

SCUS:
{scu_listing(scus)}

CANDIDATE:
{candidate}"""
    return call_model(prompt, model).get("present", {})


def judge_claims(chunk, scus, sources_text, model):
    prompt = f"""Split the candidate excerpt into its own atomic claims (one number or relation each).
Label each claim:
- SUPPORTED: an SCU states it (cite ids)
- CONTRADICTED: an SCU or the sources give a conflicting value (cite ids, state both values)
- UNSUPPORTED: no SCU covers it (say whether the raw sources below back it anyway)
Be exact on numbers, ranges and trends; a trend claim needs evidence of the trend itself.
Return a JSON array: [{{"claim": "...", "label": "...", "scus": ["S1"], "note": "..."}}]

SCUS:
{scu_listing(scus)}

RAW SOURCES:
{sources_text}

CANDIDATE EXCERPT:
{chunk}"""
    return call_model(prompt, model)


def chunk_candidate(text, n):
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    size = max(1, -(-sum(len(p) for p in paras) // n))
    chunks, cur = [], ""
    for p in paras:
        if cur and len(cur) + len(p) > size:
            chunks.append(cur)
            cur = ""
        cur += p + "\n\n"
    if cur:
        chunks.append(cur)
    return chunks


def metrics(scus, present):
    weights = sorted((s["weight"] for s in scus), reverse=True)
    wmap = {s["scu"]: s["weight"] for s in scus}
    raw = sum(wmap.get(p, 0) for p in present)
    k = len(present)
    max_k = sum(weights[:k])
    top = max(weights) if weights else 0
    top_ids = {s["scu"] for s in scus if s["weight"] == top}
    hist = {w: weights.count(w) for w in sorted(set(weights))}
    return {"n_scus": len(scus), "weight_hist": hist, "raw": raw, "k": k, "max_k": max_k,
            "pyramid_score": round(raw / max_k, 3) if max_k else 0,
            "weighted_recall": round(raw / sum(weights), 3) if weights else 0,
            f"w{top}_recall": round(len(top_ids & set(present)) / len(top_ids), 3) if top_ids else None}


def cmd_score(a):
    global EFFORT
    EFFORT = a.effort
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sources = dict(read_source(s) for s in a.source)
    candidate = Path(a.candidate).read_text()
    t = {}

    t0 = time.time()
    with ThreadPoolExecutor(len(sources)) as ex:
        futs = {n: ex.submit(extract, n, txt, a.extract_model, a.facts_per_source) for n, txt in sources.items()}
        facts = {n: f.result() for n, f in futs.items()}
    t["extract"] = time.time() - t0
    (out / "facts.json").write_text(json.dumps(facts, indent=2))

    t0 = time.time()
    scus = merge(facts, a.merge_model)
    t["merge"] = time.time() - t0
    (out / "scus.json").write_text(json.dumps(
        {"id": a.id, "baselines": list(sources), "scus": scus}, indent=2))

    t0 = time.time()
    sources_text = "\n\n".join(f"=== SOURCE {n} ===\n{txt}" for n, txt in sources.items()) \
        if a.judge_with_sources else "(not provided)"
    chunks = chunk_candidate(candidate, a.claim_shards)
    with ThreadPoolExecutor(1 + len(chunks)) as ex:
        pres_f = ex.submit(judge_presence, scus, candidate, a.judge_model)
        claim_fs = [ex.submit(judge_claims, c, scus, sources_text, a.judge_model) for c in chunks]
        present = pres_f.result()
        claims = [c for f in claim_fs for c in f.result()]
    t["judge"] = time.time() - t0

    present_ids = [p for p in present if any(s["scu"] == p for s in scus)]
    for i, c in enumerate(claims):
        c["c"] = f"C{i + 1}"
    m = metrics(scus, present_ids)
    labels = {}
    for c in claims:
        labels[c["label"]] = labels.get(c["label"], 0) + 1
    score = {"id": a.id, "scored": {"candidate": {
        "present": present_ids, "absent": [s["scu"] for s in scus if s["scu"] not in present_ids],
        "evidence": present}}, "candidate_claims": claims, "metrics": m, "claim_labels": labels,
        "seconds": {k: round(v, 1) for k, v in t.items()}}
    (out / "score.json").write_text(json.dumps(score, indent=2))

    print(json.dumps({"metrics": m, "claim_labels": labels, "seconds": score["seconds"]}, indent=2))
    for c in claims:
        if c["label"] != "SUPPORTED":
            print(f"{c['c']} {c['label']}: {c['claim']} -- {c.get('note', '')}")


def transcript_rows(path):
    for line in open(path):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") in ("user", "assistant"):
            yield d


def render(d):
    c = d["message"].get("content")
    if isinstance(c, str):
        return [f"[{d['type']}] {c}"]
    out = []
    for b in c or []:
        t = b.get("type")
        if t == "text":
            out.append(f"[{d['type']} text] {b['text']}")
        elif t == "tool_use":
            out.append(f"[tool_use {b['name']}] {json.dumps(b.get('input'))[:600]}")
        elif t == "tool_result":
            r = b.get("content")
            r = r if isinstance(r, str) else " ".join(x.get("text", "") for x in r or [] if isinstance(x, dict))
            out.append(f"[tool_result] {r[:2500]}")
    return out


def cmd_transcript(a):
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    if a.slice_out:
        Path(a.slice_out).parent.mkdir(parents=True, exist_ok=True)
    rows = list(transcript_rows(a.session))
    hit = None
    for i, d in enumerate(rows):
        c = d["message"].get("content")
        if d["type"] == "assistant" and isinstance(c, list):
            for b in c:
                if b.get("type") == "text" and a.match in b["text"]:
                    hit = i
                    Path(a.out).write_text(b["text"])
    if hit is None:
        sys.exit("match not found in any assistant text")
    print(f"candidate: row {hit} of {len(rows)} at {rows[hit].get('timestamp')}")
    if a.slice_from:
        start = next(i for i, d in enumerate(rows) if a.slice_from in json.dumps(d["message"].get("content")))
        lines = [ln for d in rows[start:hit] for ln in render(d)]
        Path(a.slice_out).write_text("\n\n".join(lines))
        print(f"slice: rows {start}..{hit - 1} -> {a.slice_out}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("--source", action="append", required=True, help="NAME=path[,path...]")
    s.add_argument("--candidate", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--id", default="candidate")
    s.add_argument("--extract-model", default="sonnet")
    s.add_argument("--merge-model", default="sonnet")
    s.add_argument("--judge-model", default="sonnet")
    s.add_argument("--claim-shards", type=int, default=3)
    s.add_argument("--facts-per-source", type=int, default=60)
    s.add_argument("--effort", default="low")
    s.add_argument("--no-judge-sources", dest="judge_with_sources", action="store_false")
    s.set_defaults(func=cmd_score)
    t = sub.add_parser("transcript")
    t.add_argument("--session", required=True)
    t.add_argument("--match", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--slice-from")
    t.add_argument("--slice-out")
    t.set_defaults(func=cmd_transcript)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
