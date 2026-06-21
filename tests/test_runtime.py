import pytest

from cgppl.graph import Edge, Graph, GraphError, Node
from cgppl.parser import parse_program
from cgppl.runtime import (
    GraphMatchFailed,
    RecursionLimitExceeded,
    RuleFailed,
    apply_rule,
    execute_program,
)


def test_executes_skip_rule_against_tiny_graph():
    program = parse_program("program Demo { rule main => skip; }")
    graph = Graph.empty().add_node(Node("n1", labels=["Root"]))

    result = execute_program(program, graph)

    assert result.program_name == "Demo"
    assert result.entry_point == "main"
    assert result.graph is graph
    assert result.graph.get_node("n1").labels == ("Root",)


def test_rule_call_dispatches_to_target_rule():
    program = parse_program("program Demo { rule main => helper(); rule helper => skip; }")
    graph = Graph.empty().add_node(Node("n1"))

    assert apply_rule(program, graph) is graph


def test_require_node_statement_succeeds_when_node_exists():
    program = parse_program('program Demo { rule main => require node "n1"; }')
    graph = Graph.empty().add_node(Node("n1"))

    assert execute_program(program, graph).graph is graph


def test_require_edge_statement_succeeds_when_edge_exists():
    program = parse_program("program Demo { rule main => require edge(e1); }")
    graph = Graph(nodes=(Node("a"), Node("b")), edges=(Edge("e1", "a", "b"),))

    assert execute_program(program, graph).graph is graph


def test_require_node_statement_fails_when_node_is_missing():
    program = parse_program('program Demo { rule main => require node "missing"; }')

    with pytest.raises(GraphMatchFailed, match="required node not found: missing"):
        execute_program(program, Graph.empty())


def test_delete_node_statement_removes_node_and_incident_edges():
    program = parse_program('program Demo { rule main => delete node "a"; }')
    graph = Graph(nodes=(Node("a"), Node("b")), edges=(Edge("e1", "a", "b"),))

    result = execute_program(program, graph)

    assert result.graph.node_ids == ("b",)
    assert result.graph.edge_ids == ()
    assert graph.node_ids == ("a", "b")
    assert graph.edge_ids == ("e1",)


def test_delete_edge_statement_removes_only_selected_edge():
    program = parse_program("program Demo { rule main => delete edge(e1); }")
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("e1", "a", "b"), Edge("e2", "b", "a")),
    )

    result = execute_program(program, graph)

    assert result.graph.node_ids == ("a", "b")
    assert result.graph.edge_ids == ("e2",)


def test_delete_node_statement_fails_when_node_is_missing():
    program = parse_program('program Demo { rule main => delete node "missing"; }')

    with pytest.raises(GraphMatchFailed, match="delete node target not found: missing"):
        execute_program(program, Graph.empty())


def test_add_node_statement_appends_new_node():
    program = parse_program('program Demo { rule main => add node "b"; }')
    graph = Graph.empty().add_node(Node("a"))

    result = execute_program(program, graph)

    assert graph.node_ids == ("a",)
    assert result.graph.node_ids == ("a", "b")
    assert result.graph.get_node("b").labels == ()


def test_add_edge_statement_appends_new_edge():
    program = parse_program('program Demo { rule main => add edge "e1" from "a" to "b"; }')
    graph = Graph(nodes=(Node("a"), Node("b")))

    result = execute_program(program, graph)

    assert result.graph.edge_ids == ("e1",)
    assert result.graph.get_edge("e1") == Edge("e1", "a", "b")


def test_add_edge_statement_rejects_missing_endpoint():
    program = parse_program('program Demo { rule main => add edge "e1" from "a" to "missing"; }')
    graph = Graph.empty().add_node(Node("a"))

    with pytest.raises(GraphError, match="missing target node: missing"):
        execute_program(program, graph)


def test_block_statement_threads_graph_updates_in_order():
    program = parse_program(
        'program Demo { rule main => { require node "a"; delete node "a"; require node "b"; } }'
    )
    graph = Graph(nodes=(Node("a"), Node("b")), edges=(Edge("e1", "a", "b"),))

    result = execute_program(program, graph)

    assert result.graph.node_ids == ("b",)
    assert result.graph.edge_ids == ()


def test_block_statement_can_delete_and_construct_graph_structure():
    program = parse_program(
        'program Demo { rule main => { delete node "a"; add node "c"; add edge "e2" from "b" to "c"; } }'
    )
    graph = Graph(nodes=(Node("a"), Node("b")), edges=(Edge("e1", "a", "b"),))

    result = execute_program(program, graph)

    assert result.graph.node_ids == ("b", "c")
    assert result.graph.edge_ids == ("e2",)
    assert result.graph.get_edge("e2") == Edge("e2", "b", "c")


def test_block_statement_stops_at_first_failure():
    program = parse_program(
        'program Demo { rule main => { require node "missing"; delete node "a"; } }'
    )
    graph = Graph.empty().add_node(Node("a"))

    with pytest.raises(GraphMatchFailed, match="required node not found: missing"):
        execute_program(program, graph)

    assert graph.node_ids == ("a",)


def test_fail_rule_raises_runtime_failure():
    program = parse_program("program Demo { rule main => fail; }")

    with pytest.raises(RuleFailed, match="rule failed: main"):
        execute_program(program, Graph.empty())


def test_recursive_rule_calls_are_rejected_until_runtime_strategy_exists():
    program = parse_program("program Demo { rule main => main(); }")

    with pytest.raises(RecursionLimitExceeded, match="recursive rule calls are not implemented"):
        execute_program(program, Graph.empty())
