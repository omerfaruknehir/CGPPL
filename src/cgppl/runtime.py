"""Minimal graph runtime for the implemented CGPPL subset."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .ast import (
    AddEdgeStmt,
    AddNodeStmt,
    AttrExpr,
    AttrPredicate,
    BlockStmt,
    CallStmt,
    DeleteEdgeStmt,
    DeleteNodeStmt,
    EndpointRef,
    FailStmt,
    FieldExpr,
    GraphRef,
    LiteralExpr,
    LiteralValue,
    MatchEdgeStmt,
    MatchNodeStmt,
    Program,
    RequireEdgeAttrStmt,
    RequireEdgeLabelStmt,
    RequireEdgeStmt,
    RequireNoEdgeStmt,
    RequireNoNodeStmt,
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
    UnsetEdgeAttrStmt,
    UnsetEdgeLabelStmt,
    UnsetNodeAttrStmt,
    UnsetNodeLabelStmt,
    VarExpr,
    VarRef,
    WhereExpr,
    WherePredicate,
)
from .graph import Edge, Graph, GraphError, Node
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
ComparableValue = LiteralValue | None


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
    """Validate and execute a program entry rule against an immutable graph."""

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
        return _execute_block(statement, rules, state, call_stack=call_stack)
    if isinstance(statement, TryOrStmt):
        return _execute_try_or(statement, rules, state, call_stack=call_stack)
    if isinstance(statement, SkipStmt):
        return state
    if isinstance(statement, FailStmt):
        raise RuleFailed(f"rule failed: {_location(call_stack)}")
    if isinstance(statement, RequireNoNodeStmt):
        if _forbidden_node_exists(statement, state, call_stack):
            raise GraphMatchFailed(
                f"forbidden node matched {_format_graph_ref(statement.node_id)} "
                f"in rule {_location(call_stack)}"
            )
        return state
    if isinstance(statement, RequireNoEdgeStmt):
        if _forbidden_edge_exists(statement, state, call_stack):
            raise GraphMatchFailed(
                f"forbidden edge matched {_format_graph_ref(statement.edge_id)} "
                f"in rule {_location(call_stack)}"
            )
        return state
    if isinstance(statement, RequireNodeStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if graph.has_node(node_id):
            return state
        raise GraphMatchFailed(f"required node not found: {node_id} in rule {_location(call_stack)}")
    if isinstance(statement, RequireEdgeStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if graph.has_edge(edge_id):
            return state
        raise GraphMatchFailed(f"required edge not found: {edge_id} in rule {_location(call_stack)}")
    if isinstance(statement, RequireNodeAttrStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if not graph.has_node(node_id):
            raise GraphMatchFailed(f"required node not found: {node_id} in rule {_location(call_stack)}")
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
            raise GraphMatchFailed(f"required edge not found: {edge_id} in rule {_location(call_stack)}")
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
            raise GraphMatchFailed(f"required node not found: {node_id} in rule {_location(call_stack)}")
        if graph.get_node(node_id).has_label(statement.label):
            return state
        raise GraphMatchFailed(
            f"required node label missing: {node_id} label {statement.label!r} in rule {_location(call_stack)}"
        )
    if isinstance(statement, RequireEdgeLabelStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if not graph.has_edge(edge_id):
            raise GraphMatchFailed(f"required edge not found: {edge_id} in rule {_location(call_stack)}")
        if graph.get_edge(edge_id).has_label(statement.label):
            return state
        raise GraphMatchFailed(
            f"required edge label missing: {edge_id} label {statement.label!r} in rule {_location(call_stack)}"
        )
    if isinstance(statement, MatchNodeStmt):
        return _execute_match_node(statement, state, call_stack)
    if isinstance(statement, MatchEdgeStmt):
        return _execute_match_edge(statement, state, call_stack)
    if isinstance(statement, DeleteNodeStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if graph.has_node(node_id):
            return _ExecutionState(graph.remove_node(node_id), state.bindings)
        raise GraphMatchFailed(f"delete node target not found: {node_id} in rule {_location(call_stack)}")
    if isinstance(statement, DeleteEdgeStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if graph.has_edge(edge_id):
            return _ExecutionState(graph.remove_edge(edge_id), state.bindings)
        raise GraphMatchFailed(f"delete edge target not found: {edge_id} in rule {_location(call_stack)}")
    if isinstance(statement, AddNodeStmt):
        node_id, current = _resolve_construction_ref(statement.node_id, state, "node", call_stack)
        attrs = _attrs_from_predicates(statement.attrs)
        try:
            return _ExecutionState(
                current.graph.add_node(Node(node_id, labels=statement.labels, attrs=attrs)),
                current.bindings,
            )
        except GraphError as error:
            raise GraphMatchFailed(f"add node failed: {error} in rule {_location(call_stack)}") from error
    if isinstance(statement, AddEdgeStmt):
        edge_id, current = _resolve_construction_ref(statement.edge_id, state, "edge", call_stack)
        source_id, current = _resolve_endpoint_ref(
            statement.source_endpoint,
            current,
            "edge source",
            call_stack,
        )
        target_id, current = _resolve_endpoint_ref(
            statement.target_endpoint,
            current,
            "edge target",
            call_stack,
        )
        attrs = _attrs_from_predicates(statement.attrs)
        try:
            return _ExecutionState(
                current.graph.add_edge(Edge(edge_id, source_id, target_id, labels=statement.labels, attrs=attrs)),
                current.bindings,
            )
        except GraphError as error:
            raise GraphMatchFailed(f"add edge failed: {error} in rule {_location(call_stack)}") from error
    if isinstance(statement, SetNodeAttrStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if not graph.has_node(node_id):
            raise GraphMatchFailed(f"set node target not found: {node_id} in rule {_location(call_stack)}")
        return _ExecutionState(
            graph.replace_node(graph.get_node(node_id).with_attr(statement.attr_name, statement.value)),
            state.bindings,
        )
    if isinstance(statement, SetEdgeAttrStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if not graph.has_edge(edge_id):
            raise GraphMatchFailed(f"set edge target not found: {edge_id} in rule {_location(call_stack)}")
        return _ExecutionState(
            graph.replace_edge(graph.get_edge(edge_id).with_attr(statement.attr_name, statement.value)),
            state.bindings,
        )
    if isinstance(statement, SetNodeLabelStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if not graph.has_node(node_id):
            raise GraphMatchFailed(f"set node target not found: {node_id} in rule {_location(call_stack)}")
        return _ExecutionState(graph.replace_node(graph.get_node(node_id).with_label(statement.label)), state.bindings)
    if isinstance(statement, SetEdgeLabelStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if not graph.has_edge(edge_id):
            raise GraphMatchFailed(f"set edge target not found: {edge_id} in rule {_location(call_stack)}")
        return _ExecutionState(graph.replace_edge(graph.get_edge(edge_id).with_label(statement.label)), state.bindings)
    if isinstance(statement, UnsetNodeAttrStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if not graph.has_node(node_id):
            raise GraphMatchFailed(f"unset node target not found: {node_id} in rule {_location(call_stack)}")
        return _ExecutionState(
            graph.replace_node(graph.get_node(node_id).without_attr(statement.attr_name)),
            state.bindings,
        )
    if isinstance(statement, UnsetEdgeAttrStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if not graph.has_edge(edge_id):
            raise GraphMatchFailed(f"unset edge target not found: {edge_id} in rule {_location(call_stack)}")
        return _ExecutionState(
            graph.replace_edge(graph.get_edge(edge_id).without_attr(statement.attr_name)),
            state.bindings,
        )
    if isinstance(statement, UnsetNodeLabelStmt):
        node_id = _resolve_ref(statement.node_id, state.bindings, "node", call_stack)
        if not graph.has_node(node_id):
            raise GraphMatchFailed(f"unset node target not found: {node_id} in rule {_location(call_stack)}")
        return _ExecutionState(graph.replace_node(graph.get_node(node_id).without_label(statement.label)), state.bindings)
    if isinstance(statement, UnsetEdgeLabelStmt):
        edge_id = _resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
        if not graph.has_edge(edge_id):
            raise GraphMatchFailed(f"unset edge target not found: {edge_id} in rule {_location(call_stack)}")
        return _ExecutionState(graph.replace_edge(graph.get_edge(edge_id).without_label(statement.label)), state.bindings)
    if isinstance(statement, CallStmt):
        return _execute_rule(statement.name, rules, state, call_stack=call_stack)
    raise RuntimeFailure(f"unsupported statement: {statement!r}")


def _execute_block(
    statement: BlockStmt,
    rules: dict[str, RuleDecl],
    state: _ExecutionState,
    *,
    call_stack: tuple[str, ...],
) -> _ExecutionState:
    return _execute_sequence(statement.statements, rules, state, call_stack=call_stack)


def _execute_sequence(
    statements: tuple[object, ...],
    rules: dict[str, RuleDecl],
    state: _ExecutionState,
    *,
    call_stack: tuple[str, ...],
) -> _ExecutionState:
    if not statements:
        return state

    first, rest = statements[0], statements[1:]
    last_error: RuleFailed | None = None
    for candidate in _statement_candidate_states(first, rules, state, call_stack=call_stack):
        try:
            return _execute_sequence(rest, rules, candidate, call_stack=call_stack)
        except RuleFailed as error:
            last_error = error

    if last_error is not None:
        raise last_error
    raise RuntimeFailure("statement produced no candidate states")


def _statement_candidate_states(
    statement: object,
    rules: dict[str, RuleDecl],
    state: _ExecutionState,
    *,
    call_stack: tuple[str, ...],
) -> Iterable[_ExecutionState]:
    if isinstance(statement, MatchNodeStmt):
        yield from _iter_match_node_states(statement, state, call_stack)
        return
    if isinstance(statement, MatchEdgeStmt):
        yield from _iter_match_edge_states(statement, state, call_stack)
        return
    yield _execute_statement(statement, rules, state, call_stack=call_stack)


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
    for candidate in _iter_match_node_states(statement, state, call_stack):
        return candidate
    raise RuntimeFailure("node matcher produced no candidate state")


def _iter_match_node_states(
    statement: MatchNodeStmt,
    state: _ExecutionState,
    call_stack: tuple[str, ...],
) -> Iterable[_ExecutionState]:
    graph = state.graph
    existing = state.bindings.get(statement.node_id.name)
    if existing is not None:
        if graph.has_node(existing) and _node_matches(graph.get_node(existing), statement, state, call_stack):
            yield state
            return
        raise GraphMatchFailed(
            f"matched node variable {statement.node_id.display()} no longer satisfies matcher "
            f"in rule {_location(call_stack)}"
        )

    matched = False
    for node in graph.nodes:
        if _node_static_matches(node, statement):
            candidate = _bind_variable(state, statement.node_id, node.id)
            if _where_predicates_match(node, statement.where, candidate, call_stack):
                matched = True
                yield candidate

    if not matched:
        raise GraphMatchFailed(f"no node matched {statement.node_id.display()} in rule {_location(call_stack)}")


def _execute_match_edge(
    statement: MatchEdgeStmt,
    state: _ExecutionState,
    call_stack: tuple[str, ...],
) -> _ExecutionState:
    for candidate in _iter_match_edge_states(statement, state, call_stack):
        return candidate
    raise RuntimeFailure("edge matcher produced no candidate state")


def _iter_match_edge_states(
    statement: MatchEdgeStmt,
    state: _ExecutionState,
    call_stack: tuple[str, ...],
) -> Iterable[_ExecutionState]:
    existing = state.bindings.get(statement.edge_id.name)
    if existing is not None:
        edge = state.graph.get_edge(existing) if state.graph.has_edge(existing) else None
        if edge is not None:
            candidate = _match_edge_candidate(statement, edge, state, call_stack)
            if candidate.matched:
                yield candidate.state
                return
        raise GraphMatchFailed(
            f"matched edge variable {statement.edge_id.display()} no longer satisfies matcher "
            f"in rule {_location(call_stack)}"
        )

    matched = False
    for edge in state.graph.edges:
        edge_state = _bind_variable(state, statement.edge_id, edge.id)
        candidate = _match_edge_candidate(statement, edge, edge_state, call_stack)
        if candidate.matched:
            matched = True
            yield candidate.state

    if not matched:
        raise GraphMatchFailed(f"no edge matched {statement.edge_id.display()} in rule {_location(call_stack)}")


def _forbidden_node_exists(
    statement: RequireNoNodeStmt,
    state: _ExecutionState,
    call_stack: tuple[str, ...],
) -> bool:
    for node in state.graph.nodes:
        candidate = _try_match_ref(statement.node_id, node.id, state)
        if not candidate.matched:
            continue
        if not _node_constraints_match(node, statement.labels, statement.attrs):
            continue
        if _where_predicates_match(node, statement.where, candidate.state, call_stack):
            return True
    return False


def _forbidden_edge_exists(
    statement: RequireNoEdgeStmt,
    state: _ExecutionState,
    call_stack: tuple[str, ...],
) -> bool:
    for edge in state.graph.edges:
        current = _try_match_ref(statement.edge_id, edge.id, state)
        if not current.matched:
            continue
        if not _edge_constraints_match(edge, statement.labels, statement.attrs):
            continue
        if statement.source_id is not None:
            source = _try_match_ref(statement.source_id, edge.source, current.state)
            if not source.matched:
                continue
            current = source
        if statement.target_id is not None:
            target = _try_match_ref(statement.target_id, edge.target, current.state)
            if not target.matched:
                continue
            current = target
        if _where_predicates_match(edge, statement.where, current.state, call_stack):
            return True
    return False


def _node_static_matches(node: Node, statement: MatchNodeStmt) -> bool:
    return _node_constraints_match(node, statement.labels, statement.attrs)


def _node_constraints_match(node: Node, labels: tuple[str, ...], attrs: tuple[AttrPredicate, ...]) -> bool:
    if not _labels_match(node, labels):
        return False
    return _attrs_match(node, attrs)


def _node_matches(
    node: Node,
    statement: MatchNodeStmt,
    state: _ExecutionState,
    call_stack: tuple[str, ...],
) -> bool:
    if not _node_static_matches(node, statement):
        return False
    return _where_predicates_match(node, statement.where, state, call_stack)


def _match_edge_candidate(
    statement: MatchEdgeStmt,
    edge: Edge,
    state: _ExecutionState,
    call_stack: tuple[str, ...],
) -> _BindOutcome:
    if not _edge_constraints_match(edge, statement.labels, statement.attrs):
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
    if not _where_predicates_match(edge, statement.where, current, call_stack):
        return _BindOutcome(False, current)
    return _BindOutcome(True, current)


def _edge_constraints_match(edge: Edge, labels: tuple[str, ...], attrs: tuple[AttrPredicate, ...]) -> bool:
    if not _labels_match(edge, labels):
        return False
    return _attrs_match(edge, attrs)


def _labels_match(item: Node | Edge, labels: tuple[str, ...]) -> bool:
    return all(item.has_label(label) for label in labels)


def _attrs_match(item: Node | Edge, predicates: tuple[AttrPredicate, ...]) -> bool:
    for predicate in predicates:
        if not _values_equal(item.attr(predicate.name), predicate.value):
            return False
    return True


def _attrs_from_predicates(predicates: tuple[AttrPredicate, ...]) -> tuple[tuple[str, LiteralValue], ...]:
    return tuple((predicate.name, predicate.value) for predicate in predicates)


def _where_predicates_match(
    item: Node | Edge,
    predicates: tuple[WherePredicate, ...],
    state: _ExecutionState,
    call_stack: tuple[str, ...],
) -> bool:
    for predicate in predicates:
        left = _eval_where_expr(item, predicate.left, state.bindings, call_stack)
        right = _eval_where_expr(item, predicate.right, state.bindings, call_stack)
        if not _compare_values(left, predicate.operator, right):
            return False
    return True


def _eval_where_expr(
    item: Node | Edge,
    expr: WhereExpr,
    bindings: Bindings,
    call_stack: tuple[str, ...],
) -> ComparableValue:
    if isinstance(expr, AttrExpr):
        return item.attr(expr.name)
    if isinstance(expr, FieldExpr):
        if expr.name == "id":
            return item.id
        if isinstance(item, Edge) and expr.name == "source":
            return item.source
        if isinstance(item, Edge) and expr.name == "target":
            return item.target
        return None
    if isinstance(expr, LiteralExpr):
        return expr.value
    if isinstance(expr, VarExpr):
        value = bindings.get(expr.name)
        if value is None:
            raise GraphMatchFailed(f"unbound where variable {expr.display()} in rule {_location(call_stack)}")
        return value
    raise RuntimeFailure(f"unsupported where expression: {expr!r}")


def _compare_values(left: ComparableValue, operator: str, right: ComparableValue) -> bool:
    if operator == "==":
        return _values_equal(left, right)
    if operator == "!=":
        return not _values_equal(left, right)
    if type(left) is not type(right):
        return False
    if isinstance(left, bool):
        return False
    if isinstance(left, int) and isinstance(right, int):
        if operator == "<":
            return left < right
        if operator == "<=":
            return left <= right
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
    if isinstance(left, str) and isinstance(right, str):
        if operator == "<":
            return left < right
        if operator == "<=":
            return left <= right
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
    return False


def _resolve_ref(ref: GraphRef, bindings: Bindings, kind: str, call_stack: tuple[str, ...]) -> str:
    if isinstance(ref, VarRef):
        value = bindings.get(ref.name)
        if value is None:
            raise GraphMatchFailed(f"unbound {kind} variable {ref.display()} in rule {_location(call_stack)}")
        return value
    return ref


def _resolve_construction_ref(
    ref: GraphRef,
    state: _ExecutionState,
    kind: str,
    call_stack: tuple[str, ...],
) -> tuple[str, _ExecutionState]:
    if isinstance(ref, VarRef):
        value = state.bindings.get(ref.name)
        if value is not None:
            return value, state
        if kind == "node":
            value = _fresh_graph_id(ref.name, state.graph.node_ids)
        elif kind == "edge":
            value = _fresh_graph_id(ref.name, state.graph.edge_ids)
        else:
            raise RuntimeFailure(f"unsupported construction target kind: {kind}")
        return value, _bind_variable(state, ref, value)
    if not ref:
        raise GraphMatchFailed(f"empty {kind} construction target in rule {_location(call_stack)}")
    return ref, state


def _resolve_endpoint_ref(
    endpoint: EndpointRef,
    state: _ExecutionState,
    kind: str,
    call_stack: tuple[str, ...],
) -> tuple[str, _ExecutionState]:
    if not endpoint.auto_create:
        return _resolve_ref(endpoint.ref, state.bindings, kind, call_stack), state

    node_id, current = _resolve_construction_ref(endpoint.ref, state, "node", call_stack)
    if current.graph.has_node(node_id):
        return node_id, current
    try:
        return node_id, _ExecutionState(current.graph.add_node(Node(node_id)), current.bindings)
    except GraphError as error:
        raise GraphMatchFailed(f"add edge endpoint failed: {error} in rule {_location(call_stack)}") from error


def _fresh_graph_id(base: str, existing_ids: tuple[str, ...]) -> str:
    existing = set(existing_ids)
    if base not in existing:
        return base
    suffix = 2
    while f"{base}_{suffix}" in existing:
        suffix += 1
    return f"{base}_{suffix}"


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


def _values_equal(actual: ComparableValue, expected: ComparableValue) -> bool:
    return type(actual) is type(expected) and actual == expected


def _format_value(value: ComparableValue) -> str:
    if value is None:
        return "<missing>"
    return repr(value)


def _format_graph_ref(ref: GraphRef) -> str:
    if isinstance(ref, VarRef):
        return ref.display()
    return repr(ref)


def _location(call_stack: tuple[str, ...]) -> str:
    return " -> ".join(call_stack) or "<entry>"
