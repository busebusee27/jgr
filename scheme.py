"""This file implements the Scheme REPL and top-level driver.

Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48
"""

import sys
import argparse
import scheme_core
import scheme_reader
import scheme_primitives


def read_eval_print_loop(next_line, env, quiet=False,
                         interactive=False, cmd_line_args=None):
    """Read and evaluate input.

    Interpretation continues until an end of file or keyboard
    interrupt.
    """
    if cmd_line_args and cmd_line_args.load_files:
        for filename in cmd_line_args.load_files:
            scheme_load(filename, env)

    while True:
        try:
            read_eval_print_one(next_line(), env, quiet)
        except KeyboardInterrupt:  # <Control>-C
            if cmd_line_args is None:
                raise
            print('\nKeyboardInterrupt')
            if not interactive:
                return
        except EOFError:  # <Control>-D, etc.
            return
        except (ArithmeticError, NameError, RecursionError,
                SyntaxError, TypeError, ValueError,
                scheme_core.SchemeError) as err:
            if cmd_line_args and cmd_line_args.fail_on_error:
                raise
            print('Error:', err)


def read_eval_print_one(src, env, quiet):
    """Read and evaluate a single expression from src."""
    while src.more_on_line:
        expression = scheme_reader.scheme_read(src)
        result = scheme_core.scheme_eval(expression, env)
        handle_eval_result(result, expression, quiet)


def handle_eval_result(result, expression, quiet):
    """Print the result if not quiet."""
    assert result is not None, ('scheme_eval returned None: ' +
                                str(expression))
    if not quiet:
        print(scheme_core.scheme_to_string(result))


def scheme_load(filename, env, quiet=True):
    """Load a Scheme source file.."""
    with scheme_open(filename) as infile:
        lines = infile.readlines()
    args = (lines, None) if quiet else (lines,)

    try:
        read_eval_print_loop(lambda: scheme_reader.buffer_lines(*args),
                             env, quiet=quiet)
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt')
        return


def scheme_open(filename):
    """Open a Scheme file.

    If either FILENAME or FILENAME.scm is the name of a valid file,
    returns a Python file opened to it. Otherwise, raises an error.
    """
    try:
        return open(filename)
    except IOError as exc:
        if filename.endswith('.scm'):
            raise scheme_core.SchemeError(str(exc))
    try:
        return open(filename + '.scm')
    except IOError as exc:
        raise scheme_core.SchemeError(str(exc))


def main():
    """Run the interpreter with command-line options."""
    parser = argparse.ArgumentParser(description='Scheme interpreter.')
    parser.add_argument('filename', default=None, nargs='?',
                        help='Optional file to interpret. Omitting '
                        'this will take input from standard input.')
    parser.add_argument('-load', '--load-files', nargs='+',
                        metavar='FILE', default=[],
                        help='Files to load before interpreting '
                        'filename or standard input.')
    parser.add_argument('-e', '--fail-on-error', action='store_true',
                        help='Disable suppression of errors, causing '
                        'the interpreter to crash when an error '
                        'occurs.')
    args = parser.parse_args()
    next_line = scheme_reader.buffer_input
    interactive = True
    if args.filename is not None:
        try:
            input_file = open(args.filename)
            lines = input_file.readlines()

            def buffer_lines():
                """Produce input over lines."""
                return scheme_reader.buffer_lines(lines)

            next_line = buffer_lines
            interactive = False
        except IOError as err:
            print(err)
            sys.exit(1)
    read_eval_print_loop(next_line,
                         scheme_primitives.create_report_environment(),
                         interactive=interactive, cmd_line_args=args)
    print('Bye.')


if __name__ == '__main__':
    main()
