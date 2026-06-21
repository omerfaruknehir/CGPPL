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


def test_run_command_can_inspect_graph_contents(tmp_path, capsys):
    source_path = tmp_path / "require-node.cgppl"
    source_path.write_text('program Check { rule main => require node "n1"; }', encoding="utf-8")

    graph_payload = {"nodes": [{"id": "n1"}], "edges": []}
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {"nodes": [{"id": "n1", "labels": [], "attrs": {}}], "edges": []}


def test_run_command_can_mutate_graph_contents(tmp_path, capsys):
    source_path = tmp_path / "delete-node.cgppl"
    source_path.write_text('program Delete { rule main => delete node "n1"; }', encoding="utf-8")

    graph_payload = {
        "nodes": [{"id": "n1"}, {"id": "n2"}],
        "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path), "--compact"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        "nodes": [{"id": "n2", "labels": [], "attrs": {}}],
        "edges": [],
    }


def test_run_command_can_execute_sequential_block(tmp_path, capsys):
    source_path = tmp_path / "sequence-delete.cgppl"
    source_path.write_text(
        'program Delete { rule main => { require node "n1"; delete node "n1"; } }',
        encoding="utf-8",
    )

    graph_payload = {
        "nodes": [{"id": "n1"}, {"id": "n2"}],
        "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path), "--compact"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        "nodes": [{"id": "n2", "labels": [], "attrs": {}}],
        "edges": [],
    }


def test_run_command_can_delete_and_construct_graph_contents(tmp_path, capsys):
    source_path = tmp_path / "add-replacement.cgppl"
    source_path.write_text(
        'program Replace { rule main => { require node "n1"; delete node "n1"; add node "n3"; add edge "e2" from "n2" to "n3"; } }',
        encoding="utf-8",
    )

    graph_payload = {
        "nodes": [{"id": "n1"}, {"id": "n2"}],
        "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path), "--compact"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        "nodes": [
            {"id": "n2", "labels": [], "attrs": {}},
            {"id": "n3", "labels": [], "attrs": {}},
        ],
        "edges": [
            {"id": "e2", "source": "n2", "target": "n3", "labels": [], "attrs": {}}
        ],
    }


def test_run_command_reports_failed_graph_requirement(tmp_path, capsys):
    source_path = tmp_path / "require-node.cgppl"
    source_path.write_text('program Check { rule main => require node "missing"; }', encoding="utf-8")

    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps({"nodes": [], "edges": []}), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "cgppl: runtime error:" in captured.out
    assert "required node not found: missing" in captured.out


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
