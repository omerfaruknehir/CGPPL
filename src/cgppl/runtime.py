"""Minimal graph runtime for the implemented CGPPL subset."""

from __future__ import annotations

from dataclasses import dataclass

from .ast import CallStmt, FailStmt, Program, RequireEdgeStmt, RequireNodeStmt, RuleDecl, SkipStmt
from .graph import Graph
from .semantics import validate_program


class RuntimeFailure(RuntimeError):
    pass


class RuleFailed(RuntimeFailure):
    pass


class GraphMatchFailed(RuleFailed):
    pass


class RecursionLimitExceeded(RuntimeFailure):
    pass


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    program_name: str
    entry_point: str
    graph: Graph


def execute_program(
    program: Program,
    graph: Graph,
    *,
    entry_point: str = "main",
) -> ExecutionResult:
    """Validate and execute a program entry rule against an immutable graph.

    The current runtime implements control flow plus the first graph-inspection
    primitive, `require node` / `require edge`. It still returns an immutable graph
    even when no rewrite occurs, keeping the integration point stable for later
    graph mutation statements.
    """

    return ExecutionResult(
        program_name=program.name,
        entry_point=entry_point,
        graph=apply_rule(program, graph, rule_name=entry_point),
    )


def apply_rule(program: Program, graph: Graph, *, rule_name: str = "main") -> Graph:
    validate_program(program, entry_point=rule_name)
    rules = {rule.name: rule for rule in program.rules}
    return _execute_rule(rule_name, rules, graph, call_stack=())


def _execute_rule(
    rule_name: str,
    rules: dict[str, RuleDecl],
    graph: Graph,
    *,
    call_stack: tuple[str, ...],
) -> Graph:
    if rule_name in call_stack:
        cycle = " -> ".join(call_stack + (rule_name,))
        raise RecursionLimitExceeded(f"recursive rule calls are not implemented: {cycle}")
    rule = rules[rule_name]
    return _execute_statement(rule.body, rules, graph, call_stack=call_stack + (rule_name,))


def _execute_statement(
    statement: object,
    rules: dict[str, RuleDecl],
    graph: Graph,
    *,
    call_stack: tuple[str, ...],
) -> Graph:
    if isinstance(statement, SkipStmt):
        return graph
    if isinstance(statement, FailStmt):
        location = _location(call_stack)
        raise RuleFailed(f"rule failed: {location}")
    if isinstance(statement, RequireNodeStmt):
        if graph.has_node(statement.node_id):
            return graph
        raise GraphMatchFailed(
            f"required node not found: {statement.node_id} in rule {_location(call_stack)}"
        )
    if isinstance(statement, RequireEdgeStmt):
        if graph.has_edge(statement.edge_id):
            return graph
        raise GraphMatchFailed(
            f"required edge not found: {statement.edge_id} in rule {_location(call_stack)}"
        )
    if isinstance(statement, CallStmt):
        return _execute_rule(statement.name, rules, graph, call_stack=call_stack)
    raise RuntimeFailure(f"unsupported statement: {statement!r}")


def _location(call_stack: tuple[str, ...]) -> str:
    return " -> ".join(call_stack) or "<entry>"
