# Suite8080

[Suite8080](https://github.com/pamoroso/suite8080) is a suite of Intel 8080 Assembly cross-development tools written in Python.

![Disassembler output](https://raw.githubusercontent.com/pamoroso/suite8080/master/suite8080.jpg)

The suite comprises the following command-line programs:

* `ar80`: object library archiver (not available yet)
* `asm80`: assembler
* `dis80`: disassembler
* `ln80`: linker (not available yet)

This project is inspired by [a series of blog posts](https://briancallahan.net/blog/20210407.html) by Brian Robert Callahan on demystifying programs that create programs. See the `docs` directory in the source tree for some design and usage notes.

The executable files generated and processed by the tools are supposed to run on any Intel 8080 system such as CP/M computers, both actual devices and emulated ones.

Suite8080, which is developed with [Replit](https://replit.com), requires Python 3.6 or later and depends on Pytest for unit tests.


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




## Sample programs

The `asm` directory of the source tree contains sample Assembly programs, some of which run on CP/M and others on a bare Intel 8080 system with no host environment. You can use the Suite8080 tools to process these programs, for example assemble the sources with `asm80` and disassemble the executables with `dis80`.


## Status

Suite8080 is in early development and some of the planned tools and features are not available yet.


## Release history

See the [list of releases](https://github.com/pamoroso/suite8080/releases) for notes on the changes in each version.


## Author

[Paolo Amoroso](https://www.paoloamoroso.com/) developed Suite8080. Email: `info@paoloamoroso.com`


## License

This code is distributed under the MIT license, see the `LICENSE` file.
