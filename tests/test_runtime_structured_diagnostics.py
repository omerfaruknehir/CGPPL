from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


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

    try:
        execute_program(program, graph)
    except GraphMatchFailed as error:
        assert str(error) == (
            'no match for node $n with label "Root", label "Selected", '
            'attr "kind" = "root", where attr "rank" >= 2 in rule main'
        )
    else:
        raise AssertionError("expected GraphMatchFailed")


def test_match_edge_runtime_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => match edge $e from "a" to "b" '
        'label "link" where attr("weight") >= 2; }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("e1", "a", "b", labels=("link",), attrs=(("weight", 1),)),),
    )

    try:
        execute_program(program, graph)
    except GraphMatchFailed as error:
        assert str(error) == (
            'no match for edge $e from "a" to "b" with label "link", '
            'where attr "weight" >= 2 in rule main'
        )
    else:
        raise AssertionError("expected GraphMatchFailed")


def test_negative_node_runtime_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => require no node $bad '
        'label "Denied" attr "active" = true; }'
    )
    graph = Graph(nodes=(Node("bad", labels=("Denied",), attrs=(("active", True),)),))

    try:
        execute_program(program, graph)
    except GraphMatchFailed as error:
        assert str(error) == (
            'forbidden match for node $bad with label "Denied", '
            'attr "active" = true in rule main'
        )
    else:
        raise AssertionError("expected GraphMatchFailed")


def test_negative_edge_runtime_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => { match node $target label "Target"; '
        'require no edge $e from "a" to $target label "denied" '
        'where target == $target; } }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b", labels=("Target",))),
        edges=(Edge("e1", "a", "b", labels=("denied",)),),
    )

    try:
        execute_program(program, graph)
    except GraphMatchFailed as error:
        assert str(error) == (
            'forbidden match for edge $e from "a" to $target with label "denied", '
            'where field target == $target in rule main'
        )
    else:
        raise AssertionError("expected GraphMatchFailed")
