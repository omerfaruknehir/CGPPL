"""Runtime adapter for structured construction diagnostics."""

from __future__ import annotations

from typing import Any

from .ast import AddEdgeStmt, AddNodeStmt
from .graph import Edge, GraphError, Node
from .runtime_diagnostics import (
    format_add_edge_endpoint_failure,
    format_add_edge_failure,
    format_add_node_failure,
)

_installed = False


def install_construction_diagnostics() -> None:
    """Route construction GraphError failures through structured diagnostics."""

    global _installed
    if _installed:
        return

    from . import runtime

    original_execute_statement = runtime._execute_statement
    original_resolve_endpoint_ref = runtime._resolve_endpoint_ref

    def resolve_endpoint_ref_with_construction_diagnostics(
        endpoint: Any,
        state: Any,
        kind: str,
        call_stack: tuple[str, ...],
    ) -> tuple[str, Any]:
        if not endpoint.auto_create:
            return runtime._resolve_ref(endpoint.ref, state.bindings, kind, call_stack), state

        node_id, current = runtime._resolve_construction_ref(endpoint.ref, state, "node", call_stack)
        if current.graph.has_node(node_id):
            return node_id, current
        try:
            return node_id, runtime._ExecutionState(current.graph.add_node(Node(node_id)), current.bindings)
        except GraphError as error:
            raise runtime.GraphMatchFailed(format_add_edge_endpoint_failure(str(error), call_stack)) from error

    def execute_statement_with_construction_diagnostics(
        statement: object,
        rules: dict[str, Any],
        state: Any,
        *,
        call_stack: tuple[str, ...],
    ) -> Any:
        if isinstance(statement, AddNodeStmt):
            node_id, current = runtime._resolve_construction_ref(statement.node_id, state, "node", call_stack)
            attrs = runtime._attrs_from_predicates(statement.attrs)
            try:
                return runtime._ExecutionState(
                    current.graph.add_node(Node(node_id, labels=statement.labels, attrs=attrs)),
                    current.bindings,
                )
            except GraphError as error:
                raise runtime.GraphMatchFailed(format_add_node_failure(statement, str(error), call_stack)) from error

        if isinstance(statement, AddEdgeStmt):
            edge_id, current = runtime._resolve_construction_ref(statement.edge_id, state, "edge", call_stack)
            source_id, current = runtime._resolve_endpoint_ref(
                statement.source_endpoint,
                current,
                "edge source",
                call_stack,
            )
            target_id, current = runtime._resolve_endpoint_ref(
                statement.target_endpoint,
                current,
                "edge target",
                call_stack,
            )
            attrs = runtime._attrs_from_predicates(statement.attrs)
            try:
                return runtime._ExecutionState(
                    current.graph.add_edge(Edge(edge_id, source_id, target_id, labels=statement.labels, attrs=attrs)),
                    current.bindings,
                )
            except GraphError as error:
                raise runtime.GraphMatchFailed(format_add_edge_failure(statement, str(error), call_stack)) from error

        return original_execute_statement(statement, rules, state, call_stack=call_stack)

    runtime._resolve_endpoint_ref = resolve_endpoint_ref_with_construction_diagnostics
    runtime._execute_statement = execute_statement_with_construction_diagnostics
    _installed = True
