# CGPPL

C++-like General Purpose Programming Language.

This repository now contains the first incremental implementation scaffold for CGPPL.

## Current status

- Python package metadata in `pyproject.toml`.
- `src/cgppl/lexer.py`: strict lexer with source spans, comments, literals, keywords, operators, graph-construction keywords, and graph-attribute keywords.
- `src/cgppl/ast.py`: typed AST nodes for the first implemented subset, including sequential statement blocks, graph construction statements, graph attribute requirement statements, and graph attribute mutation statements.
- `src/cgppl/parser.py`: recursive-descent parser for `program Name { ... }`, rule declarations, `skip`, `fail`, rule calls, graph requirement statements, graph attribute requirement statements, graph delete statements, graph add statements, graph attribute set statements, and brace-delimited statement blocks.
- `src/cgppl/semantics.py`: validation for duplicate rules, undefined calls, nested calls inside blocks, and configurable entry rule checks.
- `src/cgppl/graph.py`: immutable graph IR with node/edge records, endpoint validation, graph updates, attribute updates, and dict serialization.
- `src/cgppl/runtime.py`: minimal runtime for `skip`, `fail`, rule-call dispatch, `require node` / `require edge` graph inspection, `require ... attr ... = ...` graph attribute predicates, `delete node` / `delete edge` graph mutation, `add node` / `add edge` graph construction, `set node attr` / `set edge attr` graph attribute mutation, and sequential block execution.
- `src/cgppl/cli.py`: `cgppl lex`, `cgppl parse`, `cgppl validate`, and `cgppl run` commands.
- `tests/`: pytest coverage for lexer, parser, semantic validation, graph IR behavior, runtime dispatch, graph inspection, graph attribute inspection, graph mutation, graph construction, graph attribute mutation, sequential execution, and CLI graph execution.
- `examples/hello.cgppl`: minimal source file used by the CLI.
- `examples/require-node.cgppl`: graph-inspection example requiring node `n1`.
- `examples/require-attrs.cgppl`: graph-attribute inspection example requiring node and edge attributes.
- `examples/delete-node.cgppl`: graph-mutation example deleting node `n1`.
- `examples/sequence-delete.cgppl`: sequential rewrite example that requires and then deletes node `n1`.
- `examples/add-replacement.cgppl`: graph-construction example that deletes node `n1`, adds node `n3`, and connects `n2 -> n3`.
- `examples/set-attrs.cgppl`: graph-attribute example that constructs `n3`, connects `n2 -> n3`, and writes node/edge attributes.
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

Use the graph/runtime API from Python:

    from cgppl.graph import Graph, Node
    from cgppl.parser import parse_program
    from cgppl.runtime import execute_program

    program = parse_program('program Demo { rule main => { add node "n3"; set node "n3" attr "kind" = "replacement"; require node "n3" attr "kind" = "replacement"; } }')
    graph = Graph.empty()
    result = execute_program(program, graph)
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
    rule main => delete node "n1";
    rule main => delete edge(e1);
    rule main => add node "n3";
    rule main => add edge "e2" from "n2" to "n3";
    rule main => set node "n3" attr "kind" = "replacement";
    rule main => set edge "e2" attr "weight" = 1;
    rule main => set node "n3" attr "active" = true;

A rule body can also be a brace-delimited sequence:

    rule main => {
      require node "n1";
      require node "n1" attr "kind" = "root";
      require edge "e1" attr "weight" = 1;
      delete node "n1";
      add node "n3";
      set node "n3" attr "kind" = "replacement";
      add edge "e2" from "n2" to "n3";
      set edge "e2" attr "weight" = 1;
    }

`require node` and `require edge` are runtime graph inspections. They leave the graph unchanged when the required item exists and fail the rule when it does not.

`require node ... attr ... = ...` and `require edge ... attr ... = ...` are runtime graph attribute predicates. Values currently support strings, integers, and booleans. Attribute comparisons are type-sensitive, so `true` and `1` are not treated as equal.

`delete node` and `delete edge` are runtime graph mutations. Deleting a node also deletes incident edges through the immutable graph IR.

`add node` and `add edge` are runtime graph construction mutations. Duplicate IDs and missing edge endpoints are rejected by the immutable graph IR validation path.

`set node ... attr ... = ...` and `set edge ... attr ... = ...` are runtime graph attribute mutations. Values currently support strings, integers, and booleans. Missing target nodes or edges fail the rule.

Sequential blocks run each child statement in order and thread the immutable graph result from one statement into the next. Execution stops at the first failing statement.

## Next implementation step

Add label predicates and label mutation so rules can branch on graph roles before full pattern matching exists:

1. extend the AST and parser with `require node "id" label "Name";`, `require edge "id" label "Name";`, `add node "id" label "Name";`, or a small `set/add label` form,
2. execute label checks against the normalized `Node.labels` / `Edge.labels` tuples and fail with `GraphMatchFailed` on mismatch,
3. add immutable label update helpers to `Node` and `Edge` if mutation syntax is selected,
4. add CLI tests for successful and failed label predicates, then use those as the stepping stone toward real pattern variables.
