"""Runtime adapter for structured annotation-target diagnostics."""

from __future__ import annotations

from typing import Any

from .ast import (
    SetEdgeAttrStmt,
    SetEdgeLabelStmt,
    SetNodeAttrStmt,
    SetNodeLabelStmt,
    UnsetEdgeAttrStmt,
    UnsetEdgeLabelStmt,
    UnsetNodeAttrStmt,
    UnsetNodeLabelStmt,
)
from .runtime_diagnostics import (
    format_missing_set_edge_attr_target_failure,
    format_missing_set_edge_label_target_failure,
    format_missing_set_node_attr_target_failure,
    format_missing_set_node_label_target_failure,
    format_missing_unset_edge_attr_target_failure,
    format_missing_unset_edge_label_target_failure,
    format_missing_unset_node_attr_target_failure,
    format_missing_unset_node_label_target_failure,
)

_installed = False


def install_annotation_target_diagnostics() -> None:
    """Route annotation mutation target misses through structured diagnostics."""

    global _installed
    if _installed:
        return

    from . import runtime

    original = runtime._execute_statement

    def execute_statement_with_annotation_diagnostics(
        statement: object,
        rules: dict[str, Any],
        state: Any,
        *,
        call_stack: tuple[str, ...],
    ) -> Any:
        graph = state.graph

        if isinstance(statement, SetNodeAttrStmt):
            node_id = runtime._resolve_ref(statement.node_id, state.bindings, "node", call_stack)
            if not graph.has_node(node_id):
                raise runtime.GraphMatchFailed(format_missing_set_node_attr_target_failure(statement, call_stack))

        if isinstance(statement, SetEdgeAttrStmt):
            edge_id = runtime._resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
            if not graph.has_edge(edge_id):
                raise runtime.GraphMatchFailed(format_missing_set_edge_attr_target_failure(statement, call_stack))

        if isinstance(statement, SetNodeLabelStmt):
            node_id = runtime._resolve_ref(statement.node_id, state.bindings, "node", call_stack)
            if not graph.has_node(node_id):
                raise runtime.GraphMatchFailed(format_missing_set_node_label_target_failure(statement, call_stack))

        if isinstance(statement, SetEdgeLabelStmt):
            edge_id = runtime._resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
            if not graph.has_edge(edge_id):
                raise runtime.GraphMatchFailed(format_missing_set_edge_label_target_failure(statement, call_stack))

        if isinstance(statement, UnsetNodeAttrStmt):
            node_id = runtime._resolve_ref(statement.node_id, state.bindings, "node", call_stack)
            if not graph.has_node(node_id):
                raise runtime.GraphMatchFailed(format_missing_unset_node_attr_target_failure(statement, call_stack))

        if isinstance(statement, UnsetEdgeAttrStmt):
            edge_id = runtime._resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
            if not graph.has_edge(edge_id):
                raise runtime.GraphMatchFailed(format_missing_unset_edge_attr_target_failure(statement, call_stack))

        if isinstance(statement, UnsetNodeLabelStmt):
            node_id = runtime._resolve_ref(statement.node_id, state.bindings, "node", call_stack)
            if not graph.has_node(node_id):
                raise runtime.GraphMatchFailed(format_missing_unset_node_label_target_failure(statement, call_stack))

        if isinstance(statement, UnsetEdgeLabelStmt):
            edge_id = runtime._resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
            if not graph.has_edge(edge_id):
                raise runtime.GraphMatchFailed(format_missing_unset_edge_label_target_failure(statement, call_stack))

        return original(statement, rules, state, call_stack=call_stack)

    runtime._execute_statement = execute_statement_with_annotation_diagnostics
    _installed = True
