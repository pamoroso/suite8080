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
    global lineno, source_pass

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
    else:
        report_error(f'unknown mnemonic "{mnemonic}"')


def report_error(message):
    """Display an error message and exit returning an error code."""
    global lineno

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
    global source_pass, label, mnemonic, address, output

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
    global symbol_table, address, label

    if label in symbol_table:
        report_error(f'duplicate label: "{label}"')
    symbol_table[label] = address


# nop: 0x00
def nop():
    global operand1, operand2

    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x00')


# mov: 0x40 + (8-bit first register offset << 3) + (8-bit second register offsett)
# mov m, m: 0x76 (hlt)
def mov():
    global operand1, operand2

    check_operands(operand1 != '' and operand2 != '')
    # 0x40 = 64
    opcode = 64 + (register_offset8(operand1) << 3) + register_offset8(operand2)
    pass_action(1, opcode.to_bytes(1, byteorder='little'))


# hlt: 0x76
def hlt():
    global operand1, operand2

    check_operands(operand1 == operand2 == '')
    pass_action(1, b'\x76')


def register_offset8(register):
    """Return 8-bit encoding of register."""
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


def check_operands(valid):
    "Report error if argument isn't Truthy."
    if not(valid):
        report_error(f'invalid operands for mnemonic "{mnemonic}"')


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
