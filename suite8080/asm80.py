"""An Intel 8080 cross-assembler."""

import argparse
from pathlib import Path
import sys


# Current source line number
lineno = 0

# Address of current instruction
address = 0

# This is a 2-pass assembler, so keep track of which pass we're in
source_pass = 1

# Assembled machine code
output = b''

# Tokens
label = ''
mnemonic = ''
operand1 = ''
operand2 = ''
comment = ''

# Symbol table: {'label1': <address1>, 'label2': <address2>, ...}
symbol_table = {}


def assemble(lines, outfile):
    """Assemble source and write output to a file."""
    global source_pass

    source_pass = 1
    for lineno, line in enumerate(lines):
        parse(line)
        process_instruction()

    source_pass = 2
    for lineno, line in enumerate(lines):
        parse(line)
        process_instruction()
    
    write_binary_file(outfile)


def write_binary_file(filename):
    """Write machine code output to a binary file."""
    with open(filename, 'wb') as file:
        file.write(output)


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
    
    # Split second operand from the remainder
    operand2_l, operand2_sep, operand2_r = comment_l.rpartition(',')
    if operand2_sep:
        operand2 = operand2_r.strip().lower()
    else:
        operand2_l = operand2_r.rstrip().lower()
    
    # Split first operand from the remainder
    operand1_l, operand1_sep, operand1_r = operand2_l.rpartition('\t')
    if operand1_sep:
        operand1 = operand1_r.strip().lower()
    else:
        operand1_l, operand1_sep, operand1_r = operand2_l.rpartition(' ')
        if operand1_sep:
            operand1 = operand1_r.strip().lower()
        else:
            operand1_l = operand1_r.rstrip()
    
    # Split mnemonic from label
    mnemonic_l, mnemonic_sep, mnemonic_r = operand1_l.rpartition(':')
    if mnemonic_sep:
        mnemonic = mnemonic_r.strip().lower()
        label = mnemonic_l.strip().lower()
    else:
        mnemonic_l = mnemonic_r.rstrip().lower()
        mnemonic = mnemonic_l.strip().lower()
    
    # Fixup for the case in which the mnemonic ends up as the first operand (mnemonic = '' and operand1 = 'mnemonic'):
    #
    # label: mnemonic
    if operand1 and not(mnemonic):
        mnemonic = operand1.strip().lower()
        operand1 = ''

    # This parser is based on the algorithm in this post by Brian Rober Callahan:
    # https://briancallahan.net/blog/20210410.html
    # Although he mentions a fixup for the case in which the mnemonic and the
    # first operand may both end up in the first operand, I'm not sure my
    # implementation is affected by the same issue the fixup is supposed to address.

    return label, mnemonic, operand1, operand2, comment


# Using a dictionary to similate a switch statement or dispatch on the mnemonic
# wouldn't save much code or make it more clear, as we need a separate function
# per mnemonic anyway to check the operands.
def process_instruction():
    """Check instruction operands and generate code."""
    global label, mnemonic, operand1, operand2, comment

    # Line completely blank or containing only a label and/or comment
    if mnemonic == operand1 == operand2 == '':
        pass_action(0, b'')
        return

    if mnemonic == 'nop':
        nop()
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
    else:
        report_error(f'unknown mnemonic "{mnemonic}"')


def report_error(message):
    """Display an error message and exit returning an error code."""

    # List indexes start at 0 but humans count lines starting at 1
    print(f'asm80> line {lineno + 1}: {message}', file=sys.stderr)
    sys.exit(1)


def pass_action(instruction_size, output_byte):
    """Build symbol table in pass 1, generate code in pass 2.
    
    Parameters
    ----------
        instruction_size : int
            Number of bytes of the instruction
        output_byte : bytes
            Opcode, b'' if no output should be generated. 
    """
    global address, output

    if source_pass == 1:
        # Add new symbol if we have a label
        if label:
            add_label()
            # Increment address counter by the size of the instruction
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


def register_offset8(register):
    """Return encoding of 8-bit register."""
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
    if operand1 == 'b':
        return 0  # 0x00
    elif operand1 == 'd':
        return 16  # 0x10
    elif operand1 == 'h':
        return 32  # 0x20
    elif operand1 == 'psw':
        return 48  # 0x30
    else:
        report_error(f'invalid register "{operand1}" for instruction "{mnemonic}"')


def check_operands(valid):
    "Report error if argument isn't Truthy."
    if not(valid):
        report_error(f'invalid operands for mnemonic "{mnemonic}"')


# BUG: doesn't work for operands <= 0
def immediate_operand():
    """Generate code for an 8-bit immediate operand."""
    global output

    if operand1[0].isdigit():
        number = get_number(operand1)
    elif source_pass == 2:
        number = symbol_table.get(operand1, False)
        if not(number):
            report_error(f'undefined label "{operand1}"')

    if source_pass == 2:
        output += number.to_bytes(1, byteorder='little')


# BUG: doesn't work with immediate addresses like ffh; labels aren't added to
# symbol table as pass 1 isn't handled
def address16():
    """Generate code for 16-bit addresses."""
    global output

    if operand1[0].isdigit():
        number = get_number(operand1)
    else:
        number = symbol_table.get(operand1, -1)
        if source_pass == 2 and number < 0:
            report_error(f'undefined label "{operand1}"')

    if source_pass == 2:
        output += number.to_bytes(2, byteorder='little')


def get_number(input):
    """Return value of hex or decimal numeric input string."""
    if input.endswith('h'):
        number = int(input[:-1], 16)
    else:
        number = int(input)
    return number


def main(infile):
    """Parse the command line and pass the input file to the assembler."""
    with open(infile, 'r') as file:
        lines = [line for line in file]

    outfile = Path(infile.stem + '.com')
    assemble(lines, outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help=' A file name')
    args = parser.parse_args()

    main(Path(args.filename))
