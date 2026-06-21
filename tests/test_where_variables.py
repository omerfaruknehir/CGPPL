import pytest

from cgppl.ast import FieldExpr, MatchNodeStmt, VarExpr, VarRef, WherePredicate
from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_parser_accepts_variable_operands_in_where_predicates():
    program = parse_program(
        'program Demo { rule main => { match node $target label "Selected"; '
        'match node $n where id == $target; } }'
    )

    assert program.rules[0].body.statements[1] == MatchNodeStmt(
        VarRef("n"),
        None,
        (),
        (WherePredicate(FieldExpr("id"), "==", VarExpr("target")),),
    )


def test_node_where_predicate_can_compare_id_to_bound_variable():
    program = parse_program(
        'program Demo { rule main => { match node $target label "Selected"; '
        'match node $n where id == $target; set node $n label "MatchedAgain"; } }'
    )
    graph = Graph(nodes=(Node("a"), Node("b", labels=("Selected",))))

    result = execute_program(program, graph)

    assert result.graph.get_node("a").labels == ()
    assert result.graph.get_node("b").labels == ("Selected", "MatchedAgain")


def test_edge_where_predicate_can_compare_endpoint_variables_after_binding():
    program = parse_program(
        'program Demo { rule main => { match edge $e from $a to $b where $a != $b; '
        'set edge $e label "NonLoop"; } }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("loop", "a", "a"), Edge("forward", "a", "b")),
    )

    result = execute_program(program, graph)

    assert result.graph.get_edge("loop").labels == ()
    assert result.graph.get_edge("forward").labels == ("NonLoop",)


def test_edge_where_predicate_can_compare_edge_variable_to_literal_id():
    program = parse_program(
        'program Demo { rule main => { match edge $e where $e == "selected"; '
        'set edge $e label "Picked"; } }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("ignored", "a", "b"), Edge("selected", "b", "a")),
    )

    result = execute_program(program, graph)

    assert result.graph.get_edge("ignored").labels == ()
    assert result.graph.get_edge("selected").labels == ("Picked",)


def test_where_predicate_rejects_unbound_variable_operand():
    program = parse_program('program Demo { rule main => match node $n where id == $missing; }')
    graph = Graph.empty().add_node(Node("a"))

    with pytest.raises(GraphMatchFailed, match="unbound where variable \\$missing"):
        execute_program(program, graph)
