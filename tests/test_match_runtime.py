import pytest

from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_match_node_label_binds_variable_for_later_delete():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Root"; delete node $n; } }'
    )
    graph = Graph(
        nodes=(Node("a", labels=["Root"]), Node("b", labels=["Leaf"])),
        edges=(Edge("e1", "a", "b"),),
    )

    result = execute_program(program, graph)

    assert result.graph.node_ids == ("b",)
    assert result.graph.edge_ids == ()


def test_match_node_label_can_bind_variable_for_later_attribute_mutation():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Root"; set node $n attr "seen" = true; } }'
    )
    graph = Graph.empty().add_node(Node("a", labels=["Root"]))

    result = execute_program(program, graph)

    assert result.graph.get_node("a").attr("seen") is True


def test_match_node_label_fails_when_no_candidate_matches():
    program = parse_program('program Demo { rule main => match node $n label "Root"; }')
    graph = Graph.empty().add_node(Node("a", labels=["Leaf"]))

    with pytest.raises(GraphMatchFailed, match="no node matched"):
        execute_program(program, graph)


def test_unbound_variable_reference_fails_clearly():
    program = parse_program('program Demo { rule main => delete node $n; }')

    with pytest.raises(GraphMatchFailed, match="unbound node variable"):
        execute_program(program, Graph.empty())


def test_match_edge_label_binds_edge_and_endpoint_variables():
    program = parse_program(
        'program Demo { rule main => { match edge $e from $a to $b label "link"; '
        'set node $a label "Source"; set node $b label "Target"; delete edge $e; } }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b"), Node("c")),
        edges=(Edge("noise", "b", "c"), Edge("e1", "a", "b", labels=["link"])),
    )

    result = execute_program(program, graph)

    assert result.graph.edge_ids == ("noise",)
    assert result.graph.get_node("a").has_label("Source")
    assert result.graph.get_node("b").has_label("Target")


def test_match_edge_honors_bound_endpoint_variable():
    program = parse_program(
        'program Demo { rule main => { match node $a label "Root"; '
        'match edge $e from $a to $b label "link"; set node $b label "Reached"; } }'
    )
    graph = Graph(
        nodes=(Node("a", labels=["Root"]), Node("b"), Node("c")),
        edges=(Edge("wrong", "c", "b", labels=["link"]), Edge("right", "a", "b", labels=["link"])),
    )

    result = execute_program(program, graph)

    assert result.graph.get_node("b").has_label("Reached")
    assert not result.graph.get_node("c").has_label("Reached")
