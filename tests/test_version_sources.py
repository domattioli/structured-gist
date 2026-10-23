"""Every version source in the repo names the same release version.

stdlib + pytest only. Sources: pyproject.toml [project] version, SKILL.md
frontmatter, plugin.json, CITATION.cff, .zenodo.json and the
_FALLBACK_VERSION constant in claim_list.py.
"""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]


def _pyproject_version():
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    try:
        import tomllib
    except ImportError:  # Python < 3.11
        section = re.search(r"(?ms)^\[project\]\s*$(.*?)(?=^\[|\Z)", text)
        assert section, "pyproject.toml has no [project] table"
        match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', section.group(1))
        assert match, "pyproject.toml [project] has no static version"
        return match.group(1)
    return tomllib.loads(text)["project"]["version"]


def _skill_version():
    text = (REPO / "skills/structured-gist/SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"(?s)^---\n(.*?)\n---\n", text)
    assert frontmatter, "SKILL.md has no frontmatter"
    match = re.search(r'(?m)^version:\s*"?([^"\s]+)"?\s*$', frontmatter.group(1))
    assert match, "SKILL.md frontmatter has no version"
    return match.group(1)


def _plugin_version():
    path = REPO / "plugins/structured-gist/.claude-plugin/plugin.json"
    return json.loads(path.read_text(encoding="utf-8"))["version"]


def _citation_version():
    text = (REPO / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version:\s*"?([^"\s]+)"?\s*$', text)
    assert match, "CITATION.cff has no version"
    return match.group(1)


def _zenodo_version():
    return json.loads((REPO / ".zenodo.json").read_text(encoding="utf-8"))["version"]


def _claim_list_fallback_version():
    text = (REPO / "skills/structured-gist/render/claim_list.py").read_text(encoding="utf-8")
    match = re.search(r'(?m)^_FALLBACK_VERSION\s*=\s*"([^"]+)"', text)
    assert match, "claim_list.py has no _FALLBACK_VERSION"
    return match.group(1)


def test_all_version_sources_agree():
    versions = {
        "pyproject.toml": _pyproject_version(),
        "SKILL.md": _skill_version(),
        "plugin.json": _plugin_version(),
        "CITATION.cff": _citation_version(),
        ".zenodo.json": _zenodo_version(),
        "claim_list.py": _claim_list_fallback_version(),
    }
    assert len(set(versions.values())) == 1, versions
