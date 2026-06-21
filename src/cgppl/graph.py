"""Immutable in-memory graph IR for CGPPL execution experiments."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

Value = str | int | bool
AttrItems = tuple[tuple[str, Value], ...]
AttrInput = Mapping[str, Value] | Iterable[tuple[str, Value]] | None


class GraphError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Node:
    id: str
    labels: Iterable[str] | None = field(default_factory=tuple)
    attrs: AttrInput = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_id(self.id, "node")
        object.__setattr__(self, "labels", _normalize_labels(self.labels))
        object.__setattr__(self, "attrs", _normalize_attrs(self.attrs))

    def has_label(self, label: str) -> bool:
        return label in self.labels

    def with_label(self, label: str) -> Node:
        return Node(self.id, labels=self.labels + (label,), attrs=self.attrs)

    def without_label(self, label: str) -> Node:
        return Node(self.id, labels=tuple(item for item in self.labels if item != label), attrs=self.attrs)

    def attr(self, name: str, default: Value | None = None) -> Value | None:
        for key, value in self.attrs:
            if key == name:
                return value
        return default

    def with_attr(self, name: str, value: Value) -> Node:
        attrs = dict(self.attrs)
        attrs[name] = value
        return Node(self.id, labels=self.labels, attrs=attrs)

    def without_attr(self, name: str) -> Node:
        return Node(
            self.id,
            labels=self.labels,
            attrs=tuple((key, value) for key, value in self.attrs if key != name),
        )


@dataclass(frozen=True, slots=True)
class Edge:
    id: str
    source: str
    target: str
    labels: Iterable[str] | None = field(default_factory=tuple)
    attrs: AttrInput = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_id(self.id, "edge")
        _require_id(self.source, "edge source")
        _require_id(self.target, "edge target")
        object.__setattr__(self, "labels", _normalize_labels(self.labels))
        object.__setattr__(self, "attrs", _normalize_attrs(self.attrs))

    def has_label(self, label: str) -> bool:
        return label in self.labels

    def with_label(self, label: str) -> Edge:
        return Edge(self.id, self.source, self.target, labels=self.labels + (label,), attrs=self.attrs)

    def without_label(self, label: str) -> Edge:
        return Edge(
            self.id,
            self.source,
            self.target,
            labels=tuple(item for item in self.labels if item != label),
            attrs=self.attrs,
        )

    def attr(self, name: str, default: Value | None = None) -> Value | None:
        for key, value in self.attrs:
            if key == name:
                return value
        return default

    def with_attr(self, name: str, value: Value) -> Edge:
        attrs = dict(self.attrs)
        attrs[name] = value
        return Edge(self.id, self.source, self.target, labels=self.labels, attrs=attrs)

    def without_attr(self, name: str) -> Edge:
        return Edge(
            self.id,
            self.source,
            self.target,
            labels=self.labels,
            attrs=tuple((key, value) for key, value in self.attrs if key != name),
        )


@dataclass(frozen=True, slots=True)
class Graph:
    nodes: tuple[Node, ...] = field(default_factory=tuple)
    edges: tuple[Edge, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        nodes = tuple(self.nodes)
        edges = tuple(self.edges)
        node_ids: set[str] = set()
        edge_ids: set[str] = set()

        for node in nodes:
            if node.id in node_ids:
                raise GraphError(f"duplicate node id: {node.id}")
            node_ids.add(node.id)

        for edge in edges:
            if edge.id in edge_ids:
                raise GraphError(f"duplicate edge id: {edge.id}")
            if edge.source not in node_ids:
                raise GraphError(f"edge {edge.id} references missing source node: {edge.source}")
            if edge.target not in node_ids:
                raise GraphError(f"edge {edge.id} references missing target node: {edge.target}")
            edge_ids.add(edge.id)

        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "edges", edges)

    @classmethod
    def empty(cls) -> Graph:
        return cls()

    @property
    def node_ids(self) -> tuple[str, ...]:
        return tuple(node.id for node in self.nodes)

    @property
    def edge_ids(self) -> tuple[str, ...]:
        return tuple(edge.id for edge in self.edges)

    def has_node(self, node_id: str) -> bool:
        return any(node.id == node_id for node in self.nodes)

    def has_edge(self, edge_id: str) -> bool:
        return any(edge.id == edge_id for edge in self.edges)

    def get_node(self, node_id: str) -> Node:
        for node in self.nodes:
            if node.id == node_id:
                return node
        raise GraphError(f"missing node: {node_id}")

    def get_edge(self, edge_id: str) -> Edge:
        for edge in self.edges:
            if edge.id == edge_id:
                return edge
        raise GraphError(f"missing edge: {edge_id}")

    def add_node(self, node: Node) -> Graph:
        if self.has_node(node.id):
            raise GraphError(f"duplicate node id: {node.id}")
        return Graph(self.nodes + (node,), self.edges)

    def add_edge(self, edge: Edge) -> Graph:
        if self.has_edge(edge.id):
            raise GraphError(f"duplicate edge id: {edge.id}")
        return Graph(self.nodes, self.edges + (edge,))

    def replace_node(self, node: Node) -> Graph:
        if not self.has_node(node.id):
            raise GraphError(f"missing node: {node.id}")
        nodes = tuple(node if existing.id == node.id else existing for existing in self.nodes)
        return Graph(nodes, self.edges)

    def replace_edge(self, edge: Edge) -> Graph:
        if not self.has_edge(edge.id):
            raise GraphError(f"missing edge: {edge.id}")
        edges = tuple(edge if existing.id == edge.id else existing for existing in self.edges)
        return Graph(self.nodes, edges)

    def remove_node(self, node_id: str) -> Graph:
        if not self.has_node(node_id):
            raise GraphError(f"missing node: {node_id}")
        nodes = tuple(node for node in self.nodes if node.id != node_id)
        edges = tuple(edge for edge in self.edges if edge.source != node_id and edge.target != node_id)
        return Graph(nodes, edges)

    def remove_edge(self, edge_id: str) -> Graph:
        if not self.has_edge(edge_id):
            raise GraphError(f"missing edge: {edge_id}")
        return Graph(self.nodes, tuple(edge for edge in self.edges if edge.id != edge_id))

    def to_dict(self) -> dict[str, object]:
        return {
            "nodes": [
                {"id": node.id, "labels": list(node.labels), "attrs": dict(node.attrs)}
                for node in self.nodes
            ],
            "edges": [
                {
                    "id": edge.id,
                    "source": edge.source,
                    "target": edge.target,
                    "labels": list(edge.labels),
                    "attrs": dict(edge.attrs),
                }
                for edge in self.edges
            ],
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Graph:
        nodes = tuple(
            Node(
                str(item["id"]),
                labels=item.get("labels", ()),
                attrs=item.get("attrs", ()),
            )
            for item in _expect_items(payload, "nodes")
        )
        edges = tuple(
            Edge(
                str(item["id"]),
                str(item["source"]),
                str(item["target"]),
                labels=item.get("labels", ()),
                attrs=item.get("attrs", ()),
            )
            for item in _expect_items(payload, "edges")
        )
        return cls(nodes=nodes, edges=edges)


def _expect_items(payload: Mapping[str, object], key: str) -> tuple[Mapping[str, object], ...]:
    value = payload.get(key, ())
    if not isinstance(value, list | tuple):
        raise GraphError(f"graph field must be a list: {key}")
    if not all(isinstance(item, Mapping) for item in value):
        raise GraphError(f"graph field must contain objects: {key}")
    return tuple(value)


def _normalize_labels(labels: Iterable[str] | None) -> tuple[str, ...]:
    if labels is None:
        return ()
    normalized: list[str] = []
    seen: set[str] = set()
    for label in labels:
        if not isinstance(label, str) or not label:
            raise GraphError("labels must be non-empty strings")
        if label not in seen:
            normalized.append(label)
            seen.add(label)
    return tuple(sorted(normalized))


def _normalize_attrs(attrs: AttrInput) -> AttrItems:
    if attrs is None:
        return ()
    items = attrs.items() if isinstance(attrs, Mapping) else attrs
    normalized: list[tuple[str, Value]] = []
    seen: set[str] = set()
    for key, value in items:
        if not isinstance(key, str) or not key:
            raise GraphError("attribute names must be non-empty strings")
        if key in seen:
            raise GraphError(f"duplicate attribute: {key}")
        if not isinstance(value, str | int | bool):
            raise GraphError(f"unsupported attribute value for {key}: {value!r}")
        normalized.append((key, value))
        seen.add(key)
    return tuple(sorted(normalized))


def _require_id(value: str, kind: str) -> None:
    if not isinstance(value, str) or not value:
        raise GraphError(f"{kind} id must be a non-empty string")
