import json

from cgppl.cli import main


def test_run_command_supports_where_variable_operands(tmp_path, capsys):
    source_path = tmp_path / "where-vars.cgppl"
    source_path.write_text(
        'program WhereVars { rule main => { match edge $e from $a to $b where $a != $b; '
        'set edge $e label "NonLoop"; } }',
        encoding="utf-8",
    )

    graph_payload = {
        "nodes": [{"id": "a"}, {"id": "b"}],
        "edges": [
            {"id": "loop", "source": "a", "target": "a"},
            {"id": "forward", "source": "a", "target": "b"},
        ],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path), "--compact"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        "nodes": [
            {"id": "a", "labels": [], "attrs": {}},
            {"id": "b", "labels": [], "attrs": {}},
        ],
        "edges": [
            {"id": "loop", "source": "a", "target": "a", "labels": [], "attrs": {}},
            {"id": "forward", "source": "a", "target": "b", "labels": ["NonLoop"], "attrs": {}},
        ],
    }
