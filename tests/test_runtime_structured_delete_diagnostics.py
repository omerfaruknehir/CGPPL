import pytest

from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_delete_node_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => delete node "missing"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing delete target for node "missing" in rule main'


def test_delete_edge_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => delete edge "missing"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing delete target for edge "missing" in rule main'


def test_bound_delete_node_runtime_failure_reports_structured_context():
    program = parse_program(
        'program Demo { rule main => { match node $n; delete node $n; delete node $n; } }'
    )
    graph = Graph.empty().add_node(Node("a"))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == "missing delete target for node $n in rule main"


def test_bound_delete_edge_runtime_failure_reports_structured_context():
    program = parse_program(
        'program Demo { rule main => { match edge $e; delete edge $e; delete edge $e; } }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("e1", "a", "b"),),
    )

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == "missing delete target for edge $e in rule main"
