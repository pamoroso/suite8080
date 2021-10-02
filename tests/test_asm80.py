"""Tests for the suite8080.asm80 module."""

from unittest import mock

import pytest

from suite8080 import asm80


@pytest.mark.parametrize('source_line, expected', [
    # Label, mnemonic, operand1, operand2, comment
    #
    # Blank line
    ('', ('', '', '', '', '')),
    # All spaces
    ('   ', ('', '', '', '', '')),
    # Mixed whitespace
    ('\t  \t  ', ('', '', '', '', '')),
    # Comment only
    ('  ; Comment only', ('', '', '', '', 'Comment only')),
    # Label only
    ('label:', ('label', '', '', '', '')),
    # Only mnemonic
    ('nop', ('', 'nop', '', '', '')),
    # One operand
    ('xra a', ('', 'xra', 'a', '', '')),
    # Two operands
    ('mov b, a', ('', 'mov', 'b', 'a', '')),
    # Immediate operand
    ('adi 01h', ('', 'adi', '01h', '', '')),
    # Label operand
    ('jmp loop', ('', 'jmp', 'loop', '', '')),
    # All tokens
    ('label: mov b, a ; Comment', ('label', 'mov', 'b', 'a', 'Comment')),
    # Tabs
    ('label:\tmov\tb, a\t; Comment', ('label', 'mov', 'b', 'a', 'Comment')),
    # All tokens separated by tabs
    ('label:\tmov\tb,\ta\t;\tComment', ('label', 'mov', 'b', 'a', 'Comment')),
    # Incorrect syntax: missing label terminator
    ('label mov b, a', ('', 'label mov', 'b', 'a', '')),
    # Incorrect syntax: missing comment start character
    ('label: mov b, a comment', ('label', 'mov', 'b', 'a comment', '')),
    # Immediate operand
    ('mvi c, 09h', ('', 'mvi', 'c', '09h', '')),
    # Label reference
    ('lxi d, message', ('', 'lxi', 'd', 'message', '')),
    # org directive
    ('org 100h', ('', 'org', '100h', '', '')),
    # end directive
    ('end', ('', 'end', '', '', '')),
    # Numeric db
    ('label: db 5', ('label', 'db', '5', '', '')),
    # String db
    ("message: db 'Hello$'", ('message', 'db', 'Hello$', '', '')),
])
def test_parse(source_line, expected):
    assert asm80.parse(source_line) == expected


@pytest.mark.parametrize('string, result', [
    ("", False),
    ("abc", False),
    ("'abc'", True),
    ("abc'", False),
    ("'abc", False),
    ("' a b c '", True),
    ("' a ' b ''", True),
    ("' a ' b", False),
])
def test_is_quote_delimited(string, result):
    assert asm80.is_quote_delimited(string) == result


@pytest.mark.parametrize('source_line, expected', [
    # Not a multiarg db directive
    ('mov b, c', ('', '', '')),
    ('lxi d, message', ('', '', '')),
    ('nop', ('', '', '')),
    # Multiple decimal args
    ('label: db 0, 1, 2', ('label', 'db', '0, 1, 2')),
    # Multiple hex args
    ('label: db 10h, 20h, 30h', ('label', 'db', '10h, 20h, 30h')),
    # No label supplied
    ('db 3, 4, 5', ('', 'db', '3, 4, 5')),
    # Single arg
    ('db 1', ('', 'db', '1')),
])
def test_parse_db(source_line, expected):
    assert asm80.parse_db(source_line) == expected


def test_parse_db_invalid_label_syntax(capsys):
    with pytest.raises(SystemExit):
        asm80.parse_db('label db 1, 2, 3')
        captured = capsys.readouterr()
        assert 'invalid label' in captured.err


def test_parse_db_invalid_label(capsys):
    with pytest.raises(SystemExit):
        asm80.parse_db('3label: db 1, 2, 3')
        captured = capsys.readouterr()
        assert 'invalid label' in captured.err


def test_report_error(capsys):
    with pytest.raises(SystemExit):
        expected = 'error message'
        asm80.report_error('error message')
        captured = capsys.readouterr()
        assert expected in captured.err


# The tests that use multiple patching may be replaced with patch.multiple().
# If I can figure how it works.

@mock.patch('suite8080.asm80.label', 'label')
@mock.patch('suite8080.asm80.address', 0)
@mock.patch('suite8080.asm80.symbol_table', {})
def test_add_label_address0():
    expected = asm80.address
    asm80.add_label()
    assert asm80.symbol_table[asm80.label] == expected


@mock.patch('suite8080.asm80.label', 'label')
@mock.patch('suite8080.asm80.address', 10)
@mock.patch('suite8080.asm80.symbol_table', {})
def test_add_label_new():
    expected = asm80.address
    asm80.add_label()
    assert asm80.symbol_table[asm80.label] == expected


@mock.patch('suite8080.asm80.label', 'label')
@mock.patch('suite8080.asm80.address', 10)
@mock.patch('suite8080.asm80.symbol_table', {'label': 10})
def test_add_label_duplicate(capsys):
    with pytest.raises(SystemExit):
        expected = 'duplicate label'
        asm80.symbol_table['label'] = 10
        asm80.add_label()
        captured = capsys.readouterr()
        assert expected in captured.err


# There's a bug but I can't figure where.
@pytest.mark.skip(reason='bug')
@mock.patch('suite8080.asm80.operand1', 'b')
@mock.patch('suite8080.asm80.operand2', 'c')
@mock.patch('suite8080.asm80.source_pass', 2)
@mock.patch('suite8080.asm80.output', b'')
def test_mov_b_c():
    expected = b'0x41'  # 65
    asm80.mov()
    assert asm80.output == expected


@pytest.mark.parametrize('register, opcode', [
    ('b', 0),
    ('B', 0),
    ('c', 1),
    ('C', 1),
    ('d', 2),
    ('D', 2),
    ('e', 3),
    ('E', 3),
    ('h', 4),
    ('H', 4),
    ('l', 5),
    ('L', 5),
    ('m', 6),
    ('M', 6),
    ('a', 7),
    ('A', 7),
])
def test_register_offset8(register, opcode):
    assert asm80.register_offset8(register) == opcode


@mock.patch('suite8080.asm80.operand1', 'b')
@mock.patch('suite8080.asm80.operand2', 'invalid')
def test_register_offset8_invalid_register(capsys):
    with pytest.raises(SystemExit):
        expected = 'invalid register'
        asm80.mov()
        captured = capsys.readouterr()
        assert expected in captured.err


@mock.patch('suite8080.asm80.operand1', 'b')
@mock.patch('suite8080.asm80.operand2', '')
def test_register_offset8_missing_register(capsys):
    with pytest.raises(SystemExit):
        expected = 'invalid register'
        asm80.mov()
        captured = capsys.readouterr()
        assert expected in captured.err


@pytest.mark.skip(reason='bug')
@mock.patch('suite8080.asm80.operand1', '12')
@mock.patch('suite8080.asm80.output', b'')
def test_immediate_operand_decimal():
    expected = b'\x0c'
    asm80.immediate_operand()
    assert asm80.output == expected


@pytest.mark.parametrize('input, number', [
    ('123', 123),
    ('123h', 291),
    ('02h', 2),
    ('02', 2),
    ('0ah', 10),
    ('10H', 16),
    ('00001111B', 15),
    ('10o', 8),
])
def test_get_number(input, number):
    assert asm80.get_number(input) == number


@pytest.mark.parametrize('current_address, expression, value', [
    (2, '$+2', 4),
    (2, '$-2', 0),
    (2, '$*2', 4),
    (2, '$/2', 1),
    (2, '$%2', 0),
    (2, '$+02h', 4),
])
def test_dollar(current_address, expression, value):
    assert asm80.dollar(current_address, expression) == value


def test_dollar_invalid_expression(capsys):
    with pytest.raises(SystemExit):
        asm80.dollar(0, '$#2')
        captured = capsys.readouterr()
        assert 'invalid "equ" expression' in captured.err