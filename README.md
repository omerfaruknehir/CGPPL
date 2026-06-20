# CGPPL

C++-like General Purpose Programming Language.

This repository now contains the first incremental implementation scaffold for CGPPL.

## Current status

- Python package metadata in `pyproject.toml`.
- `src/cgppl/lexer.py`: strict lexer with source spans, comments, literals, keywords, and operators.
- `src/cgppl/ast.py`: typed AST nodes for the first implemented subset.
- `src/cgppl/parser.py`: recursive-descent parser for `program Name { ... }`, rule declarations, `skip`, `fail`, and rule calls.
- `src/cgppl/semantics.py`: validation for duplicate rules, undefined calls, and configurable entry rule checks.
- `src/cgppl/cli.py`: `cgppl lex`, `cgppl parse`, and `cgppl validate` commands.
- `tests/`: pytest coverage for lexer, parser, and semantic validation behavior.
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

## Next implementation step

Add the first graph IR layer:

1. immutable node and edge records,
2. an in-memory graph container,
3. parser support for graph literals or graph-loading stubs,
4. tests that apply one trivial rule to a tiny graph.
