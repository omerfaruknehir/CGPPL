# Construction failure diagnostics

This slice routes construction-time failures toward the same structured runtime diagnostic helper layer used by predicate and mutation failures.

Target diagnostic shapes:

```text
add node "existing" failed: duplicate node id: existing in rule main
add edge $edge failed: edge edge references missing target node: missing in rule main
add edge endpoint failed: duplicate node id: source in rule main
```

Implemented so far:

- `format_add_node_failure(...)`
- `format_add_edge_failure(...)`
- `format_add_edge_endpoint_failure(...)`
- formatter unit coverage for literal and variable construction targets
- runtime regression coverage for add-node, add-edge, and endpoint auto-create failures
- `src/cgppl/runtime_construction_wiring.py`, a temporary import-time adapter that makes the runtime tests pass while direct runtime wiring is pending
- `tests/test_runtime_construction_direct_wiring.py`, an intentional `xfail` cleanup contract requiring the adapter to be removed

Current caveat:

Construction diagnostics are functionally active, but not yet in the final architecture. `src/cgppl/__init__.py` still installs `runtime_construction_wiring.py` at import time. The next cleanup must fold the adapter directly into `src/cgppl/runtime.py`, then remove the adapter and installer.

Direct runtime wiring checklist:

1. Import `format_add_node_failure`, `format_add_edge_failure`, and `format_add_edge_endpoint_failure` in `src/cgppl/runtime.py`.
2. Replace the `AddNodeStmt` `GraphError` wrapper with `format_add_node_failure(statement, str(error), call_stack)`.
3. Replace the `AddEdgeStmt` `GraphError` wrapper with `format_add_edge_failure(statement, str(error), call_stack)`.
4. Replace the `_resolve_endpoint_ref` auto-create `GraphError` wrapper with `format_add_edge_endpoint_failure(str(error), call_stack)`.
5. Delete `src/cgppl/runtime_construction_wiring.py`.
6. Remove `install_construction_diagnostics` import/call from `src/cgppl/__init__.py`.
7. Remove the `xfail` marker from `tests/test_runtime_construction_direct_wiring.py`.
