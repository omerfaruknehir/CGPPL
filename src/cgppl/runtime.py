"""Minimal graph runtime for the implemented CGPPL subset."""

from __future__ import annotations

from dataclasses import dataclass

from .ast import (
    AddEdgeStmt,
    AddNodeStmt,
    BlockStmt,
    CallStmt,
    DeleteEdgeStmt,
    DeleteNodeStmt,
    FailStmt,
    LiteralValue,
    Program,
    RequireEdgeAttrStmt,
    RequireEdgeStmt,
    RequireNodeAttrStmt,
    RequireNodeStmt,
    RuleDecl,
    SetEdgeAttrStmt,
    SetNodeAttrStmt,
    SkipStmt,
)
from .graph import Edge, Graph, Node
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

    The current runtime implements control flow, ID-based graph inspection,
    ID-based graph mutations, graph construction statements, graph attribute
    predicates/mutations, and sequential statement blocks. It still keeps all
    graph updates immutable so the integration point remains stable for later
    pattern matching and rewrite semantics.
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
    if isinstance(statement, BlockStmt):
        current = graph
        for child in statement.statements:
            current = _execute_statement(child, rules, current, call_stack=call_stack)
        return current
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
    if isinstance(statement, RequireNodeAttrStmt):
        if not graph.has_node(statement.node_id):
            raise GraphMatchFailed(
                f"required node not found: {statement.node_id} in rule {_location(call_stack)}"
            )
        actual = graph.get_node(statement.node_id).attr(statement.attr_name)
        if _values_equal(actual, statement.value):
            return graph
        raise GraphMatchFailed(
            "required node attribute mismatch: "
            f"{statement.node_id}.{statement.attr_name} expected {_format_value(statement.value)} "
            f"but found {_format_value(actual)} in rule {_location(call_stack)}"
        )
    if isinstance(statement, RequireEdgeAttrStmt):
        if not graph.has_edge(statement.edge_id):
            raise GraphMatchFailed(
                f"required edge not found: {statement.edge_id} in rule {_location(call_stack)}"
            )
        actual = graph.get_edge(statement.edge_id).attr(statement.attr_name)
        if _values_equal(actual, statement.value):
            return graph
        raise GraphMatchFailed(
            "required edge attribute mismatch: "
            f"{statement.edge_id}.{statement.attr_name} expected {_format_value(statement.value)} "
            f"but found {_format_value(actual)} in rule {_location(call_stack)}"
        )
    if isinstance(statement, DeleteNodeStmt):
        if graph.has_node(statement.node_id):
            return graph.remove_node(statement.node_id)
        raise GraphMatchFailed(
            f"delete node target not found: {statement.node_id} in rule {_location(call_stack)}"
        )
    if isinstance(statement, DeleteEdgeStmt):
        if graph.has_edge(statement.edge_id):
            return graph.remove_edge(statement.edge_id)
        raise GraphMatchFailed(
            f"delete edge target not found: {statement.edge_id} in rule {_location(call_stack)}"
        )
    if isinstance(statement, AddNodeStmt):
        return graph.add_node(Node(statement.node_id))
    if isinstance(statement, AddEdgeStmt):
        return graph.add_edge(Edge(statement.edge_id, statement.source_id, statement.target_id))
    if isinstance(statement, SetNodeAttrStmt):
        if not graph.has_node(statement.node_id):
            raise GraphMatchFailed(
                f"set node target not found: {statement.node_id} in rule {_location(call_stack)}"
            )
        node = graph.get_node(statement.node_id).with_attr(statement.attr_name, statement.value)
        return graph.replace_node(node)
    if isinstance(statement, SetEdgeAttrStmt):
        if not graph.has_edge(statement.edge_id):
            raise GraphMatchFailed(
                f"set edge target not found: {statement.edge_id} in rule {_location(call_stack)}"
            )
        edge = graph.get_edge(statement.edge_id).with_attr(statement.attr_name, statement.value)
        return graph.replace_edge(edge)
    if isinstance(statement, CallStmt):
        return _execute_rule(statement.name, rules, graph, call_stack=call_stack)
    raise RuntimeFailure(f"unsupported statement: {statement!r}")


def _values_equal(actual: LiteralValue | None, expected: LiteralValue) -> bool:
    return type(actual) is type(expected) and actual == expected


def _format_value(value: LiteralValue | None) -> str:
    if value is None:
        return "<missing>"
    return repr(value)


def _location(call_stack: tuple[str, ...]) -> str:
    return " -> ".join(call_stack) or "<entry>"
