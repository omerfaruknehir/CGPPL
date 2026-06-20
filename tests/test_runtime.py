import pytest

from cgppl.graph import Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import RecursionLimitExceeded, RuleFailed, apply_rule, execute_program


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


def test_fail_rule_raises_runtime_failure():
    program = parse_program("program Demo { rule main => fail; }")

    with pytest.raises(RuleFailed, match="rule failed: main"):
        execute_program(program, Graph.empty())


def test_recursive_rule_calls_are_rejected_until_runtime_strategy_exists():
    program = parse_program("program Demo { rule main => main(); }")

    with pytest.raises(RecursionLimitExceeded, match="recursive rule calls are not implemented"):
        execute_program(program, Graph.empty())
