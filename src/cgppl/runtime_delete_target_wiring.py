"""Runtime adapter for structured delete-target diagnostics."""

from __future__ import annotations

from typing import Any

from .ast import DeleteEdgeStmt, DeleteNodeStmt
from .runtime_diagnostics import (
    format_missing_delete_edge_target_failure,
    format_missing_delete_node_target_failure,
)

_installed = False


def install_delete_target_diagnostics() -> None:
    """Route delete-node and delete-edge misses through structured diagnostics."""

    global _installed
    if _installed:
        return

    from . import runtime

    original = runtime._execute_statement

    def execute_statement_with_delete_diagnostics(
        statement: object,
        rules: dict[str, Any],
        state: Any,
        *,
        call_stack: tuple[str, ...],
    ) -> Any:
        graph = state.graph
        if isinstance(statement, DeleteNodeStmt):
            node_id = runtime._resolve_ref(statement.node_id, state.bindings, "node", call_stack)
            if graph.has_node(node_id):
                return runtime._ExecutionState(graph.remove_node(node_id), state.bindings)
            raise runtime.GraphMatchFailed(format_missing_delete_node_target_failure(statement, call_stack))

        if isinstance(statement, DeleteEdgeStmt):
            edge_id = runtime._resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
            if graph.has_edge(edge_id):
                return runtime._ExecutionState(graph.remove_edge(edge_id), state.bindings)
            raise runtime.GraphMatchFailed(format_missing_delete_edge_target_failure(statement, call_stack))

        return original(statement, rules, state, call_stack=call_stack)

    runtime._execute_statement = execute_statement_with_delete_diagnostics
    _installed = True
