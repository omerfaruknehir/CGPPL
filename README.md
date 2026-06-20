# CGPPL

C++-like General Purpose Programming Language.

This repository now contains the first incremental implementation scaffold for CGPPL.

## Current status

- Python package metadata in `pyproject.toml`.
- `src/cgppl/lexer.py`: strict lexer with source spans, comments, literals, keywords, and operators.
- `src/cgppl/ast.py`: typed AST nodes for the first implemented subset.
- `src/cgppl/parser.py`: recursive-descent parser for `program Name { ... }`, rule declarations, `skip`, `fail`, and rule calls.
- `src/cgppl/cli.py`: `cgppl lex` and `cgppl parse` commands for inspecting source files.
- `tests/`: pytest coverage for lexer and parser behavior.
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

## Next implementation step

Add semantic validation on top of the AST:

1. collect declared rule names,
2. reject duplicate rule declarations,
3. reject calls to undefined rules,
4. define which rule is the entry point, probably `main` unless the specification says otherwise.
