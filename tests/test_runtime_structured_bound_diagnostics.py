import pytest

from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


@pytest.mark.xfail(reason="bound matcher failures are not wired to structured diagnostics yet")
def test_bound_node_matcher_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => { '
        'match node $n label "Root"; '
        'match node $n label "Selected" where attr("rank") >= 2; '
        '} }'
    )
    graph = Graph(nodes=(Node("root", labels=("Root",), attrs=(("rank", 1),)),))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == (
        'no match for node $n with label "Selected", '
        'where attr "rank" >= 2 in rule main'
    )


@pytest.mark.xfail(reason="bound matcher failures are not wired to structured diagnostics yet")
def test_bound_edge_matcher_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => { '
        'match edge $e from "a" to "b" label "link"; '
        'match edge $e from "a" to "b" label "selected" where attr("weight") >= 2; '
        '} }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("e1", "a", "b", labels=("link",), attrs=(("weight", 1),)),),
    )

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == (
        'no match for edge $e with label "selected", '
        'where attr "weight" >= 2 in rule main'
    )
