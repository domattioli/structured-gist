#!/usr/bin/env python3
"""
Fixture-contract tests for the structured-gist "tell me more" drill-down.

Scope (release 0.11.0, plan GE-1): these tests check the fixture contract only.
They do not measure real-agent behaviour. All fixtures are synthetic text.

Oracle rules:
- A reply is checked at the destination width in the mode the case declares.
- A quote is a quote fence inside a leaf. The fence's leading whitespace is the
  prefix. Extraction removes exactly that prefix, joins with "\\n", and compares
  bytes with the source. Quote-fence lines are removed before linting.
- Relevance of new detail to the declared scope cannot be linted; it is judged
  only by the fixture's declared scope.
"""

import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from lint_outline import lint_text  # noqa: E402

TESTS = Path(__file__).parent
FIXTURES = TESTS / "fixtures" / "drilldown"
SKILL = TESTS.parent / "SKILL.md"
PLUGIN = TESTS.parent.parent.parent / "plugins" / "structured-gist" / ".claude-plugin" / "plugin.json"

CASE_KEYS = {
    "case_type", "input_mode", "output_mode", "width", "target_path", "ancestors",
    "sub_requests", "scope", "associated_span", "assertion", "r5_counts",
}
SUB_KEYS = {"request", "expected", "target_path", "ancestors", "assertion"}
ASSERTIONS = {"hierarchical", "single_fact", "notice"}
CASE_TYPES = {"positive", "checker_reject"}
MODES = {"block", "responsive"}
ROLES = {"concept", "attribute", "enumerator", "explanation"}

CASES = sorted(p.name for p in FIXTURES.iterdir() if p.is_dir()) if FIXTURES.is_dir() else []

QUOTE_OPEN = re.compile(r"^(\s*)(`{4,})\s*$")


def load(name):
    return json.loads((FIXTURES / name / "case.json").read_text(encoding="utf-8"))


def read(name, fname):
    # newline="" keeps the bytes exactly as written
    with open(FIXTURES / name / fname, encoding="utf-8", newline="") as f:
        return f.read()


def units(name):
    """Yield (label, expected_text, assertion, target_path, ancestors) per sub-request or case."""
    meta = load(name)
    if "sub_requests" in meta:
        for i, sr in enumerate(meta["sub_requests"]):
            yield (f"{name}#{i}", read(name, sr["expected"]), sr["assertion"],
                   sr["target_path"], sr["ancestors"], sr["request"])
    else:
        yield (name, read(name, "expected.md"), meta["assertion"],
               meta["target_path"], meta["ancestors"], "request.txt")


def extract_quotes(text, assertion):
    """Return list of quoted payloads. Single-fact replies are one column-0 fence."""
    lines = text.split("\n")
    if assertion == "single_fact":
        assert lines[0] == "```" and lines[-2] == "```" and lines[-1] == "", "single-fact fence shape"
        return ["\n".join(lines[1:-2])]
    payloads = []
    i = 0
    while i < len(lines):
        m = QUOTE_OPEN.match(lines[i])
        if not m:
            i += 1
            continue
        prefix, fence = m.group(1), m.group(2)
        j = i + 1
        body = []
        while j < len(lines):
            if lines[j] == prefix + fence:
                break
            assert lines[j].startswith(prefix), f"quote line missing prefix: {lines[j]!r}"
            body.append(lines[j][len(prefix):])
            j += 1
        else:
            raise AssertionError("unterminated quote fence")
        payloads.append("\n".join(body))
        i = j + 1
    return payloads


def strip_quotes(text):
    out, i, lines = [], 0, text.split("\n")
    while i < len(lines):
        m = QUOTE_OPEN.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        close = m.group(1) + m.group(2)
        i += 1
        while lines[i] != close:
            i += 1
        i += 1
    return "\n".join(out)


def provenance_ok(name):
    """Checker: every quote must occur in source.md and equal associated_span."""
    meta = load(name)
    for _label, expected, assertion, *_ in units(name):
        quotes = extract_quotes(expected, assertion) if (
            assertion == "single_fact" or "````" in expected) else []
        if not quotes:
            continue
        src = read(name, "source.md") if (FIXTURES / name / "source.md").exists() else None
        if src is None:
            return False
        for q in quotes:
            if q not in src or q != meta.get("associated_span"):
                return False
    return True


def outline_nodes(text, mode):
    """Return (role, depth, text) for each node of an outline (quotes already stripped)."""
    nodes = []
    for line in text.split("\n"):
        if not line.strip() or line.startswith("```"):
            continue
        if mode == "responsive":
            indent = len(line) - len(line.lstrip(" "))
            body = line.strip()
            if body.startswith("- "):
                body = body[2:]
            depth, bold = indent // 2, body.startswith("**")
            body = body.replace("**", "")
            if depth == 0:
                role = "concept"
            elif bold:
                role = "attribute"
            elif re.match(r"^([IVXLC]+|[ivxlc]+|[A-Za-z])\. ", body):
                role = "enumerator"
            else:
                role = "explanation"
            nodes.append((role, depth, body))
        else:
            indent = len(line) - len(line.lstrip(" "))
            body = line.strip()
            glyph = body[0]
            role = {"-": "concept", "▸": "attribute", "↪": "explanation"}.get(glyph, "enumerator")
            if role != "enumerator":
                body = body[1:].strip()
            nodes.append((role, indent // 4, body))
    return nodes


# ---------------------------------------------------------------- rule presence
def test_skill_has_drilldown_section():
    text = SKILL.read_text(encoding="utf-8")
    assert re.search(r"^## Drill-down\s*$", text, re.M), "SKILL.md lacks a '## Drill-down' section"


def test_version_agreement():
    m = re.search(r'^version:\s*"?([0-9][^"\s]*)"?\s*$', SKILL.read_text(encoding="utf-8"), re.M)
    assert m, "SKILL.md has no version"
    plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
    assert plugin["version"] == m.group(1)
    assert m.group(1) == "0.11.0"


# ---------------------------------------------------------------- fixture inventory
def test_case_count():
    assert len(CASES) == 42


@pytest.mark.parametrize("name", CASES)
def test_schema(name):
    meta = load(name)
    assert set(meta) <= CASE_KEYS, f"extra keys: {set(meta) - CASE_KEYS}"
    for req in ("case_type", "input_mode", "output_mode", "width", "scope"):
        assert req in meta
    assert meta["case_type"] in CASE_TYPES
    assert meta["input_mode"] in MODES and meta["output_mode"] in MODES
    assert isinstance(meta["width"], int)
    assert meta.get("associated_span") is None or isinstance(meta["associated_span"], str)
    if "sub_requests" in meta:
        assert meta["sub_requests"], "sub_requests must be non-empty"
        for sr in meta["sub_requests"]:
            assert set(sr) == SUB_KEYS
            assert sr["assertion"] in ASSERTIONS
            assert (FIXTURES / name / sr["request"]).is_file()
            assert (FIXTURES / name / sr["expected"]).is_file()
    else:
        for req in ("target_path", "ancestors", "assertion"):
            assert req in meta
        assert meta["assertion"] in ASSERTIONS
        assert (FIXTURES / name / "request.txt").is_file()
        assert (FIXTURES / name / "expected.md").is_file()
    assert (FIXTURES / name / "outline.md").is_file()
    if "r5_counts" in meta:
        assert set(meta["r5_counts"]) == {"leaf_arrows", "non_arrow", "expect_r5"}


@pytest.mark.parametrize("name", CASES)
def test_ancestor_shape(name):
    for _l, _e, _a, _t, anc, _r in units(name):
        for a in anc:
            assert set(a) == {"role", "depth", "text"} and a["role"] in ROLES


# ---------------------------------------------------------------- linting
HIER = [n for n in CASES
        if load(n)["case_type"] == "positive"
        and any(u[2] == "hierarchical" for u in units(n))]


@pytest.mark.parametrize("name", HIER)
def test_hierarchical_reply_lints(name):
    meta = load(name)
    for label, expected, assertion, *_ in units(name):
        if assertion != "hierarchical":
            continue
        viol = lint_text(strip_quotes(expected), str(meta["width"]))
        if "r5_counts" in meta:
            has_r5 = any(v[1] == "R5" for v in viol)
            assert has_r5 == meta["r5_counts"]["expect_r5"], (label, viol)
        else:
            assert viol == [], (label, viol)


@pytest.mark.parametrize("name", [n for n in CASES if "r5_counts" in load(n)])
def test_r5_counts(name):
    meta = load(name)
    nodes = outline_nodes(strip_quotes(read(name, "expected.md")), meta["output_mode"])
    arrows = sum(1 for n in nodes if n[0] == "explanation")
    others = sum(1 for n in nodes[1:] if n[0] != "explanation")
    assert arrows == meta["r5_counts"]["leaf_arrows"]
    assert others == meta["r5_counts"]["non_arrow"]


# ---------------------------------------------------------------- wrapper identity
@pytest.mark.parametrize("name", HIER)
def test_wrapper_identity(name):
    meta = load(name)
    for label, expected, assertion, target, anc, _r in units(name):
        if assertion != "hierarchical":
            continue
        nodes = outline_nodes(strip_quotes(expected), meta["output_mode"])
        got = [{"role": r, "depth": d, "text": t} for r, d, t in nodes[:len(anc)]]
        assert got == anc, label
        # The wrapper also keeps the target's own label on its path.
        texts = [n[2] for n in nodes]
        assert target[-1] in " ".join(texts).replace("\n", " ") or target[-1] in texts, label


# ---------------------------------------------------------------- provenance
QUOTED = [n for n in CASES if load(n)["case_type"] == "positive"
          and any(u[2] == "single_fact" or "````" in u[1] for u in units(n))]


@pytest.mark.parametrize("name", QUOTED)
def test_quote_round_trip(name):
    meta = load(name)
    assert provenance_ok(name), name
    for _l, expected, assertion, *_ in units(name):
        for q in extract_quotes(expected, assertion) if (
                assertion == "single_fact" or "````" in expected) else []:
            assert q == meta["associated_span"]
            assert q in read(name, "source.md")


@pytest.mark.parametrize("name", [n for n in CASES if load(n)["case_type"] == "checker_reject"])
def test_checker_rejects(name):
    assert not provenance_ok(name), f"{name} must be rejected by the provenance checker"


def test_quote_lint_exempt():
    """Quote-fence lines never reach the linter, so long and marker-leading payloads pass."""
    for name in ("quote_combined_long", "quote_combined_marker_leading"):
        assert "````" in read(name, "expected.md")
        assert lint_text(strip_quotes(read(name, "expected.md")), "64") == []


# ---------------------------------------------------------------- notices and single facts
@pytest.mark.parametrize("name", [n for n in CASES if load(n).get("assertion") == "notice"
                                 or "sub_requests" in load(n)])
def test_notice_is_prose(name):
    for _l, expected, assertion, *_ in units(name):
        if assertion == "notice":
            assert expected.strip() and "▸" not in expected and not expected.startswith("```")


def test_source_unavailable_has_no_source_file():
    assert not (FIXTURES / "source_unavailable" / "source.md").exists()
    assert not (FIXTURES / "claim_list_only" / "source.md").exists()


def test_scope_values():
    assert load("scope_single_node")["scope"] == "single-node"
    assert load("scope_subtree")["scope"] == "subtree"


def test_modes_recorded_separately():
    assert load("cross_mode_conversion")["input_mode"] != load("cross_mode_conversion")["output_mode"]
    c = load("cross_mode_responsive_to_block")
    assert (c["input_mode"], c["output_mode"]) == ("responsive", "block")
