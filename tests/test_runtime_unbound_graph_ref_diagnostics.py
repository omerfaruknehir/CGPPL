from cgppl.ast import VarRef
from cgppl.runtime_diagnostics import format_unbound_graph_ref_failure


def test_formats_unbound_graph_ref_failure():
    assert format_unbound_graph_ref_failure(VarRef("missing"), "edge source", ("main", "helper")) == (
        "unbound edge source variable $missing in rule main -> helper"
    )


def test_runtime_resolves_unbound_graph_refs_through_helper():
    runtime_source = open("src/cgppl/runtime.py", encoding="utf-8").read()

    assert "format_unbound_graph_ref_failure" in runtime_source
    assert "unbound {kind} variable" not in runtime_source
