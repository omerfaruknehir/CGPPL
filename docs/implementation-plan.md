# CGPPL implementation plan

This document tracks the next practical implementation slices for the executable CGPPL subset.

## Current baseline

The current runtime can lex, parse, validate, and execute a useful graph-rewrite subset with:

- rule declarations and calls
- sequential blocks
- `try { ... } or { ... }` fallback blocks with rollback
- graph requirements, including negative requirements
- node and edge matching with labels, attributes, endpoint constraints, and `where` predicates
- node and edge construction with inline labels and inline attributes
- multi-label matcher, negative-requirement, and construction clauses
- variable-bound construction IDs with deterministic fresh-ID generation
- rule-local construction precondition diagnostics for duplicate IDs and strict missing edge endpoints
- endpoint construction policy metadata and opt-in runtime endpoint auto-creation for `add edge` source/target refs
- shared source-like diagnostic formatting helpers for graph refs, literals, constraints, where expressions, and rule locations
- direct runtime structured diagnostics for matcher, negative-requirement, positive-requirement, unbound `where` variable, delete-target, and annotation-target mutation paths
- label/attribute mutation and idempotent annotation removal
- constructed-object lifecycle tests for match/require/delete/no-require flows

## Completed feature slice: multi-label predicates and construction

Target syntax:

```cgppl
rule main => {
  add node "generated" label "Generated" label "Replacement" attr "kind" = "generated";
  add edge "new-link" from "n1" to "generated" label "new" label "owned";

  match node $n label "Generated" label "Replacement";
  match edge $e from "n1" to $n label "new" label "owned";
  require no node $bad label "Generated" label "Blocked";
}
```

Implementation status:

1. Done: matcher, negative-requirement, and constructor AST nodes now carry normalized `labels` tuples while preserving the old `label` compatibility field.
2. Done: parser accumulates repeated `label` clauses and rejects duplicate same-label clauses in the same predicate/constructor.
3. Done: runtime node/edge predicate checks require every listed label to be present.
4. Done: construction runtime applies every inline label at creation time.
5. Done: tests cover positive multi-label node matching, edge matching, negative requirements, construction, and duplicate same-label rejection.
6. Done: executable example and README syntax/status updates were added.

## Completed feature slice: variable-bound construction IDs

This slice allows construction targets to come from variables. Rules can now derive new graph objects from earlier matches without hard-coded literal IDs.

Target syntax:

```cgppl
rule main => {
  match node $source label "Root";
  add node $replacement label "Generated";
  add edge $new_edge from $source to $replacement label "new";
}
```

Semantics:

- Literal construction IDs keep the existing behavior.
- Bound construction variables resolve to their existing binding.
- Unbound construction variables generate deterministic fresh IDs from the variable name, then bind the variable for later statements. For example, `$replacement` first tries `replacement`; if that ID already exists, it tries `replacement_2`, `replacement_3`, and so on.
- Node construction variables avoid existing node IDs. Edge construction variables avoid existing edge IDs.
- Edge source/target variables are still normal graph references unless the endpoint is explicitly marked with `add`.

Implementation status:

1. Done: decided unbound construction variables generate deterministic fresh IDs rather than requiring prior bindings.
2. Done: `AddNodeStmt.node_id` and `AddEdgeStmt.edge_id` were widened from `str` to `GraphRef`.
3. Done: parser `add node` and `add edge` targets now parse graph refs instead of graph IDs.
4. Done: runtime construction resolves bound variables, generates deterministic fresh IDs for unbound construction target variables, and binds generated variables.
5. Done: tests cover literal construction compatibility, generated IDs, collision suffixing, duplicate bound IDs, edge target construction, and unbound source errors.
6. Done: executable example and README syntax/status updates were added.

## Completed feature slice: constructor precondition diagnostics

This slice converts graph-IR construction failures into rule-local failures. Construction duplicate-ID and strict missing-endpoint failures now include rule context and participate in `try-or` fallback behavior.

Example:

```cgppl
rule main => try {
  add node "existing" label "Duplicate";
} or {
  add node "fallback" label "Recovered";
}
```

Implementation status:

1. Done: runtime wraps `GraphError` raised by node/edge construction as `GraphMatchFailed` with rule context.
2. Done: duplicate node construction now fails as a rule failure instead of escaping as a graph-IR exception.
3. Done: missing edge endpoint construction reports `add edge failed: ... in rule ...`.
4. Done: tests cover duplicate-ID diagnostics, missing-endpoint diagnostics, and `try-or` fallback after construction precondition failure.
5. Done: README status and notes were updated.

## Completed feature slice: endpoint construction policy

Decision: plain `add edge` keeps explicit endpoint preconditions. It does not auto-create missing endpoint nodes. This avoids silently creating misspelled or weakly matched nodes and keeps node creation visible in rewrite programs.

Detailed policy is recorded in [`docs/endpoint-construction-policy.md`](endpoint-construction-policy.md).

Opt-in syntax for endpoint auto-creation:

```cgppl
add edge $new_edge from add $source to add $target label "new";
```

Runtime semantics:

- Without `add`, endpoints remain strict graph references and must already exist.
- With `add` before an endpoint variable, an unbound variable creates a fresh node ID using the existing deterministic construction-ID rule, then binds the variable.
- With `add` before a literal endpoint, the runtime ensures a node with that literal ID exists; if absent, it creates it.
- With `add` before an already-bound variable, the runtime uses the binding and ensures that the bound node exists.
- Auto-created endpoint nodes start with no labels or attributes.

Implementation status:

1. Done: design decision recorded; default edge construction remains explicit-only.
2. Done: opt-in syntax and proposed semantics were documented.
3. Done: parser tests cover strict, opt-in, and mixed endpoint policies.
4. Done: `EndpointRef` records endpoint graph refs plus an `auto_create` flag.
5. Done: `AddEdgeStmt` exposes `source_endpoint` and `target_endpoint` compatibility properties while preserving existing `source_id` / `target_id` fields.
6. Done: parser records `from add ...` and `to add ...` as endpoint auto-create metadata.
7. Done: runtime endpoint auto-creation creates or ensures endpoint nodes before constructing the edge.
8. Done: runtime tests cover opt-in source creation, target creation, mixed strict/auto-create policy, existing literal endpoints, variable binding, and strict precondition preservation.
9. Done: CLI execution tests cover endpoint auto-creation through the command-line entry point.
10. Done: executable example and README syntax/status updates were added.

## Completed feature slice: structured predicate diagnostics

This slice standardized graph predicate failure messages before adding more predicate forms. Matchers and negative requirements now report source-like refs and constraints consistently.

Implementation status:

1. Done: added `src/cgppl/diagnostics.py` with shared formatting helpers for graph refs, literals, where predicates, graph predicate constraints, graph predicate failures, and rule call-stack locations.
2. Done: added unit coverage for diagnostic formatting behavior.
3. Done: added `src/cgppl/runtime_diagnostics.py` with runtime-specific adapters for node/edge matcher failures and negative node/edge requirement failures.
4. Done: added unit coverage for runtime diagnostic adapter output with labels, attrs, `where` predicates, and nested rule locations.
5. Done: wired matcher and negative-requirement runtime failure paths to the runtime diagnostic adapters.
6. Done: added regression tests proving actual runtime failure messages use the structured helpers for fresh matchers, bound matchers, and negative requirements.

## Completed feature slice: edge endpoint diagnostics

This slice extends structured edge diagnostics so endpoint predicates are visible in failure messages.

Target diagnostic shape:

```text
no match for edge $e from "a" to $target with label "link", where attr "weight" >= 2 in rule main
forbidden match for edge $bad from $source to $target with label "blocked" in rule main
```

Implementation status:

1. Done: shared graph-predicate formatting accepts optional `source_id` and `target_id` refs.
2. Done: runtime diagnostic adapters pass edge source/target refs for edge matcher and negative-edge failures.
3. Done: unit/runtime tests cover endpoint-aware edge diagnostic messages.
4. Done: CI passed and the endpoint diagnostics slice was merged.

## Completed feature slice: positive require diagnostics

This slice extends structured diagnostics to positive `require` statements.

Target diagnostic shape:

```text
missing requirement for node "missing" in rule main
missing requirement for edge $e with label "link" in rule main
missing requirement for node "n1" with attr "kind" = "root"; found "leaf" in rule main
```

Implementation status:

1. Done: runtime diagnostic adapter helpers cover missing node, missing edge, missing node label, missing edge label, node attribute mismatch, and edge attribute mismatch messages.
2. Done: unit tests cover the new positive-require adapter helpers.
3. Done: runtime regression tests verify the target messages for positive require failures.
4. Done: CLI/runtime/backtracking expectations were updated from old direct strings to structured diagnostics.
5. Done: CI passed and the positive-require diagnostics slice was merged.
6. Done: positive require diagnostics are wired directly in `src/cgppl/runtime.py`.
7. Done: the import-time adapter module was removed and package initialization no longer mutates runtime dispatch.

## Completed feature slice: where variable diagnostics

This slice routes unbound `where` variable failures through the runtime diagnostic helper layer.

Implementation status:

1. Done: added `format_unbound_where_variable_failure(...)` to `src/cgppl/runtime_diagnostics.py`.
2. Done: `_eval_where_expr` now uses the helper for unbound `VarExpr` operands.
3. Done: formatter and runtime regression tests cover the emitted message.
4. Done: CI passed and the where-variable diagnostic slice was merged.

## Completed feature slice: mutation target structured diagnostics

This slice extends structured diagnostics to delete-target mutation lookups.

Target diagnostic shape:

```text
missing delete target for node "missing" in rule main
missing delete target for edge $e in rule main -> helper
```

Implementation status:

1. Done: added `format_missing_delete_node_target_failure(...)` and `format_missing_delete_edge_target_failure(...)` to the runtime diagnostic helper layer.
2. Done: unit tests cover the new delete-target diagnostic helpers.
3. Done: runtime regression tests cover literal and bound delete-node/delete-edge target failures.
4. Done: stale runtime expectations were updated from the legacy `delete node target not found` wording.
5. Done: CI passed and the delete-target diagnostics slice was merged.
6. Done: delete-target diagnostics are wired directly in `src/cgppl/runtime.py`.
7. Done: the temporary delete-target adapter module was removed and package initialization no longer mutates runtime dispatch.

## Completed feature slice: annotation target structured diagnostics

This slice extends structured diagnostics to label/attribute mutation target lookups.

Target diagnostic shape:

```text
missing set target for node "missing" with attr "kind" in rule main
missing set target for edge $e with label "selected" in rule main
missing unset target for node $n with attr "kind" in rule main
missing unset target for edge "missing" with label "selected" in rule main
```

Implementation status:

1. Done: added missing set/unset target helpers for node attrs, edge attrs, node labels, and edge labels to `src/cgppl/runtime_diagnostics.py`.
2. Done: unit tests cover all annotation-target diagnostic helper variants.
3. Done: runtime regression coverage now covers all literal annotation target miss shapes.
4. Done: runtime regression coverage now covers bound node/edge targets that are matched, deleted, and then used by a later annotation mutation.
5. Done: stale runtime expectations were updated from the legacy `set ... target not found` and `unset ... target not found` wording.
6. Done: CI passed and the expanded annotation-target diagnostics coverage slice was merged.
7. Done: annotation-target diagnostics are wired directly in `src/cgppl/runtime.py`.
8. Done: the temporary annotation-target adapter module was removed and package initialization no longer mutates runtime dispatch.

## Completed cleanup slice: direct mutation-target runtime wiring

Delete-target and annotation-target diagnostics now use canonical runtime dispatch instead of import-time adapters.

Implementation status:

1. Done: `src/cgppl/runtime.py` imports and calls all delete-target and annotation-target diagnostic helpers directly.
2. Done: `src/cgppl/runtime_delete_target_wiring.py` and `src/cgppl/runtime_annotation_target_wiring.py` were removed.
3. Done: package initialization no longer imports or calls mutation-target adapter installers.
4. Done: the direct-wiring regression contract was enabled.
5. Done: CI passed and the direct mutation-target runtime wiring cleanup was merged.

## Next feature slice: construction failure structured diagnostics

The next useful diagnostics slice is construction-time failure cleanup. `AddNodeStmt`, `AddEdgeStmt`, and opt-in endpoint auto-creation still wrap `GraphError` with direct runtime strings instead of routing through `src/cgppl/runtime_diagnostics.py`.

Target diagnostic shape:

```text
add node "existing" failed: duplicate node id: existing in rule main
add edge $edge failed: edge edge references missing target node: missing in rule main
add edge endpoint failed: duplicate node id: source in rule main
```

Next concrete code step:

- Add formatter helpers for `AddNodeStmt`, `AddEdgeStmt`, and endpoint auto-create failures in `src/cgppl/runtime_diagnostics.py`, add unit coverage for those helpers, then wire the `GraphError` wrappers in `src/cgppl/runtime.py` to the helpers and update stale construction failure expectations.
