"""Tests for the suite8080.asm80 module."""

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
    # All tokens separated by tabs
    ('label:\tmov\tb,\ta\t;\tComment', ('label', 'mov', 'b', 'a', 'Comment')),
    # All caps Code
    ('LABEL: MOV B, A ; Comment', ('label', 'mov', 'b', 'a', 'Comment')),
    # Incorrect syntax: missing label terminator
    ('label mov b, a ; Comment', ('', 'label mov', 'b', 'a', 'Comment')),
    # Incorrect syntax: missing comment start character
    ('label: mov b, a Comment', ('label', 'mov', 'b', 'a comment', '')),
])
def test_parse(source_line, expected):
    assert asm80.parse(source_line) == expected


# The tests involving globals should wrap the test code within saving and restoring
# the globals.

def test_report_error(capsys):
    with pytest.raises(SystemExit):
        expected = 'error message'
        asm80.report_error('error message')
        captured = capsys.readouterr()
        assert expected in captured.err


def test_add_label_address0():
    asm80.label = 'label1'
    asm80.address = 0
    expected = asm80.address
    asm80.add_label()
    assert asm80.symbol_table[asm80.label] == expected


def test_add_label_new():
    asm80.label = 'label2'
    asm80.address = 10
    expected = asm80.address
    asm80.add_label()
    assert asm80.symbol_table[asm80.label] == expected


def test_add_label_duplicate(capsys):
    asm80.label = 'label3'
    asm80.address = 10
    expected = asm80.address
    with pytest.raises(SystemExit):
        expected = 'duplicate label'
        asm80.symbol_table['label3'] = 10
        asm80.add_label()
        captured = capsys.readouterr()
        assert expected in captured.err