#!/usr/bin/env python3
"""
Migration script to add epistemic category support and attaches_to field to gold.json files.

This script:
1. Scans each fact's source_quote for hedge/qualifier language
2. Marks facts with hedge language as "epistemic" category (weight 3)
3. Adds optional "attaches_to" field support (for referencing other facts)
4. Is idempotent (safe to run multiple times)
5. Logs changes and flags ambiguous cases
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set

# Hedge/qualifier language patterns
HEDGE_PATTERNS = [
    r'\blikely\b',
    r'\bpossibly\b',
    r'\bunconfirmed\b',
    r'\bprobably\b',
    r'\bmay\b',
    r'\bmight\b',
    r'\bcould\b',
    r'\bappears\b',
    r'\bappears to\b',
    r'\bseems\b',
    r'\bseems to\b',
    r'\bsuggest\b',
    r'\bindicates\b',
    r'\bhints\b',
    r'\bsuspected\b',
    r'\bbelieved\b',
    r'\ballege\b',
    r'\bresembles\b',
    r'\blooks like\b',
    r'\bapparently\b',
    r'\bpresumably\b',
]

HEDGE_REGEX = re.compile('|'.join(HEDGE_PATTERNS), re.IGNORECASE)

# Categories that are too specific to overwrite with epistemic
SPECIFIC_CATEGORIES = {
    'outcome', 'cause_rationale', 'negation', 'failure', 'decision',
    'unresolved_question', 'comparative_outcome'
}

# Categories that are generic enough to convert to epistemic
GENERIC_CATEGORIES = {'descriptive'}


def contains_hedge(text: str) -> bool:
    """Check if text contains hedge/qualifier language."""
    return bool(HEDGE_REGEX.search(text))


def migrate_fact(fact: Dict, file_path: str, fact_id: str) -> tuple[bool, str]:
    """
    Migrate a single fact.
    Returns (changed, log_message)
    """
    changes = []
    source_quote = fact.get('source_quote', '')
    current_category = fact.get('category', '')

    # Check for hedge language in source_quote
    if contains_hedge(source_quote):
        # Already has epistemic? Skip.
        if current_category == 'epistemic':
            return False, None

        # If it's a generic category, convert to epistemic
        if current_category in GENERIC_CATEGORIES:
            fact['category'] = 'epistemic'
            fact['weight'] = 3
            changes.append(f"converted '{current_category}' → 'epistemic'")

        # If it's a specific category, flag as candidate
        elif current_category in SPECIFIC_CATEGORIES:
            if 'epistemic_candidate' not in fact:
                fact['epistemic_candidate'] = True
                changes.append(f"flagged as epistemic_candidate (current: '{current_category}')")

        # If no category, set to epistemic
        elif not current_category:
            fact['category'] = 'epistemic'
            fact['weight'] = 3
            changes.append("set category to 'epistemic' (was empty)")

    # Ensure attaches_to field is schema-legal (optional, may not be populated)
    # This is a no-op for migration, but documents that the field is supported
    if 'attaches_to' not in fact and contains_hedge(source_quote):
        # We could demonstrate setting attaches_to for obvious dependencies,
        # but the task says "should NOT need to populate this for every fact"
        # so we'll just ensure the field CAN be present
        pass

    if changes:
        log_msg = f"{file_path} :: {fact_id}: {', '.join(changes)}"
        return True, log_msg
    return False, None


def migrate_gold_json(file_path: str) -> tuple[bool, List[str]]:
    """
    Migrate a single gold.json file.
    Returns (changed, list of log messages)
    """
    with open(file_path, 'r') as f:
        data = json.load(f)

    logs = []
    changed = False

    # Migrate facts
    if 'facts' in data:
        for fact in data['facts']:
            fact_id = fact.get('id', 'unknown')
            fact_changed, log_msg = migrate_fact(fact, Path(file_path).name, fact_id)
            if fact_changed:
                changed = True
                if log_msg:
                    logs.append(log_msg)

    # Validate attaches_to references (optional check during migration)
    if 'facts' in data:
        fact_ids: Set[str] = {fact.get('id') for fact in data['facts'] if fact.get('id')}
        for fact in data['facts']:
            if 'attaches_to' in fact:
                target_id = fact.get('attaches_to')
                if target_id not in fact_ids:
                    logs.append(
                        f"{Path(file_path).name} :: {fact.get('id')}: "
                        f"WARNING: attaches_to '{target_id}' does not exist"
                    )

    # Write back only if changed
    if changed:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logs.insert(0, f"✓ {Path(file_path).name}")

    return changed, logs


def main():
    """Migrate all gold.json files under regression/ and pressure-tests/."""
    repo_root = Path(__file__).parent.parent  # benchmarks/semantic-compression/

    target_dirs = [
        repo_root / 'regression',
        repo_root / 'pressure-tests',
    ]

    all_logs = []
    file_count = 0
    changed_count = 0

    for target_dir in target_dirs:
        if not target_dir.exists():
            print(f"Skipping non-existent directory: {target_dir}")
            continue

        # Find all gold.json files (skip registrar-hedge which has none)
        for gold_file in sorted(target_dir.glob('*/gold.json')):
            file_count += 1
            changed, logs = migrate_gold_json(str(gold_file))
            if changed:
                changed_count += 1
            all_logs.extend(logs)

    # Print summary
    print(f"\n{'='*70}")
    print(f"Migration Summary: {changed_count}/{file_count} files changed")
    print(f"{'='*70}\n")

    for log in all_logs:
        print(log)

    if changed_count > 0:
        print(f"\n{'='*70}")
        print(f"✓ Migration complete. {changed_count} file(s) updated.")
        print(f"{'='*70}")
    else:
        print("\nNo changes needed.")


if __name__ == '__main__':
    main()
