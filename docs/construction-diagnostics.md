# Construction failure diagnostics

This slice starts routing construction-time failures toward the same structured runtime diagnostic helper layer used by predicate and mutation failures.

Target diagnostic shapes:

```text
add node "existing" failed: duplicate node id: existing in rule main
add edge $edge failed: edge edge references missing target node: missing in rule main
add edge endpoint failed: duplicate node id: source in rule main
```

Implemented in this slice:

- `format_add_node_failure(...)`
- `format_add_edge_failure(...)`
- `format_add_edge_endpoint_failure(...)`
- formatter unit coverage for literal and variable construction targets
- `xfail` runtime regression coverage documenting the pending runtime wiring

Runtime wiring is intentionally left for the next incremental slice. The current runtime still wraps construction `GraphError`s with direct strings until `AddNodeStmt`, `AddEdgeStmt`, and endpoint auto-create failure paths are wired to these helpers.
