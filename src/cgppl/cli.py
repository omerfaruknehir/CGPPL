"""Command line interface for CGPPL tooling."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .lexer import LexerError, TokenKind, tokenize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cgppl", description="CGPPL language tools")
    subcommands = parser.add_subparsers(dest="command", required=True)

    lex_cmd = subcommands.add_parser("lex", help="tokenize a CGPPL source file")
    lex_cmd.add_argument("path", type=Path)
    lex_cmd.add_argument("--json", action="store_true", help="emit machine-readable token JSON")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "lex":
        return _lex(args.path, emit_json=args.json)
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


if __name__ == "__main__":
    raise SystemExit(main())
