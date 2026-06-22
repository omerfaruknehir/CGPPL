"""Shared formatting helpers for CGPPL runtime diagnostics."""

from __future__ import annotations

import json

from .ast import (
    AttrExpr,
    AttrPredicate,
    FieldExpr,
    GraphRef,
    LiteralExpr,
    LiteralValue,
    VarExpr,
    VarRef,
    WhereExpr,
    WherePredicate,
)

ComparableValue = LiteralValue | None


def format_rule_location(call_stack: tuple[str, ...]) -> str:
    """Return a stable human-readable rule call location."""

    return " -> ".join(call_stack) or "<entry>"


def format_graph_ref(ref: GraphRef) -> str:
    """Format a graph object reference as source-like CGPPL text."""

    if isinstance(ref, VarRef):
        return ref.display()
    return json.dumps(ref)


def format_literal(value: ComparableValue) -> str:
    """Format a literal value as source-like CGPPL text."""

    if value is None:
        return "<missing>"
    return json.dumps(value)


def format_where_expr(expr: WhereExpr) -> str:
    """Format a where-expression as a compact diagnostic fragment."""

    if isinstance(expr, AttrExpr):
        return f'attr {json.dumps(expr.name)}'
    if isinstance(expr, FieldExpr):
        return f"field {expr.name}"
    if isinstance(expr, LiteralExpr):
        return format_literal(expr.value)
    if isinstance(expr, VarExpr):
        return expr.display()
    raise TypeError(f"unsupported where expression: {expr!r}")


def format_where_predicate(predicate: WherePredicate) -> str:
    """Format a single where predicate as source-like CGPPL text."""

    return (
        f"{format_where_expr(predicate.left)} "
        f"{predicate.operator} "
        f"{format_where_expr(predicate.right)}"
    )


def format_graph_predicate(
    kind: str,
    ref: GraphRef,
    *,
    labels: tuple[str, ...] = (),
    attrs: tuple[AttrPredicate, ...] = (),
    where: tuple[WherePredicate, ...] = (),
) -> str:
    """Format a node/edge predicate with its labels, attrs, and where clauses."""

    pieces = [f"{kind} {format_graph_ref(ref)}"]
    constraints: list[str] = []
    constraints.extend(f"label {json.dumps(label)}" for label in labels)
    constraints.extend(
        f"attr {json.dumps(predicate.name)} = {format_literal(predicate.value)}"
        for predicate in attrs
    )
    constraints.extend(f"where {format_where_predicate(predicate)}" for predicate in where)
    if constraints:
        pieces.append("with " + ", ".join(constraints))
    return " ".join(pieces)


def format_graph_predicate_failure(
    action: str,
    kind: str,
    ref: GraphRef,
    *,
    labels: tuple[str, ...] = (),
    attrs: tuple[AttrPredicate, ...] = (),
    where: tuple[WherePredicate, ...] = (),
    call_stack: tuple[str, ...],
) -> str:
    """Format a full rule-local graph predicate failure message."""

    predicate = format_graph_predicate(kind, ref, labels=labels, attrs=attrs, where=where)
    return f"{action} {predicate} in rule {format_rule_location(call_stack)}"
