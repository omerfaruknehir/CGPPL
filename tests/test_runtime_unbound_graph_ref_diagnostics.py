import pytest

from cgppl.ast import VarRef
from cgppl.graph import Graph, Node
from cgppl.parser import parse_program
from cgppl.runtime import GraphMatchFailed, execute_program
from cgppl.runtime_diagnostics import format_unbound_graph_ref_failure


def test_formats_unbound_graph_ref_failure():
    assert format_unbound_graph_ref_failure(VarRef("missing"), "edge source", ("main", "helper")) == (
        "unbound edge source variable $missing in rule main -> helper"
    )


@pytest.mark.xfail(reason="_resolve_ref still emits the unbound graph-ref diagnostic directly")
def test_runtime_uses_structured_unbound_graph_ref_failure_for_edge_endpoint():
    program = parse_program(
        'program Demo { rule main => add edge $new_edge from $missing to "target" label "new"; }'
    )
    graph = Graph(nodes=(Node("target"),))

    with pytest.raises(
        GraphMatchFailed,
        match="unbound edge source variable \\$missing in rule main",
    ):
        execute_program(program, graph)
