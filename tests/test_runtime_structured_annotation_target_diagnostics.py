import pytest

from cgppl.graph import Graph
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


@pytest.mark.xfail(reason="annotation mutation runtime paths are not wired to structured diagnostics yet")
def test_set_node_attr_missing_target_reports_structured_context():
    program = parse_program('program Demo { rule main => set node "missing" attr "kind" = "root"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing set target for node "missing" with attr "kind" in rule main'


@pytest.mark.xfail(reason="annotation mutation runtime paths are not wired to structured diagnostics yet")
def test_set_edge_label_missing_target_reports_structured_context():
    program = parse_program('program Demo { rule main => set edge "missing" label "link"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing set target for edge "missing" with label "link" in rule main'


@pytest.mark.xfail(reason="annotation mutation runtime paths are not wired to structured diagnostics yet")
def test_unset_node_attr_missing_target_reports_structured_context():
    program = parse_program('program Demo { rule main => unset node "missing" attr "kind"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing unset target for node "missing" with attr "kind" in rule main'


@pytest.mark.xfail(reason="annotation mutation runtime paths are not wired to structured diagnostics yet")
def test_unset_edge_label_missing_target_reports_structured_context():
    program = parse_program('program Demo { rule main => unset edge "missing" label "link"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing unset target for edge "missing" with label "link" in rule main'
