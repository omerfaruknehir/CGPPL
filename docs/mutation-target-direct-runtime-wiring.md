# Mutation target direct runtime wiring

Delete-target and annotation-target structured diagnostics are currently functional, but they are installed through runtime adapter modules during package initialization.

This cleanup slice should make `src/cgppl/runtime.py` the canonical dispatcher for mutation-target diagnostics.

## Direct wiring contract

`src/cgppl/runtime.py` should import and call these helpers directly:

```python
format_missing_delete_node_target_failure
format_missing_delete_edge_target_failure
format_missing_set_node_attr_target_failure
format_missing_set_edge_attr_target_failure
format_missing_set_node_label_target_failure
format_missing_set_edge_label_target_failure
format_missing_unset_node_attr_target_failure
format_missing_unset_edge_attr_target_failure
format_missing_unset_node_label_target_failure
format_missing_unset_edge_label_target_failure
```

The direct wiring should cover these statement handlers:

```text
DeleteNodeStmt
DeleteEdgeStmt
SetNodeAttrStmt
SetEdgeAttrStmt
SetNodeLabelStmt
SetEdgeLabelStmt
UnsetNodeAttrStmt
UnsetEdgeAttrStmt
UnsetNodeLabelStmt
UnsetEdgeLabelStmt
```

After the direct wiring lands, package initialization should no longer import or call adapter installers, and these adapter modules should be deleted:

```text
src/cgppl/runtime_delete_target_wiring.py
src/cgppl/runtime_annotation_target_wiring.py
```

The `tests/test_runtime_mutation_target_direct_wiring.py` regression contract is intentionally marked `xfail` until this cleanup is complete.
