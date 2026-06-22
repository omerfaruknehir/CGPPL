import pytest

from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_set_node_attr_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => set node "missing" attr "kind" = "new"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing set target for node "missing" with attr "kind" in rule main'


def test_set_edge_attr_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => set edge "missing" attr "weight" = 2; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing set target for edge "missing" with attr "weight" in rule main'


def test_set_node_label_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => set node "missing" label "Selected"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing set target for node "missing" with label "Selected" in rule main'


def test_set_edge_label_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => set edge "missing" label "selected"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing set target for edge "missing" with label "selected" in rule main'


def test_unset_node_attr_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => unset node "missing" attr "kind"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing unset target for node "missing" with attr "kind" in rule main'


def test_unset_edge_attr_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => unset edge "missing" attr "weight"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing unset target for edge "missing" with attr "weight" in rule main'


def test_unset_node_label_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => unset node "missing" label "Selected"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing unset target for node "missing" with label "Selected" in rule main'


def test_unset_edge_label_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => unset edge "missing" label "selected"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing unset target for edge "missing" with label "selected" in rule main'


def test_bound_set_node_label_target_failure_reports_structured_context():
    program = parse_program(
        'program Demo { rule main => { match node $n; delete node $n; set node $n label "Selected"; } }'
    )
    graph = Graph.empty().add_node(Node("a"))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == 'missing set target for node $n with label "Selected" in rule main'


def test_bound_unset_edge_attr_target_failure_reports_structured_context():
    program = parse_program(
        'program Demo { rule main => { match edge $e; delete edge $e; unset edge $e attr "weight"; } }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("e1", "a", "b", attrs=(("weight", 2),)),),
    )

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == 'missing unset target for edge $e with attr "weight" in rule main'
