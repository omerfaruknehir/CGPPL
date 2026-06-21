import pytest

from cgppl.ast import (
    AddEdgeStmt,
    AddNodeStmt,
    BlockStmt,
    CallStmt,
    DeleteEdgeStmt,
    DeleteNodeStmt,
    FailStmt,
    MatchEdgeStmt,
    MatchNodeStmt,
    RequireEdgeAttrStmt,
    RequireEdgeLabelStmt,
    RequireEdgeStmt,
    RequireNodeAttrStmt,
    RequireNodeLabelStmt,
    RequireNodeStmt,
    SetEdgeAttrStmt,
    SetEdgeLabelStmt,
    SetNodeAttrStmt,
    SetNodeLabelStmt,
    SkipStmt,
    VarRef,
)
from cgppl.parser import ParserError, parse_program


def test_parses_program_with_rule_and_body_call():
    program = parse_program("program Demo { rule main => skip; main(); }")

    assert program.name == "Demo"
    assert len(program.rules) == 1
    assert program.rules[0].name == "main"
    assert isinstance(program.rules[0].body, SkipStmt)
    assert program.body == (CallStmt("main"),)


def test_parses_fail_statement_rule_body():
    program = parse_program("program Demo { rule stop -> fail; }")
    assert isinstance(program.rules[0].body, FailStmt)


def test_parses_graph_requirement_statements():
    program = parse_program(
        'program Demo { rule main => require node "n1"; require edge(e1); }'
    )

    assert program.rules[0].body == RequireNodeStmt("n1")
    assert program.body == (RequireEdgeStmt("e1"),)


def test_parses_graph_attribute_requirement_statements():
    program = parse_program(
        'program Demo { rule main => require node "n1" attr "kind" = "root"; '
        'require edge(e1) attr(weight) = 1; }'
    )

    assert program.rules[0].body == RequireNodeAttrStmt("n1", "kind", "root")
    assert program.body == (RequireEdgeAttrStmt("e1", "weight", 1),)


def test_parses_boolean_attribute_requirement_values():
    program = parse_program('program Demo { rule main => require node(n1) attr(active) = true; }')

    assert program.rules[0].body == RequireNodeAttrStmt("n1", "active", True)


def test_rejects_non_literal_attribute_requirement_value():
    with pytest.raises(ParserError, match="expected literal value"):
        parse_program('program Demo { rule main => require node "n1" attr "kind" = helper; }')


def test_parses_graph_label_requirement_statements():
    program = parse_program(
        'program Demo { rule main => require node "n1" label "Root"; '
        'require edge(e1) label(link); }'
    )

    assert program.rules[0].body == RequireNodeLabelStmt("n1", "Root")
    assert program.body == (RequireEdgeLabelStmt("e1", "link"),)


def test_parses_node_match_and_variable_reference():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Root"; delete node $n; } }'
    )

    assert program.rules[0].body == BlockStmt(
        (MatchNodeStmt(VarRef("n"), "Root"), DeleteNodeStmt(VarRef("n")))
    )


def test_parses_edge_match_with_endpoint_variables():
    program = parse_program(
        'program Demo { rule main => { match edge $e from $a to "b" label "link"; '
        'require node $a; delete edge $e; } }'
    )

    assert program.rules[0].body == BlockStmt(
        (
            MatchEdgeStmt(VarRef("e"), VarRef("a"), "b", "link"),
            RequireNodeStmt(VarRef("a")),
            DeleteEdgeStmt(VarRef("e")),
        )
    )


def test_rejects_match_node_without_variable():
    with pytest.raises(ParserError, match="expected symbol"):
        parse_program('program Demo { rule main => match node "n1" label "Root"; }')


def test_parses_graph_delete_statements():
    program = parse_program(
        'program Demo { rule main => delete node "n1"; delete edge(e1); }'
    )

    assert program.rules[0].body == DeleteNodeStmt("n1")
    assert program.body == (DeleteEdgeStmt("e1"),)


def test_parses_graph_add_statements():
    program = parse_program(
        'program Demo { rule main => add node "n3"; add edge(e2) from(n2) to "n3"; }'
    )

    assert program.rules[0].body == AddNodeStmt("n3")
    assert program.body == (AddEdgeStmt("e2", "n2", "n3"),)


def test_parses_graph_add_statements_with_labels():
    program = parse_program(
        'program Demo { rule main => add node "n3" label "Replacement"; '
        'add edge(e2) from(n2) to "n3" label(link); }'
    )

    assert program.rules[0].body == AddNodeStmt("n3", "Replacement")
    assert program.body == (AddEdgeStmt("e2", "n2", "n3", "link"),)


def test_parses_graph_add_edge_with_variable_endpoint():
    program = parse_program(
        'program Demo { rule main => { match node $n label "Root"; add edge "e2" from $n to "n3"; } }'
    )

    assert program.rules[0].body == BlockStmt(
        (MatchNodeStmt(VarRef("n"), "Root"), AddEdgeStmt("e2", VarRef("n"), "n3"))
    )


def test_parses_graph_attribute_set_statements():
    program = parse_program(
        'program Demo { rule main => set node "n3" attr "kind" = "replacement"; '
        'set edge(e2) attr(weight) = 1; }'
    )

    assert program.rules[0].body == SetNodeAttrStmt("n3", "kind", "replacement")
    assert program.body == (SetEdgeAttrStmt("e2", "weight", 1),)


def test_parses_boolean_attribute_values():
    program = parse_program('program Demo { rule main => set node(n1) attr(active) = true; }')

    assert program.rules[0].body == SetNodeAttrStmt("n1", "active", True)


def test_rejects_non_literal_attribute_value():
    with pytest.raises(ParserError, match="expected literal value"):
        parse_program('program Demo { rule main => set node "n1" attr "kind" = helper; }')


def test_parses_graph_label_set_statements():
    program = parse_program(
        'program Demo { rule main => set node "n3" label "Visited"; '
        'set edge(e2) label(link); }'
    )

    assert program.rules[0].body == SetNodeLabelStmt("n3", "Visited")
    assert program.body == (SetEdgeLabelStmt("e2", "link"),)


def test_rejects_set_without_attr_or_label():
    with pytest.raises(ParserError, match="expected 'attr' or 'label'"):
        parse_program('program Demo { rule main => set node "n1"; }')


def test_parses_block_rule_body():
    program = parse_program(
        'program Demo { rule main => { require node "n1"; delete node "n1"; } }'
    )

    assert program.rules[0].body == BlockStmt(
        (RequireNodeStmt("n1"), DeleteNodeStmt("n1"))
    )


def test_parses_empty_block_rule_body():
    program = parse_program("program Demo { rule main => { } }")

    assert program.rules[0].body == BlockStmt(())


def test_rejects_unclosed_block():
    with pytest.raises(ParserError, match="expected symbol"):
        parse_program('program Demo { rule main => { require node "n1"; }')


def test_rejects_missing_program_wrapper():
    with pytest.raises(ParserError):
        parse_program("rule main => skip;")
