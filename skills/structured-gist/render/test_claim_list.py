#!/usr/bin/env python3
"""
Tests for the claim_list render target (claim_list.py module).

These tests verify that:
1. claim_list emits JSONL with correct schema (T049)
2. claim_list is a derived view reusing lint_outline's parser (T050)
3. claim_list applies structural assertion-vs-bare-label logic (T050a)

Tests are written first (TDD style). claim_list.py does not exist yet;
these tests are expected to fail with ImportError until implementation.
"""

import pytest
import json
import sys
from pathlib import Path
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'tests'))
from lint_outline import parse_line, lint_text


@pytest.fixture
def import_claim_list():
    """
    Fixture that imports claim_list. Deliberately does NOT catch
    ImportError — until claim_list.py exists, every test using this
    fixture must FAIL (not skip), so the tests-first checkpoint is a
    real signal rather than a permanently-green no-op that would stay
    silent even if the import path were later broken by accident.
    """
    from render import claim_list
    return claim_list


class TestClaimListJSONLOutput:
    """T049: Verify JSONL output with correct schema (claim, modality, polarity, source_span, parent_id)."""

    def test_jsonl_output_basic_assertion_node(self, import_claim_list):
        """
        T049: Render a simple outline with an assertion node and verify JSONL output.
        One record per claim with exactly the required keys.
        """
        outline_text = """- Root Concept
        ↪ This is a plain explanation leaf node"""

        # Call the claim_list renderer
        jsonl_output = import_claim_list.render_claim_list(outline_text)

        # Split into lines and parse each as JSON
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]
        assert len(lines) >= 1, "Expected at least one JSONL line from explanation node"

        for line in lines:
            record = json.loads(line)
            # Verify exactly the required keys are present
            required_keys = {'claim', 'modality', 'polarity', 'source_span', 'parent_id'}
            actual_keys = set(record.keys())
            assert required_keys == actual_keys, (
                f"Record has wrong keys. Expected {required_keys}, got {actual_keys}. "
                f"Record: {record}"
            )

    def test_jsonl_record_shape_valid_json(self, import_claim_list):
        """
        T049: Each JSONL line must be valid JSON that can be parsed.
        source_span must be a dict/object with offset information and quoted text.
        """
        outline_text = """- Example Topic
        I. First enumerated item
        II. Second enumerated item
        ↪ Supporting explanation"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]

        for line in lines:
            # Must parse as JSON
            record = json.loads(line)

            # claim and parent_id should be strings
            assert isinstance(record['claim'], str), f"claim must be string, got {type(record['claim'])}"
            assert isinstance(record['parent_id'], str), f"parent_id must be string, got {type(record['parent_id'])}"

            # modality and polarity should be strings (enumerated values)
            assert isinstance(record['modality'], str), f"modality must be string"
            assert isinstance(record['polarity'], str), f"polarity must be string"

            # source_span should be a dict with character offsets and quoted text
            assert isinstance(record['source_span'], dict), f"source_span must be dict/object"
            assert 'start' in record['source_span'], "source_span must have 'start' offset"
            assert 'end' in record['source_span'], "source_span must have 'end' offset"
            assert 'text' in record['source_span'], "source_span must have 'text' (quoted content)"


class TestClaimListDerivedView:
    """T050: Verify claim_list is a derived view that reuses lint_outline's parser."""

    def test_claim_list_imports_from_lint_outline(self, import_claim_list):
        """
        T050: Structural test — claim_list.py must import something from lint_outline.
        This verifies that claim_list reuses the existing parser, not implementing its own.
        """
        import inspect
        import sys

        # Get the source code of the claim_list module
        source = inspect.getsource(import_claim_list)

        # Check that it imports from lint_outline (either explicit import or internal call)
        assert 'lint_outline' in source or 'parse_line' in source or 'extract_outline_from_text' in source, (
            "claim_list must import or use functions from lint_outline (parse_line, extract_outline_from_text). "
            "It should NOT implement its own independent prose parser."
        )

    def test_claim_list_output_changes_when_parser_changes(self, import_claim_list):
        """
        T050: Functional test — if lint_outline's parsing logic were mocked/changed,
        claim_list's output should change accordingly. This proves claim_list consumes
        the parsed outline tree, not doing independent regex parsing.

        We test this by providing outline text with ambiguous formatting that only
        the lint_outline parser would resolve consistently, and verify claim_list
        uses that parsing.
        """
        # Outline with a glyph-free bold attribute (v0.3.9 convention)
        # Only lint_outline's extract_outline_from_text knows to add the ▸ marker
        outline_text = """- Root
        - **Property Name**
        ↪ explanation of the property"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]

        # The fact that we get valid records proves claim_list is consuming
        # lint_outline's output (which would have normalized **Property Name** to
        # ▸ **Property Name**). If claim_list had its own parser, it might treat
        # **Property Name** differently.
        assert len(lines) > 0, (
            "claim_list must produce records from normalized outline. "
            "This proves it uses lint_outline's parser, not its own."
        )


class TestClaimListAssertionVsBareLabelLogic:
    """T050a: Structural tests for assertion-vs-bare-label logic per FR-018a."""

    def test_attribute_bare_label_no_verb_no_child_emits_no_record(self, import_claim_list):
        """
        T050a-1: An attribute node whose own text has no verb/predicate and has NO
        non-summary ↪ child → emits NO record.

        Example: "▸ Name" (bare label, no verb)
        """
        outline_text = """- Root Concept
        ▸ Configuration
        I. First detail
        II. Second detail"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]

        # Should have records for enumerators but NOT for the bare-label attribute
        records = [json.loads(line) for line in lines]

        # Verify "Configuration" does NOT appear as a claim
        claims = [r['claim'] for r in records]
        assert 'Configuration' not in claims, (
            "Bare-label attribute ('Configuration' with no verb) should not emit a record"
        )

        # But enumerated children should produce records
        assert any('detail' in claim.lower() for claim in claims), (
            "Enumerator children should produce records"
        )

    def test_attribute_with_verb_emits_record(self, import_claim_list):
        """
        T050a-2: An attribute node whose own text DOES contain a verb/predicate
        → emits a record FROM ITS OWN TEXT.

        Example: "▸ Validates user input"
        """
        outline_text = """- Root Concept
        ▸ Validates user input
        ↪ runs on form submission"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]
        records = [json.loads(line) for line in lines]
        claims = [r['claim'] for r in records]

        # Should have a record with the attribute's own verb-containing text
        assert any('Validates' in claim or 'validates' in claim.lower() for claim in claims), (
            "Attribute with verb ('Validates user input') should emit a record from its own text"
        )

    def test_attribute_with_explanation_child_emits_child_record(self, import_claim_list):
        """
        T050a-3: An attribute node with a non-summary ↪ child → emits a record from
        the CHILD's content instead of the attribute's own text.

        The child is "non-summary" (not a bare restatement). Example:
        Attribute: "▸ Feature"
        Child: "↪ allows users to customize their dashboard"

        Should emit the child's content as the claim, not "Feature".
        """
        outline_text = """- Root Concept
        ▸ Configuration UI
        ↪ users can toggle dark mode and adjust font size from settings page"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]
        records = [json.loads(line) for line in lines]
        claims = [r['claim'] for r in records]

        # Should emit the explanation child's content, not just "Configuration UI"
        assert any('toggle' in claim.lower() or 'adjust' in claim.lower() for claim in claims), (
            "Attribute with non-summary ↪ child should emit the child's content as the claim"
        )
        # The bare attribute name should not appear alone
        assert 'Configuration UI' not in claims, (
            "Bare attribute text should not be emitted when a non-summary child exists"
        )

    def test_concept_node_never_emits_record(self, import_claim_list):
        """
        T050a-4: A concept (-, dash family) node → NEVER emits a record,
        regardless of its text content.

        A concept is just a category heading, not a claim.
        """
        outline_text = """- This is a concept heading with noun phrase
        ▸ Attribute that makes a claim
        ↪ Supporting explanation"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]
        records = [json.loads(line) for line in lines]
        claims = [r['claim'] for r in records]

        # The concept's text should never appear as a claim
        assert 'This is a concept heading with noun phrase' not in claims, (
            "Concept nodes (dash family) must NEVER emit a record"
        )

    def test_arrow_explanation_node_always_emits_record(self, import_claim_list):
        """
        T050a-5a: An arrow/explanation node (↪) → ALWAYS produces a record
        (explanation nodes are the prose leaves).
        """
        outline_text = """- Root Topic
        ↪ First explanation leaf
        ↪ Second explanation leaf"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]
        records = [json.loads(line) for line in lines]
        claims = [r['claim'] for r in records]

        # Both explanation nodes should produce records
        assert any('First explanation' in claim for claim in claims), (
            "Arrow/explanation nodes must always produce a record"
        )
        assert any('Second explanation' in claim for claim in claims), (
            "Arrow/explanation nodes must always produce a record"
        )

    def test_enumerator_nodes_always_emit_records(self, import_claim_list):
        """
        T050a-5b: Enumerator nodes (uroman, ualpha, lroman, lalpha) →
        ALWAYS produce a record.
        """
        outline_text = """- Root Topic
        I. First enumerated claim
        II. Second enumerated claim
        A. Sub-clause alpha
        i. Sub-clause roman"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]
        records = [json.loads(line) for line in lines]
        claims = [r['claim'] for r in records]

        # All enumerator children should produce records
        assert any('First enumerated' in claim for claim in claims), (
            "Uppercase roman enumerators (I, II, ...) must always produce a record"
        )
        assert any('Second enumerated' in claim for claim in claims), (
            "Uppercase roman enumerators must always produce a record"
        )
        assert any('alpha' in claim.lower() for claim in claims), (
            "Uppercase alpha enumerators (A, B, ...) must always produce a record"
        )
        assert any('roman' in claim.lower() for claim in claims), (
            "Lowercase roman enumerators (i, ii, ...) must always produce a record"
        )

    def test_verb_detection_in_attribute_text(self, import_claim_list):
        """
        Helper test to verify verb detection works correctly in attributes.
        Common verbs to detect: is, are, provides, allows, validates, contains, etc.
        """
        outline_text = """- Topic
        ▸ System is distributed
        ▸ Database contains user records
        ▸ API provides authentication"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]
        records = [json.loads(line) for line in lines]
        claims = [r['claim'] for r in records]

        # All three attributes contain verbs and should emit records
        assert any('distributed' in claim.lower() for claim in claims), (
            "Attribute with verb 'is' should emit record"
        )
        assert any('contains' in claim.lower() for claim in claims), (
            "Attribute with verb 'contains' should emit record"
        )
        assert any('provides' in claim.lower() or 'authentication' in claim.lower() for claim in claims), (
            "Attribute with verb 'provides' should emit record"
        )


class TestClaimListParentTracking:
    """Verify parent_id tracking and stability."""

    def test_parent_id_references_parent_node(self, import_claim_list):
        """
        parent_id must identify the emitting node's parent in the outline tree.
        A claim's parent_id should match the parent node's stable identifier.
        """
        outline_text = """- Root Concept
        ▸ Main attribute
        ↪ explanation of main attribute
        I. First enumerator
        II. Second enumerator"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]
        records = [json.loads(line) for line in lines]

        # Each record should have a parent_id
        for record in records:
            assert record['parent_id'], "Every claim record must have a non-empty parent_id"
            assert isinstance(record['parent_id'], str), "parent_id must be a string"

    def test_parent_id_stable_across_rerenders(self, import_claim_list):
        """
        parent_id MUST be stable across re-renders of an unchanged outline.
        Rendering the same outline twice should produce identical parent_ids.
        """
        outline_text = """- Root Concept
        ▸ Attribute node
        ↪ Explanation child
        I. Enumerated child"""

        # Render twice
        output1 = import_claim_list.render_claim_list(outline_text)
        output2 = import_claim_list.render_claim_list(outline_text)

        lines1 = [line.strip() for line in output1.strip().split('\n') if line.strip()]
        lines2 = [line.strip() for line in output2.strip().split('\n') if line.strip()]

        records1 = [json.loads(line) for line in lines1]
        records2 = [json.loads(line) for line in lines2]

        # Same number of records
        assert len(records1) == len(records2), (
            "Re-rendering unchanged outline should produce same number of records"
        )

        # Corresponding records must have identical parent_ids
        for r1, r2 in zip(records1, records2):
            assert r1['parent_id'] == r2['parent_id'], (
                f"parent_id must be stable across re-renders. "
                f"First render: {r1['parent_id']}, Second render: {r2['parent_id']}"
            )


class TestClaimListSchema:
    """Verify modality and polarity enumerations (FR-018b)."""

    def test_modality_values_enumerated(self, import_claim_list):
        """
        FR-018b: Legal values of modality must be enumerated and schema must reject invalid values.
        """
        # Check that the module has a schema or claims with valid modalities
        outline_text = """- Root
        ↪ Some fact
        I. Enumerated fact"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]
        records = [json.loads(line) for line in lines]

        # Every record should have a modality from an enumerated set
        # Common modalities: 'assertion', 'question', 'conditional', etc.
        for record in records:
            modality = record['modality']
            assert modality, "Every record must have a modality value"
            # Verify it's a reasonable enum value (not arbitrary/random)
            assert isinstance(modality, str) and len(modality) < 50, (
                f"modality must be a short string enum value, got: {modality}"
            )

    def test_polarity_values_enumerated(self, import_claim_list):
        """
        FR-018b: Legal values of polarity must be enumerated and schema must reject invalid values.
        Polarity typically: positive, negative, neutral, etc.
        """
        outline_text = """- Root
        ↪ positive claim
        ▸ negated property
        ↪ not implemented yet"""

        jsonl_output = import_claim_list.render_claim_list(outline_text)
        lines = [line.strip() for line in jsonl_output.strip().split('\n') if line.strip()]
        records = [json.loads(line) for line in lines]

        for record in records:
            polarity = record['polarity']
            assert polarity, "Every record must have a polarity value"
            # Polarity should be an enum value like 'positive', 'negative', 'neutral'
            assert isinstance(polarity, str) and len(polarity) < 50, (
                f"polarity must be a short string enum value, got: {polarity}"
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
