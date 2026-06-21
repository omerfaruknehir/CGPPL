# CGPPL

C++-like General Purpose Programming Language.

This repository now contains the first incremental implementation scaffold for CGPPL.

## Current status

- Python package metadata in `pyproject.toml`.
- `src/cgppl/lexer.py`: strict lexer with source spans, comments, literals, keywords, and operators.
- `src/cgppl/ast.py`: typed AST nodes for the first implemented subset.
- `src/cgppl/parser.py`: recursive-descent parser for `program Name { ... }`, rule declarations, `skip`, `fail`, rule calls, graph requirement statements, and graph delete statements.
- `src/cgppl/semantics.py`: validation for duplicate rules, undefined calls, and configurable entry rule checks.
- `src/cgppl/graph.py`: immutable graph IR with node/edge records, endpoint validation, graph updates, and dict serialization.
- `src/cgppl/runtime.py`: minimal runtime for `skip`, `fail`, rule-call dispatch, `require node` / `require edge` graph inspection, and `delete node` / `delete edge` graph mutation.
- `src/cgppl/cli.py`: `cgppl lex`, `cgppl parse`, `cgppl validate`, and `cgppl run` commands.
- `tests/`: pytest coverage for lexer, parser, semantic validation, graph IR behavior, runtime dispatch, graph inspection, graph mutation, and CLI graph execution.
- `examples/hello.cgppl`: minimal source file used by the CLI.
- `examples/require-node.cgppl`: graph-inspection example requiring node `n1`.
- `examples/delete-node.cgppl`: graph-mutation example deleting node `n1`.
- `examples/tiny-graph.json`: minimal graph input for `cgppl run`.

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

Run the graph-mutation example program against a graph:

    cgppl run examples/delete-node.cgppl --graph examples/tiny-graph.json

Use the graph/runtime API from Python:

    from cgppl.graph import Graph, Node
    from cgppl.parser import parse_program
    from cgppl.runtime import execute_program

    program = parse_program('program Demo { rule main => delete node "n1"; }')
    graph = Graph.empty().add_node(Node("n1"))
    result = execute_program(program, graph)
    assert result.graph.node_ids == ()

## Implemented subset syntax

A rule body can currently contain one statement:

    rule main => skip;
    rule stop => fail;
    rule main => helper();
    rule main => require node "n1";
    rule main => require edge(e1);
    rule main => delete node "n1";
    rule main => delete edge(e1);

`require node` and `require edge` are runtime graph inspections. They leave the graph unchanged when the required item exists and fail the rule when it does not.

`delete node` and `delete edge` are runtime graph mutations. Deleting a node also deletes incident edges through the immutable graph IR.

## Next implementation step

Add the first sequencing form so a rule can perform more than one operation:

1. extend the AST and parser with a `block { ... }` or brace-delimited statement sequence form,
2. execute each child statement in order while threading the immutable graph through the sequence,
3. add CLI tests for `require node "n1"; delete node "n1";` in one rule,
4. then use sequences as the bridge toward real graph rewrite rules and pattern matching.
