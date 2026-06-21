"""CGPPL language implementation package."""

from .ast import VarRef
from .graph import Edge, Graph, GraphError, Node
from .lexer import Lexer, LexerError, Token, TokenKind, tokenize
from .parser import Parser, ParserError, parse_program
from .runtime import (
    ExecutionResult,
    GraphMatchFailed,
    RecursionLimitExceeded,
    RuleFailed,
    RuntimeFailure,
    apply_rule,
    execute_program,
)
from .semantics import Diagnostic, SemanticError, validate_program
