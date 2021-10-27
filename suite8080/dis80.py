"""An Intel 8080 disassembler."""

import argparse

# Offsets of the fields within the tuple holding an instruction table entry.
MNEMONIC = 0
SIZE = 1

# A potential data structure for the instruction table may be a list of named
# tuples. But dozens of verbose named tuple creations would clutter the table.
#
# So I went with a much cleaner list of ordinary tuples. The slightly more complex
# references (e.g. instructions[i1][i2]) are only a couple and can be made a bit
# more readable via MNEMONIC and SIZE (e.g. instructions[i][MNEMONIC] or
# instructions[i][SIZE]).
instructions = [
   ('nop',      1),
   ('lxi b,',   3),
   ('stax b',   1),
   ('inx b',    1),
   ('inr b',    1),
   ('dcr b',    1),
   ('mvi b,',   2),
   ('rlc',      1),
   ('nop',      1),
   ('dad',      1),
   ('ldax b',   1),
   ('dcx b',    1),
   ('inr c',    1),
   ('dcr c',    1),
   ('mvi c,',   2),
   ('rrc',      1),
   ('nop',      1),
   ('lxi d,',   3),
   ('stax d',   1),
   ('inx d',    1),
   ('inr d',    1),
   ('dcr d',    1),
   ('mvi d,',   2),
   ('ral',      1),
   ('nop',      1),
   ('dad d',    1),
   ('ldax d',   1),
   ('dcx d' ,   1),
   ('inr e',    1),
   ('dcr e',    1),
   ('mvi e,',   2),
   ('rar',      1),
   ('nop',      1),
   ('lxi h,',   3),
   ('shld ',    3),
   ('inx h',    1),
   ('inr h',    1),
   ('dcr h',    1),
   ('mvi h,',   2),
   ('daa',      1),
   ('nop',      1),
   ('dad h',    1),
   ('lhld',     3),
   ('dcx h',    1),
   ('inr l',    1),
   ('dcr l',    1),
   ('mvi l,',   2),
   ('cma',      1),
   ('nop',      1),
   ('lxi sp,',  3),
   ('sta',      3),
   ('inx sp',   1),
   ('inr m',    1),
   ('dcr m',    1),
   ('mvi m,',   2),
   ('stc',      1),
   ('nop',      1),
   ('dad sp',   1),
   ('lda',      3),
   ('dcx sp',   1),
   ('inr a',    1),
   ('dcr a',    1),
   ('mvi a,',   2),
   ('cmc',      1),
   ('mov b, b', 1),
   ('mov b, c', 1),
   ('mov b, d', 1),
   ('mov b, e', 1),
   ('mov b, h', 1),
   ('mov b, l', 1),
   ('mov b, m', 1),
   ('mov b, a', 1),
   ('mov c, b', 1),
   ('mov c, c', 1),
   ('mov c, d', 1),
   ('mov c, e', 1),
   ('mov c, h', 1),
   ('mov c, l', 1),
   ('mov c, m', 1),
   ('mov c, a', 1),
   ('mov d, b', 1),
   ('mov d, c', 1),
   ('mov d, d', 1),
   ('mov d, e', 1),
   ('mov d, h', 1),
   ('mov d, l', 1),
   ('mov d, m', 1),
   ('mov d, a', 1),
   ('mov e, b', 1),
   ('mov e, c', 1),
   ('mov e, d', 1),
   ('mov e, e', 1),
   ('mov e, h', 1),
   ('mov e, l', 1),
   ('mov e, m', 1),
   ('mov e, a', 1),
   ('mov h, b', 1),
   ('mov h, c', 1),
   ('mov h, d', 1),
   ('mov h, e', 1),
   ('mov h, h', 1),
   ('mov h, l', 1),
   ('mov h, m', 1),
   ('mov h, a', 1),
   ('mov l, b', 1),
   ('mov l, c', 1),
   ('mov l, d', 1),
   ('mov l, e', 1),
   ('mov l, h', 1),
   ('mov l, l', 1),
   ('mov l, m', 1),
   ('mov l, a', 1),
   ('mov m, b', 1),
   ('mov m, c', 1),
   ('mov m, d', 1),
   ('mov m, e', 1),
   ('mov m, h', 1),
   ('mov m, l', 1),
   ('hlt',      1),
   ('mov m, a', 1),
   ('mov a, b', 1),
   ('mov a, c', 1),
   ('mov a, d', 1),
   ('mov a, e', 1),
   ('mov a, h', 1),
   ('mov a, l', 1),
   ('mov a, m', 1),
   ('mov a, a', 1),
   ('add b',    1),
   ('add c',    1),
   ('add d',    1),
   ('add e',    1),
   ('add h',    1),
   ('add l',    1),
   ('add m',    1),
   ('add a',    1),
   ('adc b',    1),
   ('adc c',    1),
   ('adc d',    1),
   ('adc e',    1),
   ('adc h',    1),
   ('adc l',    1),
   ('adc m',    1),
   ('adc a',    1),
   ('sub b',    1),
   ('sub c',    1),
   ('sub d',    1),
   ('sub e',    1),
   ('sub h',    1),
   ('sub l',    1),
   ('sub m',    1),
   ('sub a',    1),
   ('sbb b',    1),
   ('sbb c',    1),
   ('sbb d',    1),
   ('sbb e',    1),
   ('sbb h',    1),
   ('sbb l',    1),
   ('sbb m',    1),
   ('sbb a',    1),
   ('ana b',    1),
   ('ana c',    1),
   ('ana d',    1),
   ('ana e',    1),
   ('ana h',    1),
   ('ana l',    1),
   ('ana m',    1),
   ('ana a',    1),
   ('xra b',    1),
   ('xra c',    1),
   ('xra d',    1),
   ('xra e',    1),
   ('xra h',    1),
   ('xra l',    1),
   ('xra m',    1),
   ('xra a',    1),
   ('ora b',    1),
   ('ora c',    1),
   ('ora d',    1),
   ('ora e',    1),
   ('ora h',    1),
   ('ora l',    1),
   ('ora m',    1),
   ('ora a',    1),
   ('cmp b',    1),
   ('cmp c',    1),
   ('cmp d',    1),
   ('cmp e',    1),
   ('cmp h',    1),
   ('cmp l',    1),
   ('cmp m',    1),
   ('cmp a',    1),
   ('rnz',      1),
   ('pop b',    1),
   ('jnz',      3),
   ('jmp',      3),
   ('cnz',      3),
   ('push b',   1),
   ('adi',      2),
   ('rst 0',    1),
   ('rz',       1),
   ('ret',      1),
   ('jz',       3),
   ('jmp',      3),
   ('cz',       3),
   ('call',     3),
   ('aci',      2),
   ('rst 1',    1),
   ('rnc',      1),
   ('pop d',    1),
   ('jnc',      3),
   ('out',      2),
   ('cnc',      3),
   ('push d',   1),
   ('sui',      2),
   ('rst 2',    1),
   ('rc',       1),
   ('ret',      1),
   ('jc',       3),
   ('in',       2),
   ('cc',       3),
   ('call',     3),
   ('sbi',      2),
   ('rst 3',    1),
   ('rpo',      1),
   ('pop h',    1),
   ('jpo',      3),
   ('xthl',     1),
   ('cpo',      3),
   ('push h',   1),
   ('ani',      2),
   ('rst 4',    1),
   ('rpe',      1),
   ('pchl',     1),
   ('jpe',      3),
   ('xchg',     1),
   ('cpe',      3),
   ('call',     3),
   ('xri',      2),
   ('rst 5',    1),
   ('rp',       1),
   ('pop psw',  1),
   ('jp',       3),
   ('di',       1),
   ('cp',       3),
   ('push psw', 1),
   ('ori',      2),
   ('rst 6',    1),
   ('rm',       1),
   ('sphl',     1),
   ('jm',       3),
   ('ei',       1),
   ('cm',       3),
   ('call',     3),
   ('cpi',      2),
   ('rst 7',    1)
]

program = b''


def disassemble():
    address = 0
    mnemonic = ''
    program_length = len(program)

    while address < program_length:
        opcode = program[address]
        instruction = instructions[opcode]
        mnemonic = instruction[MNEMONIC]
        size = instruction[SIZE]

        # If there's a data section at the end of a program, some code may be
        # disassembled as an instruction requiring nonexistent operands referenced
        # past the end of the program, which causes an ouf of bounds situation. We
        # silently end the disassembly rather than aborting with an error because
        # it's a common case and reporting an error may be misleading.
        if address + size > program_length:
            break

        # Opcode argument bytes dumped to the output.
        arg1 = arg2 = '  '
        # Least (lsb) and most (most) significant byte of a 16-bit address operand.
        lsb = msb = ''

        # After the opcode we dump the arguments in the same little-endian byte
        # order they're in the program. But we print msb of an address first (if
        # size > 3 we have a 16-bit addres) as it's easier to read 16-bit hex
        # numbers.
        if size > 1:
            if size == 3:
                arg2 = f'{program[address + 2]:02x}'
                msb = f'{program[address + 2]:02x}'
            arg1 = f'{program[address + 1]:02x}'
            lsb = f'{program[address + 1]:02x}h'
        output = f'{address:04x} {opcode:02x} {arg1} {arg2}\t\t{mnemonic} {msb}{lsb}'
        print(output)

        address += size


def main():
    global program
    dis80_description = f'Intel 8080 disassembler / Suite8080'

    parser = argparse.ArgumentParser(description=dis80_description)
    parser.add_argument('filename', type=str, help=' A file name')
    args = parser.parse_args()
    filename = args.filename

    with open(filename, 'rb') as file:
        program = file.read()
        disassemble()


if __name__ == '__main__':
    main()