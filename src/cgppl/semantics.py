"""Semantic checks for the currently implemented CGPPL subset."""

from __future__ import annotations

from dataclasses import dataclass

from .ast import CallStmt, Program, RuleDecl


@dataclass(frozen=True, slots=True)
class Diagnostic:
    message: str


class SemanticError(ValueError):
    def __init__(self, diagnostics: list[Diagnostic]) -> None:
        self.diagnostics = diagnostics
        message = "\n".join(diagnostic.message for diagnostic in diagnostics)
        super().__init__(message)


def validate_program(program: Program, *, entry_point: str | None = "main") -> None:
    diagnostics: list[Diagnostic] = []
    rule_names: set[str] = set()

    for rule in program.rules:
        if rule.name in rule_names:
            diagnostics.append(Diagnostic(f"duplicate rule declaration: {rule.name}"))
        rule_names.add(rule.name)

    if entry_point is not None and entry_point not in rule_names:
        diagnostics.append(Diagnostic(f"missing entry rule: {entry_point}"))

    for rule in program.rules:
        _check_statement_calls(rule.body, rule_names, diagnostics)
    for statement in program.body:
        _check_statement_calls(statement, rule_names, diagnostics)

    if diagnostics:
        raise SemanticError(diagnostics)


def _check_statement_calls(statement: object, rule_names: set[str], diagnostics: list[Diagnostic]) -> None:
    if isinstance(statement, CallStmt) and statement.name not in rule_names:
        diagnostics.append(Diagnostic(f"undefined rule call: {statement.name}"))
