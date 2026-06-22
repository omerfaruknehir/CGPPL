from cgppl.ast import (
    AttrExpr,
    AttrPredicate,
    FieldExpr,
    LiteralExpr,
    MatchEdgeStmt,
    MatchNodeStmt,
    RequireEdgeAttrStmt,
    RequireEdgeLabelStmt,
    RequireEdgeStmt,
    RequireNoEdgeStmt,
    RequireNoNodeStmt,
    RequireNodeAttrStmt,
    RequireNodeLabelStmt,
    RequireNodeStmt,
    VarExpr,
    VarRef,
    WherePredicate,
)
from cgppl.runtime_diagnostics import (
    format_forbidden_edge_failure,
    format_forbidden_node_failure,
    format_match_edge_failure,
    format_match_node_failure,
    format_required_edge_attr_failure,
    format_required_edge_failure,
    format_required_edge_label_failure,
    format_required_node_attr_failure,
    format_required_node_failure,
    format_required_node_label_failure,
)


def test_formats_match_node_failure_with_constraints():
    statement = MatchNodeStmt(
        VarRef("n"),
        labels=("Root", "Selected"),
        attrs=(AttrPredicate("kind", "root"),),
        where=(WherePredicate(AttrExpr("rank"), ">=", LiteralExpr(2)),),
    )

    assert format_match_node_failure(statement, ("main",)) == (
        'no match for node $n with label "Root", label "Selected", '
        'attr "kind" = "root", where attr "rank" >= 2 in rule main'
    )


def test_formats_match_edge_failure_with_constraints():
    statement = MatchEdgeStmt(
        VarRef("e"),
        source_id=VarRef("source"),
        target_id="target",
        labels=("new",),
        where=(WherePredicate(FieldExpr("source"), "==", VarExpr("source")),),
    )

    assert format_match_edge_failure(statement, ("main", "helper")) == (
        'no match for edge $e from $source to "target" with label "new", '
        'where field source == $source in rule main -> helper'
    )


def test_formats_forbidden_node_failure_with_constraints():
    statement = RequireNoNodeStmt(
        VarRef("blocked"),
        labels=("Blocked",),
        attrs=(AttrPredicate("active", True),),
    )

    assert format_forbidden_node_failure(statement, ("main",)) == (
        'forbidden match for node $blocked with label "Blocked", '
        'attr "active" = true in rule main'
    )


def test_formats_forbidden_edge_failure_with_constraints():
    statement = RequireNoEdgeStmt(
        VarRef("e"),
        source_id=VarRef("source"),
        target_id=VarRef("target"),
        labels=("blocked",),
        where=(WherePredicate(FieldExpr("target"), "!=", VarExpr("target")),),
    )

    assert format_forbidden_edge_failure(statement, ("main",)) == (
        'forbidden match for edge $e from $source to $target with label "blocked", '
        'where field target != $target in rule main'
    )


def test_formats_required_node_failure():
    statement = RequireNodeStmt("missing")

    assert format_required_node_failure(statement, ("main",)) == (
        'missing requirement for node "missing" in rule main'
    )


def test_formats_required_edge_failure():
    statement = RequireEdgeStmt(VarRef("e"))

    assert format_required_edge_failure(statement, ("main", "helper")) == (
        "missing requirement for edge $e in rule main -> helper"
    )


def test_formats_required_node_label_failure():
    statement = RequireNodeLabelStmt("n1", "Root")

    assert format_required_node_label_failure(statement, ("main",)) == (
        'missing requirement for node "n1" with label "Root" in rule main'
    )


def test_formats_required_edge_label_failure():
    statement = RequireEdgeLabelStmt(VarRef("e"), "link")

    assert format_required_edge_label_failure(statement, ("main",)) == (
        'missing requirement for edge $e with label "link" in rule main'
    )


def test_formats_required_node_attr_failure_with_actual_value():
    statement = RequireNodeAttrStmt("n1", "kind", "root")

    assert format_required_node_attr_failure(statement, "leaf", ("main",)) == (
        'missing requirement for node "n1" with attr "kind" = "root"; '
        'found "leaf" in rule main'
    )


def test_formats_required_edge_attr_failure_with_missing_value():
    statement = RequireEdgeAttrStmt(VarRef("e"), "weight", 2)

    assert format_required_edge_attr_failure(statement, None, ("main",)) == (
        'missing requirement for edge $e with attr "weight" = 2; '
        "found <missing> in rule main"
    )
