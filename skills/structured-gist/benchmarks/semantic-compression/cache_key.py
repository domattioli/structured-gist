#!/usr/bin/env python3
"""
Cache key primitive: deterministic hash of semantic-compression run inputs.
Used by run.py to track whether a cached result can be reused.
"""
import hashlib


def compute_cache_key(case_id, level, rendering_content, gold_content, prompt_content, model_id):
    """
    Compute a SHA-256 cache key from run inputs.

    Args:
        case_id: str, case directory name (e.g., "near-identical-numbers")
        level: str, compression level (e.g., "skim", "standard", "deep")
        rendering_content: str, rendered compression output to be judged
        gold_content: str, gold.json content (serialized reference)
        prompt_content: str, prompt used in the semantic compression call
        model_id: str, model identifier (e.g., "claude-opus-4-8")

    Returns:
        str, hex-encoded SHA-256 hash of the input tuple
    """
    # Create a stable input tuple and hash it
    input_tuple = (case_id, level, rendering_content, gold_content, prompt_content, model_id)
    # Convert to string representation for hashing
    input_str = repr(input_tuple)
    digest = hashlib.sha256(input_str.encode('utf-8')).hexdigest()
    return digest
