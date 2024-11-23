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
    if len(args) == 0:
        return 1
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

class Frame:
    def __init__(self, bindings={}, parent = None):
        self.bindings = bindings.copy()
        self.parent = parent

    def __contains__(self, item):
        if item in self.bindings:
            return True
        if self.parent is not None and item in self.parent:
            return True
        return False

    def __getitem__(self, item):
        if item in self.bindings:
            return self.bindings[item]
        if self.parent is not None:
            return self.parent[item]
        raise SchemeError('here')
    
    def __setitem__(self, item, val):
        self.bindings[item] = val


class Lambda:
    def __init__(self, body, params, frame):
        self.body = body
        self.params = params
        self.frame = frame

    def __call__(self, *args):
        if len(self.params) != len(args):
            raise SchemeEvaluationError(f'Expected {len(self.params)} arguments, but got {len(args)}')

        args_to_pass = list(map(lambda x: evaluate(x, self.frame), args))
        new_frame = Frame(parent=self.frame)

        for param, arg in zip(self.params, args_to_pass):
            new_frame[param] = arg

        return evaluate(self.body, new_frame)


def make_initial_frame():
    global_frame = Frame(bindings=scheme_builtins.copy())
    empty_frame = Frame(parent=global_frame)
    return empty_frame

def evaluate(tree, frame=make_initial_frame()):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if not isinstance(tree, list):
        if isinstance(tree, str):
            if tree in frame:
                return frame[tree]
            else:
                raise SchemeNameError(f'Name `{tree}` not found')
        return tree
    
    # tree is a list.
    if tree[0] == 'define':
        if isinstance(tree[1], str):
            var_name = tree[1]
            var_val = evaluate(tree[2], frame)
            frame[var_name] = var_val
            return frame[var_name]
        else:
            func_definition = tree[1]
            func_body = tree[2]
            func_name = func_definition[0]
            if len(func_definition) == 1: # no params
                func_params = []
            else:
                func_params = func_definition[1:]
            
            frame[func_name] = Lambda(func_body, func_params, frame)
            return frame[func_name]

    elif tree[0] == 'lambda':
        try:
            params = tree[1]
            body = tree[2]
            return Lambda(body, params, frame)
        except:
            raise SchemeEvaluationError('Incorrectly defined function')

    else:
        evaluated_subtree = list(map(lambda x: evaluate(x, frame), tree))
        func, args = evaluated_subtree[0], evaluated_subtree[1:]

        if not callable(func):
            raise SchemeEvaluationError
        
        return func(*args)


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    import os
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl
    schemerepl.SchemeREPL(sys.modules[__name__], use_frames=False, verbose=False).cmdloop()