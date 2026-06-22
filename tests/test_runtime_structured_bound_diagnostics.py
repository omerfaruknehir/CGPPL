from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_bound_node_matcher_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => { '
        'match node $n label "Root"; '
        'match node $n label "Chosen" where attr("rank") >= 2; '
        '} }'
    )
    graph = Graph(nodes=(Node("root", labels=("Root",), attrs=(("rank", 1),)),))

    try:
        execute_program(program, graph)
    except GraphMatchFailed as error:
        assert str(error) == (
            'no match for node $n with label "Chosen", '
            'where attr "rank" >= 2 in rule main'
        )
    else:
        raise AssertionError("expected GraphMatchFailed")


def test_bound_edge_matcher_failure_reports_structured_predicate_context():
    program = parse_program(
        'program Demo { rule main => { '
        'match edge $e label "link"; '
        'match edge $e label "chosen" where attr("weight") >= 2; '
        '} }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("e1", "a", "b", labels=("link",), attrs=(("weight", 1),)),),
    )

    try:
        execute_program(program, graph)
    except GraphMatchFailed as error:
        assert str(error) == (
            'no match for edge $e with label "chosen", '
            'where attr "weight" >= 2 in rule main'
        )
    else:
        raise AssertionError("expected GraphMatchFailed")
