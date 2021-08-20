# Suite8080

Suite8080 is a suite of Intel 8080 Assembly cross-development tools written in Python. It comprises the following command-line programs:

* `dis80`: a disassembler
* `asm80`: an assembler
* `ln80`: a linker
* `ar80`: an object library archiver

This hobby programming project is inspired by [a series of blog posts](https://briancallahan.net/blog/20210407.html) by Brian Robert Callahan on demystifying programs that create programs.

The executable files generated and processed by the tools are supposed to run on any Intel 8080 system such as CP/M-80 computers, both actual devices and emulated ones.

Suite8080, which was developed with [Replit](https://replit.com), requires Python 3.6 or later and has no other dependencies.

See the document `design.md` in the source tree for some design notes.


## Installation

It will eventually be possible to install Suite8080 from PyPi. In the meantime, download the source code from the [project's site](https://github.com/pamoroso/suite8080) and expand it into a directory.


## Usage

### Running on Replit

To run the programs online on Replit visit the [Suite8080 REPL](https://replit.com/@PaoloAmoroso/suite8080) with a browser, open the Shell pane and edit `~/.bashrc` to add `export PYTHONPATH=.:$PYTHONPATH`. Next, click `Run`. Finally, in the Shell pane change to the `suite8080` directory and execute the following commands to run the disassembler:

```bash
$ export PYTHONPATH=.:$PYTHONPATH
$ python3 -m dis80 file.com
```

where `file.com` is an executable Intel 8080 program.


### Running elsewhere

Change to the `suite8080` directory in the source tree and execute the following command to run the disassembler:

```bash
$ python3 -m dis80 file.com
```

where `file.com` is an executable Intel 8080 program.


## Author

[Paolo Amoroso](https://www.paoloamoroso.com/) developed Suite8080. Email: `info@paoloamoroso.com`


## License

This code is distributed under the MIT license, see the `LICENSE` file.
