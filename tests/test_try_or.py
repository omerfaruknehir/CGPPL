import json

import pytest

from cgppl.ast import BlockStmt, FailStmt, MatchNodeStmt, SetNodeLabelStmt, TryOrStmt, VarRef
from cgppl.cli import main
from cgppl.graph import Graph, Node
from cgppl.parser import ParserError, parse_program
from cgppl.runtime import RuleFailed, execute_program
from cgppl.semantics import SemanticError, validate_program


def test_parses_try_or_statement_with_block_branches():
    program = parse_program(
        'program Demo { rule main => try { match node $n label "Missing"; } '
        'or { match node $n label "Root"; set node $n label "FallbackUsed"; } }'
    )

    assert program.rules[0].body == TryOrStmt(
        first=BlockStmt((MatchNodeStmt(VarRef("n"), "Missing"),)),
        second=BlockStmt(
            (
                MatchNodeStmt(VarRef("n"), "Root"),
                SetNodeLabelStmt(VarRef("n"), "FallbackUsed"),
            )
        ),
    )


def test_rejects_try_without_or_branch():
    with pytest.raises(ParserError, match="expected keyword 'or'"):
        parse_program('program Demo { rule main => try { skip; } }')


def test_validate_checks_calls_inside_try_or_branches():
    program = parse_program('program Demo { rule main => try missing(); or fail; }')

    with pytest.raises(SemanticError, match="undefined rule call: missing"):
        validate_program(program)


def test_try_or_uses_first_successful_branch():
    program = parse_program(
        'program Demo { rule main => try { match node $n label "Root"; set node $n label "Primary"; } '
        'or { match node $n label "Leaf"; set node $n label "Fallback"; } }'
    )
    graph = Graph(nodes=(Node("a", labels=["Root"]), Node("b", labels=["Leaf"])))

    result = execute_program(program, graph)

    assert result.graph.get_node("a").has_label("Primary")
    assert not result.graph.get_node("b").has_label("Fallback")


def test_try_or_discards_failed_branch_graph_and_bindings_before_fallback():
    program = parse_program(
        'program Demo { rule main => try { match node $n label "Root"; '
        'set node $n label "ShouldRollback"; match node $missing label "Missing"; } '
        'or { match node $n label "Leaf"; set node $n label "FallbackUsed"; } }'
    )
    graph = Graph(nodes=(Node("a", labels=["Root"]), Node("b", labels=["Leaf"])))

    result = execute_program(program, graph)

    assert not result.graph.get_node("a").has_label("ShouldRollback")
    assert result.graph.get_node("b").has_label("FallbackUsed")


def test_try_or_fails_when_both_branches_fail():
    program = parse_program(
        'program Demo { rule main => try { match node $n label "Missing"; } '
        'or { fail; } }'
    )

    with pytest.raises(RuleFailed, match="all try-or branches failed"):
        execute_program(program, Graph.empty())


def test_run_command_executes_try_or_fallback(tmp_path, capsys):
    source_path = tmp_path / "try-fallback.cgppl"
    source_path.write_text(
        'program TryFallback { rule main => try { match node $n label "Missing"; '
        'set node $n label "ShouldNotAppear"; } '
        'or { match node $n label "Root"; set node $n label "FallbackUsed"; } }',
        encoding="utf-8",
    )

    graph_payload = {
        "nodes": [{"id": "n1", "labels": ["Root"]}, {"id": "n2", "labels": ["Leaf"]}],
        "edges": [],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")

    exit_code = main(["run", str(source_path), "--graph", str(graph_path), "--compact"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == {
        "nodes": [
            {"id": "n1", "labels": ["FallbackUsed", "Root"], "attrs": {}},
            {"id": "n2", "labels": ["Leaf"], "attrs": {}},
        ],
        "edges": [],
    }
