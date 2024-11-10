"""This module implements a parser for Scheme expressions.

Pairs and lists are defined in scheme_core.py, as well as a
representation for an unspecified value. Other data types in Scheme
are represented by their corresponding type in Python:
    number:       int or float
    symbol:       string
    string:       quoted string
    boolean:      bool

Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48
"""

from buffer import Buffer, make_input_reader, make_line_reader
from scheme_tokens import Tokenizer, PUNCTUATORS
from scheme_core import Pair, Nil


# Scheme list parser

# Quotation markers
QUOTES = {"'":  'quote',
          '`':  'quasiquote',
          ',':  'unquote',
          ',@': 'unquote-splicing'}


def scheme_read(src):
    """Read the next expression from SRC, a Buffer of tokens.

    >>> lines = ['(+ 1 ', '(+ 23 4)) (']
    >>> src = Buffer(Tokenizer().tokenize_lines(lines))
    >>> print(scheme_read(src))
    (+ 1 (+ 23 4))
    >>> read_line("'hello")
    Pair('quote', Pair('hello', Nil))
    >>> print(read_line("(car '(1 2))"))
    (car (quote (1 2)))
    """
    if src.current() is None:
        raise EOFError
    val = src.pop()
    if val not in PUNCTUATORS:
        return val
    if val in QUOTES:
        pass  # fill in your solution here
    if val == '(':
        return read_tail(src)
    raise SyntaxError('unexpected token: {0}'.format(val))


def read_tail(src, item_count=0):
    """Return the remainder of a list in SRC.

    SRC must be positioned before an element or ). item_count is the
    number of items so far in the list.

    >>> read_tail(Buffer(Tokenizer().tokenize_lines([')'])))
    Nil
    >>> read_tail(Buffer(Tokenizer().tokenize_lines(['2 3)'])))
    Pair(2, Pair(3, Nil))
    >>> read_tail(Buffer(Tokenizer().tokenize_lines(['2 (3 4))'])))
    Pair(2, Pair(Pair(3, Pair(4, Nil)), Nil))
    >>> read_line('(1 . 2)')
    Pair(1, 2)
    >>> read_line('(1 2 . 3)')
    Pair(1, Pair(2, 3))
    >>> read_line('(1 . 2 3)')
    Traceback (most recent call last):
        ...
    SyntaxError: Expected one element after .
    >>> read_line('(. 2 3)')
    Traceback (most recent call last):
        ...
    SyntaxError: . must have at least one element before it
    >>> scheme_read(Buffer(Tokenizer().tokenize_lines(
    ...     ['(1', '2 .', "'(3 4))", '4']
    ... )))
    Pair(1, Pair(2, Pair('quote', Pair(Pair(3, Pair(4, Nil)), Nil))))
    >>> print(read_line("(car `(1 2 , x ,@ '(4)))"))
    (car (quasiquote (1 2 (unquote x) (unquote-splicing (quote (4))))))
    """
    try:
        if src.current() is None:
            raise SyntaxError('unexpected end of file')
        if src.current() == ')':
            src.pop()
            return Nil
        # fill in your solution here

        first = scheme_read(src)
        rest = read_tail(src, item_count + 1)
        return Pair(first, rest)
    except EOFError as exc:
        raise SyntaxError('unexpected end of file') from exc


# Convenience functions

def buffer_input(prompt='scm> '):
    """Return a Buffer instance containing interactive input."""
    tokenized = Tokenizer().tokenize_lines(make_input_reader(prompt))
    return Buffer(tokenized)


def buffer_lines(lines, prompt='scm> '):
    """Return a Buffer instance iterating through LINES."""
    tokenized = Tokenizer().tokenize_lines(
        make_line_reader(lines, prompt)
    )
    return Buffer(tokenized)


def read_line(line):
    """Read a single string LINE as a Scheme expression."""
    tokenized = Tokenizer().tokenize_lines([line])
    return scheme_read(Buffer(tokenized))


def main():
    """Run a read-print loop for Scheme expressions."""
    while True:
        try:
            src = buffer_input('read> ')
            while src.more_on_line:
                expression = scheme_read(src)
                print(expression)
        except (SyntaxError, ValueError) as err:
            print(type(err).__name__ + ':', err)
        except (KeyboardInterrupt, EOFError):  # <Control>-D, etc.
            break


if __name__ == '__main__':
    main()  # Run interactive loop
