"""Compatibility wiring for structured positive-require diagnostics.

This module installs a narrow runtime adapter so positive `require` statements
use the same structured diagnostic helpers as matcher and negative-requirement
failures. It is intentionally small and delegates every unrelated statement
back to the canonical runtime implementation.
"""

from __future__ import annotations

from . import runtime as _runtime
from .ast import (
    RequireEdgeAttrStmt,
    RequireEdgeLabelStmt,
    RequireEdgeStmt,
    RequireNodeAttrStmt,
    RequireNodeLabelStmt,
    RequireNodeStmt,
)
from .runtime_diagnostics import (
    format_required_edge_attr_failure,
    format_required_edge_failure,
    format_required_edge_label_failure,
    format_required_node_attr_failure,
    format_required_node_failure,
    format_required_node_label_failure,
)


def install_positive_require_diagnostics() -> None:
    """Install structured diagnostics for positive require runtime paths."""

    original = _runtime._execute_statement

    if getattr(original, "_cgppl_positive_require_diagnostics", False):
        return

    def _execute_statement(statement: object, rules: dict[str, object], state: object, *, call_stack: tuple[str, ...]) -> object:
        graph = state.graph

        if isinstance(statement, RequireNodeStmt):
            node_id = _runtime._resolve_ref(statement.node_id, state.bindings, "node", call_stack)
            if graph.has_node(node_id):
                return state
            raise _runtime.GraphMatchFailed(format_required_node_failure(statement, call_stack))

        if isinstance(statement, RequireEdgeStmt):
            edge_id = _runtime._resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
            if graph.has_edge(edge_id):
                return state
            raise _runtime.GraphMatchFailed(format_required_edge_failure(statement, call_stack))

        if isinstance(statement, RequireNodeAttrStmt):
            node_id = _runtime._resolve_ref(statement.node_id, state.bindings, "node", call_stack)
            if not graph.has_node(node_id):
                raise _runtime.GraphMatchFailed(format_required_node_failure(RequireNodeStmt(statement.node_id), call_stack))
            actual = graph.get_node(node_id).attr(statement.attr_name)
            if _runtime._values_equal(actual, statement.value):
                return state
            raise _runtime.GraphMatchFailed(format_required_node_attr_failure(statement, actual, call_stack))

        if isinstance(statement, RequireEdgeAttrStmt):
            edge_id = _runtime._resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
            if not graph.has_edge(edge_id):
                raise _runtime.GraphMatchFailed(format_required_edge_failure(RequireEdgeStmt(statement.edge_id), call_stack))
            actual = graph.get_edge(edge_id).attr(statement.attr_name)
            if _runtime._values_equal(actual, statement.value):
                return state
            raise _runtime.GraphMatchFailed(format_required_edge_attr_failure(statement, actual, call_stack))

        if isinstance(statement, RequireNodeLabelStmt):
            node_id = _runtime._resolve_ref(statement.node_id, state.bindings, "node", call_stack)
            if not graph.has_node(node_id):
                raise _runtime.GraphMatchFailed(format_required_node_failure(RequireNodeStmt(statement.node_id), call_stack))
            if graph.get_node(node_id).has_label(statement.label):
                return state
            raise _runtime.GraphMatchFailed(format_required_node_label_failure(statement, call_stack))

        if isinstance(statement, RequireEdgeLabelStmt):
            edge_id = _runtime._resolve_ref(statement.edge_id, state.bindings, "edge", call_stack)
            if not graph.has_edge(edge_id):
                raise _runtime.GraphMatchFailed(format_required_edge_failure(RequireEdgeStmt(statement.edge_id), call_stack))
            if graph.get_edge(edge_id).has_label(statement.label):
                return state
            raise _runtime.GraphMatchFailed(format_required_edge_label_failure(statement, call_stack))

        return original(statement, rules, state, call_stack=call_stack)

    _execute_statement._cgppl_positive_require_diagnostics = True
    _runtime._execute_statement = _execute_statement
