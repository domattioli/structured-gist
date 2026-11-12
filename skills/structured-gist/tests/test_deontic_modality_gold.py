"""Deterministic checks for the deontic-modality pressure-test gold."""

import json
import re
from pathlib import Path

import pytest


SUITE_DIR = Path(__file__).resolve().parents[1] / "benchmarks" / "semantic-compression"
CASE_DIR = SUITE_DIR / "pressure-tests" / "deontic-modality"


@pytest.fixture
def case():
    source = (CASE_DIR / "source.md").read_text(encoding="utf-8")
    gold = json.loads((CASE_DIR / "gold.json").read_text(encoding="utf-8"))
    return source, gold


def test_metadata_and_collection_types(case):
    _, gold = case
    assert isinstance(gold, dict)
    assert {"case_id", "size_bucket", "pressure_tags", "source_word_count",
            "facts", "relations", "questions"} <= gold.keys()
    assert gold["case_id"] == CASE_DIR.name
    assert gold["size_bucket"] in {"small", "medium"}
    assert isinstance(gold["pressure_tags"], list)
    assert {"deontic", "modality"} <= set(gold["pressure_tags"])
    assert type(gold["source_word_count"]) is int
    for key in ("facts", "relations", "questions"):
        assert isinstance(gold[key], list)


def test_fact_relation_and_question_shapes(case):
    _, gold = case
    fact_ids = []
    for fact in gold["facts"]:
        assert isinstance(fact, dict)
        for key in ("id", "text", "category", "source_quote"):
            assert isinstance(fact[key], str)
        assert type(fact["weight"]) in (int, float)
        assert type(fact["precision_sensitive"]) is bool
        if "attaches_to" in fact:
            assert isinstance(fact["attaches_to"], str)
        fact_ids.append(fact["id"])
    assert len(fact_ids) == len(set(fact_ids))

    for collection, string_fields in (
        ("relations", ("id", "type", "text", "source_quote")),
        ("questions", ("id", "question", "gold_answer", "type")),
    ):
        for item in gold[collection]:
            assert isinstance(item, dict)
            for key in string_fields:
                assert isinstance(item[key], str)
            assert isinstance(item["fact_ids"], list)
            assert all(isinstance(ref, str) for ref in item["fact_ids"])


def test_quotes_are_verbatim(case):
    source, gold = case
    for item in gold["facts"] + gold["relations"]:
        assert item["source_quote"] and item["source_quote"] in source


def test_references_resolve_and_attachments_target_non_epistemic_facts(case):
    _, gold = case
    facts = {fact["id"]: fact for fact in gold["facts"]}
    for fact in gold["facts"]:
        if "attaches_to" in fact:
            assert fact["attaches_to"] in facts
            assert facts[fact["attaches_to"]]["category"] != "epistemic"
    for item in gold["relations"] + gold["questions"]:
        assert set(item["fact_ids"]) <= set(facts)


def test_each_modality_qualifies_its_matching_policy_claim(case):
    _, gold = case
    facts = {fact["id"]: fact for fact in gold["facts"]}
    # Issue 17 fixes the subjects of these three policies, but not their IDs.
    subjects = {"MUST": "documentation", "SHOULD": "rules", "MAY": "examples"}
    targets = set()
    for modality, subject in subjects.items():
        marker = re.compile(rf"\b{modality}\b")
        qualifiers = [fact for fact in gold["facts"]
                      if fact["category"] == "epistemic"
                      and marker.search(fact["source_quote"])]
        assert len(qualifiers) == 1
        qualifier = qualifiers[0]
        assert qualifier["weight"] == 3
        assert "attaches_to" in qualifier
        target = facts[qualifier["attaches_to"]]
        assert target["category"] in {"descriptive", "outcome"}
        assert subject in target["text"].lower()
        assert subject in target["source_quote"].lower()
        assert marker.search(target["source_quote"])
        targets.add(target["id"])
    assert len(targets) == 3


def test_source_word_count(case):
    source, gold = case
    assert gold["source_word_count"] == len(source.split())
    assert 250 <= gold["source_word_count"] <= 400


def test_case_is_the_tenth_deterministic_roster_entry():
    suite = json.loads((SUITE_DIR / "suite.json").read_text(encoding="utf-8"))
    cases = suite["cases"]
    assert len(cases) == 10
    matches = [entry for entry in cases if entry["id"] == CASE_DIR.name]
    assert len(matches) == 1
    assert matches[0]["lane"] == "deterministic"
    assert cases[-1] == matches[0]
