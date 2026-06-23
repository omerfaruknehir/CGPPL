# Unbound graph-ref diagnostics

This slice routes unbound graph-reference variable failures through the runtime diagnostic helper layer.

Current legacy runtime site:

```python
_resolve_ref(...)
```

Target diagnostic shape:

```text
unbound edge source variable $missing in rule main
unbound node variable $n in rule main -> helper
```

Implemented in this slice:

- Added `format_unbound_graph_ref_failure(...)` to `src/cgppl/runtime_diagnostics.py`.
- Added helper-level coverage in `tests/test_runtime_unbound_graph_ref_diagnostics.py`.
- Added an intentional `xfail` direct-wiring contract requiring `src/cgppl/runtime.py` to import and call the helper instead of emitting the f-string inline.

Next cleanup step:

1. Import `format_unbound_graph_ref_failure` in `src/cgppl/runtime.py`.
2. Replace `_resolve_ref`'s direct `GraphMatchFailed(f"unbound {kind} variable ...")` with `GraphMatchFailed(format_unbound_graph_ref_failure(ref, kind, call_stack))`.
3. Remove the `xfail` marker from `tests/test_runtime_unbound_graph_ref_diagnostics.py`.
4. Update any stale assertions if CI finds tests matching the direct string loosely or expecting old wording.
