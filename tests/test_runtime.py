import pytest

from cgppl.graph import Edge, Graph, Node
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

    with pytest.raises(GraphMatchFailed, match='missing requirement for node "missing" in rule main'):
        execute_program(program, Graph.empty())


def test_require_node_attr_statement_succeeds_when_value_matches():
    program = parse_program('program Demo { rule main => require node "a" attr "kind" = "root"; }')
    graph = Graph.empty().add_node(Node("a", attrs={"kind": "root"}))

    assert execute_program(program, graph).graph is graph


def test_require_edge_attr_statement_succeeds_when_value_matches():
    program = parse_program('program Demo { rule main => require edge "e1" attr "weight" = 2; }')
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("e1", "a", "b", attrs={"weight": 2}),),
    )

    assert execute_program(program, graph).graph is graph


def test_require_node_attr_statement_supports_boolean_values():
    program = parse_program('program Demo { rule main => require node "a" attr "active" = true; }')
    graph = Graph.empty().add_node(Node("a", attrs={"active": True}))

    assert execute_program(program, graph).graph is graph


def test_require_node_attr_statement_is_type_sensitive():
    program = parse_program('program Demo { rule main => require node "a" attr "flag" = true; }')
    graph = Graph.empty().add_node(Node("a", attrs={"flag": 1}))

    with pytest.raises(
        GraphMatchFailed,
        match='missing requirement for node "a" with attr "flag" = true; found 1 in rule main',
    ):
        execute_program(program, graph)


def test_require_node_attr_statement_fails_when_value_differs():
    program = parse_program('program Demo { rule main => require node "a" attr "kind" = "root"; }')
    graph = Graph.empty().add_node(Node("a", attrs={"kind": "leaf"}))

    with pytest.raises(
        GraphMatchFailed,
        match='missing requirement for node "a" with attr "kind" = "root"; found "leaf" in rule main',
    ):
        execute_program(program, graph)


def test_require_edge_attr_statement_fails_when_attr_is_missing():
    program = parse_program('program Demo { rule main => require edge "e1" attr "weight" = 2; }')
    graph = Graph(nodes=(Node("a"), Node("b")), edges=(Edge("e1", "a", "b"),))

    with pytest.raises(
        GraphMatchFailed,
        match='missing requirement for edge "e1" with attr "weight" = 2; found <missing> in rule main',
    ):
        execute_program(program, graph)


def test_require_node_label_statement_succeeds_when_label_exists():
    program = parse_program('program Demo { rule main => require node "a" label "Root"; }')
    graph = Graph.empty().add_node(Node("a", labels=["Root"]))

    assert execute_program(program, graph).graph is graph


def test_require_edge_label_statement_succeeds_when_label_exists():
    program = parse_program('program Demo { rule main => require edge "e1" label "link"; }')
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("e1", "a", "b", labels=["link"]),),
    )

    assert execute_program(program, graph).graph is graph


def test_require_node_label_statement_fails_when_label_is_missing():
    program = parse_program('program Demo { rule main => require node "a" label "Root"; }')
    graph = Graph.empty().add_node(Node("a", labels=["Leaf"]))

    with pytest.raises(GraphMatchFailed, match='missing requirement for node "a" with label "Root" in rule main'):
        execute_program(program, graph)


def test_require_edge_label_statement_fails_when_label_is_missing():
    program = parse_program('program Demo { rule main => require edge "e1" label "link"; }')
    graph = Graph(nodes=(Node("a"), Node("b")), edges=(Edge("e1", "a", "b"),))

    with pytest.raises(GraphMatchFailed, match='missing requirement for edge "e1" with label "link" in rule main'):
        execute_program(program, graph)


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

    with pytest.raises(GraphMatchFailed, match='missing delete target for node "missing" in rule main'):
        execute_program(program, Graph.empty())


def test_add_node_statement_appends_new_node():
    program = parse_program('program Demo { rule main => add node "b"; }')
    graph = Graph.empty().add_node(Node("a"))

    result = execute_program(program, graph)

    assert graph.node_ids == ("a",)
    assert result.graph.node_ids == ("a", "b")
    assert result.graph.get_node("b").labels == ()


def test_add_node_statement_can_create_labeled_node():
    program = parse_program('program Demo { rule main => add node "b" label "Created"; }')
    graph = Graph.empty().add_node(Node("a"))

    result = execute_program(program, graph)

    assert result.graph.get_node("b").labels == ("Created",)


def test_add_edge_statement_appends_new_edge():
    program = parse_program('program Demo { rule main => add edge "e1" from "a" to "b"; }')
    graph = Graph(nodes=(Node("a"), Node("b")))

    result = execute_program(program, graph)

    assert result.graph.edge_ids == ("e1",)
    assert result.graph.get_edge("e1") == Edge("e1", "a", "b")


def test_add_edge_statement_can_create_labeled_edge():
    program = parse_program('program Demo { rule main => add edge "e1" from "a" to "b" label "link"; }')
    graph = Graph(nodes=(Node("a"), Node("b")))

    result = execute_program(program, graph)

    assert result.graph.get_edge("e1").labels == ("link",)


def test_add_edge_statement_rejects_missing_endpoint():
    program = parse_program('program Demo { rule main => add edge "e1" from "a" to "missing"; }')
    graph = Graph.empty().add_node(Node("a"))

    with pytest.raises(
        GraphMatchFailed,
        match='add edge "e1" failed: edge e1 references missing target node: missing in rule main',
    ):
        execute_program(program, graph)


def test_set_node_attr_statement_replaces_node_attr():
    program = parse_program('program Demo { rule main => set node "a" attr "kind" = "new"; }')
    graph = Graph.empty().add_node(Node("a", attrs={"kind": "old"}))

    result = execute_program(program, graph)

    assert graph.get_node("a").attr("kind") == "old"
    assert result.graph.get_node("a").attr("kind") == "new"


def test_set_edge_attr_statement_replaces_edge_attr():
    program = parse_program('program Demo { rule main => set edge "e1" attr "weight" = 3; }')
    graph = Graph(
        nodes=(Node("a"), Node("b")),
        edges=(Edge("e1", "a", "b", attrs={"weight": 1}),),
    )

    result = execute_program(program, graph)

    assert graph.get_edge("e1").attr("weight") == 1
    assert result.graph.get_edge("e1").attr("weight") == 3


def test_set_node_attr_statement_supports_boolean_values():
    program = parse_program('program Demo { rule main => set node "a" attr "active" = false; }')
    graph = Graph.empty().add_node(Node("a"))

    result = execute_program(program, graph)

    assert result.graph.get_node("a").attr("active") is False


def test_set_node_attr_statement_fails_when_node_is_missing():
    program = parse_program('program Demo { rule main => set node "missing" attr "kind" = "new"; }')

    with pytest.raises(
        GraphMatchFailed,
        match='missing set target for node "missing" with attr "kind" in rule main',
    ):
        execute_program(program, Graph.empty())


def test_set_edge_label_statement_fails_when_edge_is_missing():
    program = parse_program('program Demo { rule main => set edge "missing" label "selected"; }')

    with pytest.raises(
        GraphMatchFailed,
        match='missing set target for edge "missing" with label "selected" in rule main',
    ):
        execute_program(program, Graph.empty())


def test_unset_node_attr_statement_fails_when_node_is_missing():
    program = parse_program('program Demo { rule main => unset node "missing" attr "kind"; }')

    with pytest.raises(
        GraphMatchFailed,
        match='missing unset target for node "missing" with attr "kind" in rule main',
    ):
        execute_program(program, Graph.empty())


def test_unset_edge_label_statement_fails_when_edge_is_missing():
    program = parse_program('program Demo { rule main => unset edge "missing" label "selected"; }')

    with pytest.raises(
        GraphMatchFailed,
        match='missing unset target for edge "missing" with label "selected" in rule main',
    ):
        execute_program(program, Graph.empty())


def test_rule_fail_statement_raises_rule_failed():
    program = parse_program("program Demo { rule main => fail; }")

    with pytest.raises(RuleFailed, match="rule failed: main"):
        execute_program(program, Graph.empty())


def test_recursive_rule_call_is_rejected():
    program = parse_program("program Demo { rule main => helper(); rule helper => main(); }")

    with pytest.raises(RecursionLimitExceeded, match="main -> helper -> main"):
        execute_program(program, Graph.empty())
