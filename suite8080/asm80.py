"""An Intel 8080 cross-assembler."""

import argparse
from pathlib import Path
import sys


# Current source line number.
lineno = 0

# Address of current instruction.
address = 0

# This is a 2-pass assembler, so keep track of which pass we're in.
source_pass = 1

# Assembled machine code.
output = b''

# Tokens
label = ''
mnemonic = ''
operand1 = ''
operand2 = ''
comment = ''

# Symbol table: {'label1': <address1>, 'label2': <address2>, ...}
symbol_table = {}


# Immediate operand type, 8-bit or 16-bit. An enum would be overkill and verbose.
IMMEDIATE8=8
IMMEDIATE16=16


# Default output file name
OUTFILE = 'program'


def assemble(lines):
    """Assemble source lines."""
    global lineno, source_pass

    # The end Assembly directive raises StopIteration, which we catch and do
    # nothing so that instuction parsing and processing ends and execution can
    # proceed with the succeeding statements.
    source_pass = 1
    try:
        for lineno, line in enumerate(lines):
            parse(line)
            process_instruction()
    except StopIteration:
        pass

    source_pass = 2
    try:
        for lineno, line in enumerate(lines):
            parse(line)
            process_instruction()
    except StopIteration:
        pass


# A source line has the following syntax:
#
# [label:] [mnemonic [operand1[, operand2]]] [; comment]
def parse(line):
    """Parse a source line."""
    global label, mnemonic, operand1, operand2, comment

    label = ''
    mnemonic = ''
    operand1 = ''
    operand2 = ''
    comment = ''

    # Remove leading whitespace
    preprocess = line.lstrip()
    # The order or tabs in the source line may confuse the parses, which scans the
    # line from a single direction (eg right to left). To work around this I replace
    # all tabs (HTAB: ASCII 9) with spaces (SPACE: ASCII 32).
    tab_to_space = {9: 32}
    preprocess = preprocess.translate(tab_to_space)

    # Split comment from the rest of the line.
    #
    # _l: left part of the string split by rpartition
    # _sep: separator of the string split by rpartition
    # _r: left part of the string split by rpartition
    comment_l, comment_sep, comment_r = preprocess.rpartition(';')
    if comment_sep:
        comment = comment_r.strip()
    else:
        # If the separator isn't found, the first 2 elements of the 3-tuple
        # rpartition returns are empty strings. So use the 3rd element with
        # the argument string as the remainder to parse. Also strip trailing
        # whitespace as it may interfere with the whitespace we search for later.
        comment_l = comment_r.rstrip()

    # db directive?
    db_label, directive, arguments = parse_db(comment_l)
    if directive == 'db':
        label = db_label
        mnemonic = directive
        operand1 = arguments
        return label, mnemonic, operand1, operand2, comment

    # Split second operand from the remainder.
    operand2_l, operand2_sep, operand2_r = comment_l.rpartition(',')
    if operand2_sep:
        operand2 = operand2_r.strip()
    else:
        operand2_l = operand2_r.rstrip()
    
    # Split first operand from the remainder.
    #
    # Checking for tabs is now obsolete as we convert to spaces early in the parsing.
    operand1_l, operand1_sep, operand1_r = operand2_l.rpartition('\t')
    if operand1_sep == '\t':
        operand1 = operand1_r.strip()
    else:
        operand1_l, operand1_sep, operand1_r = operand2_l.rpartition(' ')
        if operand1_sep == ' ':
            operand1 = operand1_r.strip()
        else:
            operand1_l = operand1_r.rstrip()

    # Split mnemonic from label.
    mnemonic_l, mnemonic_sep, mnemonic_r = operand1_l.rpartition(':')
    if mnemonic_sep:
        mnemonic = mnemonic_r.strip()
        label = mnemonic_l.strip()
    else:
        mnemonic_l = mnemonic_r.rstrip()
        mnemonic = mnemonic_l.strip()

    # Fixup for the equ directive.
    equ_l, equ_sep, equ_r = comment_l.partition('equ')
    if equ_sep == 'equ':
        if label != '' or operand2 != '':
            report_error(f'invalid "equ" syntax: {operand1}')
        label = equ_l.strip()
        mnemonic = equ_sep.strip()
        operand1 = equ_r.strip()


    # Fixup for the case in which the mnemonic ends up as the first operand
    # (mnemonic = '' and operand1 = 'mnemonic'):
    #
    # label: mnemonic
    if mnemonic == '' and operand1 != '' and operand2 == '':
        mnemonic = operand1.strip()
        operand1 = ''

    # This parser is based on the algorithm in this post by Brian Rober Callahan:
    # https://briancallahan.net/blog/20210410.html
    #
    # Although he mentions a fixup for the case in which the mnemonic and the
    # first operand may both end up in the first operand, I'm not sure my
    # implementation is affected by the same issue the fixup is supposed to address.

    label = label.lower()
    mnemonic = mnemonic.lower()
    return label, mnemonic, operand1, operand2, comment


def parse_db(line):
    """Parse db directive.

    Parse the source line to check whether it's a valid db directive. If it is
    return 'db' as the second value and the arguments as the third. The first
    value is the label if present, otherwise a null string.

    Assume the source line doesn't contain a comment.

    Parameters
    ----------
        line : string
            Source line
    
    Returns
    -------
        label
            Lowercase label if present, otherwise ''
        directive
            'db' if line contains a valid db directive, otherwise ''
        arguments
            Arguments if line contains a db directive, otherwise ''
    """
    db_label = db_directive = db_arguments = ''

    # The separator argument of .partition() is case-sensitive.
    left1, sep1, right1 = line.partition('db')
    if sep1 == '':
        left1, sep1, right1 = line.partition('DB')
    # No db directive found.
    if sep1 == '':
        return db_label, db_directive, db_arguments

    db_arguments = right1.strip()

    left2, sep2, _ = left1.partition(':')
    # Check if the supplied label is alphanumeric and doesn't start with a digit.
    if sep2 == ':':
        left2 = left2.strip()
        if (not left2.isalnum()) or (left2[0].isdigit()):
            report_error(f'invalid label "{left2}"')
        db_label = left2
    # A string not terminated by a colon preceeds the db directive
    elif sep2 != ':' and left2.strip() != '':
        report_error(f'invalid label "{left2}"')

    return db_label.lower(), 'db', db_arguments


# Using a dictionary to similate a switch statement or dispatch on the mnemonic
# wouldn't save much code or make it more clear, as we need a separate function
# per mnemonic anyway to check the operands.
def process_instruction():
    """Check instruction operands and generate code."""
    #global label, mnemonic, operand1, operand2, comment

    if mnemonic == operand1 == operand2 == '':
        pass_action(0, b'')
        return

    if mnemonic == 'nop':
        nop()
    elif mnemonic == 'lxi':
        lxi()
    elif mnemonic == 'stax':
        stax()
    elif mnemonic == 'inx':
        inx()
    elif mnemonic == 'inr':
        inr()
    elif mnemonic == 'dcr':
        dcr()
    elif mnemonic == 'mvi':
        mvi()
    elif mnemonic == 'rlc':
        rlc()
    elif mnemonic == 'dad':
        dad()
    elif mnemonic == 'ldax':
        ldax()
    elif mnemonic == 'dcx':
        dcx()
    elif mnemonic == 'rrc':
        rrc()
    elif mnemonic == 'ral':
        ral()
    elif mnemonic == 'rar':
        rar()
    elif mnemonic == 'shld':
        shld()
    elif mnemonic == 'daa':
        daa()
    elif mnemonic == 'lhld':
        lhld()
    elif mnemonic == 'cma':
        cma()
    elif mnemonic == 'sta':
        sta()
    elif mnemonic == 'stc':
        stc()
    elif mnemonic == 'lda':
        lda()
    elif mnemonic == 'cmc':
        cmc()
    elif mnemonic == 'mov':
        mov()
    elif mnemonic == 'hlt':
        hlt()
    elif mnemonic == 'add':
        add()
    elif mnemonic == 'adc':
        adc()
    elif mnemonic == 'sub':
        sub()
    elif mnemonic == 'sbb':
        sbb()
    elif mnemonic == 'ana':
        ana()
    elif mnemonic == 'xra':
        xra()
    elif mnemonic == 'ora':
        ora()
    elif mnemonic == 'cmp':
        cmp()
    elif mnemonic == 'rnz':
        rnz()
    elif mnemonic == 'pop':
        pop()
    elif mnemonic == 'jnz':
        jnz()
    elif mnemonic == 'jmp':
        jmp()
    elif mnemonic == 'cnz':
        cnz()
    elif mnemonic == 'push':
        push()
    elif mnemonic == 'adi':
        adi()
    elif mnemonic == 'rst':
        rst()
    elif mnemonic == 'rz':
        rz()
    elif mnemonic == 'ret':
        ret()
    elif mnemonic == 'jz':
        jz()
    elif mnemonic == 'cz':
        cz()
    elif mnemonic == 'call':
        call()
    elif mnemonic == 'aci':
        aci()
    elif mnemonic == 'rnc':
        rnc()
    elif mnemonic == 'jnc':
        jnc()
    elif mnemonic == 'out':
        i80_out()
    elif mnemonic == 'cnc':
        cnc()
    elif mnemonic == 'sui':
        sui()
    elif mnemonic == 'rc':
        rc()
    elif mnemonic == 'jc':
        jc()
    elif mnemonic == 'in':
        i80_in()
    elif mnemonic == 'cc':
        cc()
    elif mnemonic == 'sbi':
        sbi()
    elif mnemonic == 'jpe':
        jpe()
    elif mnemonic == 'rpo':
        rpo()
    elif mnemonic == 'jpo':
        jpo()
    elif mnemonic == 'xthl':
        xthl()
    elif mnemonic == 'cpo':
        cpo()
    elif mnemonic == 'ani':
        ani()
    elif mnemonic == 'rpe':
        rpe()
    elif mnemonic == 'pchl':
        pchl()
    elif mnemonic == 'xchg':
        xchg()
    elif mnemonic == 'cpe':
        cpe()
    elif mnemonic == 'xri':
        xri()
    elif mnemonic == 'rp':
        rp()
    elif mnemonic == 'jp':
        jp()
    elif mnemonic == 'di':
        di()
    elif mnemonic == 'cp':
        cp()
    elif mnemonic == 'ori':
        ori()
    elif mnemonic == 'rm':
        rm()
    elif mnemonic == 'sphl':
        sphl()
    elif mnemonic == 'jm':
        jm()
    elif mnemonic == 'ei':
        ei()
    elif mnemonic == 'cm':
        cm()
    elif mnemonic == 'cpi':
        cpi()
    elif mnemonic == 'db':
        db()
    elif mnemonic == 'ds':
        ds()
    elif mnemonic == 'dw':
        dw()
    elif mnemonic == 'end':
        end()
    elif mnemonic == 'equ':
        equ()
    elif mnemonic == 'name':
        name()
    elif mnemonic == 'org':
        org()
    elif mnemonic == 'title':
        title()
    else:
        report_error(f'unknown mnemonic "{mnemonic}"')


def report_error(message):
    """Display an error message and exit returning an error code."""

    # List indexes start at 0 but humans count lines starting at 1.
    print(f'asm80> line {lineno + 1}: {message}', file=sys.stderr)
    sys.exit(1)


def pass_action(instruction_size, output_byte, should_add_label=True):
    """Build symbol table in pass 1, generate code in pass 2.
    
    Parameters
    ----------
        instruction_size : int
            Number of bytes of the instruction
        output_byte : bytes
            Opcode, b'' if no output should be generated.
        should_add_label : Boolean
            True if the label, when present, should be added
    """
    global address, output

    if source_pass == 1:
        # Add new symbol if we have a label, unless should_add_label tells not to
        # in order to prevent duplicate label errors with multiargument db.
        if label and should_add_label:
            add_label()
            # Increment address counter by the size of the instruction.
        address += instruction_size
    else:
        # Pass 2. Output the byte representing the opcode. For instructions with
        # additional arguments or data we'll output that in a separate function.
        if output_byte != b'':
            output += output_byte


def add_label():
    """Add a label to the symbol table."""
    global symbol_table

    if label in symbol_table:
        report_error(f'duplicate label: "{label}"')
    symbol_table[label] = address


# nop: 0x00
def nop():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x00')


# lxi: 0x01 + 16-bit register offset
def lxi():
    check_operands(operand1 != '' and operand2 != '')
    # 0x01 = 1
    opcode = 1 + register_offset16()
    pass_action(3, opcode.to_bytes(1, byteorder='little'))
    immediate_operand(IMMEDIATE16)


# We add a special case here rather than changing register_offset16() for just
# 2 instructions, stax and ldax.
# stax: 0x02 + 16-bit register offset
def stax():
    check_operands(operand1 != '' and operand2 == '')
    if operand1 == 'b':
        pass_action(1, b'\x02')
    elif operand1 == 'd':
        pass_action(1, b'\x12')
    else:
        report_error(f'"stax" only takes "b" or "d", not "{operand1}"')


# inx: 0x03
def inx():
    check_operands(operand1 != '' and operand2 == '')
    # 0x03 = 3
    opcode = 3 + register_offset16()
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# inr: 0x04
def inr():
    check_operands(operand1 != '' and operand2 == '')
    # 0x04 = 4
    opcode = 4 + (register_offset8(operand1) << 3)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# dcr: 0x05
def dcr():
    check_operands(operand1 != '' and operand2 == '')
    # 0x05 = 5
    opcode = 5 + (register_offset8(operand1) << 3)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# mvi: 0x06 + (8-bit register offset << 3)
def mvi():
    check_operands(operand1 != '' and operand2 != '')
    # 0x06 = 6
    opcode = 6 + (register_offset8(operand1) << 3)
    pass_action(2, opcode.to_bytes(1, byteorder='little'))
    immediate_operand()


# rlc: 0x07
def rlc():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x07')


# Is `dad b` a valid instruction? asm80 handles it and dis80 disassembles it as
# just `dad` but I'm not sure `dad b` is legal.
# dad: 0x09
def dad():
    check_operands(operand1 != '' and operand2 == '')
    # 0x09 = 9
    opcode = 9 + register_offset16()
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# We add a special case here rather than changing register_offset16() for just
# 2 instructions, stax and ldax.
# ldax: 0x0a + 16-bit register offset
def ldax():
    check_operands(operand1 != '' and operand2 == '')
    if operand1 == 'b':
        pass_action(1, b'\x0a')
    elif operand1 == 'd':
        pass_action(1, b'\x1a')
    else:
        report_error(f'"ldax" only takes "b" or "d", not "{operand1}"')


# dcx: 0x0b
def dcx():
    check_operands(operand1 != '' and operand2 == '')
    # 0x0b = 11
    opcode = 11 + register_offset16()
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# rrc: 0x0f
def rrc():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x0f')


# ral: 0x17
def ral():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x17')


# rar: 0x1f
def rar():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x1f')


# shld: 0x22
def shld():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\x22')
    address16()


# daa: 0x27
def daa():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x27')


# lhld: 0x2a
def lhld():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\x2a')
    address16()


# cma: 0x2f
def cma():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x2f')


# sta: 0x32
def sta():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\x32')
    address16()


# stc: 0x37
def stc():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x37')


# lda: 0x3a
def lda():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\x3a')
    address16()


# cmc: 0x3f
def cmc():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x3f')


# mov: 0x40 + (8-bit first register offset << 3) + (8-bit second register offset)
# mov m, m: 0x76 (hlt)
def mov():
    check_operands(operand1 != '' and operand2 != '')
    # 0x40 = 64
    opcode = 64 + (register_offset8(operand1) << 3) + register_offset8(operand2)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# hlt: 0x76
def hlt():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x76')


# add: 0x80 + 8-bit register offset
def add():
    check_operands(operand1 != '' and operand2 == '')
    # 0x80 = 128
    opcode = 128 + register_offset8(operand1)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# adc: 0x88 + 8-bit register offset
def adc():
    check_operands(operand1 != '' and operand2 == '')
    # 0x88 = 136
    opcode = 136 + register_offset8(operand1)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# sub: 0x90 + 8-bit register offset
def sub():
    check_operands(operand1 != '' and operand2 == '')
    # 0x90 = 144
    opcode = 144 + register_offset8(operand1)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# sbb: 0x98 + 8-bit register offset
def sbb():
    check_operands(operand1 != '' and operand2 == '')
    # 0x98 = 152
    opcode = 152 + register_offset8(operand1)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# ana: 0xa0 + 8-bit register offset
def ana():
    check_operands(operand1 != '' and operand2 == '')
    # 0xa0 = 160
    opcode = 160 + register_offset8(operand1)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# xra: 0xa8 + 8-bit register offset
def xra():
    check_operands(operand1 != '' and operand2 == '')
    # 0xa8 = 168
    opcode = 168 + register_offset8(operand1)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# ora: 0xb0 + 8-bit register offset
def ora():
    check_operands(operand1 != '' and operand2 == '')
    # 0xb0 = 176
    opcode = 176 + register_offset8(operand1)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# cmp: 0xb8 + 8-bit register offset
def cmp():
    check_operands(operand1 != '' and operand2 == '')
    # 0xb8 = 184
    opcode = 184 + register_offset8(operand1)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# rnz: 0xc0
def rnz():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xc0')


# pop: 0xc1 + 16-bit register offset
def pop():
    check_operands(operand1 != '' and operand2 == '')
    # 0xc1 = 193
    opcode = 193 + register_offset16()
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# jnz: 0xc2
def jnz():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xc2')
    address16()


# jmp: 0xc3
def jmp():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xc3')
    address16()


# cnz: 0xc4
def cnz():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xc4')
    address16()


# push: 0xc5 + 16-bit register offset
def push():
    check_operands(operand1 != '' and operand2 == '')
    # 0xc5 = 197
    opcode = 197 + register_offset16()
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# adi: 0xc6
def adi():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(2, b'\xc6')
    immediate_operand()


# rst: 0xc7 + (8 * restart vector number)
def rst():
    check_operands(operand1 != '' and operand2 == '')
    offset = int(operand1, 10)
    if 0 <= offset <= 7:
        # 0xc7 = 199
        opcode = 199 + (offset << 3)
        pass_action(1, opcode.to_bytes(1, byteorder='little'))
    else:
        report_error(f'invalid restart vector "{operand1}"')


# rz: 0xc8
def rz():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xc8')


# ret: 0xc9
def ret():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xc9')


# jz: 0xca
def jz():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xca')
    address16()


# cz: 0xcc
def cz():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xcc')
    address16()


# call: 0xcd
def call():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xcd')
    address16()


# aci: 0xce
def aci():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(2, b'\xce')
    immediate_operand()


# rnc: 0xd0
def rnc():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xd0')


# jnc: 0xd2
def jnc():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xd2')
    address16()


# out: 0xd3
def i80_out():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(2, b'\xd3')
    immediate_operand()


# cnc: 0xd4
def cnc():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xd4')
    address16()


# sui: 0xd6
def sui():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(2, b'\xd6')
    immediate_operand()


# rc: 0xd8
def rc():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xd8')


# jc: 0xda
def jc():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xda')
    address16()


# in: 0xdb
def i80_in():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(2, b'\xdb')
    immediate_operand()


# cc: 0xdc
def cc():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xdc')
    address16()


# sbi: 0xde
def sbi():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(2, b'\xde')
    immediate_operand()


# jpe: 0xea
def jpe():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xea')
    address16()


# rpo: 0xe0
def rpo():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xe0')


# jpo: 0xe2
def jpo():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xe2')
    address16()


# xthl: 0xe3
def xthl():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xe3')


# cpo: 0xe4
def cpo():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xe4')
    address16()


# ani: 0xe6
def ani():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(2, b'\xe6')
    immediate_operand()


# rpe: 0xe8
def rpe():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xe8')


# pchl: 0xe9
def pchl():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xe9')


# xchg: 0xeb
def xchg():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xeb')


# cpe: 0xec
def cpe():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xec')
    address16()


# xri: 0xee
def xri():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(2, b'\xee')
    immediate_operand()


# rp: 0xf0
def rp():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xf0')


# jp: 0xf2
def jp():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xf2')
    address16()


# di: 0xf3
def di():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xf3')


# cp: 0xf4
def cp():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xf4')
    address16()


# ori: 0xf6
def ori():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(2, b'\xf6')
    immediate_operand()


# rm: 0xf8
def rm():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xf8')


# sphl: 0xf9
def sphl():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xf9')


# jm: 0xfa
def jm():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xfa')
    address16()


# ei: 0xfb
def ei():
    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\xfb')


# cm: 0xfc
def cm():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(3, b'\xfc')
    address16()


# cpi: 0xfe
def cpi():
    check_operands(operand1 != '' and operand2 == '')
    pass_action(2, b'\xfe')
    immediate_operand()


# DIRECTIVES

def db():
    global address, output
    should_add_label = True

    check_operands(operand1 != '' and operand2 == '')

    arguments = parse_db_arguments(operand1)
    for argument in arguments:
        # Numeric literal.
        if argument[0].isdigit():
            value = get_number(argument)
            pass_action(1, value.to_bytes(1, byteorder='little'),
                        label != '' and should_add_label)
            # If we add a label, prevent it from being added again when multiple
            # arguments are present.
            should_add_label = False
        # Character constant, e.g. 'Z'.
        elif is_char_constant(argument):
            value = ord(argument[1])
            pass_action(1, value.to_bytes(1, byteorder='little'),
                        label != '' and should_add_label)
            should_add_label = False
        # String, e.g. 'string'
        elif is_quote_delimited(argument):
            string_length = len(argument) - 2  # Account for enclosing ' pair
            if source_pass == 1:
                if label != '' and should_add_label:
                    add_label()
                    should_add_label = False
                address += string_length
            else:
                # Strip enclosing ' characters when adding to output.
                output += bytes(argument[1:-1], encoding='utf-8')
                address += string_length
        # Label.
        else:
            if source_pass == 2:
                if argument not in symbol_table:
                    report_error(f'undefined label "{argument}"')
                value = symbol_table[argument]
                value_size = 1 if (0 <= value <= 255) else 2
                output += value.to_bytes(value_size, byteorder='little')
                address += value_size


def parse_db_arguments(string):
    """Return a list of db arguments parsed from string.
    
    Split string into arguments, strip whitespace from them, and return a list of
    the resulting arguments.
    """
    arguments = string.split(',')
    arguments = [argument.strip() for argument in arguments]
    return arguments


def is_char_constant(string):
    """Return True if string is a character constant.

    A character constant is a quote-delimited string containing only one character
    such as 'Z' or '*'.
    """
    return len(string) == 3 and is_quote_delimited(string)


def is_quote_delimited(string):
    """Return True if string is enclosed between single or double quotes."""
    stripped = string.strip()
    return ((stripped.startswith("'") and stripped.endswith("'")) or
            (stripped.startswith('"') and stripped.endswith('"')))


def ds():
    global address, output

    check_operands(operand1 != '' and operand2 == '')
    if source_pass == 1:
        if label != '':
            add_label()
    elif source_pass == 2:
        # Doesn't work with hex numbers
        output += bytes(get_number(operand1))
    # BUG: Doesn't work with hex numbers; address is incrmented twice, once per pass.
    address += get_number(operand1)


def dw():
    global address

    check_operands(operand1 != '' and operand2 == '')
    if source_pass == 1:
        if label != '':
            add_label()
    address16()
    address += 2


def end():
    check_operands(label == operand1 == operand2 == '')
    raise StopIteration


def equ():
    global address

    if label == '':
        report_error(f'missing "equ" label')
    
    # Expression, e.g $+3 or $*2.
    if operand1.startswith('$'):
        value = dollar(address, operand1)
    # Character constant, e.g. 'Z'
    elif is_char_constant(operand1):
        value = ord(operand1[1])
    # Number.
    else:
        value = get_number(operand1)
    
    if source_pass == 1:
        saved = address
        address = value
        add_label()
        address = saved


def dollar(current_address, expression):
    """Calculate value of $-address expression."""
    value = current_address
    if len(expression) > 1:
        if expression[1] == '+':
            value += get_number(expression[2:])
        elif expression[1] == '-':
            value -= get_number(expression[2:])
        elif expression[1] == '*':
            value *= get_number(expression[2:])
        elif expression[1] == '/':
            value /= get_number(expression[2:])
        elif expression[1] == '%':
            value %= get_number(expression[2:])
        else:
            report_error(f'invalid "equ" expression "{expression}"')

    return int(value)


# Skipped.
def name():
    check_operands(operand1 != '' and (label == operand2 == ''))


def org():
    global address

    check_operands(operand1 != '' and (label == operand2 == ''))
    if operand1[0].isdigit():
        if source_pass == 1:
            address = get_number(operand1)
    else:
        report_error(f'"org" requires a numeric operand, not "{operand1}"')


# Skipped.
def title():
    check_operands(operand1 != '' and (label == operand2 == ''))


def register_offset8(raw_register):
    """Return encoding of 8-bit register."""
    register = raw_register.lower()
    if register == 'b':
        return 0
    elif register == 'c':
        return 1
    elif register == 'd':
        return 2
    elif register == 'e':
        return 3
    elif register == 'h':
        return 4
    elif register == 'l':
        return 5
    elif register == 'm':
        return 6
    elif register == 'a':
        return 7
    else:
        report_error(f'invalid register "{register}"')


def register_offset16():
    """Return encoding of 16-bit register pair."""
    if operand1 in ('b', 'B', 'bc', 'BC'):
        return 0  # 0x00
    elif operand1 in ('d', 'D', 'de', 'DE'):
        return 16  # 0x10
    elif operand1 in ('h', 'H', 'hl', 'HL'):
        return 32  # 0x20
    elif operand1 in ('psw', 'PSW'):
        if (mnemonic == 'push' or mnemonic == 'pop'):
            return 48  # 0x30
        else:
            report_error(f'"psw" can not be used with instruction "{mnemonic}"')
    elif operand1 == 'sp':
        if (mnemonic != 'push' and mnemonic != 'pop'):
            return 48  # 0x30
        else:
            report_error(f'"sp" can not be used with instruction "{mnemonic}"')
    else:
        report_error(f'invalid register "{operand1}" for instruction "{mnemonic}"')


def check_operands(valid):
    "Report error if argument isn't Truthy."
    if not(valid):
        report_error(f'invalid operands for mnemonic "{mnemonic}"')


# Should it work with negative operands?
def immediate_operand(operand_type=IMMEDIATE8):
    """Generate code for an 8-bit or 16-bit immediate operand."""
    global output

    if mnemonic == 'lxi' or mnemonic == 'mvi':
        operand = operand2
    else:
        operand = operand1

    # Numeric literal.
    if operand[0].isdigit():
        number = get_number(operand)
    # Character constant, e.g. 'Z'.
    elif operand_type == IMMEDIATE8 and is_char_constant(operand):
        number = ord(operand[1])
    # Label.
    elif source_pass == 2:
        # Testing for membership seems clearer than using .get() with a default
        # (which complicates parsing valid numeric literals) and accepts also an
        # operand = 0.
        if operand not in symbol_table:
            report_error(f'undefined label "{operand}"')
        number = symbol_table[operand]

    if source_pass == 2:
        operand_size = 1 if operand_type == IMMEDIATE8  else 2
        output += number.to_bytes(operand_size, byteorder='little')


# BUG: doesn't work with immediate addresses like ffh; labels aren't added to
# symbol table as pass 1 isn't handled.
def address16():
    """Generate code for 16-bit addresses."""
    global output

    if operand1[0].isdigit():
        number = get_number(operand1)
    else:
        # Valid addresses are non-negative, so a negative address is an appropriate
        # default for a label not in the symbol table.
        number = symbol_table.get(operand1, -1)
        if source_pass == 2 and number < 0:
            report_error(f'undefined label "{operand1}"')

    if source_pass == 2:
        output += number.to_bytes(2, byteorder='little')


def get_number(input):
    """Return value of hex or decimal numeric input string."""
    if input.endswith(('h', 'H')):
        base = 16
    elif input.endswith(('q', 'Q')):
        base = 8
    elif input.endswith(('b', 'B')):
        base = 2
    else:
        base = 10

    if base != 10:
        number = int(input[:-1], base)
    else:
        number = int(input)

    return number


def main():
    """Parse the command line and pass the input file to the assembler."""
    asm80_description = f'Intel 8080 assembler / Suite8080'
    parser = argparse.ArgumentParser(description=asm80_description)
    parser.add_argument('filename', default='-', help="input file, stdin if '-'")
    parser.add_argument('-o', '--outfile',
                        help=f'output file, {OUTFILE + ".com"} if input is - and -o not supplied')
    parser.add_argument('-s', '--symtab', action='store_true',
                        help='save symbol table')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')
    args = parser.parse_args()

    if args.filename == '-':
        lines = sys.stdin.readlines()
    else:
        infile = Path(args.filename)
        with open(infile, 'r') as file:
            lines = file.readlines()

    if args.filename == '-':
        outfile = args.outfile if args.outfile else OUTFILE + '.com'
        symfile = Path(args.outfile).stem + '.sym' if args.outfile else OUTFILE + '.sym'
    elif args.outfile:
        outfile = Path(args.outfile)
        symfile = Path(args.outfile).stem + '.sym'
    else:
        outfile = Path(infile.stem + '.com')
        symfile = Path(infile.stem + '.sym')

    assemble(lines)
    bytes_written = write_binary_file(outfile, output)
    if args.symtab:
        symbol_count = write_symbol_table(symbol_table, symfile)

    if args.verbose:
        print(f'{bytes_written} bytes written')
        if args.symtab:
            print(f'{symbol_count} symbols written')


def write_binary_file(filename, binary_data):
    """Write binary_data to filename and return number of bytes written."""
    with open(filename, 'wb') as file:
        file.write(binary_data)
    return len(binary_data)


# The symbol table is saved in the .sym CP/M file format described in section
# "1.1 SID Startup" on page 4 of "SID Users Guide" by Digital Research:
# http://www.cpm.z80.de/randyfiles/DRI/SID_ZSID.pdf

def write_symbol_table(table, filename):
    """Save symbol table to filename and return the number of symbols written.
    
    The table is written to a text file in the CP/M .sym file format. No file
    is created if the table is empty."""
    symbol_count = len(table)
    if symbol_count == 0:
        return symbol_count

    with open(filename, 'w', encoding='utf-8') as file:
        for symbol in table:
            print(f'{table[symbol]:04X} {symbol[:16].upper()}', file=file)

    return symbol_count


if __name__ == '__main__':
    main()
