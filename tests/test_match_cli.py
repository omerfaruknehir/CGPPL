import json

from cgppl.cli import main


def test_run_command_can_match_labeled_node_and_delete_it(tmp_path, capsys):
    source_path = tmp_path / "match-node.cgppl"
    source_path.write_text(
        'program MatchDelete { rule main => { match node $n label "Root"; delete node $n; } }',
        encoding="utf-8",
    )

    graph_payload = {
        "nodes": [{"id": "n1", "labels": ["Root"]}, {"id": "n2", "labels": ["Leaf"]}],
        "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path), "--compact"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        "nodes": [{"id": "n2", "labels": ["Leaf"], "attrs": {}}],
        "edges": [],
    }


def test_run_command_can_match_edge_and_mutate_endpoint(tmp_path, capsys):
    source_path = tmp_path / "match-edge.cgppl"
    source_path.write_text(
        'program MatchEdge { rule main => { match edge $e from $a to $b label "link"; '
        'set node $b label "Reached"; delete edge $e; } }',
        encoding="utf-8",
    )

    graph_payload = {
        "nodes": [{"id": "n1"}, {"id": "n2"}],
        "edges": [{"id": "e1", "source": "n1", "target": "n2", "labels": ["link"]}],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path), "--compact"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        "nodes": [
            {"id": "n1", "labels": [], "attrs": {}},
            {"id": "n2", "labels": ["Reached"], "attrs": {}},
        ],
        "edges": [],
    }
