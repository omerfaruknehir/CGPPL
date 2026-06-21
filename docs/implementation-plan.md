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

## Current feature slice: multi-label predicates and construction

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

## Next feature slice: variable-bound construction IDs

The next likely high-value slice is allowing construction targets to come from variables. This would let rewrite rules derive new graph objects from earlier matches without hard-coded literal IDs.

Target syntax:

```cgppl
rule main => {
  match node $source label "Root";
  add node $replacement label "Generated";
  add edge $new_edge from $source to $replacement label "new";
}
```

Concrete implementation steps:

1. Decide whether unbound construction variables generate IDs or whether construction variables must already be bound.
2. Extend `AddNodeStmt.node_id` and `AddEdgeStmt.edge_id` from `str` to `GraphRef` if construction should accept bound variables.
3. Update parser `add node` and `add edge` targets to parse graph refs instead of graph IDs.
4. Update runtime construction to resolve variable targets before adding nodes/edges.
5. Add parser/runtime tests for literal construction compatibility, bound-variable construction, duplicate ID errors, and unbound-variable errors.
6. Add an executable example and update README implemented syntax.
