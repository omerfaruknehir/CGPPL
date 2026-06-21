import json

from cgppl.cli import main


def test_run_command_loads_graph_and_prints_result(tmp_path, capsys):
    source_path = tmp_path / "hello.cgppl"
    source_path.write_text("program Hello { rule main => skip; }", encoding="utf-8")

    graph_payload = {
        "nodes": [{"id": "n1", "labels": ["Root"], "attrs": {"value": 1}}],
        "edges": [],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == graph_payload


def test_run_command_uses_selected_entry_point(tmp_path, capsys):
    source_path = tmp_path / "hello.cgppl"
    source_path.write_text(
        "program Hello { rule main => other(); rule other => skip; }",
        encoding="utf-8",
    )

    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps({"nodes": [], "edges": []}), encoding="utf-8")

    exit_code = main(
        ["run", str(source_path), "--graph", str(graph_path), "--entry-point", "other"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {"nodes": [], "edges": []}


def test_run_command_reports_invalid_graph(tmp_path, capsys):
    source_path = tmp_path / "hello.cgppl"
    source_path.write_text("program Hello { rule main => skip; }", encoding="utf-8")

    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "nodes": [{"id": "a"}],
                "edges": [{"id": "e1", "source": "a", "target": "ghost"}],
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["run", str(source_path), "--graph", str(graph_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "cgppl: graph error:" in captured.out
    assert "missing target node: ghost" in captured.out
