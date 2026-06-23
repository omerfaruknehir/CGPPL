"""CGPPL language implementation package."""

from .ast import (
    AttrExpr,
    AttrPredicate,
    FieldExpr,
    LiteralExpr,
    TryOrStmt,
    UnsetEdgeAttrStmt,
    UnsetEdgeLabelStmt,
    UnsetNodeAttrStmt,
    UnsetNodeLabelStmt,
    VarExpr,
    VarRef,
    WherePredicate,
)
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
from .runtime_construction_wiring import install_construction_diagnostics
from .semantics import Diagnostic, SemanticError, validate_program

install_construction_diagnostics()
