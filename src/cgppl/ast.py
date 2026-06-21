"""Abstract syntax tree nodes for the implemented CGPPL subset."""

from __future__ import annotations

from dataclasses import dataclass

LiteralValue = str | int | bool


@dataclass(frozen=True, slots=True)
class VarRef:
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("variable name must be a non-empty string")

    def display(self) -> str:
        return f"${self.name}"


GraphRef = str | VarRef


@dataclass(frozen=True, slots=True)
class AttrPredicate:
    name: str
    value: LiteralValue

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("attribute name must be a non-empty string")


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
class TryOrStmt:
    first: object
    second: object


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
    node_id: GraphRef


@dataclass(frozen=True, slots=True)
class RequireEdgeStmt:
    edge_id: GraphRef


@dataclass(frozen=True, slots=True)
class RequireNodeAttrStmt:
    node_id: GraphRef
    attr_name: str
    value: LiteralValue


@dataclass(frozen=True, slots=True)
class RequireEdgeAttrStmt:
    edge_id: GraphRef
    attr_name: str
    value: LiteralValue


@dataclass(frozen=True, slots=True)
class RequireNodeLabelStmt:
    node_id: GraphRef
    label: str


@dataclass(frozen=True, slots=True)
class RequireEdgeLabelStmt:
    edge_id: GraphRef
    label: str


@dataclass(frozen=True, slots=True)
class MatchNodeStmt:
    node_id: VarRef
    label: str | None = None
    attrs: tuple[AttrPredicate, ...] = ()


@dataclass(frozen=True, slots=True)
class MatchEdgeStmt:
    edge_id: VarRef
    source_id: GraphRef | None = None
    target_id: GraphRef | None = None
    label: str | None = None
    attrs: tuple[AttrPredicate, ...] = ()


@dataclass(frozen=True, slots=True)
class DeleteNodeStmt:
    node_id: GraphRef


@dataclass(frozen=True, slots=True)
class DeleteEdgeStmt:
    edge_id: GraphRef


@dataclass(frozen=True, slots=True)
class AddNodeStmt:
    node_id: str
    label: str | None = None


@dataclass(frozen=True, slots=True)
class AddEdgeStmt:
    edge_id: str
    source_id: GraphRef
    target_id: GraphRef
    label: str | None = None


@dataclass(frozen=True, slots=True)
class SetNodeAttrStmt:
    node_id: GraphRef
    attr_name: str
    value: LiteralValue


@dataclass(frozen=True, slots=True)
class SetEdgeAttrStmt:
    edge_id: GraphRef
    attr_name: str
    value: LiteralValue


@dataclass(frozen=True, slots=True)
class SetNodeLabelStmt:
    node_id: GraphRef
    label: str


@dataclass(frozen=True, slots=True)
class SetEdgeLabelStmt:
    edge_id: GraphRef
    label: str
