# Suite8080 Design Notes

[Suite8080](https://github.com/pamoroso/suite8080) is a suite of Intel 8080 Assembly cross-development tools. See the `README.md` file in the source tree for an overview of what the system does and how to use it.

The initial implementation of Suite8080 closely follows the design of the corresponding tools developed in D language by Brian Robert Callahan and published in a [blog post series](https://briancallahan.net/blog/20210407.html).

Therefore, the features and limitations, the function and variable names, the data structures, and the source organization are similar to Brian's code except where Python features make the code more readable or idiomatic with little effort. I renamed some of the variables to make them less terse and more clear. In Suite8080 a few functions, unlike in Brian's code, return values to simplify testing.

As I gain confidence with the algorithms and the system, I will refactor to make the code more Pythonic and add new features.


## Source code organization

The `suite/suite8080` directory in the source tree defines a package and contains the source files of the command-line programs in the suite, one Python module for each tool. For example, `dis80.py` holds the code of the disassembler.

Replit Python projects require a `main.py` file at the root of the source tree. The Suite8080 `main.py` file is currently empty but I may add some code to demo the tools.


## Future work

I'd like to add to Suite8080 an IDE with a GUI to provide a dashboard for running the various tools and viewing their output. The project's `main.py` file may hold the IDE's source or code to start the IDE.