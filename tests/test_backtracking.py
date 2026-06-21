import json

import pytest

from cgppl.cli import main
from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import RuleFailed, execute_program


def test_block_backtracks_node_match_when_later_statement_fails():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Candidate"; '
        'require node $n attr "kind" = "winner"; set node $n label "Selected"; } }'
    )
    graph = Graph(
        nodes=(
            Node("first", labels=["Candidate"], attrs={"kind": "loser"}),
            Node("second", labels=["Candidate"], attrs={"kind": "winner"}),
        )
    )

    result = execute_program(program, graph)

    assert not result.graph.get_node("first").has_label("Selected")
    assert result.graph.get_node("second").has_label("Selected")


def test_match_node_attribute_predicate_filters_candidates_directly():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Candidate" attr "kind" = "winner"; '
        'set node $n label "Selected"; } }'
    )
    graph = Graph(
        nodes=(
            Node("first", labels=["Candidate"], attrs={"kind": "loser"}),
            Node("second", labels=["Candidate"], attrs={"kind": "winner"}),
        )
    )

    result = execute_program(program, graph)

    assert not result.graph.get_node("first").has_label("Selected")
    assert result.graph.get_node("second").has_label("Selected")


def test_match_node_attribute_predicate_is_type_sensitive():
    program = parse_program('program Demo { rule main => match node $n attr "flag" = true; }')
    graph = Graph.empty().add_node(Node("n1", attrs={"flag": 1}))

    with pytest.raises(RuleFailed, match="no node matched"):
        execute_program(program, graph)


def test_block_backtracks_edge_match_when_later_statement_fails():
    program = parse_program(
        'program Demo { rule main => { match edge $e from $a to $b label "link"; '
        'require node $b attr "kind" = "target"; set node $b label "Reached"; delete edge $e; } }'
    )
    graph = Graph(
        nodes=(
            Node("source"),
            Node("wrong", attrs={"kind": "noise"}),
            Node("right", attrs={"kind": "target"}),
        ),
        edges=(
            Edge("bad", "source", "wrong", labels=["link"]),
            Edge("good", "source", "right", labels=["link"]),
        ),
    )

    result = execute_program(program, graph)

    assert result.graph.has_edge("bad")
    assert not result.graph.has_edge("good")
    assert not result.graph.get_node("wrong").has_label("Reached")
    assert result.graph.get_node("right").has_label("Reached")


def test_match_edge_attribute_predicate_filters_candidates_directly():
    program = parse_program(
        'program Demo { rule main => { match edge $e from $a to $b label "link" attr "weight" = 7; '
        'set node $b label "Reached"; delete edge $e; } }'
    )
    graph = Graph(
        nodes=(Node("source"), Node("wrong"), Node("right")),
        edges=(
            Edge("bad", "source", "wrong", labels=["link"], attrs={"weight": 1}),
            Edge("good", "source", "right", labels=["link"], attrs={"weight": 7}),
        ),
    )

    result = execute_program(program, graph)

    assert result.graph.has_edge("bad")
    assert not result.graph.has_edge("good")
    assert not result.graph.get_node("wrong").has_label("Reached")
    assert result.graph.get_node("right").has_label("Reached")


def test_match_edge_supports_multiple_attribute_predicates():
    program = parse_program(
        'program Demo { rule main => { match edge $e attr "weight" = 7 attr "active" = true; '
        'set edge $e label "Selected"; } }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(
            Edge("wrong", "a", "b", attrs={"weight": 7, "active": False}),
            Edge("right", "a", "b", attrs={"weight": 7, "active": True}),
        ),
    )

    result = execute_program(program, graph)

    assert not result.graph.get_edge("wrong").has_label("Selected")
    assert result.graph.get_edge("right").has_label("Selected")


def test_block_backtracks_earlier_node_candidate_to_make_later_edge_match_succeed():
    program = parse_program(
        'program Demo { rule main => { match node $a label "Root"; '
        'match edge $e from $a to $b label "link"; '
        'require node $b attr "kind" = "target"; set node $b label "Reached"; } }'
    )
    graph = Graph(
        nodes=(
            Node("root1", labels=["Root"]),
            Node("root2", labels=["Root"]),
            Node("bad", attrs={"kind": "noise"}),
            Node("target", attrs={"kind": "target"}),
        ),
        edges=(
            Edge("e1", "root1", "bad", labels=["link"]),
            Edge("e2", "root2", "target", labels=["link"]),
        ),
    )

    result = execute_program(program, graph)

    assert not result.graph.get_node("bad").has_label("Reached")
    assert result.graph.get_node("target").has_label("Reached")


def test_block_backtracking_fails_after_exhausting_all_candidates():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Candidate"; '
        'require node $n attr "kind" = "winner"; } }'
    )
    graph = Graph(
        nodes=(
            Node("first", labels=["Candidate"], attrs={"kind": "loser"}),
            Node("second", labels=["Candidate"], attrs={"kind": "also-loser"}),
        )
    )

    with pytest.raises(RuleFailed, match="attribute mismatch"):
        execute_program(program, graph)


def test_run_command_backtracks_match_candidate(tmp_path, capsys):
    source_path = tmp_path / "backtracking.cgppl"
    source_path.write_text(
        'program Backtracking { rule main => { match node $n; '
        'require node $n label "Leaf"; set node $n label "Selected"; } }',
        encoding="utf-8",
    )

    graph_payload = {
        "nodes": [
            {"id": "n1", "labels": ["Root"]},
            {"id": "n2", "labels": ["Leaf"]},
        ],
        "edges": [],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path), "--compact"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        "nodes": [
            {"id": "n1", "labels": ["Root"], "attrs": {}},
            {"id": "n2", "labels": ["Leaf", "Selected"], "attrs": {}},
        ],
        "edges": [],
    }


def test_run_command_filters_match_candidates_by_attribute(tmp_path, capsys):
    source_path = tmp_path / "match-attrs.cgppl"
    source_path.write_text(
        'program MatchAttrs { rule main => { match node $n label "Candidate" attr "kind" = "winner"; '
        'set node $n label "Selected"; } }',
        encoding="utf-8",
    )

    graph_payload = {
        "nodes": [
            {"id": "n1", "labels": ["Candidate"], "attrs": {"kind": "loser"}},
            {"id": "n2", "labels": ["Candidate"], "attrs": {"kind": "winner"}},
        ],
        "edges": [],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path), "--compact"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        "nodes": [
            {"id": "n1", "labels": ["Candidate"], "attrs": {"kind": "loser"}},
            {"id": "n2", "labels": ["Candidate", "Selected"], "attrs": {"kind": "winner"}},
        ],
        "edges": [],
    }
