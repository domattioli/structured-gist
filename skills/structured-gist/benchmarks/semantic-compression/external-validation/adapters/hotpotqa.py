#!/usr/bin/env python3
"""Thin HotpotQA-specific adapter surface. All scoring/validation logic
lives in common.py; this module only names the dataset and its
native-evidence-id scheme (`{title}::sent{sent_id}`, see
ADAPTER_DESIGN.md). Every case here is pressure_only -- see
../hotpotqa/cases/*/external_gold.json's native_metadata."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402

DATASET = "hotpotqa"


def load_case(case_id: str) -> dict:
    return {
        "native_gold": common.load_native_gold(DATASET, case_id),
        "derived_gold": common.load_derived_gold(DATASET, case_id),
        "blind_weights": common.load_blind_weights(DATASET, case_id),
        "provenance": common.load_native_provenance(DATASET, case_id),
    }


def native_evidence_ids(native_gold: dict) -> set[str]:
    return common.hotpotqa_native_evidence_ids(native_gold)
