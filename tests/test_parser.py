import pytest

from cgppl.ast import (
    CallStmt,
    DeleteEdgeStmt,
    DeleteNodeStmt,
    FailStmt,
    RequireEdgeStmt,
    RequireNodeStmt,
    SkipStmt,
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


 def test_parses_graph_delete_statements():
    program = parse_program(
        'program Demo { rule main => delete node "n1"; delete edge(e1); }'
    )

    assert program.rules[0].body == DeleteNodeStmt("n1")
    assert program.body == (DeleteEdgeStmt("e1"),)


 def test_rejects_missing_program_wrapper():
    with pytest.raises(ParserError):
        parse_program("rule main => skip;")
