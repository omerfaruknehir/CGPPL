# CGPPL

C++-like General Purpose Programming Language.

This repository now contains the first incremental implementation scaffold for CGPPL.

## Current status

- Python package metadata in `pyproject.toml`.
- `src/cgppl/lexer.py`: strict lexer with source spans, comments, literals, keywords, and operators.
- `src/cgppl/ast.py`: typed AST nodes for the first implemented subset.
- `src/cgppl/parser.py`: recursive-descent parser for `program Name { ... }`, rule declarations, `skip`, `fail`, and rule calls.
- `src/cgppl/semantics.py`: validation for duplicate rules, undefined calls, and configurable entry rule checks.
- `src/cgppl/graph.py`: immutable graph IR with node/edge records, endpoint validation, graph updates, and dict serialization.
- `src/cgppl/runtime.py`: minimal graph-preserving runtime for `skip`, `fail`, and rule-call dispatch.
- `src/cgppl/cli.py`: `cgppl lex`, `cgppl parse`, and `cgppl validate` commands.
- `tests/`: pytest coverage for lexer, parser, semantic validation, graph IR behavior, and runtime dispatch.
- `examples/hello.cgppl`: minimal source file used by the CLI.

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

Use the graph/runtime API from Python:

    from cgppl.graph import Graph, Node
    from cgppl.parser import parse_program
    from cgppl.runtime import execute_program

    program = parse_program("program Demo { rule main => skip; }")
    graph = Graph.empty().add_node(Node("n1"))
    result = execute_program(program, graph)
    assert result.graph is graph

## Next implementation step

Add graph input/output to the command line:

1. accept a JSON graph file for `cgppl run`,
2. execute the selected entry rule against that graph,
3. print the resulting graph as JSON,
4. keep runtime semantics intentionally small until real graph rewrite statements are parsed.
