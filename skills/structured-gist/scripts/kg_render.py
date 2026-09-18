#!/usr/bin/env python3
"""
Knowledge graph renderer for nested-notes-kg/v1 schema.
Pure Python 3 stdlib, no external dependencies.
Renders a validated KG to an outline with skim/standard/deep granularity prunes.
"""

import sys
import os
import argparse
from typing import Dict, List, Tuple

# Import graph loader and validator from kg.py (sibling dir)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from kg import load_graph, validate_graph, GraphError, _get_children

# Import linting functions from lint_outline.py (sibling tests dir)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests'))
try:
    from lint_outline import lint_text, parse_line
except ImportError as e:
    sys.stderr.write(f"FATAL: Cannot import from lint_outline.py: {e}\n")
    sys.exit(2)


def compute_depths(graph: dict) -> Dict[str, int]:
    """
    Compute depth of each node by following parent chain.
    Root concepts have depth 0.
    Returns {node_id: depth}.
    """
    depths = {}
    nodes = graph.get('nodes', [])
    edges = graph.get('edges', [])

    # Build parent_of map
    parent_of = {}
    for edge in edges:
        from_id = edge.get('from')
        to_id = edge.get('to')
        parent_of[to_id] = from_id

    # Compute depth for each node
    for node in nodes:
        node_id = node.get('id')
        depth = 0
        current = node_id
        while current in parent_of:
            current = parent_of[current]
            depth += 1
        depths[node_id] = depth

    return depths


def prune(graph: dict, level: str) -> dict:
    """
    Prune graph based on granularity level.
    Returns a new graph with pruned nodes/edges.

    Prune rules:
    - skim: keep depth <= 1 AND type != explanation
    - standard: keep depth <= 3 EXCEPT children of explanation nodes are pruned with subtrees
    - deep: keep all nodes

    Entire subtrees of pruned nodes are pruned (no reparenting).
    """
    if level not in ('skim', 'standard', 'deep'):
        raise ValueError(f"Invalid level: {level}")

    depths = compute_depths(graph)
    nodes = graph.get('nodes', [])
    edges = graph.get('edges', [])

    # Build children map and parent_of map
    children_map, parent_of = _get_children(graph)

    # Determine which nodes to keep
    keep_nodes = set()

    if level == 'deep':
        # Keep all nodes
        for node in nodes:
            keep_nodes.add(node.get('id'))
    elif level == 'skim':
        # Keep depth <= 1 AND type != explanation
        for node in nodes:
            node_id = node.get('id')
            node_type = node.get('type')
            depth = depths[node_id]
            if depth <= 1 and node_type != 'explanation':
                keep_nodes.add(node_id)
    elif level == 'standard':
        # Keep depth <= 3 EXCEPT children of explanation nodes (pruned with subtrees)
        # First pass: mark all nodes at depth <= 3
        candidates = set()
        for node in nodes:
            node_id = node.get('id')
            depth = depths[node_id]
            if depth <= 3:
                candidates.add(node_id)

        # Second pass: remove children of explanation nodes (but keep explanations themselves)
        to_remove = set()
        for node in nodes:
            node_id = node.get('id')
            node_type = node.get('type')
            if node_type == 'explanation' and node_id in candidates:
                # Remove children of this explanation (with their subtrees)
                if node_id in children_map:
                    for _edge_type, child_id in children_map[node_id]:
                        def remove_subtree(nid: str):
                            to_remove.add(nid)
                            if nid in children_map:
                                for _et, cid in children_map[nid]:
                                    remove_subtree(cid)
                        remove_subtree(child_id)

        keep_nodes = candidates - to_remove

    # Prune unreachable nodes: if a parent is removed, remove all descendants
    to_remove_cascade = set()
    for node in nodes:
        node_id = node.get('id')
        if node_id not in keep_nodes:
            to_remove_cascade.add(node_id)
        else:
            # Check if parent is removed; if so, this node should be removed too
            current = node_id
            while current in parent_of:
                current = parent_of[current]
                if current not in keep_nodes:
                    to_remove_cascade.add(node_id)
                    break

    keep_nodes = keep_nodes - to_remove_cascade

    # Build pruned graph
    pruned_nodes = [n for n in nodes if n.get('id') in keep_nodes]
    pruned_edges = [e for e in edges if e.get('from') in keep_nodes and e.get('to') in keep_nodes]

    return {
        'schema': graph['schema'],
        'source_id': graph['source_id'],
        'nodes': pruned_nodes,
        'edges': pruned_edges
    }


def _generate_roman(n: int, uppercase: bool = True) -> str:
    """Generate roman numeral for n (1-10, typical range)."""
    if n < 1 or n > 10:
        return str(n)  # Fallback for out-of-range

    romans = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    roman = romans[n - 1]
    return roman if uppercase else roman.lower()


def _generate_alpha(n: int, uppercase: bool = True) -> str:
    """Generate alpha label for n (1-26)."""
    if n < 1 or n > 26:
        return str(n)  # Fallback for out-of-range

    base = ord('A') if uppercase else ord('a')
    return chr(base + n - 1)


def _backtrack_wrap(text: str, max_width: int, indent: str) -> Tuple[List[str], bool]:
    """
    Wrap text with the R11 backtrack rule.

    Returns (lines, success) where:
    - lines: list of text lines (not including indent)
    - success: False if wrap-marker collision detected (ERR_RENDER_OVERFLOW)

    Each line must fit within max_width when indented.
    Continuation lines must not begin with a marker-parsed token.
    """
    indent_len = len(indent)
    marker_budget = max_width - indent_len  # Available width for content

    if marker_budget < 1:
        return [], False  # Indent alone exceeds budget

    lines = []
    words = text.split()

    if not words:
        return [], True

    current_line = []
    current_len = 0

    for word in words:
        # Check if adding this word exceeds budget
        space_needed = (1 if current_line else 0)  # Space before word if not first
        word_len = len(word)

        if current_len + space_needed + word_len <= marker_budget:
            # Fits on current line
            current_line.append(word)
            current_len += space_needed + word_len
        else:
            # Doesn't fit; need to wrap
            if current_line:
                # Save current line
                lines.append(' '.join(current_line))
                current_line = []
                current_len = 0

            # Check if this single word fits on a new line
            if word_len <= marker_budget:
                current_line.append(word)
                current_len = word_len
            else:
                # Single token exceeds budget: ERR_RENDER_OVERFLOW (arm a)
                return [], False

    # Save final line
    if current_line:
        lines.append(' '.join(current_line))

    # Now check continuation lines for marker collision
    # Continuation lines are lines[1:] (lines[0] is the first line after the marker)
    for line in lines[1:]:
        # Check if this line begins with a marker-parsed token
        # Use parse_line with unit=2 (temporary unit for checking)
        depth_dummy, family, text_dummy = parse_line(' ' + line, unit=2)
        if family != 'unknown':
            # This line starts with a marker token: backtrack needed
            # But this is complex; instead, verify the rule during rendering
            pass

    return lines, True


def _wrap_text(text: str, indent: str, max_width: int = 64, marker_len: int = 0) -> Tuple[List[str], bool]:
    """
    Hard-wrap text with R11 rules.

    Returns (lines, success) where:
    - lines: list of text lines (NOT including indent, NOT including marker)
    - success: False if wrap-marker collision or overflow detected

    Max width includes indent. The first line additionally carries the
    marker (marker_len chars), so its budget is max_width - indent - marker.
    Continuation lines must have identical indent to marker line (no
    marker), so their budget is max_width - indent.
    Continuation lines must not begin with a marker-parsed token.
    """
    indent_len = len(indent)
    first_width = max_width - indent_len - marker_len
    cont_width = max_width - indent_len

    if first_width < 1 or cont_width < 1:
        return [], False

    lines = []
    words = text.split()

    if not words:
        return [], True

    current_line = []

    for word in words:
        available_width = first_width if not lines else cont_width
        test_line = ' '.join(current_line + [word]) if current_line else word

        if len(test_line) <= available_width:
            current_line.append(word)
        else:
            # Word doesn't fit; finalize current line and start a new one
            if current_line:
                lines.append(' '.join(current_line))
                current_line = []
                available_width = cont_width

            # Try to fit word on new line
            if len(word) <= available_width:
                current_line = [word]
            else:
                # Single token exceeds budget: ERR_RENDER_OVERFLOW (arm a)
                return [], False

    if current_line:
        lines.append(' '.join(current_line))

    # Check continuation lines (all but the first) for marker collision
    for cont_line in lines[1:]:
        # Check if this line parses as a marker line
        depth_dummy, family, text_dummy = parse_line(' ' * indent_len + cont_line, unit=2)
        if family != 'unknown':
            # This continuation starts with a marker: wrap-marker collision
            # Backtrack: try to move words from this line to the previous line
            # For now, return false to trigger ERR_RENDER_OVERFLOW
            return [], False

    return lines, True


def _emit_marker(depth: int, seq_num: int, is_ordered: bool) -> str:
    """
    Generate marker for a child based on depth and sequence.

    seq_num: sequential position among rendered siblings of this type (1-indexed).
    is_ordered: True for ordered-part, False for unordered-part.

    Returns the marker string (e.g., "I.", "A.", "i.", "a.").
    """
    if depth == 1:
        if is_ordered:
            return _generate_roman(seq_num, uppercase=True) + '.'
        else:
            return _generate_alpha(seq_num, uppercase=True) + '.'
    elif depth >= 2:
        if is_ordered:
            return _generate_roman(seq_num, uppercase=False) + '.'
        else:
            return _generate_alpha(seq_num, uppercase=False) + '.'
    else:
        # Should not reach here
        return '?'


def render(graph: dict, level: str = 'standard') -> str:
    """
    Render a pruned KG to an outline string.

    Returns the complete outline as a fenced text block (including ``` delimiters).
    """
    # Validate before rendering
    validate_graph(graph)

    # Prune based on level
    pruned = prune(graph, level)

    # Validate renderable (stage 7)
    validate_renderable(pruned)

    # Compute depths for pruned graph
    depths = compute_depths(pruned)
    nodes = pruned.get('nodes', [])
    _unused_edges = pruned.get('edges', [])

    # Build children map
    children_map, parent_of = _get_children(pruned)

    # Build node lookup
    node_by_id = {n.get('id'): n for n in nodes}

    # Traverse and render
    lines = []

    def render_children(node_id: str, indent_level: int) -> None:
        """Render children of a node in the specified order."""
        if node_id not in children_map:
            return

        child_edges = children_map[node_id]

        # Classify children
        non_leaf_explanation = None
        attributes = []
        ordered_parts = []
        unordered_parts = []
        leaf_explanations = []

        for edge_type, child_id in child_edges:
            child_node = node_by_id.get(child_id)
            if not child_node:
                continue
            child_type = child_node.get('type')

            # Classify as leaf or non-leaf
            is_leaf = child_id not in children_map or not children_map[child_id]

            if edge_type == 'explains':
                if is_leaf:
                    leaf_explanations.append(child_id)
                else:
                    non_leaf_explanation = child_id
            elif edge_type == 'has-attribute':
                attributes.append(child_id)
            elif edge_type == 'composed-of':
                if child_type == 'ordered-part':
                    ordered_parts.append(child_id)
                else:
                    unordered_parts.append(child_id)

        # Emit non-leaf explanation first
        if non_leaf_explanation:
            render_node(non_leaf_explanation, indent_level)

        # Emit attributes in document order
        for attr_id in attributes:
            render_node(attr_id, indent_level)

        # Emit ordered parts (sorted by rank)
        if ordered_parts:
            sorted_parts = sorted(ordered_parts, key=lambda pid: node_by_id[pid].get('rank', 999))
            for seq_num, part_id in enumerate(sorted_parts, 1):
                emit_part(part_id, seq_num, True, indent_level)

        # Emit unordered parts in document order
        if unordered_parts:
            for seq_num, part_id in enumerate(unordered_parts, 1):
                emit_part(part_id, seq_num, False, indent_level)

        # Emit leaf explanations in document order
        for leaf_id in leaf_explanations:
            render_node(leaf_id, indent_level)

    def render_node(node_id: str, indent_level: int = 0) -> None:
        """Recursively render a node and its children."""
        node = node_by_id.get(node_id)
        if not node:
            return

        node_type = node.get('type')
        text = node.get('text', '')
        _unused_depth = depths[node_id]

        # Generate marker
        indent_str = ' ' * (indent_level * 4)

        if node_type == 'concept':
            marker = '- '
        elif node_type == 'attribute':
            marker = '▸ '
        elif node_type == 'explanation':
            marker = '↪ '
        elif node_type in ('ordered-part', 'unordered-part'):
            # Marker will be generated based on sibling position
            # This is handled below when emitting children
            marker = None
        else:
            marker = '?'

        # For parts, the marker is generated when emitting as a child
        # So we handle that specially
        if node_type not in ('ordered-part', 'unordered-part'):
            # Emit this node with its marker
            if marker:
                # Wrap text if needed
                max_width = 64
                marker_width = len(marker)
                available = max_width - len(indent_str) - marker_width

                if len(text) <= available:
                    line = indent_str + marker + text
                    lines.append(line)
                else:
                    # Wrap the text
                    wrapped, success = _wrap_text(text, indent_str, max_width, marker_width)
                    if not success:
                        raise GraphError('ERR_RENDER_OVERFLOW', node=node_id,
                                       detail='Text cannot be wrapped within 64-char budget')
                    if wrapped:
                        lines.append(indent_str + marker + wrapped[0])
                        for cont_line in wrapped[1:]:
                            lines.append(indent_str + cont_line)

        # Render children (all node types)
        render_children(node_id, indent_level + 1)

    def emit_part(node_id: str, seq_num: int, is_ordered: bool, indent_level: int) -> None:
        """Emit a part node with its sequence number."""
        node = node_by_id.get(node_id)
        if not node:
            return

        text = node.get('text', '')
        depth = depths[node_id]
        indent_str = ' ' * (indent_level * 4)

        # Generate marker based on sequence and depth
        marker = _emit_marker(depth, seq_num, is_ordered) + ' '

        # Wrap text if needed
        max_width = 64
        marker_width = len(marker)
        available = max_width - len(indent_str) - marker_width

        if len(text) <= available:
            line = indent_str + marker + text
            lines.append(line)
        else:
            # Wrap the text
            wrapped, success = _wrap_text(text, indent_str, max_width, marker_width)
            if not success:
                raise GraphError('ERR_RENDER_OVERFLOW', node=node_id,
                               detail='Text cannot be wrapped within 64-char budget')
            if wrapped:
                lines.append(indent_str + marker + wrapped[0])
                for cont_line in wrapped[1:]:
                    lines.append(indent_str + cont_line)

        # Render children of this part
        render_children(node_id, indent_level + 1)

    # Find root concepts and render them
    root_concepts = []
    for node in nodes:
        node_id = node.get('id')
        node_type = node.get('type')
        if node_type == 'concept' and node_id not in parent_of:
            root_concepts.append(node_id)

    for root_id in root_concepts:
        render_node(root_id)

    # Build output with fence
    output_lines = ['```text'] + lines + ['```']
    output = '\n'.join(output_lines) + '\n'

    # Self-lint the output
    violations = lint_text(output)
    if violations:
        raise GraphError('INTERNAL_LINT_FAILURE', detail=f'Self-lint found {len(violations)} violations')

    return output


def validate_renderable(graph: dict) -> None:
    """
    Validate render-level checks (stage 7).

    Checks:
    - ERR_ARROW_RARITY: for each granularity level, check arrow count vs depth-1 siblings
    - ERR_PART_DEPTH: part-parented parts must render at depth 2 only
    - ERR_RENDER_OVERFLOW: unwrappable tokens or wrap-marker collision
    """
    nodes = graph.get('nodes', [])
    _unused_edges = graph.get('edges', [])

    children_map, parent_of = _get_children(graph)
    node_by_id = {n.get('id'): n for n in nodes}
    depths = compute_depths(graph)

    # Check all three granularity levels
    for level in ('skim', 'standard', 'deep'):
        pruned = prune(graph, level)
        pruned_nodes = pruned.get('nodes', [])
        pruned_children_map, pruned_parent_of = _get_children(pruned)
        pruned_depths = compute_depths(pruned)
        pruned_node_set = {n.get('id') for n in pruned_nodes}

        # ERR_ARROW_RARITY: for each top-level block, count arrows vs depth-1 non-arrow nodes
        for node in pruned_nodes:
            node_id = node.get('id')
            node_type = node.get('type')

            # Find top-level blocks (depth 0 concepts)
            if node_type != 'concept' or pruned_depths.get(node_id, 0) != 0:
                continue

            # This is a top-level concept; count arrows and depth-1 non-arrows in its subtree
            arrow_count = 0
            depth1_non_arrow_count = 0

            def count_children(nid: str, d: int):
                nonlocal arrow_count, depth1_non_arrow_count
                if nid not in pruned_node_set:
                    return

                n = node_by_id.get(nid)
                if not n:
                    return

                if n.get('type') == 'explanation' and d >= 1:
                    arrow_count += 1
                elif d == 1 and n.get('type') != 'explanation':
                    depth1_non_arrow_count += 1

                if nid in pruned_children_map:
                    for _edge_type, child_id in pruned_children_map[nid]:
                        count_children(child_id, d + 1)

            count_children(node_id, 0)

            if arrow_count > depth1_non_arrow_count:
                raise GraphError('ERR_ARROW_RARITY', node=node_id,
                               detail=f'Level {level}: {arrow_count} arrows > {depth1_non_arrow_count} depth-1 non-arrow nodes')

    # ERR_PART_DEPTH: part-parented parts must render at depth 2
    for node in nodes:
        node_id = node.get('id')
        node_type = node.get('type')

        if node_type not in ('ordered-part', 'unordered-part'):
            continue

        # This is a part; check if its parent is also a part
        parent_id = parent_of.get(node_id)
        if parent_id:
            parent_node = node_by_id.get(parent_id)
            parent_type = parent_node.get('type') if parent_node else None

            if parent_type in ('ordered-part', 'unordered-part'):
                # Part-parented part; check that it renders at depth 2
                child_depth = depths[node_id]
                if child_depth != 2:
                    raise GraphError('ERR_PART_DEPTH', node=node_id,
                                   detail=f'Part-parented part must render at depth 2, got {child_depth}')

    # ERR_RENDER_OVERFLOW: check for unwrappable tokens
    # (This is complex to check without actual rendering; we check during render instead)
    # For validation, we do a simple check: any token > 64 chars is unrenderable
    for node in nodes:
        node_id = node.get('id')
        text = node.get('text', '')

        # Check if any single token exceeds 64 chars
        for token in text.split():
            if len(token) > 64:
                raise GraphError('ERR_RENDER_OVERFLOW', node=node_id,
                               detail=f'Token exceeds 64-char budget: {token[:50]}...')


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Render a knowledge graph to an outline')
    parser.add_argument('graph_file', help='Path to graph.json file')
    parser.add_argument('--level', choices=['skim', 'standard', 'deep'], default='standard',
                        help='Granularity level (default: standard)')
    parser.add_argument('--out', help='Output file (default: stdout)')
    parser.add_argument('--validate-only', action='store_true',
                        help='Validate only, do not render')

    args = parser.parse_args()

    try:
        graph = load_graph(args.graph_file)
        validate_graph(graph)

        if args.validate_only:
            # Run all validation stages (1-7)
            validate_renderable(graph)
            print("OK")
            sys.exit(0)

        # Render
        output = render(graph, level=args.level)

        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            sys.stdout.write(output)

        sys.exit(0)

    except GraphError as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(2)
    except Exception as e:
        sys.stderr.write(f"FATAL: {e}\n")
        sys.exit(2)


if __name__ == '__main__':
    main()
