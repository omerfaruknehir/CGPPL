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
- shared source-like diagnostic formatting helpers for graph refs, literals, constraints, and rule locations
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

## In-progress feature slice: structured predicate diagnostics

This slice standardizes graph predicate failure messages before adding more predicate forms. The goal is to make match, require, negative-require, and future predicate failures report source-like refs and constraints consistently.

Implementation status:

1. Done: added `src/cgppl/diagnostics.py` with shared formatting helpers for graph refs, literals, where predicates, graph predicate constraints, graph predicate failures, and rule call-stack locations.
2. Done: added unit coverage for diagnostic formatting behavior.
3. Pending: wire the runtime's matcher and requirement failure paths to the shared helper.
4. Pending: add regression tests for multi-label and `where` predicate failure messages after runtime wiring.

Next concrete code step:

- Replace runtime-local `_format_value()`, `_format_graph_ref()`, and direct matcher/requirement failure strings with the new diagnostic helpers, starting with `MatchNodeStmt`, `MatchEdgeStmt`, `RequireNoNodeStmt`, and `RequireNoEdgeStmt`.
