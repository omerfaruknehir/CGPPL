import pytest

from cgppl.graph import Graph
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_set_node_attr_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => set node "missing" attr "kind" = "new"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing set target for node "missing" with attr "kind" in rule main'


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


def test_unset_edge_label_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => unset edge "missing" label "selected"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing unset target for edge "missing" with label "selected" in rule main'
