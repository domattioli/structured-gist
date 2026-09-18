#!/usr/bin/env python3
"""
Comprehensive pytest tests for nested-notes KG (knowledge graph) validation and rendering.
Tests spec 023 contracts: cli-contracts.md §4 (test_kg contract) + kg-schema.md.

Determinism: identical inputs → byte-identical output (SC-004).
Validation: every ERR_* has a rejecting fixture; INTERNAL_LINT_FAILURE has NO fixture (bug sentinel).
Self-lint: every rendered output passes lint_outline with zero violations (SC-003).
Granularity: skim ≤ standard ≤ deep word counts (FR-013).
Worked example: canonical.json renders byte-equal to SKILL.md ## Worked example.
Reference fences: every ```text fence in kg-mode.md lints clean.
"""

import pytest
import subprocess
import sys
import re
from pathlib import Path
from typing import List

# Import the linter and kg modules
sys.path.insert(0, str(Path(__file__).parent))
from lint_outline import lint_text

# Add scripts dir to path for kg imports
scripts_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))


# ============================================================================
# Test data fixtures
# ============================================================================

@pytest.fixture
def fixtures_dir():
    """Get the fixtures/kg directory."""
    return Path(__file__).parent / 'fixtures' / 'kg'


@pytest.fixture
def golden_dir(fixtures_dir):
    """Get the golden outputs directory."""
    return fixtures_dir / 'golden'


@pytest.fixture
def skill_md_path():
    """Get the SKILL.md file."""
    return Path(__file__).parent.parent / 'SKILL.md'


@pytest.fixture
def reference_kg_mode_path():
    """Get the reference/kg-mode.md file."""
    return Path(__file__).parent.parent / 'reference' / 'kg-mode.md'


def _get_valid_fixtures(fixtures_dir: Path) -> List[Path]:
    """Return list of all valid_*.json and canonical.json fixture files."""
    fixtures = []
    for f in fixtures_dir.glob('valid_*.json'):
        fixtures.append(f)
    canonical = fixtures_dir / 'canonical.json'
    if canonical.exists():
        fixtures.append(canonical)
    return sorted(fixtures)


def _get_bad_fixtures(fixtures_dir: Path) -> List[Path]:
    """Return list of all bad_*.json fixture files."""
    return sorted(fixtures_dir.glob('bad_*.json'))


def _extract_error_from_filename(filename: str) -> str:
    """
    Extract expected error name from filename.
    bad_rank_duplicate.json -> ERR_RANK
    bad_empty_text.json -> ERR_EMPTY_TEXT
    """
    # Remove bad_ prefix and .json suffix
    name = filename[4:-5]  # Strip 'bad_' and '.json'
    # Handle special case: bad_rank_duplicate -> ERR_RANK
    if name == 'rank_duplicate':
        return 'ERR_RANK'
    # Convert snake_case to UPPER_CASE
    return 'ERR_' + name.upper()


# ============================================================================
# Test 1: All valid fixtures validate cleanly
# ============================================================================

class TestValidFixtures:
    """Test that all valid_*.json fixtures pass validation at all stages."""

    def test_all_valid_fixtures_validate(self, fixtures_dir):
        """
        test_all_valid_fixtures_validate: every valid_*.json + canonical.json
        must pass kg_render.py --validate-only with exit 0.
        """
        valid_fixtures = _get_valid_fixtures(fixtures_dir)
        assert valid_fixtures, "No valid fixtures found"

        for fixture_path in valid_fixtures:
            result = subprocess.run(
                ['python3', str(scripts_dir / 'kg_render.py'), str(fixture_path), '--validate-only'],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, (
                f"{fixture_path.name} failed validation:\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )


# ============================================================================
# Test 2: Every error has a rejecting fixture
# ============================================================================

class TestErrorFixtures:
    """Test that every defined error has a rejecting fixture."""

    def test_every_err_has_rejecting_fixture(self, fixtures_dir):
        """
        test_every_err_has_rejecting_fixture: for each bad_*.json fixture,
        it must exit 2 and stderr must contain exactly the expected error name
        (derived from the filename).

        Special case: INTERNAL_LINT_FAILURE is a bug sentinel with NO fixture.
        We verify the fixture set covers all other ERR_* names from kg-schema.md.
        """
        # All error names from kg-schema.md (excluding INTERNAL_LINT_FAILURE, which is unreachable)
        expected_errors = {
            'ERR_SCHEMA',
            'ERR_DUPLICATE_ID',
            'ERR_DANGLING_REF',
            'ERR_UNKNOWN_NODE_TYPE',
            'ERR_EMPTY_TEXT',
            'ERR_WORD_BUDGET',
            'ERR_TEXT_STRAY_MARKER',
            'ERR_TEXT_DELIMITER_TAIL',
            'ERR_RANK',
            'ERR_UNKNOWN_EDGE_TYPE',
            'ERR_ATTR_UNDER_ATTR',
            'ERR_CONCEPT_DEPTH',
            'ERR_EDGE_TYPE_MISMATCH',
            'ERR_MULTIPLE_PARENTS',
            'ERR_CYCLE',
            'ERR_NO_ROOT',
            'ERR_ORPHAN',
            'ERR_MIXED_PART_ORDER',
            'ERR_MIXED_CHILD_ROLE',
            'ERR_MULTIPLE_SUMMARIES',
            'ERR_ARROW_RARITY',
            'ERR_PART_DEPTH',
            'ERR_RENDER_OVERFLOW',
        }

        bad_fixtures = _get_bad_fixtures(fixtures_dir)
        assert bad_fixtures, "No bad fixtures found"

        # Test each bad fixture
        fixture_errors = set()
        for fixture_path in bad_fixtures:
            expected_error = _extract_error_from_filename(fixture_path.name)
            fixture_errors.add(expected_error)

            result = subprocess.run(
                ['python3', str(scripts_dir / 'kg_render.py'), str(fixture_path), '--validate-only'],
                capture_output=True,
                text=True
            )

            # Should exit with 2 (rejection)
            assert result.returncode == 2, (
                f"{fixture_path.name} should reject with exit 2, got {result.returncode}\n"
                f"stderr: {result.stderr}"
            )

            # stderr should contain KG-REJECT <ERROR_NAME>
            assert 'KG-REJECT' in result.stderr, (
                f"{fixture_path.name} stderr missing 'KG-REJECT': {result.stderr}"
            )
            assert expected_error in result.stderr, (
                f"{fixture_path.name} should reject with {expected_error}, "
                f"got: {result.stderr}"
            )

        # Verify fixture set covers all expected errors
        # (INTERNAL_LINT_FAILURE explicitly excluded as per contract)
        assert fixture_errors == expected_errors, (
            f"Fixture set incomplete:\n"
            f"Missing: {expected_errors - fixture_errors}\n"
            f"Extra: {fixture_errors - expected_errors}"
        )


# ============================================================================
# Test 3: Golden byte-equality
# ============================================================================

class TestGoldenByteEquality:
    """Test that rendered output matches golden files byte-for-byte."""

    def test_golden_byte_equality(self, fixtures_dir, golden_dir):
        """
        test_golden_byte_equality: for each valid fixture × 3 levels,
        the rendered output must byte-equal the golden/<name>.<level>.md file.
        """
        valid_fixtures = _get_valid_fixtures(fixtures_dir)

        for fixture_path in valid_fixtures:
            fixture_name = fixture_path.stem  # Remove .json

            for level in ['skim', 'standard', 'deep']:
                golden_path = golden_dir / f"{fixture_name}.{level}.md"

                # Render at this level
                result = subprocess.run(
                    ['python3', str(scripts_dir / 'kg_render.py'),
                     str(fixture_path), '--level', level],
                    capture_output=True,
                    text=True
                )

                assert result.returncode == 0, (
                    f"{fixture_name} render at {level} failed:\n"
                    f"stderr: {result.stderr}"
                )

                rendered_output = result.stdout

                # Compare with golden
                assert golden_path.exists(), f"Golden file not found: {golden_path}"

                with open(golden_path, 'r', encoding='utf-8') as f:
                    golden_content = f.read()

                assert rendered_output == golden_content, (
                    f"{fixture_name}.{level} output differs from golden:\n"
                    f"Expected length: {len(golden_content)}, got: {len(rendered_output)}\n"
                    f"First diff at char: {next((i for i, (a, b) in enumerate(zip(golden_content, rendered_output)) if a != b), 'end')}\n"
                    f"Expected:\n{repr(golden_content[:200])}\n"
                    f"Got:\n{repr(rendered_output[:200])}"
                )


# ============================================================================
# Test 4: Rendered output is lint-clean
# ============================================================================

class TestLintClean:
    """Test that all rendered outputs pass linting."""

    def test_lint_clean_by_construction(self, fixtures_dir, golden_dir):
        """
        test_lint_clean_by_construction: every rendered output (all valid fixtures × 3 levels)
        must pass lint_outline.lint_text with zero violations.
        """
        valid_fixtures = _get_valid_fixtures(fixtures_dir)

        for fixture_path in valid_fixtures:
            fixture_name = fixture_path.stem

            for level in ['skim', 'standard', 'deep']:
                golden_path = golden_dir / f"{fixture_name}.{level}.md"
                assert golden_path.exists(), f"Golden file not found: {golden_path}"

                with open(golden_path, 'r', encoding='utf-8') as f:
                    rendered_output = f.read()

                violations = lint_text(rendered_output)
                assert not violations, (
                    f"{fixture_name}.{level} has lint violations:\n"
                    f"{violations}"
                )


# ============================================================================
# Test 5: Word count monotonicity
# ============================================================================

class TestWordcountMonotonicity:
    """Test that word counts are monotone: skim ≤ standard ≤ deep."""

    def test_wordcount_monotonicity(self, fixtures_dir, golden_dir):
        """
        test_wordcount_monotonicity: for each fixture, word count at skim level
        must be ≤ standard level, and standard ≤ deep level.
        """
        valid_fixtures = _get_valid_fixtures(fixtures_dir)

        for fixture_path in valid_fixtures:
            fixture_name = fixture_path.stem

            word_counts = {}
            for level in ['skim', 'standard', 'deep']:
                golden_path = golden_dir / f"{fixture_name}.{level}.md"
                assert golden_path.exists()

                with open(golden_path, 'r', encoding='utf-8') as f:
                    rendered_output = f.read()

                # Count words in the outline (excluding fence markers)
                lines = rendered_output.split('\n')
                outline_lines = [l for l in lines if l.strip() and not l.strip().startswith('```')]
                text = ' '.join(outline_lines)
                word_count = len(text.split())
                word_counts[level] = word_count

            # Check monotonicity
            assert word_counts['skim'] <= word_counts['standard'], (
                f"{fixture_name}: skim words ({word_counts['skim']}) > standard ({word_counts['standard']})"
            )
            assert word_counts['standard'] <= word_counts['deep'], (
                f"{fixture_name}: standard words ({word_counts['standard']}) > deep ({word_counts['deep']})"
            )


# ============================================================================
# Test 6: Canonical matches SKILL.md worked example
# ============================================================================

class TestCanonicalSkillMd:
    """Test canonical graph renders to match SKILL.md worked example."""

    def test_canonical_matches_skillmd_worked_example(self, fixtures_dir, skill_md_path):
        """
        test_canonical_matches_skillmd_worked_example: render canonical.json
        at standard level; extract the fence immediately following
        '## Worked example' in SKILL.md; compare contents WITHOUT fence delimiters.
        """
        canonical_path = fixtures_dir / 'canonical.json'
        assert canonical_path.exists(), "canonical.json not found"

        # Render canonical at standard level
        result = subprocess.run(
            ['python3', str(scripts_dir / 'kg_render.py'),
             str(canonical_path), '--level', 'standard'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Failed to render canonical: {result.stderr}"
        rendered = result.stdout

        # Extract the worked example from SKILL.md
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            skill_content = f.read()

        # Find '## Worked example'
        worked_example_match = re.search(
            r'## Worked example\n+(.*?)(?=\n##|\Z)',
            skill_content,
            re.DOTALL
        )
        assert worked_example_match, "## Worked example section not found in SKILL.md"

        worked_example_section = worked_example_match.group(1)

        # Extract the fence from this section
        fence_match = re.search(
            r'```text\n(.*?)\n```',
            worked_example_section,
            re.DOTALL
        )
        assert fence_match, "Fence not found in ## Worked example section"

        skillmd_content = fence_match.group(1)

        # Compare: strip fence delimiters from rendered output
        # Extract content between ``` markers
        rendered_match = re.search(r'```text\n(.*?)\n```', rendered, re.DOTALL)
        assert rendered_match, "Rendered output missing fence markers"
        rendered_content = rendered_match.group(1)

        assert rendered_content == skillmd_content, (
            f"Canonical render does not match SKILL.md worked example:\n"
            f"Rendered:\n{repr(rendered_content[:200])}\n"
            f"Expected:\n{repr(skillmd_content[:200])}"
        )


# ============================================================================
# Test 7: Double render byte stability
# ============================================================================

class TestDoubleRenderStable:
    """Test that rendering the same graph twice produces identical output."""

    def test_double_render_byte_stable(self, fixtures_dir):
        """
        test_double_render_byte_stable: render canonical.json twice at standard level,
        output must be byte-identical both times.
        """
        canonical_path = fixtures_dir / 'canonical.json'
        assert canonical_path.exists()

        outputs = []
        for _ in range(2):
            result = subprocess.run(
                ['python3', str(scripts_dir / 'kg_render.py'),
                 str(canonical_path), '--level', 'standard'],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            outputs.append(result.stdout)

        assert outputs[0] == outputs[1], (
            "Double render produced different outputs (SC-004 violated)"
        )


# ============================================================================
# Test 8: Reference kg-mode.md fences are lint-clean
# ============================================================================

class TestReferenceFences:
    """Test that all ```text fences in reference/kg-mode.md are lint-clean."""

    def test_kg_mode_reference_fences(self, reference_kg_mode_path):
        """
        test_kg_mode_reference_fences: extract every ```text fence in
        reference/kg-mode.md; each must lint cleanly via lint_outline.lint_text.
        (If there are no ```text fences, the test passes vacuously — every
        (zero) fence lints cleanly.)
        Also verify SKILL.md contains no language-tagged fences
        (every fence opener is ``` or ```text).
        """
        with open(reference_kg_mode_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract all ```text fences
        # Pattern: ```text\n...\n```
        pattern = r'```text\n(.*?)\n```'
        fences = re.findall(pattern, content, re.DOTALL)

        # Test each fence (if any exist; vacuously true if none)
        for fence_index, fence_content in enumerate(fences):
            # Each fence is an outline and must lint cleanly
            violations = lint_text(fence_content)
            assert not violations, (
                f"Fence {fence_index} in kg-mode.md has lint violations:\n"
                f"{violations}\n"
                f"Content:\n{fence_content[:200]}"
            )

    def test_skillmd_no_language_tags(self, skill_md_path):
        """
        Verify SKILL.md contains no language-tagged code fences.
        Every fence is either ``` or ```text (both representing outlines).
        """
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find any fenced blocks with language tags other than 'text'
        # Pattern: ```[language] where language is not empty and not 'text'
        bad_fence_pattern = r'```[a-z]+(?!text)'
        re.findall(bad_fence_pattern, content)

        # Also check for explicit language tags that aren't plain ``` or ```text
        explicit_pattern = r'^```(\w+)$'
        for line in content.split('\n'):
            match = re.match(explicit_pattern, line)
            if match and match.group(1) and match.group(1) != 'text':
                pytest.fail(
                    f"SKILL.md contains language-tagged fence: {line}\n"
                    f"All fences must be ``` or ```text"
                )


# ============================================================================
# Helper to ensure scripts_dir is available
# ============================================================================

scripts_dir = Path(__file__).parent.parent / 'scripts'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
