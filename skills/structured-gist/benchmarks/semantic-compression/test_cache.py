#!/usr/bin/env python3
"""
Tests for cache key hashing primitives.
Asserts that identical inputs produce identical keys and that changing
any input parameter changes the key.
"""
import pytest
from pathlib import Path
from cache_key import compute_cache_key


class TestCacheKeyHashing:
    """Test cache key determinism and sensitivity."""

    def test_identical_inputs_produce_identical_keys(self):
        """Byte-identical input tuple produces same cache key."""
        case_id = "near-identical-numbers"
        level = "standard"
        rendering = "The quick brown fox jumps over the lazy dog."
        gold = '{"facts": [{"id": "f1", "text": "fox jumps"}]}'
        prompt = "Compress to 50% while retaining all facts."
        model = "claude-opus-4-8"

        key1 = compute_cache_key(case_id, level, rendering, gold, prompt, model)
        key2 = compute_cache_key(case_id, level, rendering, gold, prompt, model)

        assert key1 == key2, "Identical inputs must produce identical keys"
        assert len(key1) == 64, "Cache key must be 64-char hex (SHA-256)"

    def test_changing_case_id_changes_key(self):
        """Changing case_id must produce different cache key."""
        level = "standard"
        rendering = "The quick brown fox jumps over the lazy dog."
        gold = '{"facts": [{"id": "f1", "text": "fox jumps"}]}'
        prompt = "Compress to 50% while retaining all facts."
        model = "claude-opus-4-8"

        key1 = compute_cache_key("case-a", level, rendering, gold, prompt, model)
        key2 = compute_cache_key("case-b", level, rendering, gold, prompt, model)

        assert key1 != key2, "Different case_id must produce different keys"

    def test_changing_level_changes_key(self):
        """Changing level must produce different cache key."""
        case_id = "near-identical-numbers"
        rendering = "The quick brown fox jumps over the lazy dog."
        gold = '{"facts": [{"id": "f1", "text": "fox jumps"}]}'
        prompt = "Compress to 50% while retaining all facts."
        model = "claude-opus-4-8"

        key1 = compute_cache_key(case_id, "skim", rendering, gold, prompt, model)
        key2 = compute_cache_key(case_id, "deep", rendering, gold, prompt, model)

        assert key1 != key2, "Different level must produce different keys"

    def test_changing_rendering_changes_key(self):
        """Changing rendering_content must produce different cache key."""
        case_id = "near-identical-numbers"
        level = "standard"
        gold = '{"facts": [{"id": "f1", "text": "fox jumps"}]}'
        prompt = "Compress to 50% while retaining all facts."
        model = "claude-opus-4-8"

        key1 = compute_cache_key(case_id, level, "rendering version 1", gold, prompt, model)
        key2 = compute_cache_key(case_id, level, "rendering version 2", gold, prompt, model)

        assert key1 != key2, "Different rendering must produce different keys"

    def test_changing_gold_changes_key(self):
        """Changing gold_content must produce different cache key."""
        case_id = "near-identical-numbers"
        level = "standard"
        rendering = "The quick brown fox jumps over the lazy dog."
        prompt = "Compress to 50% while retaining all facts."
        model = "claude-opus-4-8"

        key1 = compute_cache_key(case_id, level, rendering, '{"facts": []}', prompt, model)
        key2 = compute_cache_key(case_id, level, rendering, '{"facts": [{"id": "f1"}]}', prompt, model)

        assert key1 != key2, "Different gold must produce different keys"

    def test_changing_prompt_changes_key(self):
        """Changing prompt_content must produce different cache key."""
        case_id = "near-identical-numbers"
        level = "standard"
        rendering = "The quick brown fox jumps over the lazy dog."
        gold = '{"facts": [{"id": "f1", "text": "fox jumps"}]}'
        model = "claude-opus-4-8"

        key1 = compute_cache_key(case_id, level, rendering, gold, "Compress to 50%", model)
        key2 = compute_cache_key(case_id, level, rendering, gold, "Compress to 75%", model)

        assert key1 != key2, "Different prompt must produce different keys"

    def test_changing_model_id_changes_key(self):
        """Changing model_id must produce different cache key."""
        case_id = "near-identical-numbers"
        level = "standard"
        rendering = "The quick brown fox jumps over the lazy dog."
        gold = '{"facts": [{"id": "f1", "text": "fox jumps"}]}'
        prompt = "Compress to 50% while retaining all facts."

        key1 = compute_cache_key(case_id, level, rendering, gold, prompt, "claude-opus-4-8")
        key2 = compute_cache_key(case_id, level, rendering, gold, prompt, "claude-sonnet-4-20250514")

        assert key1 != key2, "Different model_id must produce different keys"

    def test_all_parameters_together(self):
        """Integration: all parameters affect the final key."""
        case_a = compute_cache_key("case-a", "skim", "text1", "gold1", "prompt1", "model1")
        case_b = compute_cache_key("case-b", "skim", "text1", "gold1", "prompt1", "model1")
        level_change = compute_cache_key("case-a", "deep", "text1", "gold1", "prompt1", "model1")
        rendering_change = compute_cache_key("case-a", "skim", "text2", "gold1", "prompt1", "model1")
        gold_change = compute_cache_key("case-a", "skim", "text1", "gold2", "prompt1", "model1")
        prompt_change = compute_cache_key("case-a", "skim", "text1", "gold1", "prompt2", "model1")
        model_change = compute_cache_key("case-a", "skim", "text1", "gold1", "prompt1", "model2")

        keys = [case_a, case_b, level_change, rendering_change, gold_change, prompt_change, model_change]
        # All keys should be unique
        assert len(set(keys)) == len(keys), "All parameter variations must produce unique keys"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
