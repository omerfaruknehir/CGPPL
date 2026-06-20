# CGPPL

C++-like General Purpose Programming Language.

This repository now contains the first incremental implementation scaffold for CGPPL.

## Current status

- Python package metadata in `pyproject.toml`.
- `src/cgppl/lexer.py`: strict lexer with source spans, comments, literals, keywords, and operators.
- `src/cgppl/cli.py`: `cgppl lex` command for inspecting token streams.
- `tests/test_lexer.py`: pytest coverage for normal tokens, comments, source positions, and lexer errors.
- `examples/hello.cgppl`: minimal source file used by the lexer CLI.

## Local development

Install in editable mode:

    python -m pip install -e .[dev]

Run tests:

    pytest

Lex the example program:

    cgppl lex examples/hello.cgppl

Emit JSON tokens:

    cgppl lex --json examples/hello.cgppl

## Next implementation step

Add a recursive-descent parser over the existing token stream. The next target should be a typed AST for:

1. top-level `program Name { ... }`,
2. rule declarations,
3. basic statements such as `skip`, `fail`, sequencing with `;`, and named rule calls.
