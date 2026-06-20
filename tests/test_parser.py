import pytest

from cgppl.ast import CallStmt, FailStmt, SkipStmt
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


def test_rejects_missing_program_wrapper():
    with pytest.raises(ParserError):
        parse_program("rule main => skip;")
