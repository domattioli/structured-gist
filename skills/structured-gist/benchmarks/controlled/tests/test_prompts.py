"""Prompt files: notice byte identity (FR-025), the FR-005 guard, and
template fidelity against the DomI contracts (tasks T010)."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

CB = Path(__file__).resolve().parent.parent
PROMPTS = CB / "prompts"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "prompt_hashes.json"

NOTICE_SHA256 = "463711420fb2e97f84b8ffc5ddde82ba5f116e65e8ec69e07621252fa48d6c82"

# Frozen copy of the "FR-005 guard" term list in DC/generation-prompts.md.
FR005_TERMS = [
    "▸", "↪", "•", "structured-gist", "structured gist", "gist", "concept",
    "attribute", "enumerator", "explanation", "ladder", "granularity", "skim",
    "standard", "deep", "responsive", "block mode", "hook-arrow",
    "lecture-note", "role",
]

PLAIN_ARM_FILES = ["plain_system.md", "prose_instruction.md", "bullets_instruction.md", "shared_user.md"]

ALL_PROMPT_FILES = [
    "shared_user.md", "skill_instruction.md", "plain_system.md",
    "prose_instruction.md", "bullets_instruction.md", "judge.md",
]

# (file, contract file, heading that starts the section, index of the
# ```text block inside that section, counted from 0)
TEMPLATE_SOURCES = [
    ("shared_user.md", "generation-prompts.md", "## Shared user message", 0),
    ("skill_instruction.md", "generation-prompts.md", "## Skill arm", 0),
    ("plain_system.md", "generation-prompts.md", "## Plain prose arm", 0),
    ("prose_instruction.md", "generation-prompts.md", "## Plain prose arm", 1),
    ("bullets_instruction.md", "generation-prompts.md", "## Plain bullets arm", 0),
    ("judge.md", "judge-prompt.md", "## JUDGE PROTOCOL block", 0),
]


def extract_block(markdown: str, heading: str, index: int) -> str:
    """Returns the contents of the index-th ```text fenced block inside the
    section that starts at `heading` (up to the next heading of the same or
    higher level), with the fence indent removed from every line and one
    trailing newline."""
    lines = markdown.split("\n")
    level = len(heading) - len(heading.lstrip("#"))
    try:
        start = next(i for i, ln in enumerate(lines) if ln.startswith(heading))
    except StopIteration:
        raise AssertionError(f"heading not found: {heading!r}")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        m = re.match(r"^(#+) ", lines[j])
        if m and len(m.group(1)) <= level:
            end = j
            break
    blocks = []
    i = start + 1
    while i < end:
        m = re.match(r"^( *)```text\s*$", lines[i])
        if m:
            indent = m.group(1)
            body = []
            i += 1
            while not re.match(rf"^{indent}```\s*$", lines[i]):
                ln = lines[i]
                if ln.strip() == "":
                    body.append("")
                else:
                    assert ln.startswith(indent), (heading, ln)
                    body.append(ln[len(indent):])
                i += 1
            blocks.append("\n".join(body) + "\n")
        i += 1
    assert index < len(blocks), (heading, index, len(blocks))
    return blocks[index]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# Notice byte identity (FR-025)
# --------------------------------------------------------------------------

def test_notice_bytes():
    p = PROMPTS / "provider_notice.txt"
    data = p.read_bytes()
    assert len(data) == 850
    assert all(b < 128 for b in data), "notice must be ASCII only"
    assert b"\r" not in data
    assert data.endswith(b"\n") and not data.endswith(b"\n\n")
    assert hashlib.sha256(data).hexdigest() == NOTICE_SHA256


def test_notice_equals_contract(paths):
    dc = paths["DC"] / "provider-notice.txt"
    if not dc.is_file():
        pytest.skip("DomI contracts checkout not present")
    assert (PROMPTS / "provider_notice.txt").read_bytes() == dc.read_bytes()


# --------------------------------------------------------------------------
# FR-005 guard
# --------------------------------------------------------------------------

def test_fr005_term_list_matches_contract(paths):
    dc = paths["DC"] / "generation-prompts.md"
    if not dc.is_file():
        pytest.skip("DomI contracts checkout not present")
    text = dc.read_text(encoding="utf-8")
    section = text.split("## FR-005 guard", 1)[1].split("\n## ", 1)[0]
    listed = section.split("any of the following terms:", 1)[1].split(". The test also", 1)[0]
    terms = re.findall(r"`([^`]+)`", listed)
    assert terms == FR005_TERMS


@pytest.mark.parametrize("name", PLAIN_ARM_FILES)
def test_plain_templates_have_no_banned_terms(name):
    text = (PROMPTS / name).read_text(encoding="utf-8").casefold()
    hits = [t for t in FR005_TERMS if t.casefold() in text]
    assert hits == [], f"{name} contains FR-005 banned terms: {hits}"


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def _ngrams(tokens: list[str], n: int = 6) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def test_plain_templates_share_no_6gram_with_skill(paths):
    sg = paths["SG"]
    skill_grams = _ngrams(_tokens((sg / "SKILL.md").read_text(encoding="utf-8")))
    skill_grams |= _ngrams(_tokens((sg / "reference" / "render-modes.md").read_text(encoding="utf-8")))
    for name in PLAIN_ARM_FILES:
        shared = _ngrams(_tokens((PROMPTS / name).read_text(encoding="utf-8"))) & skill_grams
        assert not shared, f"{name} shares 6-word sequences with the skill spec: {sorted(shared)[:3]}"


def test_guard_would_fire():
    # The guard itself can fail: a skill-flavoured sentence trips it.
    probe = "Use an attribute at standard granularity.".casefold()
    assert [t for t in FR005_TERMS if t in probe] == ["attribute", "granularity", "standard"]


# --------------------------------------------------------------------------
# Template fidelity
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", ALL_PROMPT_FILES)
def test_prompt_file_format(name):
    data = (PROMPTS / name).read_bytes()
    assert b"\r" not in data
    assert data.endswith(b"\n") and not data.endswith(b"\n\n")
    data.decode("utf-8")


def test_pinned_hash_fixture():
    pinned = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert sorted(pinned) == sorted(ALL_PROMPT_FILES + ["provider_notice.txt"])
    for name, sha in pinned.items():
        assert _sha(PROMPTS / name) == sha, name


@pytest.mark.parametrize("name, contract, heading, index", TEMPLATE_SOURCES)
def test_prompt_matches_contract_block(paths, name, contract, heading, index):
    dc = paths["DC"] / contract
    if not dc.is_file():
        pytest.skip("DomI contracts checkout not present")
    expected = extract_block(dc.read_text(encoding="utf-8"), heading, index)
    assert (PROMPTS / name).read_text(encoding="utf-8") == expected


def test_extract_block_dedents_nested_fence():
    md = "## A\n\n- x:\n\n  ```text\n  one\n\n  two\n  ```\n\n## B\n\n```text\nb\n```\n"
    assert extract_block(md, "## A", 0) == "one\n\ntwo\n"
    assert extract_block(md, "## B", 0) == "b\n"
