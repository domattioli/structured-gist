#!/usr/bin/env python3
"""
Deterministic pytest tests for the structured-gist linter.
Tests that real examples pass and bad fixtures fail.
"""

import pytest
from pathlib import Path
import re

# Import the linter
import sys
sys.path.insert(0, str(Path(__file__).parent))
from lint_outline import lint_file, lint_text


def _lint_all_blocks(path):
    """
    Read a file and lint EVERY fenced code block in it.
    Returns a dict {block_index: violations}, where block_index is 0-based.
    """
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract all fenced blocks using regex pattern: ```[text]\n...\n```
    pattern = r'```(?:text)?\n(.*?)\n```'
    blocks = re.findall(pattern, text, re.DOTALL)

    results = {}
    for block_index, block_body in enumerate(blocks):
        violations = lint_text(block_body)
        results[block_index] = violations

    return results


class TestRealExamples:
    """Test that the real structured-gist examples pass linting."""

    @pytest.fixture
    def examples_dir(self):
        """Get the examples directory."""
        return Path(__file__).parent.parent / 'examples'

    def test_skim_example_passes(self, examples_dir):
        """Test that skim.md lints cleanly."""
        skim_file = examples_dir / 'skim.md'
        assert skim_file.exists(), f"skim.md not found at {skim_file}"
        violations = lint_file(str(skim_file))
        assert not violations, f"skim.md has violations: {violations}"

    def test_standard_example_passes(self, examples_dir):
        """Test that standard.md lints cleanly."""
        standard_file = examples_dir / 'standard.md'
        assert standard_file.exists(), f"standard.md not found at {standard_file}"
        violations = lint_file(str(standard_file))
        assert not violations, f"standard.md has violations: {violations}"

    def test_deep_example_passes(self, examples_dir):
        """Test that deep.md lints cleanly."""
        deep_file = examples_dir / 'deep.md'
        assert deep_file.exists(), f"deep.md not found at {deep_file}"
        violations = lint_file(str(deep_file))
        assert not violations, f"deep.md has violations: {violations}"

    def test_caveman_combo_example_passes(self, examples_dir):
        """Test that caveman-combo.md lints cleanly."""
        caveman_file = examples_dir / 'caveman-combo.md'
        assert caveman_file.exists(), f"caveman-combo.md not found at {caveman_file}"
        violations = lint_file(str(caveman_file))
        assert not violations, f"caveman-combo.md has violations: {violations}"

    def test_self_explain_example_passes(self, examples_dir):
        """Test that self-explain.md lints cleanly."""
        self_explain_file = examples_dir / 'self-explain.md'
        assert self_explain_file.exists(), f"self-explain.md not found at {self_explain_file}"
        violations = lint_file(str(self_explain_file))
        assert not violations, f"self-explain.md has violations: {violations}"


class TestBadFixtures:
    """Test that bad fixtures are caught by the linter."""

    @pytest.fixture
    def fixtures_dir(self):
        """Get the fixtures directory."""
        return Path(__file__).parent / 'fixtures'

    def test_bad_ladder_caught(self, fixtures_dir):
        """Test that bad_ladder.md is caught (R1 violation)."""
        bad_file = fixtures_dir / 'bad_ladder.md'
        assert bad_file.exists(), f"bad_ladder.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_ladder.md should have violations"
        # Check that at least one violation matches R1
        rule_ids = [v[1] for v in violations]
        assert 'R1' in rule_ids, f"Expected R1 violation, got: {violations}"

    def test_bad_bullet_caught(self, fixtures_dir):
        """Test that bad_bullet.md is caught (R1 violation)."""
        bad_file = fixtures_dir / 'bad_bullet.md'
        assert bad_file.exists(), f"bad_bullet.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_bullet.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R1' in rule_ids, f"Expected R1 violation, got: {violations}"

    def test_good_attribute_passes(self, fixtures_dir):
        """Test that good_attribute.md with attribute children lints cleanly."""
        good_file = fixtures_dir / 'good_attribute.md'
        assert good_file.exists(), f"good_attribute.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_attribute.md has violations: {violations}"

    def test_good_nonleaf_arrow_passes(self, fixtures_dir):
        """Test that good_nonleaf_arrow.md with non-leaf arrow as first child lints cleanly."""
        good_file = fixtures_dir / 'good_nonleaf_arrow.md'
        assert good_file.exists(), f"good_nonleaf_arrow.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_nonleaf_arrow.md has violations: {violations}"

    def test_bad_mixed_siblings_caught(self, fixtures_dir):
        """Test that bad_mixed_siblings.md is caught (R6 violation)."""
        bad_file = fixtures_dir / 'bad_mixed_siblings.md'
        assert bad_file.exists(), f"bad_mixed_siblings.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_mixed_siblings.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R6' in rule_ids, f"Expected R6 violation, got: {violations}"

    def test_bad_wordy_top_caught(self, fixtures_dir):
        """Test that bad_wordy_top.md is caught (R7 violation)."""
        bad_file = fixtures_dir / 'bad_wordy_top.md'
        assert bad_file.exists(), f"bad_wordy_top.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_wordy_top.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R7' in rule_ids, f"Expected R7 violation, got: {violations}"

    def test_good_wrapped_continuation_passes(self, fixtures_dir):
        """Test that good_wrapped_continuation.md with hand-wrapped leaves lints cleanly."""
        good_file = fixtures_dir / 'good_wrapped_continuation.md'
        assert good_file.exists(), f"good_wrapped_continuation.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_wrapped_continuation.md has violations: {violations}"

    def test_bad_attr_self_nest_caught(self, fixtures_dir):
        """Test that bad_attr_self_nest.md is caught (R8 violation)."""
        bad_file = fixtures_dir / 'bad_attr_self_nest.md'
        assert bad_file.exists(), f"bad_attr_self_nest.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_attr_self_nest.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R8' in rule_ids, f"Expected R8 violation, got: {violations}"

    def test_bad_nonleaf_arrow_not_first_caught(self, fixtures_dir):
        """Test that bad_nonleaf_arrow_not_first.md is caught (R4 violation)."""
        bad_file = fixtures_dir / 'bad_nonleaf_arrow_not_first.md'
        assert bad_file.exists(), f"bad_nonleaf_arrow_not_first.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_nonleaf_arrow_not_first.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R4' in rule_ids, f"Expected R4 violation, got: {violations}"

    def test_good_r9_passes(self, fixtures_dir):
        """Short delimiter tails (≤2 words) must lint clean."""
        good_file = fixtures_dir / 'good_r9.md'
        assert good_file.exists(), f"good_r9.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_r9.md has violations: {violations}"

    def test_bad_r9_caught(self, fixtures_dir):
        """A >2-word delimiter tail must be caught as R9."""
        bad_file = fixtures_dir / 'bad_r9.md'
        assert bad_file.exists(), f"bad_r9.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        rule_ids = [v[1] for v in violations]
        assert 'R9' in rule_ids, f"Expected R9 violation, got: {violations}"

    def test_bad_r9_arrow_chain_caught(self, fixtures_dir):
        """The chained-arrow/semicolon splice must be caught as R9."""
        bad_file = fixtures_dir / 'bad_r9_arrow_chain.md'
        assert bad_file.exists(), f"bad_r9_arrow_chain.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        rule_ids = [v[1] for v in violations]
        assert 'R9' in rule_ids, f"Expected R9 violation, got: {violations}"

    def test_good_r9_arrow_chain_passes(self, fixtures_dir):
        """The splice re-rendered as a subtree must lint clean."""
        good_file = fixtures_dir / 'good_r9_arrow_chain.md'
        assert good_file.exists(), f"good_r9_arrow_chain.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_r9_arrow_chain.md has violations: {violations}"

    def test_splice_to_subtree_after_blocks_clean(self):
        """Golden example: every AFTER block lints clean, every BEFORE flags R9."""
        import re
        ex = (
            Path(__file__).parent.parent / 'examples' / 'splice-to-subtree.md'
        )
        assert ex.exists(), f"splice-to-subtree.md not found at {ex}"
        blocks = re.findall(r'```\n(.*?)```', ex.read_text(), re.S)
        # blocks alternate BEFORE (bad, index 0/2) / AFTER (clean, index 1/3)
        for i, b in enumerate(blocks):
            rule_ids = [v[1] for v in lint_text('```\n' + b + '```')]
            if i % 2 == 0:
                assert 'R9' in rule_ids, f"BEFORE block {i} should flag R9: {rule_ids}"
            else:
                assert not rule_ids, f"AFTER block {i} should be clean: {rule_ids}"

    def test_r9_html_entity_not_flagged(self):
        """The ';' inside an HTML entity (&amp;) is not a prose semicolon ()."""
        text = "```\n- Root\n I. Ben &amp; Jerry shipped four new flavors\n```"
        rule_ids = [v[1] for v in lint_text(text)]
        assert 'R9' not in rule_ids, f"entity ';' wrongly flagged R9: {rule_ids}"

    def test_r10_double_marker_flagged(self):
        """A dash node whose text starts with a stray '•' is a double marker ()."""
        text = "```\n- Delivery plan\n ▸ • target = PR branch\n```"
        rule_ids = [v[1] for v in lint_text(text)]
        assert 'R10' in rule_ids, f"double marker not flagged R10: {rule_ids}"

    def test_r10_midtext_arrow_not_flagged(self):
        """A mid-text 'X → Y' causality idiom does not start the node text ()."""
        text = "```\n- Root\n ↪ pin drift → refreshed on sync\n```"
        rule_ids = [v[1] for v in lint_text(text)]
        assert 'R10' not in rule_ids, f"mid-text arrow wrongly flagged R10: {rule_ids}"

    def test_good_r11_passes(self, fixtures_dir):
        """A hand-wrapped node with identical-indent continuations, all lines
        <=64 chars, must lint clean."""
        good_file = fixtures_dir / 'good_r11.md'
        assert good_file.exists(), f"good_r11.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_r11.md has violations: {violations}"

    def test_bad_r11_long_caught(self, fixtures_dir):
        """A block-mode physical line >64 chars must be flagged R11."""
        bad_file = fixtures_dir / 'bad_r11_long.md'
        assert bad_file.exists(), f"bad_r11_long.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        rule_ids = [v[1] for v in violations]
        assert 'R11' in rule_ids, f"Expected R11 violation, got: {violations}"

    def test_bad_r11_indent_caught(self, fixtures_dir):
        """A continuation line indented deeper (hanging indent) than its
        marker line must be flagged R11 — user spec: identical indent,
        not a hang."""
        bad_file = fixtures_dir / 'bad_r11_indent.md'
        assert bad_file.exists(), f"bad_r11_indent.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        rule_ids = [v[1] for v in violations]
        assert 'R11' in rule_ids, f"Expected R11 violation, got: {violations}"

    def test_good_responsive_passes(self, fixtures_dir):
        """A valid ladder expressed as a real GFM list (`responsive` mode)
        must lint clean — including a >64-char `↪` line that must NOT
        trip R11 (the renderer wraps, not the linter)."""
        good_file = fixtures_dir / 'good_responsive.md'
        assert good_file.exists(), f"good_responsive.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_responsive.md has violations: {violations}"

    def test_bad_responsive_ladder_caught(self, fixtures_dir):
        """A `▸` directly under a `▸`, expressed in responsive GFM-list
        syntax, must still be caught as R8 — proves the ladder rules
        survive the responsive-mode strip."""
        bad_file = fixtures_dir / 'bad_responsive_ladder.md'
        assert bad_file.exists(), f"bad_responsive_ladder.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        rule_ids = [v[1] for v in violations]
        assert 'R8' in rule_ids, f"Expected R8 violation, got: {violations}"

    def test_good_responsive_glyphfree_passes(self, fixtures_dir):
        """Glyph-free responsive attribute (SKILL.md v0.3.9: `- **Bold**`
        at depth>=1, no literal `▸`) must lint clean — the case the
        linter could not recognize before the bold-attr family fix."""
        good_file = fixtures_dir / 'good_responsive_glyphfree.md'
        assert good_file.exists(), f"good_responsive_glyphfree.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_responsive_glyphfree.md has violations: {violations}"

    def test_good_responsive_explanation_leaf_passes(self, fixtures_dir):
        """Glyph-free responsive explanation leaf (plain prose item, no
        literal `↪`) must lint clean under a bold attribute parent."""
        good_file = fixtures_dir / 'good_responsive_explanation_leaf.md'
        assert good_file.exists(), f"good_responsive_explanation_leaf.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_responsive_explanation_leaf.md has violations: {violations}"

    def test_good_responsive_role_ladder_passes(self, fixtures_dir):
        """Regression fixture: a full real-world glyph-free responsive
        outline (bold attributes, uppercase depth-1 enumerators, plain
        explanation leaves, split across 3 root concepts to respect R5)
        must lint clean end to end."""
        good_file = fixtures_dir / 'good_responsive_role_ladder.md'
        assert good_file.exists(), f"good_responsive_role_ladder.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_responsive_role_ladder.md has violations: {violations}"

    def test_bad_responsive_unbolded_attr_caught(self, fixtures_dir):
        """A depth>=1 label that looks like an attribute but was never
        bolded is NOT a glyph-free attribute — it must still be caught
        (as some violation; it degrades to a bare explanation leaf with
        illegal children, not silently accepted as structure)."""
        bad_file = fixtures_dir / 'bad_responsive_unbolded_attr.md'
        assert bad_file.exists(), f"bad_responsive_unbolded_attr.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_responsive_unbolded_attr.md should have violations"

    def test_responsive_mode_skips_r11(self):
        """A responsive-mode >64-char physical line must never fire R11 —
        only `block` mode (fenced) does; the chat renderer wraps
        `responsive` output itself."""
        text = "- Root\n - ↪ " + ("x " * 40).strip()
        rule_ids = [v[1] for v in lint_text(text)]
        assert 'R11' not in rule_ids, f"R11 wrongly fired in responsive mode: {rule_ids}"

    def test_plain_inline_not_misdetected_as_responsive(self):
        """A plain `inline`-mode outline (bare glyphs, no '- ' list prefix
        on nested nodes) must NOT be reclassified as `responsive` —
        detection is conservative (SKILL.md `responsive` mode spec)."""
        text = "- Root\n ▸ Purpose\n ↪ a bare inline outline, no list wrapper"
        violations = lint_text(text)
        assert not violations, f"plain inline outline should lint clean unaffected: {violations}"

    def test_r11_inline_mode_unaffected(self):
        """Inline mode (no fence) is GitHub-rendered markdown and wraps
        itself — R11 must not fire outside a fenced block even on a long,
        differently-indented markerless line."""
        text = "- Root\n " + ("x" * 80)
        rule_ids = [v[1] for v in lint_text(text)]
        assert 'R11' not in rule_ids, f"R11 wrongly fired in inline mode: {rule_ids}"

    def test_bad_r5_arrow_two_facts_caught(self, fixtures_dir):
        """Test that bad_r5_arrow_two_facts.md is caught (R5 violation)."""
        bad_file = fixtures_dir / 'bad_r5_arrow_two_facts.md'
        assert bad_file.exists(), f"bad_r5_arrow_two_facts.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_r5_arrow_two_facts.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R5' in rule_ids, f"Expected R5 violation, got: {violations}"

    def test_bad_r7_enum_depth4_overlong_caught(self, fixtures_dir):
        """Test that bad_r7_enum_depth4_overlong.md is caught (R7 violation)."""
        bad_file = fixtures_dir / 'bad_r7_enum_depth4_overlong.md'
        assert bad_file.exists(), f"bad_r7_enum_depth4_overlong.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_r7_enum_depth4_overlong.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R7' in rule_ids, f"Expected R7 violation, got: {violations}"

    def test_good_r7_arrow_overlong_not_capped_passes(self, fixtures_dir):
        """Test that good_r7_arrow_overlong_not_capped.md lints cleanly."""
        good_file = fixtures_dir / 'good_r7_arrow_overlong_not_capped.md'
        assert good_file.exists(), f"good_r7_arrow_overlong_not_capped.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_r7_arrow_overlong_not_capped.md has violations: {violations}"

    def test_good_r7_depth1_attr_within_cap_passes(self, fixtures_dir):
        """Test that good_r7_depth1_attr_within_cap.md lints cleanly."""
        good_file = fixtures_dir / 'good_r7_depth1_attr_within_cap.md'
        assert good_file.exists(), f"good_r7_depth1_attr_within_cap.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_r7_depth1_attr_within_cap.md has violations: {violations}"

    def test_bad_connective_because_caught(self, fixtures_dir):
        """Test that bad_connective_because.md is caught (R12 violation)."""
        bad_file = fixtures_dir / 'bad_connective_because.md'
        assert bad_file.exists(), f"bad_connective_because.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_connective_because.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R12' in rule_ids, f"Expected R12 violation, got: {violations}"

    def test_good_single_clause_because_fragment_passes(self, fixtures_dir):
        """Test that good_single_clause_because_fragment.md lints cleanly."""
        good_file = fixtures_dir / 'good_single_clause_because_fragment.md'
        assert good_file.exists(), f"good_single_clause_because_fragment.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_single_clause_because_fragment.md has violations: {violations}"

    def test_bad_r13_caught(self, fixtures_dir):
        """Test that bad_r13.md is caught (R13 violation)."""
        bad_file = fixtures_dir / 'bad_r13.md'
        assert bad_file.exists(), f"bad_r13.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_r13.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R13' in rule_ids, f"Expected R13 violation, got: {violations}"

    def test_good_r13_passes(self, fixtures_dir):
        """Test that good_r13.md lints cleanly."""
        good_file = fixtures_dir / 'good_r13.md'
        assert good_file.exists(), f"good_r13.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_r13.md has violations: {violations}"

    def test_bad_r14_caught(self, fixtures_dir):
        """Test that bad_r14.md is caught (R14 violation)."""
        bad_file = fixtures_dir / 'bad_r14.md'
        assert bad_file.exists(), f"bad_r14.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_r14.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R14' in rule_ids, f"Expected R14 violation, got: {violations}"

    def test_good_r14_passes(self, fixtures_dir):
        """Test that good_r14.md lints cleanly."""
        good_file = fixtures_dir / 'good_r14.md'
        assert good_file.exists(), f"good_r14.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_r14.md has violations: {violations}"

    def test_bad_r15_caught(self, fixtures_dir):
        """Test that bad_r15.md is caught (R15 violation)."""
        bad_file = fixtures_dir / 'bad_r15.md'
        assert bad_file.exists(), f"bad_r15.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_r15.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R15' in rule_ids, f"Expected R15 violation, got: {violations}"

    def test_good_r15_passes(self, fixtures_dir):
        """Test that good_r15.md lints cleanly."""
        good_file = fixtures_dir / 'good_r15.md'
        assert good_file.exists(), f"good_r15.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_r15.md has violations: {violations}"

    def test_bad_responsive_dash_at_depth1_caught(self, fixtures_dir):
        """Test that bad_responsive_dash_at_depth1.md is caught."""
        bad_file = fixtures_dir / 'bad_responsive_dash_at_depth1.md'
        assert bad_file.exists(), f"bad_responsive_dash_at_depth1.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_responsive_dash_at_depth1.md should have violations"

    def test_good_r2_no_skip_passes(self, fixtures_dir):
        """Test that good_r2_no_skip.md (proper depth progression) lints cleanly."""
        good_file = fixtures_dir / 'good_r2_no_skip.md'
        assert good_file.exists(), f"good_r2_no_skip.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_r2_no_skip.md has violations: {violations}"

    def test_bad_r2_skip_rung_caught(self, fixtures_dir):
        """Test that bad_r2_skip_rung.md (skipped rung) is caught (R2 violation)."""
        bad_file = fixtures_dir / 'bad_r2_skip_rung.md'
        assert bad_file.exists(), f"bad_r2_skip_rung.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        assert violations, "bad_r2_skip_rung.md should have violations"
        rule_ids = [v[1] for v in violations]
        assert 'R2' in rule_ids, f"Expected R2 violation, got: {violations}"

    def test_bad_r9_arrow_splice_caught(self, fixtures_dir):
        """A chained-arrow explanation node (X → Y; Z → W) must trip R9 even
        though it lives on a `↪` line — arrow nodes are not blanket-exempt."""
        bad_file = fixtures_dir / 'bad_r9_arrow_splice.md'
        assert bad_file.exists(), f"bad_r9_arrow_splice.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        rule_ids = [v[1] for v in violations]
        assert 'R9' in rule_ids, f"Expected R9 violation, got: {violations}"

    def test_bad_r10_arrow_multi_caught(self, fixtures_dir):
        """A `;`-joined 3-fact chain under one `↪` marker must trip R9."""
        bad_file = fixtures_dir / 'bad_r10_arrow_multi.md'
        assert bad_file.exists(), f"bad_r10_arrow_multi.md not found at {bad_file}"
        violations = lint_file(str(bad_file))
        rule_ids = [v[1] for v in violations]
        assert 'R9' in rule_ids, f"Expected R9 violation, got: {violations}"

    def test_good_arrow_branch_preview_passes(self, fixtures_dir):
        """A legitimate non-leaf branch-preview `↪` (first child, no depth-1
        sibling enumerator) must lint clean — regression for the R5
        arrow-rarity ratio false positive."""
        good_file = fixtures_dir / 'good_arrow_branch_preview.md'
        assert good_file.exists(), f"good_arrow_branch_preview.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_arrow_branch_preview.md has violations: {violations}"

    def test_good_r5_deep_arrows_passes(self, fixtures_dir):
        """A deep outline whose leaf arrows are balanced by non-arrow
        enumerators at depth >= 2 must lint clean — R5's denominator must
        count non-arrow nodes at any depth, not only depth 1."""
        good_file = fixtures_dir / 'good_r5_deep_arrows.md'
        assert good_file.exists(), f"good_r5_deep_arrows.md not found at {good_file}"
        violations = lint_file(str(good_file))
        assert not violations, f"good_r5_deep_arrows.md has violations: {violations}"


class TestNormativeBlocks:
    """Test that EVERY fenced block in normative files lints cleanly."""

    def test_skill_md_all_blocks_clean(self):
        """Test that all fenced blocks in SKILL.md lint cleanly."""
        skill_file = Path(__file__).parent.parent / 'SKILL.md'
        assert skill_file.exists(), f"SKILL.md not found at {skill_file}"
        block_violations = _lint_all_blocks(str(skill_file))

        for block_index, violations in block_violations.items():
            assert not violations, (
                f"SKILL.md block {block_index} has violations: {violations}"
            )

    def test_self_explain_all_blocks_clean(self):
        """Test that all fenced blocks in examples/self-explain.md lint cleanly."""
        self_explain_file = (
            Path(__file__).parent.parent / 'examples' / 'self-explain.md'
        )
        assert self_explain_file.exists(), (
            f"self-explain.md not found at {self_explain_file}"
        )
        block_violations = _lint_all_blocks(str(self_explain_file))

        for block_index, violations in block_violations.items():
            assert not violations, (
                f"self-explain.md block {block_index} has violations: {violations}"
            )

    def test_attribute_example_clean(self):
        """Test that the fenced block in examples/attribute.md lints cleanly."""
        attribute_file = (
            Path(__file__).parent.parent / 'examples' / 'attribute.md'
        )
        assert attribute_file.exists(), (
            f"attribute.md not found at {attribute_file}"
        )
        block_violations = _lint_all_blocks(str(attribute_file))

        for block_index, violations in block_violations.items():
            assert not violations, (
                f"attribute.md block {block_index} has violations: {violations}"
            )


def _extract_readme_section(readme_text: str, heading: str) -> str:
    """
    Return the body of one '## <heading>' section of README.md, up to (not
    including) the next '## ' heading. `lint_text`/`extract_outline_from_text`
    only look at content inside the FIRST fenced block when one exists
    anywhere in the input, so a section must be isolated before linting —
    passing the whole README would silently only check its first code fence
    and skip every non-fenced `responsive`-mode outline entirely (exactly
    how the Method section's broken outline shipped undetected).
    """
    pattern = re.compile(
        r'^##\s+' + re.escape(heading) + r'\s*$(.*?)(?=^##\s|\Z)',
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(readme_text)
    assert m, f"README.md section '## {heading}' not found"
    body = m.group(1)
    # Drop non-outline scaffolding this repo's README convention adds to
    # every section: the italic/plain intro sentence and the back-to-top div.
    body = re.sub(r'<div align="right">.*?</div>', '', body, flags=re.DOTALL)
    lines = [
        line for line in body.split('\n')
        if line.strip() and not line.strip().startswith('This section is')
    ]
    return '\n'.join(lines)


class TestReadmeOutlines:
    """
    Lint the README's own live `responsive`-mode outlines directly — not a
    frozen copy fixture — so an edit to README.md that reintroduces a lint
    violation fails CI immediately instead of shipping silently (the exact
    gap that let the Method section's outline ship broken: nothing in this
    suite ever looked at README.md's non-fenced content before).
    """

    @pytest.fixture
    def readme_text(self):
        readme_file = Path(__file__).parent.parent.parent.parent / 'README.md'
        assert readme_file.exists(), f"README.md not found at {readme_file}"
        return readme_file.read_text(encoding='utf-8')

    def test_method_section_outline_clean(self, readme_text):
        """README '## 2. Method' section's outline must lint clean — this
        is the section that regressed (bold-attr + plain-leaf responsive
        forms the linter couldn't recognize before the v0.4.4 fix)."""
        section = _extract_readme_section(readme_text, '2. Method')
        violations = lint_text(section)
        assert not violations, f"README Method section has violations: {violations}"
