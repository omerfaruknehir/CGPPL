import json

import pytest

from cgppl.ast import (
    AttrExpr,
    BlockStmt,
    FieldExpr,
    LiteralExpr,
    MatchEdgeStmt,
    MatchNodeStmt,
    SetEdgeLabelStmt,
    SetNodeLabelStmt,
    VarRef,
    WherePredicate,
)
from cgppl.cli import main
from cgppl.graph import Edge, Graph, Node
from cgppl.parser import ParserError, parse_program
from cgppl.runtime import RuleFailed, execute_program


def test_parses_node_match_with_where_attribute_comparison():
    program = parse_program(
        'program Demo { rule main => match node $n label "Candidate" where attr("score") >= 10; }'
    )

    assert program.rules[0].body == MatchNodeStmt(
        VarRef("n"),
        "Candidate",
        (),
        (WherePredicate(AttrExpr("score"), ">=", LiteralExpr(10)),),
    )


def test_parses_edge_match_with_where_field_comparison():
    program = parse_program(
        "program Demo { rule main => match edge $e from $a to $b where source != target; }"
    )

    assert program.rules[0].body == MatchEdgeStmt(
        VarRef("e"),
        VarRef("a"),
        VarRef("b"),
        None,
        (),
        (WherePredicate(FieldExpr("source"), "!=", FieldExpr("target")),),
    )


def test_parses_multiple_where_predicates_as_conjunction():
    program = parse_program(
        'program Demo { rule main => match node $n where attr(score) >= 10 where id != "blocked"; }'
    )

    assert program.rules[0].body == MatchNodeStmt(
        VarRef("n"),
        None,
        (),
        (
            WherePredicate(AttrExpr("score"), ">=", LiteralExpr(10)),
            WherePredicate(FieldExpr("id"), "!=", LiteralExpr("blocked")),
        ),
    )


def test_rejects_invalid_where_operand():
    with pytest.raises(ParserError, match="expected where operand"):
        parse_program('program Demo { rule main => match node $n where helper >= 10; }')


def test_match_node_where_filters_numeric_candidates():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Candidate" where attr("score") >= 10; '
        'set node $n label "Selected"; } }'
    )
    graph = Graph(
        nodes=(
            Node("low", labels=["Candidate"], attrs={"score": 3}),
            Node("high", labels=["Candidate"], attrs={"score": 10}),
        )
    )

    result = execute_program(program, graph)

    assert not result.graph.get_node("low").has_label("Selected")
    assert result.graph.get_node("high").has_label("Selected")


def test_match_node_where_supports_field_and_attr_conjunction():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Candidate" '
        'where attr("score") >= 10 where id != "blocked"; set node $n label "Selected"; } }'
    )
    graph = Graph(
        nodes=(
            Node("blocked", labels=["Candidate"], attrs={"score": 99}),
            Node("chosen", labels=["Candidate"], attrs={"score": 11}),
        )
    )

    result = execute_program(program, graph)

    assert not result.graph.get_node("blocked").has_label("Selected")
    assert result.graph.get_node("chosen").has_label("Selected")


def test_match_node_where_comparisons_are_type_sensitive():
    program = parse_program('program Demo { rule main => match node $n where attr("score") >= 10; }')
    graph = Graph.empty().add_node(Node("n1", attrs={"score": "10"}))

    with pytest.raises(
        RuleFailed,
        match=r'no match for node \$n with where attr "score" >= 10 in rule main',
    ):
        execute_program(program, graph)


def test_match_edge_where_filters_endpoint_fields():
    program = parse_program(
        'program Demo { rule main => { match edge $e where source != target; set edge $e label "Selected"; } }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(
            Edge("loop", "a", "a"),
            Edge("forward", "a", "b"),
        ),
    )

    result = execute_program(program, graph)

    assert not result.graph.get_edge("loop").has_label("Selected")
    assert result.graph.get_edge("forward").has_label("Selected")


def test_match_edge_where_filters_attribute_comparisons():
    program = parse_program(
        'program Demo { rule main => { match edge $e label "link" where attr("weight") > 1; '
        'set edge $e label "Heavy"; } }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(
            Edge("light", "a", "b", labels=["link"], attrs={"weight": 1}),
            Edge("heavy", "a", "b", labels=["link"], attrs={"weight": 2}),
        ),
    )

    result = execute_program(program, graph)

    assert not result.graph.get_edge("light").has_label("Heavy")
    assert result.graph.get_edge("heavy").has_label("Heavy")


def test_where_filters_inside_block_backtracking():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Candidate" where attr("score") >= 10; '
        'set node $n label "Selected"; fail; } }'
    )
    graph = Graph(
        nodes=(
            Node("first", labels=["Candidate"], attrs={"score": 10}),
            Node("second", labels=["Candidate"], attrs={"score": 20}),
        )
    )

    with pytest.raises(RuleFailed, match="rule failed"):
        execute_program(program, graph)

    assert not graph.get_node("first").has_label("Selected")
    assert not graph.get_node("second").has_label("Selected")


def test_run_command_filters_match_candidates_with_where(tmp_path, capsys):
    source_path = tmp_path / "match-where.cgppl"
    source_path.write_text(
        'program MatchWhere { rule main => { match node $n label "Candidate" where attr("score") >= 10; '
        'set node $n label "Selected"; } }',
        encoding="utf-8",
    )

    graph_payload = {
        "nodes": [
            {"id": "n1", "labels": ["Candidate"], "attrs": {"score": 3}},
            {"id": "n2", "labels": ["Candidate"], "attrs": {"score": 10}},
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
            {"id": "n1", "labels": ["Candidate"], "attrs": {"score": 3}},
            {"id": "n2", "labels": ["Candidate", "Selected"], "attrs": {"score": 10}},
        ],
        "edges": [],
    }
