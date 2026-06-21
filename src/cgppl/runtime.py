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
    GraphRef,
    LiteralValue,
    MatchEdgeStmt,
    MatchNodeStmt,
    Program,
    RequireEdgeAttrStmt,
    RequireEdgeLabelStmt,
    RequireEdgeStmt,
    RequireNodeAttrStmt,
    RequireNodeLabelStmt,
    RequireNodeStmt,
    RuleDecl,
    SetEdgeAttrStmt,
    SetEdgeLabelStmt,
    SetNodeAttrStmt,
    SetNodeLabelStmt,
    SkipStmt,
    TryOrStmt,
    VarRef,
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


Bindings = dict[str, str]


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    program_name: str
    entry_point: str
    graph: Graph


@dataclass(frozen=True, slots=True)
class _ExecutionState:
    graph: Graph
    bindings: Bindings


@dataclass(frozen=True, slots=True)
class _BindOutcome:
    matched: bool
    state: _ExecutionState


def execute_program(
    program: Program,
    graph: Graph,
    *,
    entry_point: str = "main",
) -> ExecutionResult:
    """Validate and execute a program entry rule against an immutable graph.

    The current runtime implements control flow, ID-based graph inspection,
    ID-based graph mutations, graph construction statements, graph attribute
    predicates/mutations, graph label predicates/mutations, pattern-variable
    matching for node and edge IDs, sequential statement blocks, and basic
    try-or fallback execution. It still keeps all graph updates immutable so
    the integration point remains stable for later full pattern matching and
    rewrite semantics.
    """

    return ExecutionResult(
        program_name=program.name,
        entry_point=entry_point,
        graph=apply_rule(program, graph, rule_name=entry_point),
    )


def apply_rule(program: Program, graph: Graph, *, rule_name: str = "main") -> Graph:
    validate_program(program, entry_point=rule_name)
    rules = {rule.name: rule for rule in program.rules}
    state = _ExecutionState(graph=graph, bindings={})
    return _execute_rule(rule_name, rules, state, call_stack=()).graph


def _execute_rule(
    rule_name: str,
    rules: dict[str, RuleDecl],
    state: _ExecutionState,
    *,
    call_stack: tuple[str, ...],
) -> _ExecutionState:
    if rule_name in call_stack:
        cycle = " -> ".join(call_stack + (rule_name,))
        raise RecursionLimitExceeded(f"recursive rule calls are not implemented: {cycle}")
    rule = rules[rule_name]
    return _execute_statement(rule.body, rules, state, call_stack=call_stack + (rule_name,))


def _execute_statement(
    statement: object,
    rules: dict[str, RuleDecl],
    state: _ExecutionState,
    *,
    call_stack: tuple[str, ...],
) -> _ExecutionState:
    graph = state.graph
    if isinstance(statement, BlockStmt):
        current = state
        for child in statement.statements:
            current = _execute_statement(child, rules, current, call_stack=call_stack)
        return current
    if isinstance(statement, TryOrStmt):
        return _execute_try_or(statement, rules, state, call_stack=call_stack)
    if isinstance(statement, SkipStmt):
        return state
    if isinstance(statement, FailStmt):
        location = _location(call_stack)
        raise RuleFailed(f"rule failed: {location}")
    if isinstance(statement, RequireNodeStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if graph.has_node(node_id):
            return state
        raise GraphMatchFailed(
            f"required node not found: {node_id} in rule {_location(call_stack)}"
        )
    if isinstance(statement, RequireEdgeStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if graph.has_edge(edge_id):
            return state
        raise GraphMatchFailed(
            f"required edge not found: {edge_id} in rule {_location(call_stack)}"
        )
    if isinstance(statement, RequireNodeAttrStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if not graph.has_node(node_id):
            raise GraphMatchFailed(
                f"required node not found: {node_id} in rule {_location(call_stack)}"
            )
        actual = graph.get_node(node_id).attr(statement.attr_name)
        if _values_equal(actual, statement.value):
            return state
        raise GraphMatchFailed(
            "required node attribute mismatch: "
            f"{node_id}.{statement.attr_name} expected {_format_value(statement.value)} "
            f"but found {_format_value(actual)} in rule {_location(call_stack)}"
        )
    if isinstance(statement, RequireEdgeAttrStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if not graph.has_edge(edge_id):
            raise GraphMatchFailed(
                f"required edge not found: {edge_id} in rule {_location(call_stack)}"
            )
        actual = graph.get_edge(edge_id).attr(statement.attr_name)
        if _values_equal(actual, statement.value):
            return state
        raise GraphMatchFailed(
            "required edge attribute mismatch: "
            f"{edge_id}.{statement.attr_name} expected {_format_value(statement.value)} "
            f"but found {_format_value(actual)} in rule {_location(call_stack)}"
        )
    if isinstance(statement, RequireNodeLabelStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if not graph.has_node(node_id):
            raise GraphMatchFailed(
                f"required node not found: {node_id} in rule {_location(call_stack)}"
            )
        if graph.get_node(node_id).has_label(statement.label):
            return state
        raise GraphMatchFailed(
            "required node label missing: "
            f"{node_id} label {statement.label!r} in rule {_location(call_stack)}"
        )
    if isinstance(statement, RequireEdgeLabelStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if not graph.has_edge(edge_id):
            raise GraphMatchFailed(
                f"required edge not found: {edge_id} in rule {_location(call_stack)}"
            )
        if graph.get_edge(edge_id).has_label(statement.label):
            return state
        raise GraphMatchFailed(
            "required edge label missing: "
            f"{edge_id} label {statement.label!r} in rule {_location(call_stack)}"
        )
    if isinstance(statement, MatchNodeStmt):
        return _execute_match_node(statement, state, call_stack)
    if isinstance(statement, MatchEdgeStmt):
        return _execute_match_edge(statement, state, call_stack)
    if isinstance(statement, DeleteNodeStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if graph.has_node(node_id):
            return _ExecutionState(graph.remove_node(node_id), state.bindings)
        raise GraphMatchFailed(
            f"delete node target not found: {node_id} in rule {_location(call_stack)}"
        )
    if isinstance(statement, DeleteEdgeStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if graph.has_edge(edge_id):
            return _ExecutionState(graph.remove_edge(edge_id), state.bindings)
        raise GraphMatchFailed(
            f"delete edge target not found: {edge_id} in rule {_location(call_stack)}"
        )
    if isinstance(statement, AddNodeStmt):
        labels = (statement.label,) if statement.label is not None else ()
        return _ExecutionState(graph.add_node(Node(statement.node_id, labels=labels)), state.bindings)
    if isinstance(statement, AddEdgeStmt):
        source_id = _resolve_ref(statement.source_id, state.bindings, "edge source", call_stack)
        target_id = _resolve_ref(statement.target_id, state.bindings, "edge target", call_stack)
        labels = (statement.label,) if statement.label is not None else ()
        return _ExecutionState(
            graph.add_edge(Edge(statement.edge_id, source_id, target_id, labels=labels)),
            state.bindings,
        )
    if isinstance(statement, SetNodeAttrStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if not graph.has_node(node_id):
            raise GraphMatchFailed(
                f"set node target not found: {node_id} in rule {_location(call_stack)}"
            )
        node = graph.get_node(node_id).with_attr(statement.attr_name, statement.value)
        return _ExecutionState(graph.replace_node(node), state.bindings)
    if isinstance(statement, SetEdgeAttrStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if not graph.has_edge(edge_id):
            raise GraphMatchFailed(
                f"set edge target not found: {edge_id} in rule {_location(call_stack)}"
            )
        edge = graph.get_edge(edge_id).with_attr(statement.attr_name, statement.value)
        return _ExecutionState(graph.replace_edge(edge), state.bindings)
    if isinstance(statement, SetNodeLabelStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if not graph.has_node(node_id):
            raise GraphMatchFailed(
                f"set node target not found: {node_id} in rule {_location(call_stack)}"
            )
        node = graph.get_node(node_id).with_label(statement.label)
        return _ExecutionState(graph.replace_node(node), state.bindings)
    if isinstance(statement, SetEdgeLabelStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if not graph.has_edge(edge_id):
            raise GraphMatchFailed(
                f"set edge target not found: {edge_id} in rule {_location(call_stack)}"
            )
        edge = graph.get_edge(edge_id).with_label(statement.label)
        return _ExecutionState(graph.replace_edge(edge), state.bindings)
    if isinstance(statement, CallStmt):
        return _execute_rule(statement.name, rules, state, call_stack=call_stack)
    raise RuntimeFailure(f"unsupported statement: {statement!r}")


def _execute_try_or(
    statement: TryOrStmt,
    rules: dict[str, RuleDecl],
    state: _ExecutionState,
    *,
    call_stack: tuple[str, ...],
) -> _ExecutionState:
    try:
        return _execute_statement(statement.first, rules, state, call_stack=call_stack)
    except RuleFailed as first_error:
        try:
            return _execute_statement(statement.second, rules, state, call_stack=call_stack)
        except RuleFailed as second_error:
            raise RuleFailed(
                "all try-or branches failed in rule "
                f"{_location(call_stack)}; first: {first_error}; second: {second_error}"
            ) from second_error


def _execute_match_node(
    statement: MatchNodeStmt,
    state: _ExecutionState,
    call_stack: tuple[str, ...],
) -> _ExecutionState:
    graph = state.graph
    existing = state.bindings.get(statement.node_id.name)
    if existing is not None:
        if graph.has_node(existing) and _node_matches(graph.get_node(existing), statement):
            return state
        raise GraphMatchFailed(
            f"matched node variable {statement.node_id.display()} no longer satisfies matcher "
            f"in rule {_location(call_stack)}"
        )

    for node in graph.nodes:
        if _node_matches(node, statement):
            return _bind_variable(state, statement.node_id, node.id)

    raise GraphMatchFailed(
        f"no node matched {statement.node_id.display()} in rule {_location(call_stack)}"
    )


def _execute_match_edge(
    statement: MatchEdgeStmt,
    state: _ExecutionState,
    call_stack: tuple[str, ...],
) -> _ExecutionState:
    existing = state.bindings.get(statement.edge_id.name)
    if existing is not None:
        edge = state.graph.get_edge(existing) if state.graph.has_edge(existing) else None
        if edge is not None:
            candidate = _match_edge_candidate(statement, edge, state)
            if candidate.matched:
                return candidate.state
        raise GraphMatchFailed(
            f"matched edge variable {statement.edge_id.display()} no longer satisfies matcher "
            f"in rule {_location(call_stack)}"
        )

    for edge in state.graph.edges:
        candidate = _match_edge_candidate(statement, edge, state)
        if candidate.matched:
            return _bind_variable(candidate.state, statement.edge_id, edge.id)

    raise GraphMatchFailed(
        f"no edge matched {statement.edge_id.display()} in rule {_location(call_stack)}"
    )


def _node_matches(node: Node, statement: MatchNodeStmt) -> bool:
    return statement.label is None or node.has_label(statement.label)


def _match_edge_candidate(statement: MatchEdgeStmt, edge: Edge, state: _ExecutionState) -> _BindOutcome:
    if statement.label is not None and not edge.has_label(statement.label):
        return _BindOutcome(False, state)

    current = state
    if statement.source_id is not None:
        source = _try_match_ref(statement.source_id, edge.source, current)
        if not source.matched:
            return source
        current = source.state
    if statement.target_id is not None:
        target = _try_match_ref(statement.target_id, edge.target, current)
        if not target.matched:
            return target
        current = target.state
    return _BindOutcome(True, current)


def _resolve_ref(
    ref: GraphRef,
    bindings: Bindings,
    kind: str,
    call_stack: tuple[str, ...],
) -> str:
    if isinstance(ref, VarRef):
        value = bindings.get(ref.name)
        if value is None:
            raise GraphMatchFailed(
                f"unbound {kind} variable {ref.display()} in rule {_location(call_stack)}"
            )
        return value
    return ref


def _try_match_ref(ref: GraphRef, value: str, state: _ExecutionState) -> _BindOutcome:
    if isinstance(ref, VarRef):
        existing = state.bindings.get(ref.name)
        if existing is not None:
            return _BindOutcome(existing == value, state)
        return _BindOutcome(True, _bind_variable(state, ref, value))
    return _BindOutcome(ref == value, state)


def _bind_variable(state: _ExecutionState, ref: VarRef, value: str) -> _ExecutionState:
    bindings = dict(state.bindings)
    bindings[ref.name] = value
    return _ExecutionState(state.graph, bindings)


def _values_equal(actual: LiteralValue | None, expected: LiteralValue) -> bool:
    return type(actual) is type(expected) and actual == expected


def _format_value(value: LiteralValue | None) -> str:
    if value is None:
        return "<missing>"
    return repr(value)


def _location(call_stack: tuple[str, ...]) -> str:
    return " -> ".join(call_stack) or "<entry>"
