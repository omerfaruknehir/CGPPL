# Mutation target direct runtime wiring

Delete-target and annotation-target structured diagnostics are now wired directly in `src/cgppl/runtime.py`.

## Direct wiring

`src/cgppl/runtime.py` imports and calls these helpers directly:

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

The direct wiring covers these statement handlers:

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

Package initialization no longer imports or calls mutation-target adapter installers, and the adapter modules have been deleted:

```text
src/cgppl/runtime_delete_target_wiring.py
src/cgppl/runtime_annotation_target_wiring.py
```

The `tests/test_runtime_mutation_target_direct_wiring.py` regression contract is now enabled.
