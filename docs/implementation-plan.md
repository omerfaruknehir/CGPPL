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
- rule-local construction precondition diagnostics for duplicate IDs and missing edge endpoints
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
- Edge source/target variables are still normal graph references: they must already be bound by a prior match or construction statement.

Implementation status:

1. Done: decided unbound construction variables generate deterministic fresh IDs rather than requiring prior bindings.
2. Done: `AddNodeStmt.node_id` and `AddEdgeStmt.edge_id` were widened from `str` to `GraphRef`.
3. Done: parser `add node` and `add edge` targets now parse graph refs instead of graph IDs.
4. Done: runtime construction resolves bound variables, generates deterministic fresh IDs for unbound construction target variables, and binds generated variables.
5. Done: tests cover literal construction compatibility, generated IDs, collision suffixing, duplicate bound IDs, edge target construction, and unbound source errors.
6. Done: executable example and README syntax/status updates were added.

## Completed feature slice: constructor precondition diagnostics

This slice converts graph-IR construction failures into rule-local failures. Construction duplicate-ID and missing-endpoint failures now include rule context and participate in `try-or` fallback behavior.

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

## Next feature slice: endpoint construction policy

The next useful slice is deciding whether edge construction should keep explicit endpoint preconditions or grow an opt-in auto-create endpoint form.

Candidate syntax if auto-create is added:

```cgppl
add edge $e from add $source to add $target label "new";
```

Practical first step:

1. Add a design note comparing explicit endpoints versus opt-in auto-create endpoints.
2. Choose the smaller semantics-preserving form.
3. Add parser tests for the chosen syntax before changing runtime behavior.
