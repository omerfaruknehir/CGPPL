from cgppl.ast import (
    AttrExpr,
    AttrPredicate,
    FieldExpr,
    LiteralExpr,
    MatchEdgeStmt,
    MatchNodeStmt,
    RequireNoEdgeStmt,
    RequireNoNodeStmt,
    VarExpr,
    VarRef,
    WherePredicate,
)
from cgppl.runtime_diagnostics import (
    format_forbidden_edge_failure,
    format_forbidden_node_failure,
    format_match_edge_failure,
    format_match_node_failure,
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
