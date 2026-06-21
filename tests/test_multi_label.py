import pytest

from cgppl.ast import (
    AddEdgeStmt,
    AddNodeStmt,
    MatchEdgeStmt,
    MatchNodeStmt,
    RequireNoNodeStmt,
    VarRef,
)
from cgppl.graph import Graph, Node
from cgppl.parser import ParserError, parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_parses_multi_label_matchers_and_constructors():
    program = parse_program(
        'program Demo { rule main => { '
        'add node "generated" label "Generated" label "Replacement"; '
        'add edge "new-link" from "n1" to "generated" label "new" label "owned"; '
        'match node $n label "Generated" label "Replacement"; '
        'match edge $e from "n1" to $n label "new" label "owned"; '
        '} }'
    )

    add_node, add_edge, match_node, match_edge = program.rules[0].body.statements

    assert isinstance(add_node, AddNodeStmt)
    assert add_node.node_id == "generated"
    assert add_node.labels == ("Generated", "Replacement")

    assert isinstance(add_edge, AddEdgeStmt)
    assert add_edge.edge_id == "new-link"
    assert add_edge.source_id == "n1"
    assert add_edge.target_id == "generated"
    assert add_edge.labels == ("new", "owned")

    assert isinstance(match_node, MatchNodeStmt)
    assert match_node.node_id == VarRef("n")
    assert match_node.labels == ("Generated", "Replacement")

    assert isinstance(match_edge, MatchEdgeStmt)
    assert match_edge.edge_id == VarRef("e")
    assert match_edge.source_id == "n1"
    assert match_edge.target_id == VarRef("n")
    assert match_edge.labels == ("new", "owned")


def test_constructed_node_receives_all_inline_labels_and_can_be_matched_immediately():
    program = parse_program(
        'program Demo { rule main => { '
        'add node "generated" label "Generated" label "Replacement"; '
        'match node $n label "Generated" label "Replacement"; '
        'set node $n label "Selected"; '
        '} }'
    )

    result = execute_program(program, Graph.empty())

    assert set(result.graph.get_node("generated").labels) == {
        "Generated",
        "Replacement",
        "Selected",
    }


def test_multi_label_node_match_requires_all_labels():
    program = parse_program(
        'program Demo { rule main => { '
        'match node $n label "Generated" label "Replacement"; '
        'set node $n label "Selected"; '
        '} }'
    )
    graph = Graph(
        nodes=(
            Node("partial", labels=("Generated",)),
            Node("complete", labels=("Generated", "Replacement")),
        )
    )

    result = execute_program(program, graph)

    assert result.graph.get_node("partial").labels == ("Generated",)
    assert set(result.graph.get_node("complete").labels) == {
        "Generated",
        "Replacement",
        "Selected",
    }


def test_constructed_edge_receives_all_inline_labels_and_can_be_matched_immediately():
    program = parse_program(
        'program Demo { rule main => { '
        'add node "a"; add node "b"; '
        'add edge "e" from "a" to "b" label "new" label "owned"; '
        'match edge $e from "a" to "b" label "new" label "owned"; '
        'set edge $e label "Selected"; '
        '} }'
    )

    result = execute_program(program, Graph.empty())

    assert set(result.graph.get_edge("e").labels) == {"new", "owned", "Selected"}


def test_negative_node_requirement_with_multiple_labels_only_fails_when_all_labels_match():
    passing = parse_program(
        'program Demo { rule main => require no node $n label "Generated" label "Blocked"; }'
    )
    graph = Graph(nodes=(Node("partial", labels=("Generated",)),))

    assert execute_program(passing, graph).graph is graph

    failing_graph = Graph(nodes=(Node("bad", labels=("Generated", "Blocked")),))
    with pytest.raises(GraphMatchFailed, match="forbidden node matched"):
        execute_program(passing, failing_graph)


def test_parses_negative_node_requirement_with_multiple_labels():
    program = parse_program(
        'program Demo { rule main => require no node $bad label "Generated" label "Blocked"; }'
    )

    statement = program.rules[0].body
    assert isinstance(statement, RequireNoNodeStmt)
    assert statement.node_id == VarRef("bad")
    assert statement.labels == ("Generated", "Blocked")


def test_rejects_duplicate_same_label_in_matcher():
    with pytest.raises(ParserError, match="duplicate node label matcher"):
        parse_program('program Demo { rule main => match node $n label "A" label "A"; }')
