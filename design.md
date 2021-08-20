# Suite8080 Design Notes

[Suite8080](https://github.com/pamoroso/suite8080) is a suite of Intel 8080 Assembly cross-development tools. See the `README.md` file in the source tree for an overview of what the system does and how to use it.

The initial implementation of Suite8080 closely follows the design of the corresponding tools developed in D language by Brian Robert Callahan and published in a [blog post series](https://briancallahan.net/blog/20210407.html).

Therefore, the features and limitations, the function and variable names, the data structures, and the source organization are similar to Brian's code except where Python features make the code more readable or idiomatic with little effort. As I gain confidence with the algorithms and the system, I will refactor to make the code more Pythonic and add new features.


## Source code organization

The `suite8080` directory in the source tree contains the source files of the command-line programs in the suite, one Python module for each tool. For example, `dis80.py` holds the code of the disassembler.

Replit Python projects require a `main.py` file at the root of the source tree. The Suite8080 file doesn't currently do much other than ensuring the other modules are evaluated.


## Future work

I'd like to add to Suite8080 an IDE with a GUI that will provide a dashboard for running the various tools and viewing their output. The project's `main.py` file may hold the IDE's source or code to start the IDE.