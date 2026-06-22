from cgppl.ast import AddEdgeStmt, EndpointRef, VarRef
from cgppl.parser import parse_program


def test_parses_strict_edge_constructor_endpoints_as_default_policy():
    program = parse_program('program Demo { rule main => add edge $edge from $source to "target" label "new"; }')

    statement = program.rules[0].body

    assert statement == AddEdgeStmt(
        VarRef("edge"),
        VarRef("source"),
        "target",
        labels=("new",),
    )
    assert statement.source_endpoint == EndpointRef(VarRef("source"), auto_create=False)
    assert statement.target_endpoint == EndpointRef("target", auto_create=False)


def test_parses_opt_in_auto_create_endpoint_markers():
    program = parse_program(
        'program Demo { rule main => add edge $edge from add $source to add $target label "new"; }'
    )

    statement = program.rules[0].body

    assert statement == AddEdgeStmt(
        VarRef("edge"),
        VarRef("source"),
        VarRef("target"),
        labels=("new",),
        source_auto_create=True,
        target_auto_create=True,
    )
    assert statement.source_endpoint == EndpointRef(VarRef("source"), auto_create=True)
    assert statement.target_endpoint == EndpointRef(VarRef("target"), auto_create=True)


def test_parses_mixed_endpoint_marker_policy():
    program = parse_program('program Demo { rule main => add edge $edge from add "source" to $target; }')

    statement = program.rules[0].body

    assert statement.source_endpoint == EndpointRef("source", auto_create=True)
    assert statement.target_endpoint == EndpointRef(VarRef("target"), auto_create=False)
