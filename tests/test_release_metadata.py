"""Every release cites the same Zenodo concept DOI ("Cite all versions").

DomI-managed template (spec 032). Copy to tests/test_release_metadata.py and set CONCEPT_DOI to
the repo's concept DOI. Zenodo's GitHub integration files each release as a new version under that
concept, so the citation never changes between releases. The release workflow's test job runs this
suite before anything is built or published. stdlib only; runs under unittest and pytest.
"""
import json
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
CONCEPT_DOI = "10.5281/zenodo.22670068"


class ReleaseMetadataTests(unittest.TestCase):
    def test_concept_doi_filled(self):
        self.assertRegex(CONCEPT_DOI, r"^10\.5281/zenodo\.\d+$", "set CONCEPT_DOI to the repo's concept DOI")

    def test_citation_cites_the_concept_doi(self):
        text = (REPO / "CITATION.cff").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"(?m)^doi:\s*(\S+)\s*$", text), [CONCEPT_DOI])

    def test_readme_uses_only_the_concept_doi(self):
        text = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"doi.org/{CONCEPT_DOI}", text)
        self.assertLessEqual(set(re.findall(r"10\.5281/zenodo\.\d+", text)), {CONCEPT_DOI})

    def test_zenodo_json_never_pins_a_doi(self):
        # A doi or concept field here would make Zenodo file the release outside the concept record.
        path = REPO / ".zenodo.json"
        if not path.exists():
            self.skipTest("no .zenodo.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("doi", "conceptdoi", "conceptrecid", "prereserve_doi"):
            self.assertNotIn(key, data)

    def test_no_operator_placeholders(self):
        for name in ("CITATION.cff", ".zenodo.json"):
            path = REPO / name
            if path.exists():
                self.assertNotIn("TODO-operator", path.read_text(encoding="utf-8"), name)


if __name__ == "__main__":
    unittest.main()
