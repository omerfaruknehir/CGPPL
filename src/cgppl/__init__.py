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
from .runtime_annotation_target_wiring import install_annotation_target_diagnostics
from .runtime_delete_target_wiring import install_delete_target_diagnostics
from .semantics import Diagnostic, SemanticError, validate_program

install_delete_target_diagnostics()
install_annotation_target_diagnostics()
