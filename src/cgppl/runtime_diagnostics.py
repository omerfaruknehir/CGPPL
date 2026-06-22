"""Runtime-specific diagnostic adapters for graph predicate failures."""

from __future__ import annotations

from .ast import MatchEdgeStmt, MatchNodeStmt, RequireNoEdgeStmt, RequireNoNodeStmt
from .diagnostics import format_graph_predicate_failure


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
