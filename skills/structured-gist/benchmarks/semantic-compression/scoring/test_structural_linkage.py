from pathlib import Path

import structural_linkage as sl


def test_tree_distance_uses_edge_count_through_lca() -> None:
    assert sl.tree_distance(("root", "left", "leaf"), ("root", "right")) == 3
    assert sl.tree_distance(("root", "branch"), ("root", "branch", "leaf")) == 1


def test_multi_node_uses_minimum_path_combination() -> None:
    left = {"multi_node": [["root", "far"], ["root", "near", "leaf"]]}
    right = {"located": ["root", "near"]}
    assert sl.minimum_distance(left, right) == 1


def test_parser_recovers_ambiguous_marker_family_from_siblings(tmp_path: Path) -> None:
    rendering = tmp_path / "standard.md"
    rendering.write_text(
        """```text
- Groups
    A. alpha
    B. beta
    C. gamma
- Steps
    I. first
    II. second
```
""",
        encoding="utf-8",
    )

    nodes = sl.parse_outline(rendering)
    assert nodes[("Groups", "gamma")][0].marker_family == "nominal"
    assert nodes[("Steps", "first")][0].marker_family == "ordinal"


def test_real_corpus_has_11_renderings_and_expected_cause_chain_flags() -> None:
    report = sl.build_report()
    assert len(report["cases"]) == 8
    assert sum(case["rendering_count"] for case in report["cases"].values()) == 11

    expected = {"r1": True, "r2": True, "r3": False, "r4": True, "r5": True, "r6": True}
    for rendering in report["cases"]["cause-chain-reversal"]["renderings"].values():
        actual = {
            relation["id"]: relation["ordered"]
            for relation in rendering["relations"]
            if relation["id"] in expected
        }
        assert actual == expected
