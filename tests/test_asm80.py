"""Tests for the suite8080.asm80 module."""

import pytest

from suite8080 import asm80


@pytest.mark.parametrize('source_line, expected', [
    # Label, mnemonic, operand1, operand2, comment
    #
    # Blank line
    ('   ', ('', '', '', '', '')),
    ('  ; Comment only', ('', '', '', '', 'Comment only')),
])
def test_parse(source_line, expected):
    assert asm80.parse(source_line) == expected
