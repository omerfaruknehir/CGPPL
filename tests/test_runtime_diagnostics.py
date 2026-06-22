from cgppl.ast import (
    AttrExpr,
    AttrPredicate,
    DeleteEdgeStmt,
    DeleteNodeStmt,
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
    SetEdgeAttrStmt,
    SetEdgeLabelStmt,
    SetNodeAttrStmt,
    SetNodeLabelStmt,
    UnsetEdgeAttrStmt,
    UnsetEdgeLabelStmt,
    UnsetNodeAttrStmt,
    UnsetNodeLabelStmt,
    VarExpr,
    VarRef,
    WherePredicate,
)
from cgppl.runtime_diagnostics import (
    format_forbidden_edge_failure,
    format_forbidden_node_failure,
    format_match_edge_failure,
    format_match_node_failure,
    format_missing_delete_edge_target_failure,
    format_missing_delete_node_target_failure,
    format_missing_set_edge_attr_target_failure,
    format_missing_set_edge_label_target_failure,
    format_missing_set_node_attr_target_failure,
    format_missing_set_node_label_target_failure,
    format_missing_unset_edge_attr_target_failure,
    format_missing_unset_edge_label_target_failure,
    format_missing_unset_node_attr_target_failure,
    format_missing_unset_node_label_target_failure,
    format_required_edge_attr_failure,
    format_required_edge_failure,
    format_required_edge_label_failure,
    format_required_node_attr_failure,
    format_required_node_failure,
    format_required_node_label_failure,
    format_unbound_where_variable_failure,
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


def test_formats_missing_delete_node_target_failure():
    statement = DeleteNodeStmt("missing")

    assert format_missing_delete_node_target_failure(statement, ("main",)) == (
        'missing delete target for node "missing" in rule main'
    )


def test_formats_missing_delete_edge_target_failure():
    statement = DeleteEdgeStmt(VarRef("e"))

    assert format_missing_delete_edge_target_failure(statement, ("main", "helper")) == (
        "missing delete target for edge $e in rule main -> helper"
    )


def test_formats_missing_set_node_attr_target_failure():
    statement = SetNodeAttrStmt("missing", "kind", "new")

    assert format_missing_set_node_attr_target_failure(statement, ("main",)) == (
        'missing set target for node "missing" with attr "kind" in rule main'
    )


def test_formats_missing_set_edge_attr_target_failure():
    statement = SetEdgeAttrStmt(VarRef("e"), "weight", 2)

    assert format_missing_set_edge_attr_target_failure(statement, ("main", "helper")) == (
        'missing set target for edge $e with attr "weight" in rule main -> helper'
    )


def test_formats_missing_set_node_label_target_failure():
    statement = SetNodeLabelStmt("missing", "Visited")

    assert format_missing_set_node_label_target_failure(statement, ("main",)) == (
        'missing set target for node "missing" with label "Visited" in rule main'
    )


def test_formats_missing_set_edge_label_target_failure():
    statement = SetEdgeLabelStmt(VarRef("e"), "selected")

    assert format_missing_set_edge_label_target_failure(statement, ("main",)) == (
        'missing set target for edge $e with label "selected" in rule main'
    )


def test_formats_missing_unset_node_attr_target_failure():
    statement = UnsetNodeAttrStmt("missing", "kind")

    assert format_missing_unset_node_attr_target_failure(statement, ("main",)) == (
        'missing unset target for node "missing" with attr "kind" in rule main'
    )


def test_formats_missing_unset_edge_attr_target_failure():
    statement = UnsetEdgeAttrStmt(VarRef("e"), "weight")

    assert format_missing_unset_edge_attr_target_failure(statement, ("main",)) == (
        'missing unset target for edge $e with attr "weight" in rule main'
    )


def test_formats_missing_unset_node_label_target_failure():
    statement = UnsetNodeLabelStmt("missing", "Visited")

    assert format_missing_unset_node_label_target_failure(statement, ("main", "cleanup")) == (
        'missing unset target for node "missing" with label "Visited" in rule main -> cleanup'
    )


def test_formats_missing_unset_edge_label_target_failure():
    statement = UnsetEdgeLabelStmt(VarRef("e"), "selected")

    assert format_missing_unset_edge_label_target_failure(statement, ("main",)) == (
        'missing unset target for edge $e with label "selected" in rule main'
    )


def test_formats_unbound_where_variable_failure():
    assert format_unbound_where_variable_failure(VarExpr("missing"), ("main", "helper")) == (
        "unbound where variable $missing in rule main -> helper"
    )
