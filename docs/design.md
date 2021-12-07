# Design notes

[Suite8080](https://github.com/pamoroso/suite8080) is a suite of Intel 8080 Assembly cross-development tools. See the `README.md` file in the source tree for an overview of what the system does and how to use it.

The initial implementation of Suite8080 closely follows the design of the corresponding tools developed in D language by Brian Robert Callahan and published in a [blog post series](https://briancallahan.net/blog/20210407.html).

Therefore, the features and limitations, the function and variable names, the data structures, and the source organization are similar to Brian's code except where Python features make the code more readable or idiomatic with little effort. I renamed some of the variables to make them less terse and more clear. In Suite8080 a few functions, unlike in Brian's code, return values to simplify testing.

As I gain confidence with the algorithms and the system, I will refactor to make the code more Pythonic and add new features.


## Source code organization

The `suite/suite8080` directory in the source tree defines a package and contains the source files of the command-line programs in the suite, one Python module for each tool. For example, `dis80.py` holds the code of the disassembler.

Replit Python projects require a `main.py` file at the root of the source tree. The Suite8080 `main.py` file is currently empty but I may add some code to demo the tools.


## Assembler

The `asm80` assembler examines one source line at a time and doesn't rely on recursive descent or traditional parsing algorithms. It doesn't have a specific lexical analysis subsystem either.


### Parser

Function `parse()` implements the parser. It scans a source line from right to left, looking for the symbols that separate successive syntactic elements. When it finds a symbol, the parser splits the line at the symbol to break the line into the syntactic element at the right of the symbol, and the rest of the line to process at the left.

For example, consider the syntax of a source line:

```
[label:] [mnemonic [operand1[, operand2]]] [; comment]
```

If the parser finds a semicolon, it splits the line at `;` to break the comment text from the rest of the line to parse. Next, it looks for the comma `,` separating the operands of the assembly instruction and splits there, thus breaking the second operand from the rest of the line to parse. And so on.

At each step, the parser calls `str.rpartition()` to scan for a symbol. The variables that unpack the values `str.rpartition()` returns have names that start with the name of the syntactic element looked for and end in `_l` (the remainder of the line at the left of the separator symbol), `_sep` (the separator symbol), and `_r` (the part of the line at the right of the symbol, i.e. the syntactic element).

Suppose the parser recognizes a comment. To scan for the `operand2` syntactic element, i.e. the second operand of the instruction, the parser then executes the statement:

```
operand2_l, operand2_sep, operand2_r = comment_l.rpartition(',')
```

The following step will start with the parser calling the `str.rpartition()` method on the `operand2_l` string, the remaining part of the line.

Function `parse()` updates the parsing state and output via a number of global variables, some of which hold the syntactic elements the scanning steps break from the line and produce as output (`label`, `mnemonic`, `operand1`, `operand2`, and `comment`). The strings in the variables are stripped of leading and trailing whitespace but are otherwise raw.

Once parsing completes, for each Assembly instruction a function with the same name accesses the global variables to further process the syntactic elements (e.g. for converting the text of a numeric literal to its value) and generate the code. These functions may access other global parsing state, such as the current address (`address`), line number (`lineno`), or source code pass (`source_pass`).

Function `parse()` supplies the syntactic elements also as return values, but they are currently used only for unit testing.

There are two exceptions to the scanning and splitting steps described above. The first is the `db` directive, which is parsed in the separate function `parse_db()`. The second is a special case inside function `parse()` to handle the `equ` directive.


## Future work

I'd like to add to Suite8080 an IDE with a GUI to provide a dashboard for running the various tools and viewing their output. The project's `main.py` file may hold the IDE's source or code to start the IDE.