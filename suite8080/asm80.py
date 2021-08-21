"""An Intel 8080 cross-assembler."""

import argparse
from pathlib import Path


def assemble(lines, outfile):
    pass


def main(infile):
    with open(infile, 'r') as file:
        lines = [line for line in file]

    outfile = Path(infile.stem + '.com')
    assemble(lines, outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help=' A file name')
    args = parser.parse_args()

    main(Path(args.filename))