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
