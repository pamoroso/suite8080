# Using the Suite8080 tools

This document describes the usage and features of the programs comprising [Suite8080](https://github.com/pamoroso/suite8080), a suite of Intel 8080 cross-development tools. See the file [`README.md`](https://github.com/pamoroso/suite8080/blob/master/README.md) in the source tree for an overview of Suite8080 and installation instructions.


## Assembler

The `asm80` cross-assembler takes an Intel 8080 Assembly source file as input and generates an executable program in `.com` format. The assembler supports the full Intel 8080 instruction set but not the additional Intel 8085 or Z80 instructions.

If the assembler detects a syntax error, it prints an error message and exits.

### Usage

The `asm80` command line program has the following syntax:

```
asm80 [-h] [-o OUTFILE] [-v] filename
```

All arguments are optional except for the input file `filename`, which may be `-` to read from standard input:

* `-h`, `--help`: prints a help message and exits
* `-o`, `--outfile`: output file name, which defaults to `program.com` if the input file is `-` and `-o` is not supplied
* `-s`, `--symtab`: saves the symbol table to a file with the name of the input file and the `.sym` extension; the argument of `-o` and the `.sym` extension; or `program.sym` if the input file is `-` and `-o` is not supplied
* `-v`, `--verbose`: increases output verbosity

Although no input file name extension is enforced, and any is accepted or may be skipped altogether, I recommend `.asm` or `.a80` for Assembly source files and `.m4` for `m4` macro files.

The symbol table is saved in the `.sym` CP/M file format described in section 1.1 "SID Startup" on page 4 of the [*SID Users Guide*](http://www.cpm.z80.de/randyfiles/DRI/SID_ZSID.pdf) manual published by Digital Research.


### Assembly syntax

Except for macros, `asm80` recognizes most of the Assembly language of early Intel 8080 assemblers such as the ones by Intel, Digital Research, and Microsoft. However, source files written for those tools may need minor adaptations to work with `asm80`.

An Assembly source line has the syntax:

```
[label:] [mnemonic [operand1[, operand2]]] [; comment]
```

Although the 8080 mnemonics and directives accept from zero to two arguments, the `db` directive can take multiple arguments that may be numbers, strings, characters constants, and labels:

```
[label:] [db [argument1[, ..., argumentN]]] [; comment]
```

Two-letter abbreviations of register pairs are valid along with single-letter ones. In other words, the assembler, for example, accepts both `d` and `de` as the name of the register pair consisting of the `d` and `e` registers.

Character constants such as `'C'` or `'*'` can be immediate operands of Assembly instructions, as well as arguments of the `db` and `equ` directives.


### Numbers

Numbers may be decimal, hexadecimal, or octal. Hexadecimal numbers must end with `h` (for example `1dh`), octal ones with `q` (e.g. `31q`). Hexadecimal numbers beginning with the digits `a` to `f` must be prefixed with `0`, such as `0bh`.

Only integer numbers are accepted.


### Expressions

The arguments of the `equ` directive support expressions of the form:

```
$OPnumber
```

where `$` is the current address, `OP` an operator, `number` a number, and no spaces are allowed at either side of the operator. Valid operands are `+`, `-`, `*`, `/`, and `%` (modulus).

No other expressions are supported.


### Strings and character constants

Strings are sequences of characters enclosed within single `'` or double `"` quotes, such as `'This is a string'`. Strings delimited by single quotes may contain double quotes, and vice versa, as in `"I'm a string"` or `'This is a "string"'`.

Character constants, also known as ASCII constants, are strings containing only one character. For example, `'F'`, `"b"`, and `'*'` are character constants.


### Macros

Reading from standard input by supplying `-` as the input file makes it possible to use the Unix program `m4` as an Assembly macro processor, as demonstrated by the sample files with the `.m4` extension in the [`asm`](https://github.com/pamoroso/suite8080/tree/master/asm) directory of the source tree. However, `m4` macros are not compatible with the ones of traditional Intel 8080 macro assemblers.

For example, to assemble the `filename.m4` source file containing `m4` macros, run a pipe such as this on Linux:

```
$ cat filename.m4 | m4 | asm80 - -o filename.com
```

To view the Assembly source with the macros expanded execute:

```
$ cat filename.m4 | m4 | more
```


### Running Intel 8080 programs

The programs `asm80` assembles can run on actual Intel 8080 or Z80 machines, such as CP/M computers, or emulated ones. I use and recommend the following emulators:

* [z80pack](https://www.autometer.de/unix4fun/z80pack): the most versatile Z80 emulator with support for different machines and CP/M versions
* [ANSI CP/M Emulator and disk image tool](https://github.com/jhallen/cpm): it allows invoking from the Linux shell the emulator and passing as an argument a CP/M program to run, e.g. `cpm cpmprogram`
* [ASM80](https://www.asm80.com): works fully in the cloud, can run code that doesn't require a host operating system environment, and supports inspecting registers, memory, and program state
* [Intel 8080 CPU Emulator](https://www.tramm.li/i8080/emu8080.html) ([documentation](https://www.tramm.li/i8080/index.html)): an online Intel 8080 and CP/M emulator


### Limitations and issues

The Assembly language syntax is currently not fully case-insensitive, so it's better to use only lowercase labels, mnemonics, operands, and directives. Most notably, `equ` can't be written in all uppercase or a combination of lowercase and uppercase.

The assembler is in early development and, although it performs basic syntax checking, there's little or no input validation.

In addition, strings must not contain comma `,` characters. As a workaround, break the string into parts not containing commas and insert the comma code (2C hex) at the appropriate place. Here's an example of allocating the string `I, robot`:

```
robot:  db  'I', 2ch, ' robot'
```


## Disassembler

The `dis80` disassembler takes an executable Intel 8080 program file as input and prints to the standard output the sequence of instructions in symbolic form, along with an hexadecimal dump of the opcodes and operands. It supports the full Intel 8080 instruction set but not the additional Intel 8085 or Z80 instructions.


### Usage

The `dis80` command line program has the following syntax:

```
dis80 [-h] filename
```

where `filename` is a required Intel 8080 executable input file. The only command line option is `-h` or `--help`, which prints a help message and exits.


### Limitations and issues

The disassembler doesn't distinguish between instructions and data bytes, which may result in spurious instructions interleaved between valid ones. In addition, if some data bytes encode a transfer of program control that results in a jump beyond the last valid address, the disassembly may end prematurely without notice.