import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import check_zenodo_concept as z  # noqa: E402

GOOD = {"id": 1, "metadata": {"version": "0.10.0"}, "conceptrecid": "22670068", "conceptdoi": z.CONCEPT_DOI}
STRAY = {"id": 23288172, "metadata": {"version": "0.11.0"}, "conceptrecid": "23286662",
         "conceptdoi": "10.5281/zenodo.23286662"}


def fake(concept_hits, repo_hits):
    def fetch(params):
        return concept_hits if params["q"].startswith("conceptrecid:") else repo_hits
    return fetch


def run(argv, fetch):
    sleeps = []
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc = z.main(argv, fetch=fetch, sleep=sleeps.append)
    return rc, sleeps


class ZenodoConceptCheckTests(unittest.TestCase):
    def test_concept_constants(self):
        self.assertEqual(z.CONCEPT_RECID, "22670068")
        self.assertEqual(z.CONCEPT_DOI, "10.5281/zenodo.22670068")

    def test_version_under_concept_passes(self):
        self.assertEqual(z.check_once("v0.10.0", fake([GOOD], []))[0], "ok")

    def test_stray_concept_fails_at_once(self):
        self.assertEqual(z.check_once("0.11.0", fake([GOOD], [STRAY]))[0], "stray")
        rc, sleeps = run(["0.11.0", "--attempts", "5"], fake([GOOD], [STRAY]))
        self.assertEqual((rc, sleeps), (1, []))

    def test_missing_retries_then_fails(self):
        rc, sleeps = run(["0.11.1", "--attempts", "3", "--interval", "7"], fake([GOOD], []))
        self.assertEqual((rc, sleeps), (1, [7.0, 7.0]))

    def test_api_error_never_passes(self):
        def boom(params):
            raise OSError("offline")
        self.assertEqual(run(["0.11.1", "--attempts", "2"], boom)[0], 1)


if __name__ == "__main__":
    unittest.main()
