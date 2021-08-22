"""An Intel 8080 cross-assembler."""

import argparse
from pathlib import Path


# Current source line number
lineno = 0

# Address of current instruction
address = 0

# This is a 2-pass assembler, so keep track of which pass we're in
source_pass = 1

# Assembled machine code
output = b''


def parse():
    """Parse an assembly source line."""
    pass


def write_binary_file(filename):
    """Write machine code output to a binary file."""
    with open(filename, 'wb') as file:
        file.write(output)


def assemble(lines, outfile):
    """Assemble source and write output to a file."""
    global lineno, source_pass

    source_pass = 1
    for lineno, line in enumerate(lines):
        parse()

    source_pass = 2
    for lineno, line in enumerate(lines):
        parse()
    
    write_binary_file(outfile)


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