from cgppl.ast import (
    AttrExpr,
    AttrPredicate,
    FieldExpr,
    LiteralExpr,
    VarExpr,
    VarRef,
    WherePredicate,
)
from cgppl.diagnostics import (
    format_graph_predicate,
    format_graph_predicate_failure,
    format_graph_ref,
    format_literal,
    format_rule_location,
    format_where_predicate,
)


def test_formats_rule_locations():
    assert format_rule_location(()) == "<entry>"
    assert format_rule_location(("main", "helper")) == "main -> helper"


def test_formats_graph_refs_as_source_like_text():
    assert format_graph_ref(VarRef("n")) == "$n"
    assert format_graph_ref("literal-id") == '"literal-id"'


def test_formats_literal_values_as_source_like_text():
    assert format_literal("root") == '"root"'
    assert format_literal(3) == "3"
    assert format_literal(True) == "true"
    assert format_literal(False) == "false"
    assert format_literal(None) == "<missing>"


def test_formats_where_predicates():
    predicate = WherePredicate(FieldExpr("id"), "==", VarExpr("selected"))

    assert format_where_predicate(predicate) == "field id == $selected"


def test_formats_graph_predicate_constraints():
    predicate = format_graph_predicate(
        "node",
        VarRef("n"),
        labels=("Root", "Selected"),
        attrs=(AttrPredicate("kind", "root"), AttrPredicate("active", True)),
        where=(WherePredicate(AttrExpr("rank"), ">=", LiteralExpr(2)),),
    )

    assert predicate == (
        'node $n with label "Root", label "Selected", attr "kind" = "root", '
        'attr "active" = true, where attr "rank" >= 2'
    )


def test_formats_edge_endpoint_constraints():
    predicate = format_graph_predicate(
        "edge",
        VarRef("e"),
        source_id=VarRef("source"),
        target_id="target",
        labels=("blocked",),
    )

    assert predicate == 'edge $e from $source to "target" with label "blocked"'


def test_formats_full_graph_predicate_failures_with_rule_context():
    message = format_graph_predicate_failure(
        "no match for",
        "edge",
        VarRef("e"),
        source_id=VarRef("source"),
        target_id=VarRef("target"),
        labels=("blocked",),
        where=(WherePredicate(FieldExpr("source"), "==", VarExpr("source")),),
        call_stack=("main",),
    )

    assert message == (
        'no match for edge $e from $source to $target with label "blocked", '
        'where field source == $source in rule main'
    )
