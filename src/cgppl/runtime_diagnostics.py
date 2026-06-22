"""Runtime-specific diagnostic adapters for graph predicate failures."""

from __future__ import annotations

from .ast import (
    AttrPredicate,
    GraphRef,
    LiteralValue,
    MatchEdgeStmt,
    MatchNodeStmt,
    RequireEdgeAttrStmt,
    RequireEdgeLabelStmt,
    RequireEdgeStmt,
    RequireNoEdgeStmt,
    RequireNoNodeStmt,
    RequireNodeAttrStmt,
    RequireNodeLabelStmt,
    RequireNodeStmt,
    VarExpr,
)
from .diagnostics import (
    format_graph_predicate,
    format_graph_predicate_failure,
    format_literal,
    format_rule_location,
    format_where_expr,
)


def format_match_node_failure(statement: MatchNodeStmt, call_stack: tuple[str, ...]) -> str:
    """Format a failed node matcher using the shared predicate diagnostic shape."""

    return format_graph_predicate_failure(
        "no match for",
        "node",
        statement.node_id,
        labels=statement.labels,
        attrs=statement.attrs,
        where=statement.where,
        call_stack=call_stack,
    )


def format_match_edge_failure(statement: MatchEdgeStmt, call_stack: tuple[str, ...]) -> str:
    """Format a failed edge matcher using the shared predicate diagnostic shape."""

    return format_graph_predicate_failure(
        "no match for",
        "edge",
        statement.edge_id,
        source_id=statement.source_id,
        target_id=statement.target_id,
        labels=statement.labels,
        attrs=statement.attrs,
        where=statement.where,
        call_stack=call_stack,
    )


def format_forbidden_node_failure(statement: RequireNoNodeStmt, call_stack: tuple[str, ...]) -> str:
    """Format a negative node requirement failure."""

    return format_graph_predicate_failure(
        "forbidden match for",
        "node",
        statement.node_id,
        labels=statement.labels,
        attrs=statement.attrs,
        where=statement.where,
        call_stack=call_stack,
    )


def format_forbidden_edge_failure(statement: RequireNoEdgeStmt, call_stack: tuple[str, ...]) -> str:
    """Format a negative edge requirement failure."""

    return format_graph_predicate_failure(
        "forbidden match for",
        "edge",
        statement.edge_id,
        source_id=statement.source_id,
        target_id=statement.target_id,
        labels=statement.labels,
        attrs=statement.attrs,
        where=statement.where,
        call_stack=call_stack,
    )


def format_required_node_failure(statement: RequireNodeStmt, call_stack: tuple[str, ...]) -> str:
    """Format a failed positive node-existence requirement."""

    return format_graph_predicate_failure(
        "missing requirement for",
        "node",
        statement.node_id,
        call_stack=call_stack,
    )


def format_required_edge_failure(statement: RequireEdgeStmt, call_stack: tuple[str, ...]) -> str:
    """Format a failed positive edge-existence requirement."""

    return format_graph_predicate_failure(
        "missing requirement for",
        "edge",
        statement.edge_id,
        call_stack=call_stack,
    )


def format_required_node_label_failure(statement: RequireNodeLabelStmt, call_stack: tuple[str, ...]) -> str:
    """Format a failed positive node-label requirement."""

    return format_graph_predicate_failure(
        "missing requirement for",
        "node",
        statement.node_id,
        labels=(statement.label,),
        call_stack=call_stack,
    )


def format_required_edge_label_failure(statement: RequireEdgeLabelStmt, call_stack: tuple[str, ...]) -> str:
    """Format a failed positive edge-label requirement."""

    return format_graph_predicate_failure(
        "missing requirement for",
        "edge",
        statement.edge_id,
        labels=(statement.label,),
        call_stack=call_stack,
    )


def format_required_node_attr_failure(
    statement: RequireNodeAttrStmt,
    actual: LiteralValue | None,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed positive node-attribute requirement."""

    return _format_required_attr_failure(
        "node",
        statement.node_id,
        AttrPredicate(statement.attr_name, statement.value),
        actual,
        call_stack,
    )


def format_required_edge_attr_failure(
    statement: RequireEdgeAttrStmt,
    actual: LiteralValue | None,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed positive edge-attribute requirement."""

    return _format_required_attr_failure(
        "edge",
        statement.edge_id,
        AttrPredicate(statement.attr_name, statement.value),
        actual,
        call_stack,
    )


def format_unbound_where_variable_failure(expr: VarExpr, call_stack: tuple[str, ...]) -> str:
    """Format an unbound variable used while evaluating a where predicate."""

    return f"unbound where variable {format_where_expr(expr)} in rule {format_rule_location(call_stack)}"


def _format_required_attr_failure(
    kind: str,
    ref: GraphRef,
    predicate: AttrPredicate,
    actual: LiteralValue | None,
    call_stack: tuple[str, ...],
) -> str:
    requirement = format_graph_predicate(kind, ref, attrs=(predicate,))
    return (
        f"missing requirement for {requirement}; "
        f"found {format_literal(actual)} in rule {format_rule_location(call_stack)}"
    )
