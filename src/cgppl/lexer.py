"""Lexer for the CGPPL front end.

The lexer is deliberately strict: it preserves source spans and rejects unknown
characters early so the parser can stay simple.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenKind(Enum):
    IDENT = auto()
    INTEGER = auto()
    STRING = auto()
    KEYWORD = auto()
    SYMBOL = auto()
    EOF = auto()


KEYWORDS = frozenset(
    {
        "program",
        "module",
        "import",
        "rule",
        "main",
        "where",
        "if",
        "then",
        "else",
        "try",
        "or",
        "skip",
        "fail",
        "require",
        "delete",
        "add",
        "from",
        "to",
        "break",
        "return",
        "let",
        "node",
        "edge",
        "graph",
        "int",
        "string",
        "bool",
        "true",
        "false",
        "red",
        "green",
        "blue",
        "grey",
        "dashed",
        "any",
    }
)

MULTI_CHAR_SYMBOLS = (
    "=>",
    "->",
    "==",
    "!=",
    "<=",
    ">=",
    "&&",
    "||",
    ":=",
)

SINGLE_CHAR_SYMBOLS = set("{}()[];,.:+-*/%<>=!&|?")


@dataclass(frozen=True, slots=True)
class SourcePos:
    index: int
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    value: str
    start: SourcePos
    end: SourcePos

    def location(self) -> str:
        return f"{self.start.line}:{self.start.column}"


class LexerError(ValueError):
    pass


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while not self._at_end():
            self._skip_space_and_comments()
            if self._at_end():
                break
            tokens.append(self._next_token())

        pos = self._pos()
        tokens.append(Token(TokenKind.EOF, "", pos, pos))
        return tokens

    def _next_token(self) -> Token:
        ch = self._peek()
        if ch.isalpha() or ch == "_":
            return self._identifier_or_keyword()
        if ch.isdigit():
            return self._integer()
        if ch == '"':
            return self._string()
        return self._symbol()

    def _identifier_or_keyword(self) -> Token:
        start = self._pos()
        value = self._consume_while(lambda c: c.isalnum() or c == "_")
        kind = TokenKind.KEYWORD if value in KEYWORDS else TokenKind.IDENT
        return Token(kind, value, start, self._pos())

    def _integer(self) -> Token:
        start = self._pos()
        value = self._consume_while(str.isdigit)
        return Token(TokenKind.INTEGER, value, start, self._pos())

    def _string(self) -> Token:
        start = self._pos()
        self._advance()  # opening quote
        chars: list[str] = []
        while not self._at_end():
            ch = self._advance()
            if ch == '"':
                return Token(TokenKind.STRING, "".join(chars), start, self._pos())
            if ch == "\\":
                chars.append(self._escape())
            elif ch == "\n":
                raise LexerError(f"unterminated string at {start.line}:{start.column}")
            else:
                chars.append(ch)
        raise LexerError(f"unterminated string at {start.line}:{start.column}")

    def _escape(self) -> str:
        if self._at_end():
            raise LexerError("unterminated escape sequence")
        ch = self._advance()
        escapes = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}
        if ch not in escapes:
            raise LexerError(f"unknown escape sequence \\{ch} at {self.line}:{self.column}")
        return escapes[ch]

    def _symbol(self) -> Token:
        start = self._pos()
        for symbol in MULTI_CHAR_SYMBOLS:
            if self.source.startswith(symbol, self.index):
                for _ in symbol:
                    self._advance()
                return Token(TokenKind.SYMBOL, symbol, start, self._pos())

        ch = self._peek()
        if ch in SINGLE_CHAR_SYMBOLS:
            self._advance()
            return Token(TokenKind.SYMBOL, ch, start, self._pos())
        raise LexerError(f"unexpected character {ch!r} at {self.line}:{self.column}")

    def _skip_space_and_comments(self) -> None:
        progressed = True
        while progressed:
            progressed = False
            while not self._at_end() and self._peek().isspace():
                self._advance()
                progressed = True
            if self.source.startswith("//", self.index):
                while not self._at_end() and self._peek() != "\n":
                    self._advance()
                progressed = True
            elif self.source.startswith("/*", self.index):
                self._advance()
                self._advance()
                while not self._at_end() and not self.source.startswith("*/", self.index):
                    self._advance()
                if self._at_end():
                    raise LexerError("unterminated block comment")
                self._advance()
                self._advance()
                progressed = True

    def _consume_while(self, predicate) -> str:
        chars: list[str] = []
        while not self._at_end() and predicate(self._peek()):
            chars.append(self._advance())
        return "".join(chars)

    def _peek(self) -> str:
        return self.source[self.index]

    def _advance(self) -> str:
        ch = self.source[self.index]
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _at_end(self) -> bool:
        return self.index >= len(self.source)

    def _pos(self) -> SourcePos:
        return SourcePos(self.index, self.line, self.column)


def tokenize(source: str) -> list[Token]:
    return Lexer(source).tokenize()
