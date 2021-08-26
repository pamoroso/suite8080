"""Tests for the suite8080.asm80 module."""

import pytest

from suite8080 import asm80


def test_parse_blank_line():
    """Test that a whitespace-only line generates no tokens."""
    source_line = '   '
    # Label, mnemonic, operand1, operand2, comment
    expected = ('', '', '', '', '')

    assert asm80.parse(source_line) == expected


def test_parse_comment_only():
    """Test that a comment-only line generates only comment token."""
    source_line = '  ; Comment only'
    # Label, mnemonic, operand1, operand2, comment
    expected = ('', '', '', '', 'Comment only')

    assert asm80.parse(source_line) == expected
