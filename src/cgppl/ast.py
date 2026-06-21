"""Abstract syntax tree nodes for the implemented CGPPL subset."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Program:
    name: str
    rules: tuple[RuleDecl, ...]
    body: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class RuleDecl:
    name: str
    body: object


@dataclass(frozen=True, slots=True)
class BlockStmt:
    statements: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class SkipStmt:
    pass


@dataclass(frozen=True, slots=True)
class FailStmt:
    pass


@dataclass(frozen=True, slots=True)
class CallStmt:
    name: str


@dataclass(frozen=True, slots=True)
class RequireNodeStmt:
    node_id: str


@dataclass(frozen=True, slots=True)
class RequireEdgeStmt:
    edge_id: str


@dataclass(frozen=True, slots=True)
class DeleteNodeStmt:
    node_id: str


@dataclass(frozen=True, slots=True)
class DeleteEdgeStmt:
    edge_id: str


@dataclass(frozen=True, slots=True)
class AddNodeStmt:
    node_id: str


@dataclass(frozen=True, slots=True)
class AddEdgeStmt:
    edge_id: str
    source_id: str
    target_id: str
