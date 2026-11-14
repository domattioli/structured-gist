import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import zenodo_deposit as zd  # noqa: E402
from tools.check_zenodo_concept import CONCEPT_DOI, CONCEPT_RECID  # noqa: E402

PARENT = {"id": 23910305, "metadata": {"version": "0.10.0"}, "conceptrecid": CONCEPT_RECID, "conceptdoi": CONCEPT_DOI}
STRAY = {"id": 5, "metadata": {"version": "0.11.0"}, "conceptrecid": "999", "conceptdoi": "10.5281/zenodo.999"}
DRAFT_URL = "https://zenodo.org/api/deposit/depositions/777"


def fetch_for(concept_hits, repo_hits=()):
    def fetch(params):
        return list(concept_hits) if params["q"].startswith("conceptrecid:") else list(repo_hits)
    return fetch


class FakeApi:
    """Records every call; answers like Zenodo's deposit API."""

    def __init__(self, token, conceptrecid=CONCEPT_RECID, publish_conceptdoi=CONCEPT_DOI):
        self.token, self.calls = token, []
        self.conceptrecid, self.publish_conceptdoi = conceptrecid, publish_conceptdoi

    def call(self, method, url, body=None, raw=False):
        self.calls.append((method, url, None if raw else body))
        if url.endswith("/actions/newversion"):
            return {"links": {"latest_draft": DRAFT_URL}}
        if method == "GET" and url == DRAFT_URL:
            return {"id": 777, "conceptrecid": self.conceptrecid,
                    "files": [{"id": "old", "filename": "structured_gist-0.10.0.tar.gz"}],
                    "links": {"bucket": "https://zenodo.org/api/files/bucket-777"}}
        if url.endswith("/actions/publish"):
            return {"id": 778, "conceptdoi": self.publish_conceptdoi, "links": {"record_html": "https://zenodo.org/records/778"}}
        return {}


class Workspace:
    def __init__(self, version="0.11.0", files=("structured_gist-0.11.0-py3-none-any.whl", "structured_gist-0.11.0.tar.gz")):
        self.tmp = tempfile.TemporaryDirectory()
        unittest.addModuleCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.dist = root / "dist"
        self.dist.mkdir()
        for name in files:
            (self.dist / name).write_bytes(b"x" * 10)
        self.zj = root / ".zenodo.json"
        self.zj.write_text(json.dumps({"title": "structured-gist", "version": version, "license": "apache-2.0",
                                       "creators": [{"name": "Mattioli, Dominik O."}], "description": "<p>d</p>"}))

    def argv(self, version="v0.11.0"):
        return [version, "--dist", str(self.dist), "--zenodo-json", str(self.zj)]


def run(argv, fetch, api_holder, env):
    out, err = io.StringIO(), io.StringIO()

    def factory(token):
        api_holder.append(FakeApi(token))
        return api_holder[-1]
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = zd.main(argv, api_factory=factory, fetch=fetch, env=env)
    return rc, out.getvalue(), err.getvalue()


class ZenodoDepositTests(unittest.TestCase):
    def test_help_runs_outside_repo_without_pythonpath(self):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run(
                [sys.executable, str(Path(zd.__file__).resolve()), "--help"],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage", result.stdout)

    def test_publishes_new_version_with_built_files_and_metadata(self):
        ws, apis = Workspace(), []
        rc, out, _ = run(ws.argv(), fetch_for([PARENT]), apis, {"ZENODO_TOKEN": "t"})
        self.assertEqual(rc, 0, out)
        methods = [(m, u.rsplit("/", 1)[-1]) for m, u, _ in apis[0].calls]
        self.assertEqual(methods[0], ("POST", "newversion"))
        self.assertIn(("DELETE", "old"), methods)
        self.assertIn(("PUT", "structured_gist-0.11.0-py3-none-any.whl"), methods)
        self.assertIn(("PUT", "structured_gist-0.11.0.tar.gz"), methods)
        meta_put = [b for m, u, b in apis[0].calls if m == "PUT" and u == DRAFT_URL][0]
        self.assertEqual(meta_put["metadata"]["version"], "0.11.0")
        self.assertEqual(meta_put["metadata"]["upload_type"], "software")
        self.assertEqual(methods[-1], ("POST", "publish"))
        self.assertIn("published 0.11.0", out)

    def test_existing_record_is_a_noop(self):
        ws, apis = Workspace(), []
        done = {**PARENT, "metadata": {"version": "0.11.0"}}
        rc, _, _ = run(ws.argv(), fetch_for([done]), apis, {"ZENODO_TOKEN": "t"})
        self.assertEqual((rc, apis), (0, []))

    def test_stray_record_refuses(self):
        ws, apis = Workspace(), []
        rc, _, err = run(ws.argv(), fetch_for([PARENT], [STRAY]), apis, {"ZENODO_TOKEN": "t"})
        self.assertEqual((rc, apis), (1, []))
        self.assertIn("FAIL", err)

    def test_missing_token_refuses_without_api_calls(self):
        ws, apis = Workspace(), []
        rc, _, err = run(ws.argv(), fetch_for([PARENT]), apis, {})
        self.assertEqual((rc, apis), (1, []))
        self.assertIn("ZENODO_TOKEN", err)

    def test_version_mismatch_refuses_before_newversion(self):
        ws, apis = Workspace(version="0.10.9"), []
        rc, _, err = run(ws.argv(), fetch_for([PARENT]), apis, {"ZENODO_TOKEN": "t"})
        self.assertEqual(rc, 1)
        self.assertEqual(apis[0].calls, [])
        self.assertIn("does not match", err)

    def test_empty_dist_refuses(self):
        ws, apis = Workspace(files=()), []
        rc, _, err = run(ws.argv(), fetch_for([PARENT]), apis, {"ZENODO_TOKEN": "t"})
        self.assertEqual(rc, 1)
        self.assertIn("no wheel or sdist", err)

    def test_draft_under_other_concept_refuses_before_publish(self):
        ws = Workspace()
        api = FakeApi("t", conceptrecid="999")
        with self.assertRaises(RuntimeError):
            zd.deposit("0.11.0", ws.dist, ws.zj, api, fetch_for([PARENT]), log=lambda *_: None)
        self.assertFalse(any(u.endswith("publish") for _, u, _ in api.calls))

    def test_api_error_is_a_failure_not_a_crash(self):
        ws, apis = Workspace(), []

        class Boom(FakeApi):
            def call(self, method, url, body=None, raw=False):
                raise RuntimeError("POST newversion -> HTTP 403: forbidden")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = zd.main(ws.argv(), api_factory=Boom, fetch=fetch_for([PARENT]), env={"ZENODO_TOKEN": "t"})
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
