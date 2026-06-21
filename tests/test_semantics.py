import pytest

from cgppl.parser import parse_program
from cgppl.semantics import SemanticError, validate_program


def test_accepts_program_with_main_rule():
    program = parse_program("program Demo { rule main => skip; }")
    validate_program(program)


def test_rejects_duplicate_rule_names():
    program = parse_program("program Demo { rule main => skip; rule main => skip; }")

    with pytest.raises(SemanticError) as exc:
        validate_program(program)

    assert "duplicate rule declaration: main" in str(exc.value)


def test_rejects_undefined_rule_calls():
    program = parse_program("program Demo { rule main => missing(); }")

    with pytest.raises(SemanticError) as exc:
        validate_program(program)

    assert "undefined rule call: missing" in str(exc.value)


def test_rejects_undefined_rule_calls_inside_blocks():
    program = parse_program("program Demo { rule main => { skip; missing(); } }")

    with pytest.raises(SemanticError) as exc:
        validate_program(program)

    assert "undefined rule call: missing" in str(exc.value)


def test_entry_point_check_can_be_disabled():
    program = parse_program("program Demo { rule helper => skip; }")
    validate_program(program, entry_point=None)
