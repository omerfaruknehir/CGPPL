import pytest

from cgppl.ast import AddEdgeStmt, AddNodeStmt, AttrPredicate, BlockStmt, MatchNodeStmt, VarRef
from cgppl.graph import Edge, Graph, Node
from cgppl.parser import ParserError, parse_program
from cgppl.runtime import execute_program


def test_parses_add_node_with_inline_attributes():
    program = parse_program(
        'program Demo { rule main => add node "n3" label "Replacement" '
        'attr "kind" = "generated" attr(active) = true; }'
    )

    assert program.rules[0].body == AddNodeStmt(
        "n3",
        "Replacement",
        (AttrPredicate("kind", "generated"), AttrPredicate("active", True)),
    )


def test_parses_add_edge_with_inline_attributes_and_variable_endpoint():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Root"; '
        'add edge "e2" from $n to "n3" label "new" attr "weight" = 1; } }'
    )

    assert program.rules[0].body == BlockStmt(
        (
            MatchNodeStmt(VarRef("n"), "Root"),
            AddEdgeStmt("e2", VarRef("n"), "n3", "new", (AttrPredicate("weight", 1),)),
        )
    )


def test_add_node_constructs_labels_and_attributes_in_one_statement():
    program = parse_program(
        'program Demo { rule main => add node "n3" label "Replacement" '
        'attr "kind" = "generated" attr(active) = true; }'
    )
    graph = Graph.empty().add_node(Node("n1"))

    result = execute_program(program, graph)

    node = result.graph.get_node("n3")
    assert node.labels == ("Replacement",)
    assert node.attrs == (("active", True), ("kind", "generated"))
    assert graph.node_ids == ("n1",)


def test_add_edge_constructs_labels_and_attributes_in_one_statement():
    program = parse_program(
        'program Demo { rule main => add edge "e2" from "a" to "b" '
        'label "new" attr "weight" = 1 attr(active) = true; }'
    )
    graph = Graph(nodes=(Node("a"), Node("b")))

    result = execute_program(program, graph)

    assert result.graph.get_edge("e2") == Edge(
        "e2",
        "a",
        "b",
        labels=("new",),
        attrs=(("active", True), ("weight", 1)),
    )


def test_constructed_node_can_be_matched_required_and_deleted_in_same_block():
    program = parse_program(
        'program Demo { rule main => { '
        'add node "tmp" label "Generated" attr "kind" = "generated"; '
        'match node $n label "Generated" attr "kind" = "generated"; '
        'require node $n label "Generated"; '
        'delete node $n; '
        'require no node "tmp"; '
        '} }'
    )

    result = execute_program(program, Graph.empty())

    assert result.graph.node_ids == ()


def test_constructed_edge_can_be_matched_required_and_deleted_in_same_block():
    program = parse_program(
        'program Demo { rule main => { '
        'add edge "tmp-edge" from "a" to "b" label "GeneratedEdge" attr "weight" = 1; '
        'match edge $e from "a" to "b" label "GeneratedEdge" attr "weight" = 1; '
        'require edge $e label "GeneratedEdge"; '
        'delete edge $e; '
        'require no edge "tmp-edge"; '
        '} }'
    )
    graph = Graph(nodes=(Node("a"), Node("b")))

    result = execute_program(program, graph)

    assert result.graph.edge_ids == ()


def test_rejects_duplicate_inline_construction_attribute():
    with pytest.raises(ParserError, match="duplicate attribute matcher"):
        parse_program(
            'program Demo { rule main => add node "n3" attr "kind" = "a" attr(kind) = "b"; }'
        )


def test_rejects_duplicate_inline_construction_label():
    with pytest.raises(ParserError, match="duplicate node constructor label"):
        parse_program('program Demo { rule main => add node "n3" label "A" label "B"; }')
