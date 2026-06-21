# CGPPL

C++-like General Purpose Programming Language.

This repository currently contains a practical Python implementation scaffold for an executable CGPPL subset. The implementation is intentionally incremental: the front end, graph IR, runtime, examples, and tests are being built in small usable slices.

## Current status

Implemented pieces:

- Python package metadata and `cgppl` CLI entry point.
- Strict lexer with source spans, comments, literals, keywords, operators, and `$variable` graph references.
- Recursive-descent parser for `program Name { ... }`, rule declarations, rule calls, `skip`, `fail`, sequential blocks, and `try { ... } or { ... }` fallback blocks.
- Immutable graph IR with node/edge records, labels, attributes, endpoint validation, serialization, and immutable update/removal helpers.
- Semantic validation for duplicate rules, undefined calls, nested calls inside blocks and try-or branches, and configurable entry rule checks.
- Runtime support for graph inspection, graph mutation, graph construction, attributes, labels, variable binding, deterministic match order, block-local match backtracking, try-or rollback, and annotation removal.
- CLI commands: `cgppl lex`, `cgppl parse`, `cgppl validate`, and `cgppl run`.
- Pytest coverage for lexer, parser, semantic validation, graph IR behavior, runtime behavior, CLI graph execution, match backtracking, fallback execution, and annotation removal.

## Local development

Install in editable mode:

```bash
python -m pip install -e .[dev]
```

Run tests:

```bash
pytest
```

Run a program against a graph:

```bash
cgppl run examples/hello.cgppl --graph examples/tiny-graph.json
cgppl run examples/backtracking.cgppl --graph examples/tiny-graph.json --compact
cgppl run examples/unset-annotations.cgppl --graph examples/tiny-graph.json --compact
```

## Implemented subset syntax

Single-statement rule bodies:

```cgppl
rule main => skip;
rule stop => fail;
rule main => helper();
rule main => require node "n1";
rule main => require edge(e1);
rule main => require node "n1" attr "kind" = "root";
rule main => require edge "e1" attr "weight" = 1;
rule main => require node "n1" label "Root";
rule main => require edge "e1" label "link";
rule main => match node $n label "Root" attr "kind" = "root";
rule main => match edge $e from $a to $b label "link" attr "weight" = 1;
rule main => delete node $n;
rule main => delete edge $e;
rule main => add node "n3" label "Replacement";
rule main => add edge "e2" from $n to "n3" label "new";
rule main => set node $n attr "kind" = "replacement";
rule main => set edge $e attr "weight" = 1;
rule main => set node $n label "Visited";
rule main => set edge $e label "selected";
rule main => unset node $n attr "kind";
rule main => unset edge $e attr "weight";
rule main => unset node $n label "Candidate";
rule main => unset edge $e label "link";
```

Sequential blocks:

```cgppl
rule main => {
  match node $n label "Root" attr "kind" = "root";
  match edge $e from $n to $target label "link" attr "weight" = 1;
  unset node $n attr "kind";
  unset edge $e label "link";
  set node $target label "Reached";
}
```

Fallback blocks:

```cgppl
rule main => try {
  match node $n label "Preferred";
  set node $n label "Selected";
} or {
  match node $n label "Fallback";
  set node $n label "SelectedFallback";
}
```

## Notes

- Attribute values currently support strings, integers, and booleans.
- Attribute comparisons are type-sensitive, so `true` and `1` are distinct.
- Match statements bind graph IDs to `$variables`; later statements can use those variables.
- Match statements backtrack inside sequential blocks when a later statement fails.
- `try-or` rolls back graph and variable changes from the failed branch before trying the fallback branch.
- `unset` is idempotent for missing labels/attributes but still fails if the target node or edge does not exist.

## Next implementation step

Add a first-class `where` predicate form for richer match constraints, for example:

```cgppl
match node $n label "Candidate" where attr("score") >= 10;
match edge $e from $a to $b where source != target;
```

This needs expression AST nodes, parser support for comparison operators, runtime evaluation against the current graph/bindings, and CLI tests proving candidate filtering works beyond exact equality.
