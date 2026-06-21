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

## Current feature slice: variable-bound construction IDs

The next high-value slice is allowing construction targets to come from variables. This lets rewrite rules derive new graph objects from earlier matches without hard-coded literal IDs.

Target syntax:

```cgppl
rule main => {
  match node $source label "Root";
  add node $replacement label "Generated";
  add edge $new_edge from $source to $replacement label "new";
}
```

Design decision:

- Literal construction IDs keep the existing behavior.
- Bound construction variables resolve to their existing binding.
- Unbound construction variables should generate deterministic fresh IDs from the variable name, then bind the variable for later statements. For example, `$replacement` first tries `replacement`; if that ID already exists, it tries `replacement_2`, `replacement_3`, and so on.
- Node construction variables must avoid existing node IDs. Edge construction variables must avoid existing edge IDs.

Implementation status:

1. Done: decided unbound construction variables generate deterministic fresh IDs rather than requiring prior bindings.
2. Done: `AddNodeStmt.node_id` and `AddEdgeStmt.edge_id` were widened from `str` to `GraphRef`.
3. Next: update parser `add node` and `add edge` targets to parse graph refs instead of graph IDs.
4. Pending: update runtime construction to resolve/generate construction IDs and bind generated variables.
5. Pending: add parser/runtime tests for literal construction compatibility, generated IDs, collision suffixing, duplicate bound IDs, and unbound source/target errors.
6. Pending: add an executable example and update README implemented syntax.
