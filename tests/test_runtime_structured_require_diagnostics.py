import pytest

from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


@pytest.mark.xfail(reason="positive require runtime paths are not wired to structured diagnostics yet")
def test_require_node_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => require node "missing"; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == 'missing requirement for node "missing" in rule main'


@pytest.mark.xfail(reason="positive require runtime paths are not wired to structured diagnostics yet")
def test_require_edge_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => require edge $e; }')

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, Graph.empty())

    assert str(error.value) == "unbound edge variable $e in rule main"


@pytest.mark.xfail(reason="positive require runtime paths are not wired to structured diagnostics yet")
def test_require_node_label_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => require node "a" label "Root"; }')
    graph = Graph.empty().add_node(Node("a", labels=("Leaf",)))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == 'missing requirement for node "a" with label "Root" in rule main'


@pytest.mark.xfail(reason="positive require runtime paths are not wired to structured diagnostics yet")
def test_require_edge_label_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => require edge "e1" label "link"; }')
    graph = Graph(nodes=(Node("a"), Node("b")), edges=(Edge("e1", "a", "b"),))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == 'missing requirement for edge "e1" with label "link" in rule main'


@pytest.mark.xfail(reason="positive require runtime paths are not wired to structured diagnostics yet")
def test_require_node_attr_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => require node "a" attr "kind" = "root"; }')
    graph = Graph.empty().add_node(Node("a", attrs={"kind": "leaf"}))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == (
        'missing requirement for node "a" with attr "kind" = "root"; '
        'found "leaf" in rule main'
    )


@pytest.mark.xfail(reason="positive require runtime paths are not wired to structured diagnostics yet")
def test_require_edge_attr_runtime_failure_reports_structured_context():
    program = parse_program('program Demo { rule main => require edge "e1" attr "weight" = 2; }')
    graph = Graph(nodes=(Node("a"), Node("b")), edges=(Edge("e1", "a", "b"),))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == (
        'missing requirement for edge "e1" with attr "weight" = 2; '
        "found <missing> in rule main"
    )
