"""Unit testing framework for the Scheme interpreter.

Usage: python3 scheme_test.py FILE

Interprets FILE as interactive Scheme source code, and compares each
line of printed output from the read-eval-print loop and from any
output functions to an expected output described in a comment. For
example,

(display (+ 2 3))
; expect 5

Differences between printed and expected outputs are printed with line
numbers.

Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48
"""

import io
import sys
import collections
from buffer import Buffer
from scheme import read_eval_print_loop
from scheme_primitives import create_report_environment
from scheme_tokens import Tokenizer


def summarize(output, expected_output):
    """Summarize results of running tests."""
    num_failed, num_expected = 0, len(expected_output)

    def failed(expected, actual, line):
        """Print error message and increment count of failed tests."""
        nonlocal num_failed
        num_failed += 1
        print('test failed at line', line)
        print('  expected', expected)
        print('   printed', actual)

    for (actual, (expected, line_number)) in zip(output, expected_output):
        if expected.startswith("Error"):
            if not actual.startswith("Error"):
                failed('an error indication', actual, line_number)
        elif actual != expected:
            failed(expected, actual, line_number)
    print('{0} tested; {1} failed.'.format(num_expected, num_failed))
    return num_failed


EXPECT_STRING = '; expect'


def make_test_reader(lines, stdout):
    """Return a reader for Scheme expressions and output.

    The resulting object keeps track of actual output from stdout,
    Scheme expressions from lines, expected output from lines, and
    line numbers.
    """
    reader = collections.namedtuple('TestReader',
                                    ('output', 'expected_output',
                                     'expressions', 'line_number'))
    last_out_len = 0
    output = []
    expected_output = []

    def iterate():
        """Iterate over expected test-case results."""
        nonlocal last_out_len
        for line in lines:
            line = line.rstrip('\n')
            reader.line_number += 1
            if line.lstrip().startswith(EXPECT_STRING):
                expected = line.split(EXPECT_STRING, 1)[1][1:].split(' ; ')
                for exp in expected:
                    expected_output.append((exp, reader.line_number))
                out_lines = stdout.getvalue().split('\n')
                if len(out_lines) > last_out_len:
                    output.extend(out_lines[-1-len(expected):-1])
                else:
                    output.extend([''] * len(expected))
                last_out_len = len(out_lines)
            yield line
        raise EOFError

    reader.output = output
    reader.expected_output = expected_output
    reader.line_number = 0
    reader.expressions = iterate()
    return reader


def run_tests(src_file):
    """Run a read-eval loop that runs the tests in src_file."""
    print('Running test {}...'.format(src_file))
    # Collect output to stdout and stderr
    sys.stderr = sys.stdout = io.StringIO()
    reader = None
    try:
        reader = make_test_reader(open(src_file).readlines(), sys.stdout)
        src = Buffer(Tokenizer().tokenize_lines(reader.expressions))

        def next_line():
            """Ensure that src has the current line ready."""
            src.current()
            return src

        read_eval_print_loop(next_line, create_report_environment())
    except BaseException:
        sys.stderr = sys.__stderr__
        if reader:
            print("Tests terminated due to unhandled exception "
                  "after line {0}:\n>>>".format(reader.line_number),
                  file=sys.stderr)
        raise
    finally:
        sys.stdout = sys.__stdout__   # Revert stdout
        sys.stderr = sys.__stderr__   # Revert stderr
    num_failed = summarize(reader.output, reader.expected_output)
    if num_failed:
        print('*** FAIL ***')
        sys.exit(1)
    else:
        print('*** PASS ***')


if __name__ == '__main__':
    for test in sys.argv[1:]:
        run_tests(test)
