import pytest

from cgppl.ast import AddEdgeStmt, AddNodeStmt, MatchEdgeStmt, MatchNodeStmt, RequireNoNodeStmt, VarRef
from cgppl.graph import Edge, Graph, Node
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

    assert add_node == AddNodeStmt("generated", labels=("Generated", "Replacement"))
    assert add_edge == AddEdgeStmt("new-link", "n1", "generated", labels=("new", "owned"))
    assert match_node == MatchNodeStmt(VarRef("n"), labels=("Generated", "Replacement"))
    assert match_edge == MatchEdgeStmt(VarRef("e"), "n1", VarRef("n"), labels=("new", "owned"))


def test_constructed_node_receives_all_inline_labels_and_can_be_matched_immediately():
    program = parse_program(
        'program Demo { rule main => { '
        'add node "generated" label "Generated" label "Replacement"; '
        'match node $n label "Generated" label "Replacement"; '
        'set node $n label "Selected"; '
        '} }'
    )

    result = execute_program(program, Graph.empty())

    assert result.graph.get_node("generated").labels == ("Generated", "Replacement", "Selected")


def test_multi_label_node_match_requires_all_labels_and_backtracks():
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
    assert result.graph.get_node("complete").labels == ("Generated", "Replacement", "Selected")


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

    assert result.graph.get_edge("e").labels == ("Selected", "new", "owned")


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

    assert program.rules[0].body == RequireNoNodeStmt(
        VarRef("bad"), labels=("Generated", "Blocked")
    )


def test_rejects_duplicate_same_label_in_matcher():
    with pytest.raises(ParserError, match="duplicate node label matcher"):
        parse_program('program Demo { rule main => match node $n label "A" label "A"; }')
