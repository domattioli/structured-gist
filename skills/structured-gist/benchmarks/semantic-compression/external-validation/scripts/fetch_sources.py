#!/usr/bin/env python3
"""
Fetches canonical upstream data for the external-validation corpus
(QMSum, Qasper, HotpotQA) into a local cache directory and records exact
provenance (revision/version, license, retrieval date, content hashes) for
everything it downloads.

Network-dependent. Not part of the committed offline verification path
(verify_corpus.py) or the pytest suite -- this is the one script in this
directory allowed to touch the network. Run it once to populate
--cache-dir before running select_cases.py / build_cases.py.

Sources (see external-validation/README.md "Licensing and provenance" for
the full record):
  - QMSum:    Yale-LILY/QMSum on GitHub, MIT license, pinned commit SHA.
  - Qasper:   official AllenAI S3 tarball (qasper-train-dev-v0.3), CC BY 4.0.
  - HotpotQA: distractor dev split. The canonical host
              (curtis.ml.cmu.edu) was unreachable from this build
              environment (connection timeout, not an HTTP error) at
              retrieval time, so this script falls back to the dataset's
              official Hugging Face mirror published by the `hotpotqa` org
              account itself (same publisher, byte-identical schema,
              pinned repo revision SHA), CC BY-SA 4.0. This deviation is
              recorded in raw_manifest.json for hotpotqa.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import sys
import tarfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "structured-gist-external-validation-corpus/1 (+https://github.com/domattioli/structured-gist)"

QMSUM_COMMIT = "83d7768c1f2b4dfeb091385d3dc7e239b8e5bb7e"
QMSUM_DOMAINS = ["Academic", "Committee", "Product"]
QMSUM_RAW_BASE = f"https://raw.githubusercontent.com/Yale-LILY/QMSum/{QMSUM_COMMIT}"
QMSUM_LICENSE_URL = f"{QMSUM_RAW_BASE}/LICENSE"

QASPER_TARBALL_URL = "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz"
QASPER_VERSION = "v0.3"

HOTPOTQA_ORIGINAL_URL = "http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json"
HOTPOTQA_HF_DATASET = "hotpotqa/hotpot_qa"
HOTPOTQA_HF_CONFIG = "distractor"
HOTPOTQA_HF_SPLIT = "validation"
HOTPOTQA_ROWS_PER_PAGE = 100


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _get(url: str, timeout: int = 60, retries: int = 6) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last_err = e
            wait = 10.0 * (attempt + 1) if e.code == 429 else 2.0 * (attempt + 1)
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError) as e:
            last_err = e
            time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_err}")


def _get_json(url: str, timeout: int = 60) -> dict:
    return json.loads(_get(url, timeout=timeout))


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _write_json(path: Path, obj) -> None:
    _write(path, (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8"))


# ---------------------------------------------------------------------------
# QMSum
# ---------------------------------------------------------------------------

def fetch_qmsum(cache_dir: Path) -> None:
    out_dir = cache_dir / "qmsum"
    license_text = _get(QMSUM_LICENSE_URL).decode("utf-8")
    assert "MIT License" in license_text, "QMSum LICENSE no longer reads as MIT -- re-verify before proceeding"
    _write(out_dir / "LICENSE", license_text.encode("utf-8"))

    manifest = {
        "dataset": "qmsum",
        "source_repo": "https://github.com/Yale-LILY/QMSum",
        "commit_sha": QMSUM_COMMIT,
        "license": "MIT",
        "license_source": QMSUM_LICENSE_URL,
        "retrieved_at": _now_iso(),
        "splits_fetched": {},
        "all_meetings_fetched": {},
    }

    # Test split per domain -- our eligibility pool.
    for domain in QMSUM_DOMAINS:
        url = f"{QMSUM_RAW_BASE}/data/{domain}/jsonl/test.jsonl"
        data = _get(url)
        dest = out_dir / "jsonl" / domain / "test.jsonl"
        _write(dest, data)
        n_lines = sum(1 for _ in data.decode("utf-8").splitlines() if _.strip())
        manifest["splits_fetched"][domain] = {
            "split": "test",
            "url": url,
            "sha256": _sha256_bytes(data),
            "n_meetings": n_lines,
        }
        print(f"[qmsum] {domain} test.jsonl: {n_lines} meetings, sha256={_sha256_bytes(data)[:12]}...")

    # data/<Domain>/all/*.json -- per-meeting files carrying QMSum's native
    # (ICSI/AMI/committee-derived) meeting identifiers, needed because the
    # jsonl split files carry no meeting-id field of their own. Fetched so
    # select_cases.py / build_cases.py can resolve a real upstream meeting
    # ID for every candidate by exact content match on meeting_transcripts.
    tree_url = f"https://api.github.com/repos/Yale-LILY/QMSum/git/trees/{QMSUM_COMMIT}?recursive=1"
    tree = _get_json(tree_url)
    all_paths = [
        item["path"]
        for item in tree.get("tree", [])
        if item["path"].startswith("data/") and "/all/" in item["path"] and item["path"].endswith(".json")
        and item["path"].split("/")[1] in QMSUM_DOMAINS
    ]
    print(f"[qmsum] fetching {len(all_paths)} per-meeting files for native-ID resolution...")

    def _fetch_one(path: str):
        url = f"{QMSUM_RAW_BASE}/{path}"
        data = _get(url)
        return path, data

    fetched = 0
    with ThreadPoolExecutor(max_workers=16) as ex:
        futures = {ex.submit(_fetch_one, p): p for p in all_paths}
        for fut in as_completed(futures):
            path, data = fut.result()
            dest = out_dir / path
            _write(dest, data)
            fetched += 1
            domain = path.split("/")[1]
            manifest["all_meetings_fetched"].setdefault(domain, 0)
            manifest["all_meetings_fetched"][domain] += 1
    print(f"[qmsum] fetched {fetched}/{len(all_paths)} per-meeting files")

    _write_json(out_dir / "raw_manifest.json", manifest)


# ---------------------------------------------------------------------------
# Qasper
# ---------------------------------------------------------------------------

def fetch_qasper(cache_dir: Path) -> None:
    out_dir = cache_dir / "qasper"
    tarball = _get(QASPER_TARBALL_URL, timeout=120)
    tarball_sha = _sha256_bytes(tarball)

    with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as tf:
        members = {m.name: m for m in tf.getmembers()}
        dev_name = next(n for n in members if n.endswith("qasper-dev-v0.3.json"))
        readme_name = next((n for n in members if n.endswith("README.md")), None)
        dev_bytes = tf.extractfile(members[dev_name]).read()
        _write(out_dir / "qasper-dev-v0.3.json", dev_bytes)
        if readme_name:
            _write(out_dir / "UPSTREAM_README.md", tf.extractfile(members[readme_name]).read())

    manifest = {
        "dataset": "qasper",
        "source_url": QASPER_TARBALL_URL,
        "version": QASPER_VERSION,
        "split_used": "dev",
        "license": "CC BY 4.0",
        "license_source": "https://huggingface.co/datasets/allenai/qasper (cardData.license = cc-by-4.0); homepage https://allenai.org/data/qasper",
        "retrieved_at": _now_iso(),
        "tarball_sha256": tarball_sha,
        "dev_json_sha256": _sha256_bytes(dev_bytes),
    }
    _write_json(out_dir / "raw_manifest.json", manifest)
    print(f"[qasper] dev-v0.3.json: sha256={manifest['dev_json_sha256'][:12]}...")


# ---------------------------------------------------------------------------
# HotpotQA
# ---------------------------------------------------------------------------

def fetch_hotpotqa(cache_dir: Path) -> None:
    out_dir = cache_dir / "hotpotqa"

    original_reachable = True
    try:
        _get(HOTPOTQA_ORIGINAL_URL, timeout=15, retries=1)
    except Exception as e:  # noqa: BLE001 -- any failure means "fall back"
        original_reachable = False
        original_error = str(e)

    api = _get_json(f"https://huggingface.co/api/datasets/{HOTPOTQA_HF_DATASET}")
    revision_sha = api["sha"]

    total = _get_json(
        "https://datasets-server.huggingface.co/rows"
        f"?dataset={HOTPOTQA_HF_DATASET.replace('/', '%2F')}&config={HOTPOTQA_HF_CONFIG}"
        f"&split={HOTPOTQA_HF_SPLIT}&offset=0&length=1"
    )["num_rows_total"]

    dest = out_dir / "distractor_validation.jsonl"
    partial = out_dir / "distractor_validation.jsonl.partial"
    rows = []
    if partial.exists():
        rows = [json.loads(line) for line in partial.read_text("utf-8").splitlines() if line.strip()]
        print(f"[hotpotqa] resuming from partial cache: {len(rows)} rows already fetched")
    offset = len(rows)
    partial.parent.mkdir(parents=True, exist_ok=True)
    with open(partial, "a", encoding="utf-8") as pf:
        while offset < total:
            page = _get_json(
                "https://datasets-server.huggingface.co/rows"
                f"?dataset={HOTPOTQA_HF_DATASET.replace('/', '%2F')}&config={HOTPOTQA_HF_CONFIG}"
                f"&split={HOTPOTQA_HF_SPLIT}&offset={offset}&length={HOTPOTQA_ROWS_PER_PAGE}"
            )
            page_rows = [r["row"] for r in page["rows"]]
            for r in page_rows:
                pf.write(json.dumps(r, sort_keys=True))
                pf.write("\n")
            pf.flush()
            rows.extend(page_rows)
            offset += HOTPOTQA_ROWS_PER_PAGE
            if offset % 1000 == 0 or offset >= total:
                print(f"[hotpotqa] fetched {min(offset, total)}/{total} rows")
            time.sleep(0.4)

    assert len(rows) == total, f"expected {total} rows, got {len(rows)}"

    buf = io.StringIO()
    for r in rows:
        buf.write(json.dumps(r, sort_keys=True))
        buf.write("\n")
    data = buf.getvalue().encode("utf-8")
    _write(dest, data)
    partial.unlink(missing_ok=True)

    manifest = {
        "dataset": "hotpotqa",
        "config": HOTPOTQA_HF_CONFIG,
        "split": HOTPOTQA_HF_SPLIT,
        "n_rows": total,
        "license": "CC BY-SA 4.0",
        "license_source": "https://hotpotqa.github.io/ (\"HotpotQA is distributed under a CC BY-SA 4.0 License\")",
        "retrieved_at": _now_iso(),
        "primary_source_url": HOTPOTQA_ORIGINAL_URL,
        "primary_source_reachable_at_build_time": original_reachable,
        "primary_source_error": None if original_reachable else original_error,
        "fallback_source": f"https://huggingface.co/datasets/{HOTPOTQA_HF_DATASET}",
        "fallback_source_repo_sha": revision_sha,
        "fallback_source_publisher": "hotpotqa (same organization that publishes the canonical hotpotqa.github.io site)",
        "deviation_note": (
            "Primary host curtis.ml.cmu.edu did not respond (TCP connect timeout, "
            "no HTTP error) from the build environment. Used the hotpotqa org's own "
            "Hugging Face mirror instead, pinned to the dataset repo's sha. Schema and "
            "content are the official distractor dev split; only the transport differs."
            if not original_reachable else
            "Primary host was reachable; HF mirror was used anyway for pagination "
            "convenience. Re-run with the primary host to cross-check if needed."
        ),
        "jsonl_sha256": _sha256_bytes(data),
    }
    _write_json(out_dir / "raw_manifest.json", manifest)
    print(f"[hotpotqa] {total} rows: sha256={manifest['jsonl_sha256'][:12]}...")


DATASETS = {
    "qmsum": fetch_qmsum,
    "qasper": fetch_qasper,
    "hotpotqa": fetch_hotpotqa,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=[*DATASETS, "all"], default="all")
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / ".raw-cache",
        help="Local cache directory for fetched upstream data (not committed).",
    )
    args = parser.parse_args()

    targets = list(DATASETS) if args.dataset == "all" else [args.dataset]
    for name in targets:
        print(f"=== fetching {name} ===")
        DATASETS[name](args.cache_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
