# Getting started

The Suite8080 tools are command line programs. Follow these instructions for installing the tools and giving them a try.


## Installation

Install Suite8080 from PyPI with the command:

```bash
$ pip install suite8080
```


## Usage examples

### Linux

To run the assembler on Linux execute:

```bash
$ asm80 file.asm
```

where `file.asm` is an Intel 8080 Assembly source file. You can disassemble the resulting program with:

```bash
$ dis80 file.com
```

where `file.com` is an executable Intel 8080 program.


### Replit

To run the programs online on Replit visit the [Suite8080 REPL](https://replit.com/@PaoloAmoroso/suite8080) with a browser. You first have to set up the environment by forking the REPL, opening the Shell pane, and editing `~/.bashrc` to add `export PYTHONPATH=.:$PYTHONPATH`. Next, click `Run`. Finally, change to the `suite8080/suite8080` directory of the source tree.

To run the assembler execute:
```bash
$ python3 -m asm80 file.asm
```
where `file.asm` is an Intel 8080 Assembly source file.

You can disassemble a program with the command:

```bash
$ python3 -m dis80 file.com
```

where `file.com` is an executable Intel 8080 program.