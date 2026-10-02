# Teri-Meri-Language
Teri-Meri-Language is a Roman-Urdu based programing language. It uses an the basic functionality to perform basic programs like printing out text, and performing basic maticulation in it .it is a small, Urdu-keyword programming language with a command-line interpreter and a PyQt6 desktop editor.


File-Extention
Like other programming languages they have their own programming language extenstin like python have (.py) c have (.c) extenstion just like that this language has (.urdu) extenstion

## Features

- Write programs using Urdu/Hinglish keywords.
- Use integer variables, arithmetic, comparisons, conditionals, and loops.
- Define and call simple functions with up to four parameters.
- Browse a project folder and open `.urdu` files in the IDE.
- View syntax highlighting, line numbers, and program output in the editor.

## Requirements

- GCC to build the interpreter.
- Python 3 and PyQt6 to run the desktop IDE.

## Build the Interpreter

From the project folder, compile the interpreter:

```sh
gcc main.c -o urdulang
```

Run a program from the same folder as the interpreter:

```sh
./urdulang example.urdu
```

The included example prints `30` and `100`.

## Start the IDE

Install PyQt6 in a virtual environment and launch the editor:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install PyQt6
python studio.py
```
## Language Basics

Comments begin with `#`. Variables hold integers and are assigned with `rakho`. Use `bol` to print a value or a basic arithmetic expression:

```urdu
# Assign values
rakho x = 10
rakho y = 20

# Print a value and a calculation
bol x
bol x + y
```

Arithmetic operators are `+`, `-`, `*`, and `/`. Comparisons are `>`, `<`, `>=`, `<=`, `==`, and `!=`.

Conditionals and loops use braces:

```urdu
rakho count = 1
agar count <= 3 {
	bol count
}

jab_tak count <= 3 {
	bol count
	rakho count = count + 1
}
```

Define a function with `kaam`, followed by its name and parameter names. Call it by writing its name and arguments:

```urdu
kaam jama a b {
	bol a + b
}

jama 10 20
```

## Current Limitations

The interpreter supports integer values and simple two-operand arithmetic; it does not currently support strings or floating-point values. Programs are read from `.urdu` files, and.
