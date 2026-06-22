import pytest

from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


@pytest.mark.xfail(reason="runtime predicate failures are not wired to structured diagnostics yet")
def test_match_node_runtime_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => match node $n label "Root" label "Selected" '
        'attr "kind" = "root" where attr("rank") >= 2; }'
    )
    graph = Graph(
        nodes=(
            Node(
                "candidate",
                labels=("Root",),
                attrs=(("kind", "root"), ("rank", 1)),
            ),
        )
    )

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == (
        'no match for node $n with label "Root", label "Selected", '
        'attr "kind" = "root", where attr "rank" >= 2 in rule main'
    )


@pytest.mark.xfail(reason="runtime predicate failures are not wired to structured diagnostics yet")
def test_match_edge_runtime_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => match edge $e from "a" to "b" '
        'label "link" where attr("weight") >= 2; }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("e1", "a", "b", labels=("link",), attrs=(("weight", 1),)),),
    )

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == (
        'no match for edge $e with label "link", '
        'where attr "weight" >= 2 in rule main'
    )


@pytest.mark.xfail(reason="runtime predicate failures are not wired to structured diagnostics yet")
def test_negative_node_runtime_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => require no node $blocked '
        'label "Blocked" attr "active" = true; }'
    )
    graph = Graph(nodes=(Node("bad", labels=("Blocked",), attrs=(("active", True),)),))

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == (
        'forbidden match for node $blocked with label "Blocked", '
        'attr "active" = true in rule main'
    )


@pytest.mark.xfail(reason="runtime predicate failures are not wired to structured diagnostics yet")
def test_negative_edge_runtime_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => { match node $target label "Target"; '
        'require no edge $blocked from "a" to $target label "blocked" '
        'where target == $target; } }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b", labels=("Target",))),
        edges=(Edge("e1", "a", "b", labels=("blocked",)),),
    )

    with pytest.raises(GraphMatchFailed) as error:
        execute_program(program, graph)

    assert str(error.value) == (
        'forbidden match for edge $blocked with label "blocked", '
        'where field target == $target in rule main'
    )
