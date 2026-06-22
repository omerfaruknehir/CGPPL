import pytest

from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_auto_create_unbound_endpoint_variables_create_nodes_and_bind_for_later_use():
    program = parse_program(
        'program Demo { rule main => { '
        'add edge $e from add $source to add $target label "new"; '
        'set node $source label "Source"; '
        'set node $target label "Target"; '
        'require edge $e; '
        '} }'
    )

    result = execute_program(program, Graph.empty())

    assert result.graph.node_ids == ("source", "target")
    assert result.graph.get_node("source").labels == ("Source",)
    assert result.graph.get_node("target").labels == ("Target",)
    assert result.graph.get_edge("e") == Edge("e", "source", "target", labels=("new",))


def test_auto_create_literal_endpoints_create_missing_nodes_and_keep_existing_nodes():
    program = parse_program(
        'program Demo { rule main => add edge "e" from add "source" to add "target" label "new"; }'
    )
    graph = Graph(nodes=(Node("target", labels=("Existing",)),))

    result = execute_program(program, graph)

    assert result.graph.node_ids == ("target", "source")
    assert result.graph.get_node("target").labels == ("Existing",)
    assert result.graph.get_node("source").labels == ()
    assert result.graph.get_edge("e") == Edge("e", "source", "target", labels=("new",))


def test_mixed_auto_create_keeps_strict_preconditions_for_unmarked_endpoint():
    program = parse_program(
        'program Demo { rule main => add edge $e from add $source to $target label "new"; }'
    )

    with pytest.raises(GraphMatchFailed, match="unbound edge target variable \\$target"):
        execute_program(program, Graph.empty())


def test_auto_create_bound_endpoint_variable_ensures_deleted_node_exists_again():
    program = parse_program(
        'program Demo { rule main => { '
        'match node $source label "Source"; '
        'delete node $source; '
        'add edge $e from add $source to add "target" label "new"; '
        'require node $source; '
        '} }'
    )
    graph = Graph(nodes=(Node("source", labels=("Source",)),))

    result = execute_program(program, graph)

    assert result.graph.node_ids == ("source", "target")
    assert result.graph.get_node("source").labels == ()
    assert result.graph.get_edge("e") == Edge("e", "source", "target", labels=("new",))
