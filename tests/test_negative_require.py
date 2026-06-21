import pytest

from cgppl.ast import (
    AttrPredicate,
    BlockStmt,
    MatchNodeStmt,
    RequireNoEdgeStmt,
    RequireNoNodeStmt,
    VarRef,
)
from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_parses_negative_node_requirement_with_matcher_constraints():
    program = parse_program(
        'program Demo { rule main => '
        'require no node $n label "Excluded" attr "kind" = "bad"; }'
    )

    assert program.rules[0].body == RequireNoNodeStmt(
        VarRef("n"), "Excluded", (AttrPredicate("kind", "bad"),)
    )


def test_parses_negative_edge_requirement_with_endpoint_variables():
    program = parse_program(
        'program Demo { rule main => '
        'require no edge $e from $a to $b label "blocked"; }'
    )

    assert program.rules[0].body == RequireNoEdgeStmt(
        VarRef("e"), VarRef("a"), VarRef("b"), "blocked"
    )


def test_negative_node_requirement_passes_when_literal_node_is_absent():
    program = parse_program('program Demo { rule main => require no node "missing"; }')
    graph = Graph.empty().add_node(Node("a"))

    assert execute_program(program, graph).graph is graph


def test_negative_node_requirement_fails_when_literal_node_exists():
    program = parse_program('program Demo { rule main => require no node "a"; }')
    graph = Graph.empty().add_node(Node("a"))

    with pytest.raises(GraphMatchFailed, match="forbidden node matched"):
        execute_program(program, graph)


def test_negative_node_requirement_treats_unbound_variable_as_existential_wildcard():
    program = parse_program(
        'program Demo { rule main => { require no node $n label "Excluded"; '
        'match node $n label "Allowed"; set node $n label "Selected"; } }'
    )
    graph = Graph.empty().add_node(Node("a", labels=["Allowed"]))

    result = execute_program(program, graph)

    assert result.graph.get_node("a").labels == ("Allowed", "Selected")


def test_negative_node_requirement_fails_when_any_unbound_candidate_matches():
    program = parse_program('program Demo { rule main => require no node $n label "Excluded"; }')
    graph = Graph(
        nodes=(Node("a", labels=["Allowed"]), Node("b", labels=["Excluded"]))
    )

    with pytest.raises(GraphMatchFailed, match="forbidden node matched"):
        execute_program(program, graph)


def test_negative_edge_requirement_respects_previously_bound_endpoint_variables():
    program = parse_program(
        'program Demo { rule main => { match node $a label "Source"; '
        'match node $b label "Target"; '
        'require no edge $e from $a to $b label "blocked"; '
        'set node $a label "Clear"; } }'
    )
    graph = Graph(
        nodes=(Node("a", labels=["Source"]), Node("b", labels=["Target"])),
        edges=(Edge("e1", "a", "b", labels=["allowed"]),),
    )

    result = execute_program(program, graph)

    assert result.graph.get_node("a").labels == ("Clear", "Source")


def test_negative_edge_requirement_fails_when_forbidden_edge_exists():
    program = parse_program(
        'program Demo { rule main => { match node $a label "Source"; '
        'match node $b label "Target"; '
        'require no edge $e from $a to $b label "blocked"; } }'
    )
    graph = Graph(
        nodes=(Node("a", labels=["Source"]), Node("b", labels=["Target"])),
        edges=(Edge("e1", "a", "b", labels=["blocked"]),),
    )

    with pytest.raises(GraphMatchFailed, match="forbidden edge matched"):
        execute_program(program, graph)


def test_negative_requirements_do_not_bind_variables_when_they_pass():
    program = parse_program(
        'program Demo { rule main => { require no node $n label "Excluded"; '
        'match node $n label "Allowed"; } }'
    )

    assert program.rules[0].body == BlockStmt(
        (
            RequireNoNodeStmt(VarRef("n"), "Excluded"),
            MatchNodeStmt(VarRef("n"), "Allowed"),
        )
    )
