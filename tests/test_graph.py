import pytest

from cgppl.graph import Edge, Graph, GraphError, Node


def test_builds_tiny_immutable_graph():
    graph = (
        Graph.empty()
        .add_node(Node("a", labels=["start"], attrs={"value": 1}))
        .add_node(Node("b", labels=["end"]))
        .add_edge(Edge("e1", "a", "b", labels=["link"], attrs={"weight": 7}))
    )

    assert graph.node_ids == ("a", "b")
    assert graph.edge_ids == ("e1",)
    assert graph.get_node("a").attr("value") == 1
    assert graph.get_node("a").has_label("start")
    assert graph.get_edge("e1").source == "a"
    assert graph.get_edge("e1").target == "b"
    assert graph.get_edge("e1").has_label("link")


def test_node_with_label_returns_deduplicated_node():
    node = Node("a", labels=["Root"])

    updated = node.with_label("Visited").with_label("Root")

    assert node.labels == ("Root",)
    assert updated.labels == ("Root", "Visited")


def test_edge_with_label_returns_deduplicated_edge():
    edge = Edge("e1", "a", "b", labels=["link"])

    updated = edge.with_label("selected").with_label("link")

    assert edge.labels == ("link",)
    assert updated.labels == ("link", "selected")


def test_rejects_duplicate_node_ids():
    with pytest.raises(GraphError, match="duplicate node id: a"):
        Graph(nodes=(Node("a"), Node("a")))


def test_rejects_edges_with_missing_endpoints():
    with pytest.raises(GraphError, match="missing target node: b"):
        Graph(nodes=(Node("a"),), edges=(Edge("e1", "a", "b"),))


def test_removing_node_also_removes_incident_edges():
    graph = Graph(nodes=(Node("a"), Node("b")), edges=(Edge("e1", "a", "b"),))

    updated = graph.remove_node("a")

    assert updated.node_ids == ("b",)
    assert updated.edge_ids == ()


def test_round_trips_graph_dict_payload():
    graph = Graph.from_dict(
        {
            "nodes": [{"id": "a", "labels": ["start"], "attrs": {"value": 1}}],
            "edges": [],
        }
    )

    assert graph.to_dict() == {
        "nodes": [{"id": "a", "labels": ["start"], "attrs": {"value": 1}}],
        "edges": [],
    }
