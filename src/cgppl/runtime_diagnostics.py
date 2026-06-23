"""Runtime-specific diagnostic adapters for graph predicate failures."""

from __future__ import annotations

import json

from .ast import (
    AddEdgeStmt,
    AddNodeStmt,
    AttrPredicate,
    DeleteEdgeStmt,
    DeleteNodeStmt,
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
    SetEdgeAttrStmt,
    SetEdgeLabelStmt,
    SetNodeAttrStmt,
    SetNodeLabelStmt,
    UnsetEdgeAttrStmt,
    UnsetEdgeLabelStmt,
    UnsetNodeAttrStmt,
    UnsetNodeLabelStmt,
    VarExpr,
)
from .diagnostics import (
    format_graph_predicate,
    format_graph_predicate_failure,
    format_graph_ref,
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


def format_missing_delete_node_target_failure(
    statement: DeleteNodeStmt,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed delete-node mutation target lookup."""

    return format_graph_predicate_failure(
        "missing delete target for",
        "node",
        statement.node_id,
        call_stack=call_stack,
    )


def format_missing_delete_edge_target_failure(
    statement: DeleteEdgeStmt,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed delete-edge mutation target lookup."""

    return format_graph_predicate_failure(
        "missing delete target for",
        "edge",
        statement.edge_id,
        call_stack=call_stack,
    )


def format_missing_set_node_attr_target_failure(
    statement: SetNodeAttrStmt,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed set-node-attribute mutation target lookup."""

    return _format_missing_annotation_target_failure(
        "set",
        "node",
        statement.node_id,
        call_stack,
        attr_name=statement.attr_name,
    )


def format_missing_set_edge_attr_target_failure(
    statement: SetEdgeAttrStmt,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed set-edge-attribute mutation target lookup."""

    return _format_missing_annotation_target_failure(
        "set",
        "edge",
        statement.edge_id,
        call_stack,
        attr_name=statement.attr_name,
    )


def format_missing_set_node_label_target_failure(
    statement: SetNodeLabelStmt,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed set-node-label mutation target lookup."""

    return _format_missing_annotation_target_failure(
        "set",
        "node",
        statement.node_id,
        call_stack,
        label=statement.label,
    )


def format_missing_set_edge_label_target_failure(
    statement: SetEdgeLabelStmt,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed set-edge-label mutation target lookup."""

    return _format_missing_annotation_target_failure(
        "set",
        "edge",
        statement.edge_id,
        call_stack,
        label=statement.label,
    )


def format_missing_unset_node_attr_target_failure(
    statement: UnsetNodeAttrStmt,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed unset-node-attribute mutation target lookup."""

    return _format_missing_annotation_target_failure(
        "unset",
        "node",
        statement.node_id,
        call_stack,
        attr_name=statement.attr_name,
    )


def format_missing_unset_edge_attr_target_failure(
    statement: UnsetEdgeAttrStmt,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed unset-edge-attribute mutation target lookup."""

    return _format_missing_annotation_target_failure(
        "unset",
        "edge",
        statement.edge_id,
        call_stack,
        attr_name=statement.attr_name,
    )


def format_missing_unset_node_label_target_failure(
    statement: UnsetNodeLabelStmt,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed unset-node-label mutation target lookup."""

    return _format_missing_annotation_target_failure(
        "unset",
        "node",
        statement.node_id,
        call_stack,
        label=statement.label,
    )


def format_missing_unset_edge_label_target_failure(
    statement: UnsetEdgeLabelStmt,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed unset-edge-label mutation target lookup."""

    return _format_missing_annotation_target_failure(
        "unset",
        "edge",
        statement.edge_id,
        call_stack,
        label=statement.label,
    )


def format_add_node_failure(
    statement: AddNodeStmt,
    message: str,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed add-node graph construction precondition."""

    return _format_add_failure("node", statement.node_id, message, call_stack)


def format_add_edge_failure(
    statement: AddEdgeStmt,
    message: str,
    call_stack: tuple[str, ...],
) -> str:
    """Format a failed add-edge graph construction precondition."""

    return _format_add_failure("edge", statement.edge_id, message, call_stack)


def format_add_edge_endpoint_failure(message: str, call_stack: tuple[str, ...]) -> str:
    """Format a failed opt-in add-edge endpoint auto-creation precondition."""

    return f"add edge endpoint failed: {message} in rule {format_rule_location(call_stack)}"


def format_unbound_graph_ref_failure(ref: GraphRef, kind: str, call_stack: tuple[str, ...]) -> str:
    """Format an unbound graph reference variable lookup."""

    return f"unbound {kind} variable {format_graph_ref(ref)} in rule {format_rule_location(call_stack)}"


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


def _format_missing_annotation_target_failure(
    action: str,
    kind: str,
    ref: GraphRef,
    call_stack: tuple[str, ...],
    *,
    attr_name: str | None = None,
    label: str | None = None,
) -> str:
    target = f"{kind} {format_graph_ref(ref)}"
    constraints: list[str] = []
    if attr_name is not None:
        constraints.append(f"attr {json.dumps(attr_name)}")
    if label is not None:
        constraints.append(f"label {json.dumps(label)}")
    if constraints:
        target = f"{target} with {', '.join(constraints)}"
    return f"missing {action} target for {target} in rule {format_rule_location(call_stack)}"


def _format_add_failure(
    kind: str,
    ref: GraphRef,
    message: str,
    call_stack: tuple[str, ...],
) -> str:
    return f"add {kind} {format_graph_ref(ref)} failed: {message} in rule {format_rule_location(call_stack)}"
