#!/usr/bin/env python3
"""
Knowledge graph validator for nested-notes-kg/v1 schema.
Pure Python 3 stdlib, no external dependencies.
Validation stages 1-6 (structural); stage 7 (render-level) lives in kg_render.py.
"""

import sys
import os
import json
from typing import Dict, List, Tuple, Optional, Set

# Import validation functions from lint_outline.py (sibling tests dir)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests'))
try:
    from lint_outline import r9_delimiter_violation, _STRAY_LEADING_MARKER
except ImportError as e:
    sys.stderr.write(f"FATAL: Cannot import from lint_outline.py: {e}\n")
    sys.exit(2)


class GraphError(Exception):
    """Named validation error for knowledge graphs."""

    def __init__(self, err: str, node: Optional[str] = None, edge: Optional[int] = None, detail: str = ""):
        self.err = err
        self.node = node if node is not None else '-'
        self.edge = edge if edge is not None else '-'
        self.detail = detail
        super().__init__(self.__str__())

    def __str__(self) -> str:
        """Format: KG-REJECT <ERR> node=<id|-> edge=<idx|-> : <detail>"""
        return f"KG-REJECT {self.err} node={self.node} edge={self.edge} : {self.detail}"


def load_graph(path: str) -> dict:
    """
    Load a KG from JSON file.
    Raises GraphError if schema != 'nested-notes-kg/v1'.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            graph = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise GraphError('ERR_SCHEMA', detail=f"Failed to parse JSON: {e}")

    # Schema check happens in validate_graph (stage 1), not here
    return graph


def save_graph(graph: dict, path: str) -> None:
    """
    Save a KG to JSON file with canonical serialization.
    Format: json.dumps(sort_keys=True, ensure_ascii=False, indent=2) + LF + trailing newline.
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write('\n')


def _get_children(graph: dict) -> Tuple[Dict[str, List[Tuple[str, str]]], Dict[str, str]]:
    """
    Build children map and parent_of map from edges.
    Returns (children_map, parent_of_map) where:
      children_map: parent_id -> list of (edge_type, child_id) in edge-list order
      parent_of_map: child_id -> parent_id (set by parent edges only)
    """
    children = {}  # parent_id -> [(edge_type, child_id), ...]
    parent_of = {}  # child_id -> parent_id

    # Build parent relationships from all edges that establish parent-child
    edges = graph.get('edges', [])
    for edge in edges:
        from_id = edge.get('from')
        to_id = edge.get('to')
        edge_type = edge.get('type')

        # Initialize parent's children list if needed
        if from_id not in children:
            children[from_id] = []
        children[from_id].append((edge_type, to_id))

        # Track parent (only has-attribute, composed-of, explains establish parent-child)
        # All edge types establish parent-child relationships
        parent_of[to_id] = from_id

    return children, parent_of


def validate_graph(graph: dict) -> None:
    """
    Validate a knowledge graph according to kg-schema.md stages 1-6.
    Raises GraphError on first failure (first-error-wins semantics).
    Stages 1-6 cover structural checks; stage 7 (render-level) is in kg_render.py.
    """

    # ========== STAGE 1: Schema ==========
    schema = graph.get('schema')
    if schema != 'nested-notes-kg/v1':
        raise GraphError('ERR_SCHEMA', detail=f"Expected 'nested-notes-kg/v1', got '{schema}'")

    # ========== STAGE 2: Identity ==========
    nodes = graph.get('nodes', [])
    edges = graph.get('edges', [])

    # Collect node IDs
    node_ids = set()
    for node in nodes:
        node_id = node.get('id')
        if node_id in node_ids:
            raise GraphError('ERR_DUPLICATE_ID', node=node_id, detail="Duplicate node ID")
        node_ids.add(node_id)

    # Check all edge references resolve
    edge_idx = 0
    for edge in edges:
        from_id = edge.get('from')
        to_id = edge.get('to')
        if from_id not in node_ids:
            raise GraphError('ERR_DANGLING_REF', edge=edge_idx, detail=f"Edge 'from' node '{from_id}' not found")
        if to_id not in node_ids:
            raise GraphError('ERR_DANGLING_REF', edge=edge_idx, detail=f"Edge 'to' node '{to_id}' not found")
        edge_idx += 1

    # ========== STAGE 3: Node fields (node-list order) ==========
    valid_node_types = {'concept', 'attribute', 'ordered-part', 'unordered-part', 'explanation'}

    for node_idx, node in enumerate(nodes):
        node_id = node.get('id')
        node_type = node.get('type')
        text = node.get('text', '').strip()

        # ERR_UNKNOWN_NODE_TYPE
        if node_type not in valid_node_types:
            raise GraphError('ERR_UNKNOWN_NODE_TYPE', node=node_id, detail=f"Unknown node type '{node_type}'")

        # ERR_EMPTY_TEXT
        if not text:
            raise GraphError('ERR_EMPTY_TEXT', node=node_id, detail="Node text is empty or whitespace-only")

        # ERR_WORD_BUDGET (concept≤3, attribute≤4, part≤6, explanation uncapped)
        word_count = len(text.split())
        if node_type == 'concept' and word_count > 3:
            raise GraphError('ERR_WORD_BUDGET', node=node_id,
                           detail=f"concept text has {word_count} words, max 3")
        if node_type == 'attribute' and word_count > 4:
            raise GraphError('ERR_WORD_BUDGET', node=node_id,
                           detail=f"attribute text has {word_count} words, max 4")
        if node_type in ('ordered-part', 'unordered-part') and word_count > 6:
            raise GraphError('ERR_WORD_BUDGET', node=node_id,
                           detail=f"part text has {word_count} words, max 6")

        # ERR_TEXT_STRAY_MARKER (all node types incl. explanation)
        if _STRAY_LEADING_MARKER.match(text):
            raise GraphError('ERR_TEXT_STRAY_MARKER', node=node_id,
                           detail=f"Text begins with stray marker glyph: '{text[0]}'")

        # ERR_TEXT_DELIMITER_TAIL (non-explanation only)
        if node_type != 'explanation':
            violation_reason = r9_delimiter_violation(text)
            if violation_reason is not None:
                raise GraphError('ERR_TEXT_DELIMITER_TAIL', node=node_id,
                               detail=f"{violation_reason}")

        # ERR_RANK (missing-rank arm only; stage 6 handles sibling-uniqueness)
        if node_type == 'ordered-part':
            if 'rank' not in node or node['rank'] is None:
                raise GraphError('ERR_RANK', node=node_id,
                               detail="ordered-part node missing 'rank' field")

    # ========== STAGE 4: Edge fields (edge-list order) ==========
    valid_edge_types = {'has-attribute', 'composed-of', 'explains'}
    edge_idx = 0
    for edge in edges:
        edge_type = edge.get('type')
        from_id = edge.get('from')
        to_id = edge.get('to')

        # ERR_UNKNOWN_EDGE_TYPE
        if edge_type not in valid_edge_types:
            raise GraphError('ERR_UNKNOWN_EDGE_TYPE', edge=edge_idx,
                           detail=f"Unknown edge type '{edge_type}'")

        # Find node types
        from_node = next((n for n in nodes if n.get('id') == from_id), None)
        to_node = next((n for n in nodes if n.get('id') == to_id), None)
        from_type = from_node.get('type') if from_node else None
        to_type = to_node.get('type') if to_node else None

        # ERR_ATTR_UNDER_ATTR (has-attribute from an attribute)
        if edge_type == 'has-attribute' and from_type == 'attribute':
            raise GraphError('ERR_ATTR_UNDER_ATTR', edge=edge_idx,
                           detail="has-attribute cannot originate from an attribute node")

        # ERR_CONCEPT_DEPTH (any edge whose to-node is a concept)
        if to_type == 'concept':
            raise GraphError('ERR_CONCEPT_DEPTH', edge=edge_idx,
                           detail="Concepts cannot be targets (children); they are roots only")

        # ERR_EDGE_TYPE_MISMATCH (endpoint types outside data-model table)
        # Data model validations per contracts/kg-schema.md:
        # has-attribute: from=(concept|part|explanation), to=attribute
        # composed-of: from=(concept|attribute|explanation|ordered-part|unordered-part), to=(ordered-part|unordered-part)
        # explains: from=any, to=explanation
        if edge_type == 'has-attribute':
            if from_type not in ('concept', 'ordered-part', 'unordered-part', 'explanation'):
                raise GraphError('ERR_EDGE_TYPE_MISMATCH', edge=edge_idx,
                               detail=f"has-attribute: 'from' type '{from_type}' invalid")
            if to_type != 'attribute':
                raise GraphError('ERR_EDGE_TYPE_MISMATCH', edge=edge_idx,
                               detail=f"has-attribute: 'to' type must be 'attribute', got '{to_type}'")
        elif edge_type == 'composed-of':
            if from_type not in ('concept', 'attribute', 'explanation', 'ordered-part', 'unordered-part'):
                raise GraphError('ERR_EDGE_TYPE_MISMATCH', edge=edge_idx,
                               detail=f"composed-of: 'from' type '{from_type}' invalid")
            if to_type not in ('ordered-part', 'unordered-part'):
                raise GraphError('ERR_EDGE_TYPE_MISMATCH', edge=edge_idx,
                               detail=f"composed-of: 'to' type must be part, got '{to_type}'")
        elif edge_type == 'explains':
            if to_type != 'explanation':
                raise GraphError('ERR_EDGE_TYPE_MISMATCH', edge=edge_idx,
                               detail=f"explains: 'to' type must be 'explanation', got '{to_type}'")

        edge_idx += 1

    # ========== STAGE 5: Tree invariants ==========
    children, parent_of = _get_children(graph)

    # ERR_MULTIPLE_PARENTS: exactly one parent per non-root node
    for child_id, parent_id in parent_of.items():
        # Count how many edges have this child as 'to'
        parent_count = sum(1 for e in edges if e.get('to') == child_id)
        if parent_count > 1:
            raise GraphError('ERR_MULTIPLE_PARENTS', node=child_id,
                           detail=f"Node has {parent_count} parents")

    # ERR_CYCLE: no cycles in parent-pointer walk
    def has_cycle(child_id: str) -> bool:
        """Check if following parent pointers from child_id leads to a cycle."""
        visited = set()
        current = child_id
        while current in parent_of:
            if current in visited:
                return True
            visited.add(current)
            current = parent_of[current]
        return False

    for node_id in node_ids:
        if has_cycle(node_id):
            raise GraphError('ERR_CYCLE', node=node_id,
                           detail="Cycle detected in parent pointer chain")

    # ERR_NO_ROOT: at least one concept node with no parent
    root_concepts = []
    for node in nodes:
        node_id = node.get('id')
        node_type = node.get('type')
        if node_type == 'concept' and node_id not in parent_of:
            root_concepts.append(node_id)

    if not root_concepts:
        raise GraphError('ERR_NO_ROOT', detail="No root concept nodes found")

    # ERR_ORPHAN: every non-root node reachable from at least one root concept
    def reachable_from_roots() -> Set[str]:
        """Return set of all nodes reachable from root concepts."""
        reachable = set()

        def dfs(node_id: str):
            if node_id in reachable:
                return
            reachable.add(node_id)
            if node_id in children:
                for _edge_type, child_id in children[node_id]:
                    dfs(child_id)

        for root_id in root_concepts:
            dfs(root_id)

        return reachable

    reachable = reachable_from_roots()
    for node_id in node_ids:
        if node_id not in reachable:
            raise GraphError('ERR_ORPHAN', node=node_id,
                           detail="Node is not reachable from any root concept")

    # ========== STAGE 6: Role composition (parent-node order) ==========
    for node in nodes:
        parent_id = node.get('id')
        if parent_id not in children:
            continue

        child_edges = children[parent_id]

        # Get child types per edge
        ordered_parts = []
        unordered_parts = []
        attributes = []
        explanations = []

        for edge_type, child_id in child_edges:
            child_node = next((n for n in nodes if n.get('id') == child_id), None)
            child_type = child_node.get('type') if child_node else None

            if edge_type == 'has-attribute':
                attributes.append(child_id)
            elif edge_type == 'composed-of':
                if child_type == 'ordered-part':
                    ordered_parts.append(child_id)
                elif child_type == 'unordered-part':
                    unordered_parts.append(child_id)
            elif edge_type == 'explains':
                explanations.append(child_id)

        # ERR_MIXED_PART_ORDER: cannot have both ordered and unordered parts under one parent
        if ordered_parts and unordered_parts:
            raise GraphError('ERR_MIXED_PART_ORDER', node=parent_id,
                           detail="Node has both ordered-part and unordered-part children")

        # ERR_MIXED_CHILD_ROLE: cannot have both attribute children and part children
        has_parts = bool(ordered_parts or unordered_parts)
        if attributes and has_parts:
            raise GraphError('ERR_MIXED_CHILD_ROLE', node=parent_id,
                           detail="Node has both attribute children and part children")

        # ERR_MULTIPLE_SUMMARIES: >1 non-leaf explanation per parent
        # A non-leaf explanation is one that has children
        non_leaf_explanations = []
        for exp_id in explanations:
            if exp_id in children and children[exp_id]:
                non_leaf_explanations.append(exp_id)

        if len(non_leaf_explanations) > 1:
            raise GraphError('ERR_MULTIPLE_SUMMARIES', node=parent_id,
                           detail=f"Node has {len(non_leaf_explanations)} non-leaf explanation children (max 1)")

        # ERR_RANK (sibling-uniqueness arm): ordered parts must have unique rank among siblings
        if ordered_parts:
            ranks = []
            for part_id in ordered_parts:
                part_node = next((n for n in nodes if n.get('id') == part_id), None)
                if part_node:
                    rank = part_node.get('rank')
                    ranks.append(rank)

            if len(ranks) != len(set(ranks)):
                # Find duplicate
                seen = set()
                for rank in ranks:
                    if rank in seen:
                        raise GraphError('ERR_RANK', node=parent_id,
                                       detail=f"Duplicate rank {rank} among ordered-part siblings")
                    seen.add(rank)


def main():
    """CLI entry point: python3 kg.py <graph.json>"""
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 kg.py <graph.json>\n")
        sys.exit(2)

    graph_path = sys.argv[1]

    try:
        graph = load_graph(graph_path)
        validate_graph(graph)
        print("OK")
        sys.exit(0)
    except GraphError as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(2)
    except Exception as e:
        sys.stderr.write(f"FATAL: {e}\n")
        sys.exit(2)


if __name__ == '__main__':
    main()
