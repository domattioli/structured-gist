"""Deposit a release on Zenodo as a new version under the structured-gist concept DOI.

Runs in the release workflow after the GitHub release when the record is missing. The
Zenodo GitHub integration stays off (CONTRIBUTING.md), so this is the only archive path.

    ZENODO_TOKEN=... python3 tools/zenodo_deposit.py v0.11.0 --dist dist

Steps: find the newest record under the concept, open a new version of it, replace its
files with the built wheel and sdist, set metadata from .zenodo.json, publish. The token
comes from the environment only and is never printed. Exit 0 on publish or when the
version already exists under the concept; exit 1 on any refusal.

Refusals (nothing is published): version already under another concept (stray), no
token, .zenodo.json version disagrees with the tag, no files in --dist, an API error.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Support direct execution from outside the repository, including the release job.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.check_zenodo_concept import CONCEPT_DOI, CONCEPT_RECID, check_once

API = "https://zenodo.org/api"


class Api:
    """Thin HTTP client. `call(method, url, body=None, raw=False)` returns parsed JSON."""

    def __init__(self, token: str):
        self.token = token

    def call(self, method: str, url: str, body=None, raw: bool = False) -> dict:
        data = body if raw else (json.dumps(body).encode() if body is not None else None)
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", "application/octet-stream" if raw else "application/json")
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:  # noqa: S310 (fixed https host)
                text = resp.read().decode() or "{}"
                return json.loads(text)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            raise RuntimeError(f"{method} {url.split('?')[0]} -> HTTP {exc.code}: {detail}") from None


def latest_record_id(fetch) -> str:
    hits = fetch({"q": f"conceptrecid:{CONCEPT_RECID}", "all_versions": "true", "sort": "mostrecent", "size": 1})
    if not hits:
        raise RuntimeError(f"no record under concept {CONCEPT_DOI}")
    return str(hits[0]["id"])


def load_metadata(zenodo_json: Path, version: str) -> dict:
    meta = json.loads(zenodo_json.read_text(encoding="utf-8"))
    if str(meta.get("version", "")).lstrip("v") != version:
        raise RuntimeError(f".zenodo.json version {meta.get('version')!r} does not match tag {version}")
    meta.setdefault("upload_type", "software")
    meta["publication_date"] = meta.get("publication_date") or _today()
    return meta


def _today() -> str:
    import datetime as _dt
    return _dt.date.today().isoformat()


def deposit(version: str, dist: Path, zenodo_json: Path, api: Api, fetch, log=print) -> str:
    """Publish version under the concept. Returns the new record URL."""
    files = sorted(p for p in dist.iterdir() if p.suffix in (".whl", ".gz") and p.is_file())
    if not files:
        raise RuntimeError(f"no wheel or sdist in {dist}")
    meta = load_metadata(zenodo_json, version)
    parent = latest_record_id(fetch)
    log(f"new version of record {parent} under {CONCEPT_DOI}")
    nv = api.call("POST", f"{API}/deposit/depositions/{parent}/actions/newversion")
    draft_url = nv["links"]["latest_draft"]
    draft = api.call("GET", draft_url)
    if draft.get("conceptrecid") and str(draft["conceptrecid"]) != CONCEPT_RECID:
        raise RuntimeError(f"draft {draft.get('id')} sits under concept {draft['conceptrecid']}, want {CONCEPT_RECID}")
    for f in draft.get("files", []):
        api.call("DELETE", f"{draft_url}/files/{f['id']}")
        log(f"removed inherited file {f['filename']}")
    bucket = draft["links"]["bucket"]
    for path in files:
        api.call("PUT", f"{bucket}/{path.name}", body=path.read_bytes(), raw=True)
        log(f"uploaded {path.name} ({path.stat().st_size} bytes)")
    api.call("PUT", draft_url, body={"metadata": meta})
    log(f"metadata set: version {meta['version']}, license {meta.get('license')}")
    pub = api.call("POST", f"{draft_url}/actions/publish")
    if pub.get("conceptdoi") != CONCEPT_DOI:
        raise RuntimeError(f"published record {pub.get('id')} has conceptdoi {pub.get('conceptdoi')}, want {CONCEPT_DOI}")
    return pub.get("links", {}).get("record_html") or pub.get("links", {}).get("html") or str(pub.get("id"))


def main(argv=None, api_factory=Api, fetch=None, env=None) -> int:
    from tools.check_zenodo_concept import _get
    fetch = fetch or _get
    env = os.environ if env is None else env
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("version", help="tag or version, v0.11.0 or 0.11.0")
    ap.add_argument("--dist", default="dist", help="directory holding the wheel and sdist")
    ap.add_argument("--zenodo-json", default=".zenodo.json")
    args = ap.parse_args(argv)
    version = args.version.strip().lstrip("v")

    status, msg = check_once(version, fetch)
    print(f"pre-check: {status}: {msg}")
    if status == "ok":
        return 0
    if status == "stray":
        print(f"FAIL: {msg}", file=sys.stderr)
        return 1
    token = env.get("ZENODO_TOKEN", "")
    if not token:
        print("FAIL: ZENODO_TOKEN is not set; add the repository secret or deposit by hand (CONTRIBUTING.md)",
              file=sys.stderr)
        return 1
    try:
        url = deposit(version, Path(args.dist), Path(args.zenodo_json), api_factory(token), fetch)
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"published {version} under {CONCEPT_DOI}: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
