"""Command line interface for CGPPL tooling."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .lexer import LexerError, TokenKind, tokenize
from .parser import ParserError, parse_program
from .semantics import SemanticError, validate_program


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cgppl", description="CGPPL language tools")
    subcommands = parser.add_subparsers(dest="command", required=True)

    lex_cmd = subcommands.add_parser("lex", help="tokenize a CGPPL source file")
    lex_cmd.add_argument("path", type=Path)
    lex_cmd.add_argument("--json", action="store_true", help="emit machine-readable token JSON")

    parse_cmd = subcommands.add_parser("parse", help="parse a CGPPL source file")
    parse_cmd.add_argument("path", type=Path)
    parse_cmd.add_argument("--json", action="store_true", help="emit AST JSON")

    validate_cmd = subcommands.add_parser("validate", help="parse and semantically validate a file")
    validate_cmd.add_argument("path", type=Path)
    validate_cmd.add_argument(
        "--entry-point",
        default="main",
        help="required entry rule name; pass an empty string to disable the check",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "lex":
        return _lex(args.path, emit_json=args.json)
    if args.command == "parse":
        return _parse(args.path, emit_json=args.json)
    if args.command == "validate":
        entry_point = args.entry_point if args.entry_point else None
        return _validate(args.path, entry_point=entry_point)
    raise AssertionError(f"unhandled command: {args.command}")


def _lex(path: Path, *, emit_json: bool) -> int:
    try:
        tokens = tokenize(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"cgppl: cannot read {path}: {exc}")
        return 2
    except LexerError as exc:
        print(f"cgppl: lexer error: {exc}")
        return 1

    if emit_json:
        payload = [
            {
                "kind": token.kind.name,
                "value": token.value,
                "line": token.start.line,
                "column": token.start.column,
            }
            for token in tokens
            if token.kind is not TokenKind.EOF
        ]
        print(json.dumps(payload, indent=2))
        return 0

    for token in tokens:
        if token.kind is TokenKind.EOF:
            continue
        print(f"{token.start.line}:{token.start.column}\t{token.kind.name}\t{token.value}")
    return 0


def _parse(path: Path, *, emit_json: bool) -> int:
    try:
        program = parse_program(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"cgppl: cannot read {path}: {exc}")
        return 2
    except (LexerError, ParserError) as exc:
        print(f"cgppl: parse error: {exc}")
        return 1

    if emit_json:
        print(json.dumps(asdict(program), indent=2))
    else:
        print(f"program {program.name}")
        print(f"rules: {len(program.rules)}")
        print(f"body statements: {len(program.body)}")
    return 0


def _validate(path: Path, *, entry_point: str | None) -> int:
    try:
        program = parse_program(path.read_text(encoding="utf-8"))
        validate_program(program, entry_point=entry_point)
    except OSError as exc:
        print(f"cgppl: cannot read {path}: {exc}")
        return 2
    except (LexerError, ParserError, SemanticError) as exc:
        print(f"cgppl: validation error: {exc}")
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
