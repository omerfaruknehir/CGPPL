# Construction failure diagnostics

This slice routes construction-time failures through the same structured runtime diagnostic helper layer used by predicate and mutation failures.

Target diagnostic shapes:

```text
add node "existing" failed: duplicate node id: existing in rule main
add edge $e failed: edge e references missing target node: missing in rule main
add edge endpoint failed: duplicate node id: source in rule main
```

Implemented:

- `format_add_node_failure(...)`
- `format_add_edge_failure(...)`
- `format_add_edge_endpoint_failure(...)`
- formatter unit coverage for literal and variable construction targets
- runtime regression coverage for add-node, add-edge, and endpoint auto-create failures
- direct runtime wiring in `src/cgppl/runtime.py` for `AddNodeStmt`, `AddEdgeStmt`, and `_resolve_endpoint_ref`
- removal of the temporary `src/cgppl/runtime_construction_wiring.py` adapter
- removal of the package-init construction diagnostics installer
- enabled direct-wiring contract coverage in `tests/test_runtime_construction_direct_wiring.py`

Architecture status:

Construction diagnostics now use canonical runtime dispatch. There is no construction diagnostics import-time adapter remaining.

Direct runtime wiring completed:

1. `src/cgppl/runtime.py` imports `format_add_node_failure`, `format_add_edge_failure`, and `format_add_edge_endpoint_failure`.
2. `AddNodeStmt` wraps construction `GraphError` with `format_add_node_failure(statement, str(error), call_stack)`.
3. `AddEdgeStmt` wraps construction `GraphError` with `format_add_edge_failure(statement, str(error), call_stack)`.
4. `_resolve_endpoint_ref` wraps endpoint auto-create `GraphError` with `format_add_edge_endpoint_failure(str(error), call_stack)`.
5. `src/cgppl/runtime_construction_wiring.py` was deleted.
6. `src/cgppl/__init__.py` no longer imports or calls the construction adapter installer.
7. `tests/test_runtime_construction_direct_wiring.py` is active.

Validation:

- PR #26 CI passed on head `a3b96e7bacaff151eace4600ae181251c89c1911`.
- PR #26 was squash-merged as `c98065c86ef4ab7e6a6b8d97f84352182153dae4`.
