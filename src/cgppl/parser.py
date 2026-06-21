"""Recursive-descent parser for the first implemented CGPPL subset."""

from __future__ import annotations

from .ast import (
    AddEdgeStmt,
    AddNodeStmt,
    BlockStmt,
    CallStmt,
    DeleteEdgeStmt,
    DeleteNodeStmt,
    FailStmt,
    LiteralValue,
    Program,
    RequireEdgeAttrStmt,
    RequireEdgeLabelStmt,
    RequireEdgeStmt,
    RequireNodeAttrStmt,
    RequireNodeLabelStmt,
    RequireNodeStmt,
    RuleDecl,
    SetEdgeAttrStmt,
    SetEdgeLabelStmt,
    SetNodeAttrStmt,
    SetNodeLabelStmt,
    SkipStmt,
)
from .lexer import Token, TokenKind, tokenize


class ParserError(ValueError):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def parse_program(self) -> Program:
        self._expect_keyword("program")
        name = self._expect(TokenKind.IDENT).value
        self._expect_symbol("{")

        rules: list[RuleDecl] = []
        body: list[object] = []
        while not self._check_symbol("}"):
            if self._check(TokenKind.EOF):
                token = self._peek()
                raise ParserError(f"expected symbol '}}' at {token.location()}")
            if self._check_keyword("rule"):
                rules.append(self._parse_rule())
            else:
                body.append(self._parse_statement())

        self._expect_symbol("}")
        self._expect(TokenKind.EOF)
        return Program(name=name, rules=tuple(rules), body=tuple(body))

    def _parse_rule(self) -> RuleDecl:
        self._expect_keyword("rule")
        name = self._expect(TokenKind.IDENT, TokenKind.KEYWORD).value
        if self._match_symbol("=>") or self._match_symbol("->"):
            body = self._parse_statement()
            return RuleDecl(name=name, body=body)
        token = self._peek()
        raise ParserError(f"expected rule arrow at {token.location()}")

    def _parse_statement(self) -> object:
        if self._match_symbol("{"):
            return self._parse_block_statement()
        if self._match_keyword("skip"):
            self._expect_symbol(";")
            return SkipStmt()
        if self._match_keyword("fail"):
            self._expect_symbol(";")
            return FailStmt()
        if self._match_keyword("require"):
            return self._parse_require_statement()
        if self._match_keyword("delete"):
            return self._parse_delete_statement()
        if self._match_keyword("add"):
            return self._parse_add_statement()
        if self._match_keyword("set"):
            return self._parse_set_statement()

        token = self._expect(TokenKind.IDENT, TokenKind.KEYWORD)
        if self._match_symbol("("):
            self._expect_symbol(")")
        self._expect_symbol(";")
        return CallStmt(token.value)

    def _parse_block_statement(self) -> BlockStmt:
        statements: list[object] = []
        while not self._check_symbol("}"):
            if self._check(TokenKind.EOF):
                token = self._peek()
                raise ParserError(f"expected symbol '}}' at {token.location()}")
            statements.append(self._parse_statement())
        self._expect_symbol("}")
        return BlockStmt(tuple(statements))

    def _parse_require_statement(self) -> object:
        if self._match_keyword("node"):
            node_id = self._parse_graph_id()
            if self._match_keyword("attr"):
                attr_name = self._parse_graph_id()
                self._expect_symbol("=")
                value = self._parse_literal()
                self._expect_symbol(";")
                return RequireNodeAttrStmt(node_id, attr_name, value)
            if self._match_keyword("label"):
                label = self._parse_graph_id()
                self._expect_symbol(";")
                return RequireNodeLabelStmt(node_id, label)
            self._expect_symbol(";")
            return RequireNodeStmt(node_id)
        if self._match_keyword("edge"):
            edge_id = self._parse_graph_id()
            if self._match_keyword("attr"):
                attr_name = self._parse_graph_id()
                self._expect_symbol("=")
                value = self._parse_literal()
                self._expect_symbol(";")
                return RequireEdgeAttrStmt(edge_id, attr_name, value)
            if self._match_keyword("label"):
                label = self._parse_graph_id()
                self._expect_symbol(";")
                return RequireEdgeLabelStmt(edge_id, label)
            self._expect_symbol(";")
            return RequireEdgeStmt(edge_id)
        token = self._peek()
        raise ParserError(f"expected 'node' or 'edge' after 'require' at {token.location()}")

    def _parse_delete_statement(self) -> object:
        if self._match_keyword("node"):
            node_id = self._parse_graph_id()
            self._expect_symbol(";")
            return DeleteNodeStmt(node_id)
        if self._match_keyword("edge"):
            edge_id = self._parse_graph_id()
            self._expect_symbol(";")
            return DeleteEdgeStmt(edge_id)
        token = self._peek()
        raise ParserError(f"expected 'node' or 'edge' after 'delete' at {token.location()}")

    def _parse_add_statement(self) -> object:
        if self._match_keyword("node"):
            node_id = self._parse_graph_id()
            label = self._parse_optional_label()
            self._expect_symbol(";")
            return AddNodeStmt(node_id, label)
        if self._match_keyword("edge"):
            edge_id = self._parse_graph_id()
            self._expect_keyword("from")
            source_id = self._parse_graph_id()
            self._expect_keyword("to")
            target_id = self._parse_graph_id()
            label = self._parse_optional_label()
            self._expect_symbol(";")
            return AddEdgeStmt(edge_id, source_id, target_id, label)
        token = self._peek()
        raise ParserError(f"expected 'node' or 'edge' after 'add' at {token.location()}")

    def _parse_set_statement(self) -> object:
        if self._match_keyword("node"):
            node_id = self._parse_graph_id()
            if self._match_keyword("attr"):
                attr_name = self._parse_graph_id()
                self._expect_symbol("=")
                value = self._parse_literal()
                self._expect_symbol(";")
                return SetNodeAttrStmt(node_id, attr_name, value)
            if self._match_keyword("label"):
                label = self._parse_graph_id()
                self._expect_symbol(";")
                return SetNodeLabelStmt(node_id, label)
            token = self._peek()
            raise ParserError(f"expected 'attr' or 'label' after node target at {token.location()}")
        if self._match_keyword("edge"):
            edge_id = self._parse_graph_id()
            if self._match_keyword("attr"):
                attr_name = self._parse_graph_id()
                self._expect_symbol("=")
                value = self._parse_literal()
                self._expect_symbol(";")
                return SetEdgeAttrStmt(edge_id, attr_name, value)
            if self._match_keyword("label"):
                label = self._parse_graph_id()
                self._expect_symbol(";")
                return SetEdgeLabelStmt(edge_id, label)
            token = self._peek()
            raise ParserError(f"expected 'attr' or 'label' after edge target at {token.location()}")
        token = self._peek()
        raise ParserError(f"expected 'node' or 'edge' after 'set' at {token.location()}")

    def _parse_optional_label(self) -> str | None:
        if self._match_keyword("label"):
            return self._parse_graph_id()
        return None

    def _parse_graph_id(self) -> str:
        parenthesized = self._match_symbol("(")
        token = self._expect(TokenKind.STRING, TokenKind.IDENT)
        if parenthesized:
            self._expect_symbol(")")
        return token.value

    def _parse_literal(self) -> LiteralValue:
        token = self._peek()
        if token.kind is TokenKind.STRING:
            self.index += 1
            return token.value
        if token.kind is TokenKind.INTEGER:
            self.index += 1
            return int(token.value)
        if token.kind is TokenKind.KEYWORD and token.value in {"true", "false"}:
            self.index += 1
            return token.value == "true"
        raise ParserError(f"expected literal value at {token.location()}")

    def _match_keyword(self, value: str) -> bool:
        if self._check_keyword(value):
            self.index += 1
            return True
        return False

    def _match_symbol(self, value: str) -> bool:
        if self._check_symbol(value):
            self.index += 1
            return True
        return False

    def _check(self, kind: TokenKind) -> bool:
        return self._peek().kind is kind

    def _check_keyword(self, value: str) -> bool:
        token = self._peek()
        return token.kind is TokenKind.KEYWORD and token.value == value

    def _check_symbol(self, value: str) -> bool:
        token = self._peek()
        return token.kind is TokenKind.SYMBOL and token.value == value

    def _expect_keyword(self, value: str) -> Token:
        token = self._peek()
        if token.kind is TokenKind.KEYWORD and token.value == value:
            self.index += 1
            return token
        raise ParserError(f"expected keyword {value!r} at {token.location()}")

    def _expect_symbol(self, value: str) -> Token:
        token = self._peek()
        if token.kind is TokenKind.SYMBOL and token.value == value:
            self.index += 1
            return token
        raise ParserError(f"expected symbol {value!r} at {token.location()}")

    def _expect(self, *kinds: TokenKind) -> Token:
        token = self._peek()
        if token.kind in kinds:
            self.index += 1
            return token
        expected = ", ".join(kind.name for kind in kinds)
        raise ParserError(f"expected {expected} at {token.location()}")

    def _peek(self) -> Token:
        return self.tokens[self.index]


def parse_program(source: str) -> Program:
    return Parser(tokenize(source)).parse_program()
