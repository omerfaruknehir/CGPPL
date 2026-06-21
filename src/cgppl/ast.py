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
class AttrExpr:
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("attribute expression name must be a non-empty string")


@dataclass(frozen=True, slots=True)
class FieldExpr:
    name: str

    def __post_init__(self) -> None:
        if self.name not in {"id", "source", "target"}:
            raise ValueError("field expression must be one of: id, source, target")


@dataclass(frozen=True, slots=True)
class LiteralExpr:
    value: LiteralValue


@dataclass(frozen=True, slots=True)
class VarExpr:
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("where variable expression name must be a non-empty string")

    def display(self) -> str:
        return f"${self.name}"


WhereExpr = AttrExpr | FieldExpr | LiteralExpr | VarExpr


@dataclass(frozen=True, slots=True)
class WherePredicate:
    left: WhereExpr
    operator: str
    right: WhereExpr

    def __post_init__(self) -> None:
        if self.operator not in {"==", "!=", "<", "<=", ">", ">="}:
            raise ValueError("unsupported where comparison operator")


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
class RequireNoNodeStmt:
    node_id: GraphRef
    label: str | None = None
    attrs: tuple[AttrPredicate, ...] = ()
    where: tuple[WherePredicate, ...] = ()


@dataclass(frozen=True, slots=True)
class RequireNoEdgeStmt:
    edge_id: GraphRef
    source_id: GraphRef | None = None
    target_id: GraphRef | None = None
    label: str | None = None
    attrs: tuple[AttrPredicate, ...] = ()
    where: tuple[WherePredicate, ...] = ()


@dataclass(frozen=True, slots=True)
class MatchNodeStmt:
    node_id: VarRef
    label: str | None = None
    attrs: tuple[AttrPredicate, ...] = ()
    where: tuple[WherePredicate, ...] = ()


@dataclass(frozen=True, slots=True)
class MatchEdgeStmt:
    edge_id: VarRef
    source_id: GraphRef | None = None
    target_id: GraphRef | None = None
    label: str | None = None
    attrs: tuple[AttrPredicate, ...] = ()
    where: tuple[WherePredicate, ...] = ()


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


@dataclass(frozen=True, slots=True)
class UnsetNodeAttrStmt:
    node_id: GraphRef
    attr_name: str


@dataclass(frozen=True, slots=True)
class UnsetEdgeAttrStmt:
    edge_id: GraphRef
    attr_name: str


@dataclass(frozen=True, slots=True)
class UnsetNodeLabelStmt:
    node_id: GraphRef
    label: str


@dataclass(frozen=True, slots=True)
class UnsetEdgeLabelStmt:
    edge_id: GraphRef
    label: str
