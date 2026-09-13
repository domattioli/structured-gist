#!/usr/bin/env python3
"""
Materializes the frozen case files (source.md, external_gold.json,
provenance.json) for every case a select_*.py script picked, plus the
top-level MANIFEST.json.

Reads: <dataset>/selection.json (committed, produced by select_*.py) and,
for qmsum/qasper, the local raw cache populated by fetch_sources.py (their
selection.json does not carry the full source text, only resolved
evidence locations -- hotpotqa's does, since its context is small).

Writes: <dataset>/cases/<case-id>/{source.md,external_gold.json,provenance.json}
and the top-level MANIFEST.json.

No structured-gist output is read, generated, or referenced. No model
calls. Case IDs are assigned by enumerating selection.json's
`selected_candidates` in the order select_*.py already wrote them (itself
a deterministic sort, documented in each select_*.py) -- case numbering is
positional, not chosen.

Run: python3 build_cases.py --dataset all --cache-dir <path> --base-dir <path to external-validation/>
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from corpus_lib import BUILD_SCRIPT_VERSION, canonical_json_bytes, read_json, sha256_hex, write_json  # noqa: E402

INTENT = {
    "qmsum": {
        "reader": "a colleague who missed this meeting and needs the answer to one specific point from it",
        "task": "answer the query below using only what survives compression of the meeting",
    },
    "qasper": {
        "reader": "someone evaluating this paper who has not read it in full",
        "task": "answer the question below using only what survives compression of the paper",
    },
    "hotpotqa": {
        "reader": "someone who needs the answer to a multi-hop question without reading all ten source paragraphs",
        "task": "answer the question below by composing evidence from at least two paragraphs, using only what survives compression",
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# QMSum
# ---------------------------------------------------------------------------

def build_qmsum_case(candidate: dict, cache_dir: Path, raw_manifest: dict, retrieval_date: str) -> dict:
    domain = candidate["domain"]
    test_path = cache_dir / "qmsum" / "jsonl" / domain / "test.jsonl"
    lines = [l for l in test_path.read_text("utf-8").splitlines() if l.strip()]
    meeting = json.loads(lines[candidate["test_line_index"]])
    transcripts = meeting["meeting_transcripts"]

    source_lines = [
        f"# QMSum meeting transcript — {domain} — {candidate['native_meeting_id']}",
        "",
        f"<!-- source: Yale-LILY/QMSum, commit {raw_manifest['commit_sha']}, MIT license -->",
        "",
    ]
    for turn in transcripts:
        source_lines.append(f"**{turn['speaker']}:** {turn['content']}")
        source_lines.append("")
    source_md = "\n".join(source_lines).rstrip() + "\n"

    native_evidence = []
    for i, (start, end) in enumerate(candidate["resolved_spans"]):
        native_evidence.append(
            {
                "span_index": i,
                "start_idx": start,
                "end_idx": end,
                "turns": transcripts[start : end + 1],
            }
        )

    external_gold = {
        "case_id": None,  # filled by caller
        "dataset": "qmsum",
        "intent": INTENT["qmsum"],
        "question_or_query": candidate["query"],
        "reference_answer": candidate["answer"],
        "native_evidence": native_evidence,
        "native_metadata": {
            "domain": domain,
            "native_meeting_id": candidate["native_meeting_id"],
            "cardinality": candidate["cardinality"],
            "n_spans": candidate["n_spans"],
            "n_turns": candidate["n_turns"],
            "source_word_count": candidate["source_word_count"],
        },
        "provenance_ref": "provenance.json",
    }

    source_payload = canonical_json_bytes({"meeting_transcripts": transcripts})
    provenance = {
        "dataset": "qmsum",
        "upstream_case_id": candidate["candidate_id"],
        "upstream_document_id": candidate["native_meeting_id"],
        "upstream_question_id": f"sq{candidate['query_index']}",
        "upstream_split": "test",
        "upstream_domain": domain,
        "upstream_source_repository": "https://github.com/Yale-LILY/QMSum",
        "upstream_revision": raw_manifest["commit_sha"],
        "license": raw_manifest["license"],
        "license_source": raw_manifest["license_source"],
        "retrieval_date": retrieval_date,
        "source_sha256": sha256_hex(source_payload),
        "transformed_case_sha256": None,  # filled by caller (needs final source.md bytes)
        "transformation_script_version": BUILD_SCRIPT_VERSION,
        "deviations": [
            "QMSum's published jsonl splits carry no per-meeting ID field; "
            "native_meeting_id was recovered by exact content match against "
            f"data/{domain}/all/{candidate['native_meeting_id']}.json in the same pinned commit.",
        ],
    }
    return {"source_md": source_md, "external_gold": external_gold, "provenance": provenance}


# ---------------------------------------------------------------------------
# Qasper
# ---------------------------------------------------------------------------

def build_qasper_case(candidate: dict, cache_dir: Path, raw_manifest: dict, retrieval_date: str) -> dict:
    data = json.loads((cache_dir / "qasper" / "qasper-dev-v0.3.json").read_text("utf-8"))
    paper = data[candidate["arxiv_id"]]

    source_lines = [f"# {paper.get('title', '')}", "", "## Abstract", "", paper.get("abstract", ""), ""]
    for section in paper.get("full_text", []):
        source_lines.append(f"## {section.get('section_name') or '(untitled section)'}")
        source_lines.append("")
        for para in section.get("paragraphs", []):
            source_lines.append(para)
            source_lines.append("")
    source_md = "\n".join(source_lines).rstrip() + "\n"

    native_evidence = []
    for loc in candidate["resolved_locations"]:
        text = paper["full_text"][loc["section_idx"]]["paragraphs"][loc["para_idx"]]
        native_evidence.append({**loc, "text": text})

    external_gold = {
        "case_id": None,
        "dataset": "qasper",
        "intent": INTENT["qasper"],
        "question_or_query": candidate["question"],
        "reference_answer": candidate["answer_text"],
        "native_evidence": native_evidence,
        "native_metadata": {
            "arxiv_id": candidate["arxiv_id"],
            "paper_title": candidate["paper_title"],
            "answer_type": candidate["answer_type"],
            "n_annotators": candidate["n_annotators"],
            "nlp_background": candidate["nlp_background"],
            "topic_background": candidate["topic_background"],
            "cardinality": candidate["cardinality"],
            "n_evidence_locations": candidate["n_evidence_locations"],
            "evidence_distance": candidate["evidence_distance"],
            "distance_bucket": candidate["distance_bucket"],
            "float_evidence_captions": candidate["float_evidence"],
            "evidence_raw": candidate["evidence_raw"],
            "source_word_count": candidate["source_word_count"],
        },
        "provenance_ref": "provenance.json",
    }

    source_payload = canonical_json_bytes(
        {"title": paper.get("title", ""), "abstract": paper.get("abstract", ""), "full_text": paper.get("full_text", [])}
    )
    provenance = {
        "dataset": "qasper",
        "upstream_case_id": candidate["candidate_id"],
        "upstream_document_id": candidate["arxiv_id"],
        "upstream_question_id": candidate["question_id"],
        "upstream_split": "dev",
        "upstream_source_repository": "https://allenai.org/data/qasper (dataset); https://huggingface.co/datasets/allenai/qasper (card)",
        "upstream_revision": raw_manifest["version"],
        "license": raw_manifest["license"],
        "license_source": raw_manifest["license_source"],
        "retrieval_date": retrieval_date,
        "source_sha256": sha256_hex(source_payload),
        "transformed_case_sha256": None,
        "transformation_script_version": BUILD_SCRIPT_VERSION,
        "deviations": [
            "Float (figure/table) evidence entries are preserved as captions in "
            "native_metadata.float_evidence_captions but are not resolved to a "
            "text location, since this corpus does not retain paper images.",
        ],
    }
    return {"source_md": source_md, "external_gold": external_gold, "provenance": provenance}


# ---------------------------------------------------------------------------
# HotpotQA
# ---------------------------------------------------------------------------

def build_hotpotqa_case(candidate: dict, raw_manifest: dict, retrieval_date: str) -> dict:
    source_lines = [f"# HotpotQA distractor context — {candidate['hotpot_id']}", ""]
    for title, sentences in zip(candidate["context_titles"], candidate["context_sentences"]):
        source_lines.append(f"## {title}")
        source_lines.append("")
        source_lines.append("".join(sentences).strip())
        source_lines.append("")
    source_md = "\n".join(source_lines).rstrip() + "\n"

    external_gold = {
        "case_id": None,
        "dataset": "hotpotqa",
        "intent": INTENT["hotpotqa"],
        "question_or_query": candidate["question"],
        "reference_answer": candidate["answer"],
        "native_evidence": candidate["supporting_facts"],
        "native_metadata": {
            "hotpot_id": candidate["hotpot_id"],
            "type": candidate["type"],
            "level": candidate["level"],
            "n_supporting_facts": candidate["n_supporting_facts"],
            "n_distinct_titles": candidate["n_distinct_titles"],
            "distinct_titles": candidate["distinct_titles"],
            "n_context_paragraphs": candidate["n_context_paragraphs"],
            "source_word_count": candidate["source_word_count"],
            "pressure_only": True,
        },
        "provenance_ref": "provenance.json",
    }

    source_payload = canonical_json_bytes(
        {"context_titles": candidate["context_titles"], "context_sentences": candidate["context_sentences"]}
    )
    provenance = {
        "dataset": "hotpotqa",
        "upstream_case_id": candidate["candidate_id"],
        "upstream_document_id": candidate["hotpot_id"],
        "upstream_question_id": candidate["hotpot_id"],
        "upstream_split": "validation (distractor)",
        "upstream_source_repository": "https://hotpotqa.github.io/ (canonical); https://huggingface.co/datasets/hotpotqa/hotpot_qa (mirror used for retrieval)",
        "upstream_revision": raw_manifest["fallback_source_repo_sha"],
        "license": raw_manifest["license"],
        "license_source": raw_manifest["license_source"],
        "retrieval_date": retrieval_date,
        "source_sha256": sha256_hex(source_payload),
        "transformed_case_sha256": None,
        "transformation_script_version": BUILD_SCRIPT_VERSION,
        "deviations": [raw_manifest["deviation_note"]],
    }
    return {"source_md": source_md, "external_gold": external_gold, "provenance": provenance}


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

BUILDERS = {
    "qmsum": lambda c, cache, rm, rd: build_qmsum_case(c, cache, rm, rd),
    "qasper": lambda c, cache, rm, rd: build_qasper_case(c, cache, rm, rd),
    "hotpotqa": lambda c, cache, rm, rd: build_hotpotqa_case(c, rm, rd),
}

ID_WIDTH = {"qmsum": 2, "qasper": 2, "hotpotqa": 2}


def build_dataset(dataset: str, base_dir: Path, cache_dir: Path) -> list[dict]:
    selection = read_json(base_dir / dataset / "selection.json")
    raw_manifest = read_json(cache_dir / dataset / "raw_manifest.json")
    retrieval_date = raw_manifest["retrieved_at"]

    manifest_entries = []
    width = ID_WIDTH[dataset]
    for i, candidate in enumerate(selection["selected_candidates"], start=1):
        case_id = f"{dataset}-{i:0{width}d}"
        built = BUILDERS[dataset](candidate, cache_dir, raw_manifest, retrieval_date)

        built["external_gold"]["case_id"] = case_id
        source_bytes = built["source_md"].encode("utf-8")
        gold_bytes = canonical_json_bytes(built["external_gold"])
        built["provenance"]["transformed_case_sha256"] = sha256_hex(source_bytes + gold_bytes)
        prov_bytes = canonical_json_bytes(built["provenance"])

        case_dir = base_dir / dataset / "cases" / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "source.md").write_bytes(source_bytes)
        (case_dir / "external_gold.json").write_bytes(gold_bytes)
        (case_dir / "provenance.json").write_bytes(prov_bytes)

        manifest_entries.append(
            {
                "case_id": case_id,
                "dataset": dataset,
                "upstream_id": built["provenance"]["upstream_case_id"],
                "split_or_domain": built["provenance"].get("upstream_domain", built["provenance"]["upstream_split"]),
                "evidence_cardinality": built["external_gold"]["native_metadata"].get("cardinality", "n/a"),
                "source_word_count": built["external_gold"]["native_metadata"]["source_word_count"],
                "source_sha256": built["provenance"]["source_sha256"],
                "transformed_case_sha256": built["provenance"]["transformed_case_sha256"],
                "provenance_path": f"{dataset}/cases/{case_id}/provenance.json",
            }
        )
    return manifest_entries


def build_manifest(base_dir: Path, all_entries: dict[str, list[dict]]) -> None:
    cases = []
    for dataset, entries in all_entries.items():
        cases.extend(entries)
    cases.sort(key=lambda e: e["case_id"])

    manifest = {
        "corpus_version": 1,
        "build_script_version": BUILD_SCRIPT_VERSION,
        "datasets": {
            "qmsum": {"case_count": len(all_entries.get("qmsum", []))},
            "qasper": {"case_count": len(all_entries.get("qasper", []))},
            "hotpotqa": {"case_count": len(all_entries.get("hotpotqa", [])), "pressure_only": True},
        },
        "cases": cases,
    }
    write_json(base_dir / "MANIFEST.json", manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=[*BUILDERS, "all"], default="all")
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--base-dir", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    targets = list(BUILDERS) if args.dataset == "all" else [args.dataset]
    all_entries = {}
    # start from whatever's already in MANIFEST.json for datasets not being rebuilt
    manifest_path = args.base_dir / "MANIFEST.json"
    if manifest_path.exists():
        existing = read_json(manifest_path)
        by_dataset = {}
        for c in existing.get("cases", []):
            by_dataset.setdefault(c["dataset"], []).append(c)
        for d, entries in by_dataset.items():
            if d not in targets:
                all_entries[d] = entries

    for dataset in targets:
        print(f"=== building {dataset} ===")
        entries = build_dataset(dataset, args.base_dir, args.cache_dir)
        all_entries[dataset] = entries
        print(f"[{dataset}] built {len(entries)} cases")

    build_manifest(args.base_dir, all_entries)
    print(f"MANIFEST.json written with {sum(len(v) for v in all_entries.values())} total cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
