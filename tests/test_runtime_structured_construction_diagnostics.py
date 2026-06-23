import pytest

from cgppl.graph import Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_add_node_duplicate_runtime_failure_reports_structured_target():
    program = parse_program('program Demo { rule main => add node "existing"; }')
    graph = Graph(nodes=(Node("existing"),))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == 'add node "existing" failed: duplicate node id: existing in rule main'


def test_add_edge_missing_endpoint_runtime_failure_reports_structured_target():
    program = parse_program('program Demo { rule main => add edge $edge from "source" to "missing"; }')
    graph = Graph(nodes=(Node("source"),))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == (
        'add edge $edge failed: edge edge references missing target node: missing in rule main'
    )


def test_add_edge_auto_created_endpoint_then_missing_target_reports_add_edge_context():
    program = parse_program(
        'program Demo { rule main => { match node $source; delete node $source; '
        'add edge "edge" from add $source to "target"; } }'
    )
    graph = Graph(nodes=(Node("source"),))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == (
        'add edge "edge" failed: edge edge references missing target node: target in rule main'
    )
