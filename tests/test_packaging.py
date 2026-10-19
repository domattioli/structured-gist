"""Wheel and sdist contents for the structured-gist PyPI distribution.

Skips unless `build` and `hatchling` import in the running interpreter.
Builds with --no-isolation into tmp_path, so it needs no network.
"""
import pathlib
import subprocess
import sys
import tarfile
import zipfile

import pytest

pytest.importorskip("build")
pytest.importorskip("hatchling")

REPO = pathlib.Path(__file__).resolve().parents[1]

WHEEL_MODULES = (
    "structured_gist/__init__.py",
    "structured_gist/lint_outline.py",
    "structured_gist/claim_list.py",
    "structured_gist/claim_list.schema.json",
)
SDIST_FORBIDDEN = (
    "skills/structured-gist/benchmarks",
    "specs",
    ".specify",
    "docs",
    ".claude",
)


def _build(kind, outdir):
    subprocess.run(
        [sys.executable, "-m", "build", f"--{kind}", "--no-isolation", "--outdir", str(outdir), str(REPO)],
        check=True,
        capture_output=True,
    )
    suffix = ".whl" if kind == "wheel" else ".tar.gz"
    (artifact,) = [p for p in outdir.iterdir() if p.name.endswith(suffix)]
    return artifact


def test_wheel_contents(tmp_path):
    wheel = _build("wheel", tmp_path)
    with zipfile.ZipFile(wheel) as zf:
        names = zf.namelist()
        for module in WHEEL_MODULES:
            assert module in names, module
        (entry_points,) = [n for n in names if n.endswith(".dist-info/entry_points.txt")]
        scripts = zf.read(entry_points).decode("utf-8")
    assert "structured-gist-lint = structured_gist.lint_outline:main" in scripts
    assert "structured-gist-claims = structured_gist.claim_list:main" in scripts


def test_sdist_excludes_agent_and_benchmark_files(tmp_path):
    sdist = _build("sdist", tmp_path)
    with tarfile.open(sdist) as tf:
        # Strip the leading "<name>-<version>/" directory.
        paths = [name.split("/", 1)[1] for name in tf.getnames() if "/" in name]
    for path in paths:
        for forbidden in SDIST_FORBIDDEN:
            assert path != forbidden and not path.startswith(forbidden + "/"), path
