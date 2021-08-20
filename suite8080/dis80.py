"""An Intel 8080 disassembler."""

import argparse


program = None


def main(filename):
    global program

    with open(filename, 'rb') as file:
        program = file.read()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help=' A file name')
    args = parser.parse_args()

    main(args.filename)