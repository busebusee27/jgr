"""
6.101 Lab:
LISP Interpreter Part 1
"""

#!/usr/bin/env python3

# import doctest # optional import
# import typing  # optional import
# import pprint  # optional import

import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    def remove_comments(text):
        # Split the text into lines and remove everything after ';' in each line
        lines = text.splitlines()
        cleaned_lines = [line.split(';', 1)[0] for line in lines]  # Remove anything after ';'
        return '\n'.join(cleaned_lines)  # Rejoin the cleaned lines

    source = remove_comments(source)
    source = source.replace('(', ' ( ').replace(')', ' ) ')
    return source.split()

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    def parse_exp(idx):
        if tokens[idx] != '(':
            return number_or_symbol(tokens[idx]), idx+1

        # We should have hit a ( now
        next_idx = idx+1
        sub_expr = []
        while tokens[next_idx] != ')':
            thing, next_idx = parse_exp(next_idx)
            sub_expr.append(thing)

        return sub_expr, next_idx+1
    
    parsed, _ = parse_exp(0)
    return parsed



######################
# Built-in Functions #
######################

def calc_sub(*args):
    if len(args) == 1:
        return -args[0]

    first_num, *rest_nums = args
    return first_num - scheme_builtins['+'](*rest_nums)

def calc_prod(*args):
    if len(args) == 1:
        return args[0]
    
    first_num, *rest_nums = args
    return first_num * scheme_builtins['*'](*rest_nums)

def calc_div(*args):
    if len(args) == 1:
        return args[0]
    
    first_num, *rest_nums = args
    return first_num / scheme_builtins['*'](*rest_nums)


scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    '*': calc_prod,
    '/': calc_div
}



##############
# Evaluation #
##############


def evaluate(tree):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if not isinstance(tree, list):
        if isinstance(tree, str):
            if tree in scheme_builtins:
                return scheme_builtins[tree]
            else:
                raise SchemeNameError
        return tree
    
    # tree is a list.
    evaluated_subtree = list(map(evaluate, tree))
    func, args = evaluated_subtree[0], evaluated_subtree[1:]

    if not callable(func):
        raise SchemeEvaluationError
    
    return func(*args)


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    # import os
    # sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    # import schemerepl
    # schemerepl.SchemeREPL(sys.modules[__name__], use_frames=False, verbose=False).cmdloop()

    print(evaluate(['a', 1, 2]))