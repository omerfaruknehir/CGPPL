# CGPPL implementation plan

This document tracks the next practical implementation slices for the executable CGPPL subset.

## Current baseline

The current runtime can lex, parse, validate, and execute a useful graph-rewrite subset with:

- rule declarations and calls
- sequential blocks
- `try { ... } or { ... }` fallback blocks with rollback
- graph requirements, including negative requirements
- node and edge matching with labels, attributes, endpoint constraints, and `where` predicates
- node and edge construction with one inline label plus inline attributes
- label/attribute mutation and idempotent annotation removal
- constructed-object lifecycle tests for match/require/delete/no-require flows

## Next feature slice: multi-label predicates and construction

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

Concrete implementation steps:

1. Extend matcher/constructor AST nodes from a single optional `label` to a tuple of required `labels` while preserving parser compatibility for existing one-label tests.
2. Replace duplicate-label parser errors in matcher, negative requirement, and constructor parsing with accumulation of multiple label clauses.
3. Update runtime node/edge predicate checks so every required label must be present.
4. Update construction runtime so every inline label is applied at creation time.
5. Add tests for positive multi-label node matching, edge matching, negative requirements, construction, and duplicate same-label normalization.
6. Add an executable example and update README implemented syntax.

## After multi-label support

The next likely high-value slice is variable-bound construction IDs or rule parameters. Multi-label support should land first because it is smaller and exercises the parser/runtime/test loop without changing binding semantics.
