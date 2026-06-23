import pytest

from cgppl.ast import AddEdgeStmt, AddNodeStmt, BlockStmt, VarRef
from cgppl.graph import Edge, Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_parses_variable_node_and_edge_construction_targets():
    program = parse_program(
        'program Demo { rule main => { '
        'add node $replacement label "Generated"; '
        'add edge $new_edge from "source" to $replacement label "new"; '
        '} }'
    )

    assert program.rules[0].body == BlockStmt(
        (
            AddNodeStmt(VarRef("replacement"), labels=("Generated",)),
            AddEdgeStmt(VarRef("new_edge"), "source", VarRef("replacement"), labels=("new",)),
        )
    )


def test_unbound_node_construction_variable_generates_id_and_binds_for_later_use():
    program = parse_program(
        'program Demo { rule main => { '
        'add node $replacement label "Generated"; '
        'set node $replacement label "Selected"; '
        'require node $replacement label "Selected"; '
        '} }'
    )

    result = execute_program(program, Graph.empty())

    assert result.graph.node_ids == ("replacement",)
    assert set(result.graph.get_node("replacement").labels) == {"Generated", "Selected"}


def test_generated_node_construction_id_uses_suffix_when_base_id_exists():
    program = parse_program(
        'program Demo { rule main => { '
        'add node $replacement label "Generated"; '
        'set node $replacement label "Selected"; '
        '} }'
    )
    graph = Graph(nodes=(Node("replacement", labels=("Existing",)),))

    result = execute_program(program, graph)

    assert result.graph.node_ids == ("replacement", "replacement_2")
    assert result.graph.get_node("replacement").labels == ("Existing",)
    assert set(result.graph.get_node("replacement_2").labels) == {"Generated", "Selected"}


def test_unbound_edge_construction_variable_generates_id_and_binds_for_later_use():
    program = parse_program(
        'program Demo { rule main => { '
        'match node $source label "Root"; '
        'add node $replacement label "Generated"; '
        'add edge $new_edge from $source to $replacement label "new"; '
        'set edge $new_edge label "Selected"; '
        '} }'
    )
    graph = Graph(nodes=(Node("root", labels=("Root",)),))

    result = execute_program(program, graph)

    assert result.graph.get_edge("new_edge") == Edge(
        "new_edge",
        "root",
        "replacement",
        labels=("Selected", "new"),
    )


def test_generated_edge_construction_id_uses_suffix_when_base_id_exists():
    program = parse_program(
        'program Demo { rule main => { '
        'add edge $new_edge from "a" to "b" label "new"; '
        'set edge $new_edge label "Selected"; '
        '} }'
    )
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("new_edge", "a", "b", labels=("Existing",)),),
    )

    result = execute_program(program, graph)

    assert result.graph.edge_ids == ("new_edge", "new_edge_2")
    assert result.graph.get_edge("new_edge").labels == ("Existing",)
    assert set(result.graph.get_edge("new_edge_2").labels) == {"new", "Selected"}


def test_bound_node_construction_variable_resolves_to_existing_binding_and_rejects_duplicate_id():
    program = parse_program(
        'program Demo { rule main => { '
        'match node $source label "Root"; '
        'add node $source label "Duplicate"; '
        '} }'
    )
    graph = Graph(nodes=(Node("root", labels=("Root",)),))

    with pytest.raises(
        GraphMatchFailed,
        match="add node \\$source failed: duplicate node id: root in rule main",
    ):
        execute_program(program, graph)


def test_unbound_edge_endpoint_variable_still_fails():
    program = parse_program(
        'program Demo { rule main => add edge $new_edge from $missing to "target" label "new"; }'
    )
    graph = Graph(nodes=(Node("target"),))

    with pytest.raises(GraphMatchFailed, match="unbound edge source variable \\$missing"):
        execute_program(program, graph)


def test_literal_construction_targets_remain_compatible():
    program = parse_program(
        'program Demo { rule main => { '
        'add node "literal" label "Generated"; '
        'add edge "literal-edge" from "source" to "literal" label "new"; '
        '} }'
    )
    graph = Graph(nodes=(Node("source"),))

    result = execute_program(program, graph)

    assert result.graph.has_node("literal")
    assert result.graph.has_edge("literal-edge")


def test_missing_edge_endpoint_reports_rule_failure_with_context():
    program = parse_program(
        'program Demo { rule main => add edge "new" from "missing" to "target" label "new"; }'
    )
    graph = Graph(nodes=(Node("target"),))

    with pytest.raises(
        GraphMatchFailed,
        match='add edge "new" failed: edge new references missing source node: missing in rule main',
    ):
        execute_program(program, graph)


def test_constructor_precondition_failure_can_fall_back_in_try_or():
    program = parse_program(
        'program Demo { rule main => try { '
        'add node "existing" label "Duplicate"; '
        '} or { '
        'add node "fallback" label "Recovered"; '
        '} }'
    )
    graph = Graph(nodes=(Node("existing", labels=("Original",)),))

    result = execute_program(program, graph)

    assert result.graph.node_ids == ("existing", "fallback")
    assert result.graph.get_node("existing").labels == ("Original",)
    assert result.graph.get_node("fallback").labels == ("Recovered",)
