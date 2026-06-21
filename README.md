# CGPPL

C++-like General Purpose Programming Language.

This repository now contains the first incremental implementation scaffold for CGPPL.

## Current status

- Python package metadata in `pyproject.toml`.
- `src/cgppl/lexer.py`: strict lexer with source spans, comments, literals, keywords, operators, graph-construction keywords, graph-attribute keywords, graph-label keywords, and `$` graph-variable tokens.
- `src/cgppl/ast.py`: typed AST nodes for the first implemented subset, including sequential statement blocks, try-or fallback statements, graph construction statements, graph attribute requirement statements, graph attribute mutation statements, graph label requirement statements, graph label mutation statements, and graph match-variable statements.
- `src/cgppl/parser.py`: recursive-descent parser for `program Name { ... }`, rule declarations, `skip`, `fail`, rule calls, graph requirement statements, graph attribute and label requirement statements, graph match-variable statements, graph delete statements, graph add statements, graph attribute and label set statements, brace-delimited statement blocks, and `try { ... } or { ... }` fallback statements.
- `src/cgppl/semantics.py`: validation for duplicate rules, undefined calls, nested calls inside blocks and try-or branches, and configurable entry rule checks.
- `src/cgppl/graph.py`: immutable graph IR with node/edge records, endpoint validation, graph updates, label helpers, attribute updates, and dict serialization.
- `src/cgppl/runtime.py`: minimal runtime for `skip`, `fail`, rule-call dispatch, `require node` / `require edge` graph inspection, `require ... attr ... = ...` graph attribute predicates, `require ... label ...` graph label predicates, `match node` / `match edge` variable binding, `delete node` / `delete edge` graph mutation, `add node` / `add edge` graph construction with optional labels and variable endpoints, `set node attr` / `set edge attr` graph attribute mutation, `set node label` / `set edge label` graph label mutation, sequential block execution, and branch-local try-or fallback execution.
- `src/cgppl/cli.py`: `cgppl lex`, `cgppl parse`, `cgppl validate`, and `cgppl run` commands.
- `tests/`: pytest coverage for lexer, parser, semantic validation, graph IR behavior, runtime dispatch, graph inspection, graph attribute inspection, graph label inspection, graph mutation, graph construction, graph label mutation, graph attribute mutation, match-variable binding, sequential execution, try-or fallback execution, and CLI graph execution.
- `examples/hello.cgppl`: minimal source file used by the CLI.
- `examples/require-node.cgppl`: graph-inspection example requiring node `n1`.
- `examples/require-attrs.cgppl`: graph-attribute inspection example requiring node and edge attributes.
- `examples/delete-node.cgppl`: graph-mutation example deleting node `n1`.
- `examples/sequence-delete.cgppl`: sequential rewrite example that requires and then deletes node `n1`.
- `examples/add-replacement.cgppl`: graph-construction example that deletes node `n1`, adds node `n3`, and connects `n2 -> n3`.
- `examples/set-attrs.cgppl`: graph-attribute example that constructs `n3`, connects `n2 -> n3`, and writes node/edge attributes.
- `examples/label-rewrite.cgppl`: graph-label example that requires labels, adds labels, and creates labeled graph structure.
- `examples/match-node.cgppl`: graph-variable example that matches a labeled node, mutates it by variable reference, and deletes it.
- `examples/try-fallback.cgppl`: try-or fallback example that rolls back a failed first branch and commits a second matching branch.
- `examples/tiny-graph.json`: minimal graph input for `cgppl run`, including sample labels and attributes.

## Local development

Install in editable mode:

    python -m pip install -e .[dev]

Run tests:

    pytest

Lex the example program:

    cgppl lex examples/hello.cgppl

Parse the example program:

    cgppl parse --json examples/hello.cgppl

Validate the example program:

    cgppl validate examples/hello.cgppl

Run the graph-preserving example program against a graph:

    cgppl run examples/hello.cgppl --graph examples/tiny-graph.json

Run the graph-inspection example program against a graph:

    cgppl run examples/require-node.cgppl --graph examples/tiny-graph.json

Run the graph-attribute inspection example program against a graph:

    cgppl run examples/require-attrs.cgppl --graph examples/tiny-graph.json --compact

Run the graph-mutation example program against a graph:

    cgppl run examples/delete-node.cgppl --graph examples/tiny-graph.json

Run the sequential graph-rewrite example against a graph:

    cgppl run examples/sequence-delete.cgppl --graph examples/tiny-graph.json --compact

Run the graph-construction example against a graph:

    cgppl run examples/add-replacement.cgppl --graph examples/tiny-graph.json --compact

Run the graph-attribute example against a graph:

    cgppl run examples/set-attrs.cgppl --graph examples/tiny-graph.json --compact

Run the graph-label example against a graph:

    cgppl run examples/label-rewrite.cgppl --graph examples/tiny-graph.json --compact

Run the match-variable example against a graph:

    cgppl run examples/match-node.cgppl --graph examples/tiny-graph.json --compact

Run the try-or fallback example against a graph:

    cgppl run examples/try-fallback.cgppl --graph examples/tiny-graph.json --compact

Use the graph/runtime API from Python:

    from cgppl.graph import Graph, Node
    from cgppl.parser import parse_program
    from cgppl.runtime import execute_program

    program = parse_program('program Demo { rule main => { add node "n3" label "Replacement"; set node "n3" attr "kind" = "replacement"; require node "n3" label "Replacement"; require node "n3" attr "kind" = "replacement"; } }')
    graph = Graph.empty()
    result = execute_program(program, graph)
    assert result.graph.get_node("n3").has_label("Replacement")
    assert result.graph.get_node("n3").attr("kind") == "replacement"

## Implemented subset syntax

A rule body can be one statement:

    rule main => skip;
    rule stop => fail;
    rule main => helper();
    rule main => require node "n1";
    rule main => require edge(e1);
    rule main => require node "n1" attr "kind" = "root";
    rule main => require edge "e1" attr "weight" = 1;
    rule main => require node "n1" label "Root";
    rule main => require edge "e1" label "link";
    rule main => match node $n label "Root";
    rule main => match edge $e from $a to $b label "link";
    rule main => delete node "n1";
    rule main => delete node $n;
    rule main => delete edge(e1);
    rule main => delete edge $e;
    rule main => add node "n3";
    rule main => add node "n3" label "Replacement";
    rule main => add edge "e2" from "n2" to "n3";
    rule main => add edge "e2" from $n to "n3" label "new";
    rule main => set node "n3" attr "kind" = "replacement";
    rule main => set node $n attr "kind" = "replacement";
    rule main => set edge "e2" attr "weight" = 1;
    rule main => set node "n3" attr "active" = true;
    rule main => set node "n3" label "Visited";
    rule main => set node $n label "Visited";
    rule main => set edge "e2" label "selected";

A rule body can also be a brace-delimited sequence:

    rule main => {
      match node $n label "Root";
      require node $n;
      require node $n attr "kind" = "root";
      set node $n label "Matched";
      match edge $e from $n to $target label "link";
      set node $target label "Reached";
      delete edge $e;
      delete node $n;
    }

A rule body can use a fallback branch:

    rule main => try {
      match node $n label "Preferred";
      set node $n label "Selected";
    } or {
      match node $n label "Fallback";
      set node $n label "SelectedFallback";
    }

`require node` and `require edge` are runtime graph inspections. They leave the graph unchanged when the required item exists and fail the rule when it does not. Their target ID may be a literal ID or a previously bound `$variable`.

`require node ... attr ... = ...` and `require edge ... attr ... = ...` are runtime graph attribute predicates. Values currently support strings, integers, and booleans. Attribute comparisons are type-sensitive, so `true` and `1` are not treated as equal.

`require node ... label ...` and `require edge ... label ...` are runtime graph label predicates. They require exact label membership in the normalized node/edge label tuples.

`match node $n label "Root"` binds `$n` to the first node with the requested label. `match edge $e from $a to $b label "link"` binds the edge ID and can also bind or check endpoint variables. Matching is deterministic over the current graph order.

`delete node` and `delete edge` are runtime graph mutations. Deleting a node also deletes incident edges through the immutable graph IR. Targets may be literal IDs or bound variables.

`add node` and `add edge` are runtime graph construction mutations. Duplicate IDs and missing edge endpoints are rejected by the immutable graph IR validation path. A single optional label can be supplied during construction. Edge endpoints may be literal IDs or bound variables.

`set node ... attr ... = ...` and `set edge ... attr ... = ...` are runtime graph attribute mutations. Values currently support strings, integers, and booleans. Missing target nodes or edges fail the rule. Targets may be literal IDs or bound variables.

`set node ... label ...` and `set edge ... label ...` are runtime graph label mutations. They add a label immutably and keep labels deduplicated through the graph IR normalization path. Targets may be literal IDs or bound variables.

Sequential blocks run each child statement in order and thread the immutable graph result and variable bindings from one statement into the next. Execution stops at the first failing statement.

`try { ... } or { ... }` executes the first branch against the current graph and bindings. If it succeeds, that result is committed and the second branch is skipped. If it fails with a rule failure or match failure, the first branch graph and bindings are discarded, then the second branch runs from the original state. If both branches fail, the whole statement fails.

## Next implementation step

Add real backtracking across match candidates inside a branch:

1. collect all matching node or edge candidates instead of committing only the first match,
2. run the rest of the sequence against each candidate snapshot,
3. commit the first full sequence that succeeds,
4. add tests where the first candidate matches the local predicate but fails a later statement while a later candidate succeeds.
