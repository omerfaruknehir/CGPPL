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
            'no match for edge $e with label "link", '
            'where attr "weight" >= 2 in rule main'
        )
    else:
        raise AssertionError("expected GraphMatchFailed")


def test_negative_node_runtime_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => require no node $blocked '
        'label "Blocked" attr "active" = true; }'
    )
    graph = Graph(nodes=(Node("bad", labels=("Blocked",), attrs=(("active", True),)),))

    try:
        execute_program(program, graph)
    except GraphMatchFailed as error:
        assert str(error) == (
            'forbidden match for node $blocked with label "Blocked", '
            'attr "active" = true in rule main'
        )
    else:
        raise AssertionError("expected GraphMatchFailed")


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

    try:
        execute_program(program, graph)
    except GraphMatchFailed as error:
        assert str(error) == (
            'forbidden match for edge $blocked with label "blocked", '
            'where field target == $target in rule main'
        )
    else:
        raise AssertionError("expected GraphMatchFailed")
