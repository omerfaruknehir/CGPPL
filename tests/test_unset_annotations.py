import json

import pytest

from cgppl.ast import (
    BlockStmt,
    MatchNodeStmt,
    UnsetEdgeAttrStmt,
    UnsetEdgeLabelStmt,
    UnsetNodeAttrStmt,
    UnsetNodeLabelStmt,
    VarRef,
)
from cgppl.cli import main
from cgppl.graph import Edge, Graph, Node
from cgppl.lexer import TokenKind, tokenize
from cgppl.parser import ParserError, parse_program
from cgppl.runtime import GraphMatchFailed, execute_program


def test_lexer_treats_unset_as_keyword():
    tokens = tokenize('program Demo { rule main => unset node "n1" attr "kind"; }')

    assert any(token.kind is TokenKind.KEYWORD and token.value == "unset" for token in tokens)


def test_parser_accepts_unset_annotation_statements():
    program = parse_program(
        'program Demo { rule main => { unset node $n attr "kind"; '
        'unset edge "e1" attr "weight"; unset node $n label "Candidate"; '
        'unset edge(e1) label(link); } }'
    )

    assert program.rules[0].body == BlockStmt(
        (
            UnsetNodeAttrStmt(VarRef("n"), "kind"),
            UnsetEdgeAttrStmt("e1", "weight"),
            UnsetNodeLabelStmt(VarRef("n"), "Candidate"),
            UnsetEdgeLabelStmt("e1", "link"),
        )
    )


def test_parser_rejects_unset_without_annotation_kind():
    with pytest.raises(ParserError, match="expected 'attr' or 'label'"):
        parse_program('program Demo { rule main => unset node "n1"; }')


def test_graph_annotation_removal_helpers_are_immutable_and_idempotent():
    node = Node("n1", labels=["Root", "Candidate"], attrs={"kind": "root", "rank": 1})
    edge = Edge("e1", "n1", "n2", labels=["link", "selected"], attrs={"weight": 2})

    updated_node = node.without_label("Candidate").without_attr("kind").without_attr("missing")
    updated_edge = edge.without_label("selected").without_attr("weight").without_label("missing")

    assert node.labels == ("Candidate", "Root")
    assert node.attr("kind") == "root"
    assert updated_node.labels == ("Root",)
    assert updated_node.attr("kind") is None
    assert updated_node.attr("rank") == 1
    assert edge.labels == ("link", "selected")
    assert edge.attr("weight") == 2
    assert updated_edge.labels == ("link",)
    assert updated_edge.attr("weight") is None


def test_runtime_unsets_node_and_edge_annotations():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Candidate" attr "kind" = "root"; '
        'match edge $e from $n to "n2" label "link" attr "weight" = 2; '
        'unset node $n attr "kind"; unset node $n label "Candidate"; '
        'unset edge $e attr "weight"; unset edge $e label "link"; } }'
    )
    graph = Graph(
        nodes=(Node("n1", labels=["Candidate", "Root"], attrs={"kind": "root"}), Node("n2")),
        edges=(Edge("e1", "n1", "n2", labels=["link"], attrs={"weight": 2}),),
    )

    result = execute_program(program, graph)

    assert graph.get_node("n1").labels == ("Candidate", "Root")
    assert graph.get_node("n1").attr("kind") == "root"
    assert result.graph.get_node("n1").labels == ("Root",)
    assert result.graph.get_node("n1").attr("kind") is None
    assert result.graph.get_edge("e1").labels == ()
    assert result.graph.get_edge("e1").attr("weight") is None


def test_runtime_unset_fails_when_target_is_missing():
    program = parse_program('program Demo { rule main => unset node "missing" attr "kind"; }')

    with pytest.raises(GraphMatchFailed, match='missing unset target for node "missing" with attr "kind" in rule main'):
        execute_program(program, Graph.empty())


def test_cli_can_unset_graph_annotations(tmp_path, capsys):
    source_path = tmp_path / "unset.cgppl"
    source_path.write_text(
        'program Clean { rule main => { unset node "n1" attr "kind"; '
        'unset node "n1" label "Candidate"; unset edge "e1" attr "weight"; '
        'unset edge "e1" label "link"; } }',
        encoding="utf-8",
    )
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "nodes": [{"id": "n1", "labels": ["Candidate", "Root"], "attrs": {"kind": "root"}}],
                "edges": [{"id": "e1", "source": "n1", "target": "n1", "labels": ["link"], "attrs": {"weight": 2}}],
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["run", str(source_path), "--graph", str(graph_path), "--compact"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        "nodes": [{"id": "n1", "labels": ["Root"], "attrs": {}}],
        "edges": [{"id": "e1", "source": "n1", "target": "n1", "labels": [], "attrs": {}}],
    }
