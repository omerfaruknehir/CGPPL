import pytest

from cgppl.lexer import LexerError, TokenKind, tokenize


def visible(tokens):
    return [(token.kind, token.value) for token in tokens if token.kind is not TokenKind.EOF]


def test_lexes_keywords_identifiers_literals_and_symbols():
    tokens = tokenize('program Demo { rule main => skip; let x := 42; let s := "ok"; }')

    assert visible(tokens) == [
        (TokenKind.KEYWORD, "program"),
        (TokenKind.IDENT, "Demo"),
        (TokenKind.SYMBOL, "{"),
        (TokenKind.KEYWORD, "rule"),
        (TokenKind.KEYWORD, "main"),
        (TokenKind.SYMBOL, "=>"),
        (TokenKind.KEYWORD, "skip"),
        (TokenKind.SYMBOL, ";"),
        (TokenKind.KEYWORD, "let"),
        (TokenKind.IDENT, "x"),
        (TokenKind.SYMBOL, ":="),
        (TokenKind.INTEGER, "42"),
        (TokenKind.SYMBOL, ";"),
        (TokenKind.KEYWORD, "let"),
        (TokenKind.IDENT, "s"),
        (TokenKind.SYMBOL, ":="),
        (TokenKind.STRING, "ok"),
        (TokenKind.SYMBOL, ";"),
        (TokenKind.SYMBOL, "}"),
    ]


def test_lexes_graph_construction_keywords():
    tokens = tokenize('add edge "e1" from "a" to "b";')

    assert visible(tokens) == [
        (TokenKind.KEYWORD, "add"),
        (TokenKind.KEYWORD, "edge"),
        (TokenKind.STRING, "e1"),
        (TokenKind.KEYWORD, "from"),
        (TokenKind.STRING, "a"),
        (TokenKind.KEYWORD, "to"),
        (TokenKind.STRING, "b"),
        (TokenKind.SYMBOL, ";"),
    ]


def test_lexes_graph_attribute_mutation_keywords():
    tokens = tokenize('set node "n1" attr "active" = true;')

    assert visible(tokens) == [
        (TokenKind.KEYWORD, "set"),
        (TokenKind.KEYWORD, "node"),
        (TokenKind.STRING, "n1"),
        (TokenKind.KEYWORD, "attr"),
        (TokenKind.STRING, "active"),
        (TokenKind.SYMBOL, "="),
        (TokenKind.KEYWORD, "true"),
        (TokenKind.SYMBOL, ";"),
    ]


def test_lexes_graph_label_keyword():
    tokens = tokenize('require node "n1" label "Root";')

    assert visible(tokens) == [
        (TokenKind.KEYWORD, "require"),
        (TokenKind.KEYWORD, "node"),
        (TokenKind.STRING, "n1"),
        (TokenKind.KEYWORD, "label"),
        (TokenKind.STRING, "Root"),
        (TokenKind.SYMBOL, ";"),
    ]


def test_lexes_match_variables():
    tokens = tokenize('match node $n label "Root"; delete node $n;')

    assert visible(tokens) == [
        (TokenKind.KEYWORD, "match"),
        (TokenKind.KEYWORD, "node"),
        (TokenKind.SYMBOL, "$"),
        (TokenKind.IDENT, "n"),
        (TokenKind.KEYWORD, "label"),
        (TokenKind.STRING, "Root"),
        (TokenKind.SYMBOL, ";"),
        (TokenKind.KEYWORD, "delete"),
        (TokenKind.KEYWORD, "node"),
        (TokenKind.SYMBOL, "$"),
        (TokenKind.IDENT, "n"),
        (TokenKind.SYMBOL, ";"),
    ]


def test_skips_line_and_block_comments():
    tokens = tokenize('program A // comment\n/* more */ rule r -> skip')
    values = [token.value for token in tokens if token.kind is not TokenKind.EOF]
    assert values == ["program", "A", "rule", "r", "->", "skip"]


def test_tracks_line_and_column():
    tokens = tokenize("program\n  Demo")
    demo = tokens[1]
    assert demo.value == "Demo"
    assert demo.start.line == 2
    assert demo.start.column == 3


def test_rejects_unknown_characters():
    with pytest.raises(LexerError):
        tokenize("program @")


def test_rejects_unterminated_string():
    with pytest.raises(LexerError):
        tokenize('"unterminated')
