"""This file implements built-in Scheme procedures.

Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48
"""

import sys
import math
import operator
import scheme_core


_PRIMITIVES = []


def primitive(*names):
    """Return a decorator that creates a primitive procedure.

    The decorator creates primitive procedures from its argument for
    each name in names and adds it to the _PRIMITIVES list. See
    examples of using primitive() as a decorator below.
    """
    def decorate(func):
        """Create primitive procedures for names that call func."""
        for name in names:
            pass  # fill in with your solution
        return func

    return decorate


def add_primitives(env):
    """Add the primitive procedures to the given environment."""
    # Primitive procedures
    for procedure in _PRIMITIVES:
        pass  # fill in with your solution


def check_type(val, predicate, index, expected, name):
    """Check the type of a value with the given predicate.

    Raises a TypeError if not PREDICATE(VAL) using "argument INDEX of
    NAME" to describe the offending value.
    """
    if not predicate(val):
        msg = 'argument {0} of {1} has wrong type {2} (expected {3})'
        raise TypeError(msg.format(index, name, type(val).__name__,
                                   expected))
    return val


# Environment-creating functions

def create_report_environment():
    """Create a single-frame environment with built-in names."""
    global_env = create_null_environment()
    add_primitives(global_env)
    return global_env


def create_null_environment():
    """Create a single-frame environment with built-in special forms.

    The resulting environment does not include primitive procedures.
    """
    global_env = scheme_core.create_environment()
    scheme_core.add_special_forms(global_env)
    return global_env


def _check_version(version, proc):
    """Check that the given version number is 5."""
    if version != 5:
        msg = 'argument to {0} must be 5'
        raise scheme_core.SchemeError(msg.format(proc))


@primitive('scheme-report-environment')
def scheme_report_environment(version):
    """Construct an environment with built-in names."""
    _check_version(version, 'scheme-report-environment')
    return create_report_environment()


@primitive('null-environment')
def scheme_null_environment(version):
    """Construct an environment with just built-in special forms."""
    _check_version(version, 'null-environment')
    return create_null_environment()


# Basic predicates

@primitive('boolean?')
def scheme_booleanp(val):
    """Return whether or not the given value is a boolean."""
    return val is True or val is False


@primitive('not')
def scheme_not(val):
    """Negate the given value."""
    return not scheme_core.is_scheme_true(val)


@primitive('eqv?', 'eq?')
def scheme_eqp(val1, val2):
    """Determine if val1 and val2 are the same Scheme object.

    Does not compare the contents of strings or pairs.
    """
    return (val1 is val2
            if (scheme_pairp(val1) or scheme_stringp(val1))
            else val1 == val2)


@primitive('equal?')
def scheme_equalp(val1, val2):
    """Determine if val1 and val2 are equivalent Scheme objects.

    Recursively compares the contents of strings or pairs.
    """
    return val1 == val2


@primitive('pair?')
def scheme_pairp(val):
    """Return whether or not the given value is a pair."""
    return isinstance(val, scheme_core.Pair)


@primitive('null?')
def scheme_nullp(val):
    """Return whether or not the given value is the empty list."""
    return val is scheme_core.Nil


@primitive('list?')
def scheme_listp(val):
    """Return whether val is a well-formed list. Assumes no cycles."""
    return scheme_core.is_scheme_list(val)


# Pair/list operations

@primitive('length')
def scheme_length(val):
    """Return the length of the given list.

    Raises an exception if val is not a well-formed list.
    """
    check_type(val, scheme_listp, 0, 'List', 'length')
    return len(val)


@primitive('cons')
def scheme_cons(first, second):
    """Construct a pair from the given values."""
    return scheme_core.Pair(first, second)


@primitive('car')
def scheme_car(val):
    """Return the first element of a pair.

    Raises an exception if val is not a pair.
    """
    check_type(val, scheme_pairp, 0, 'Pair', 'car')
    return val.first


@primitive('cdr')
def scheme_cdr(val):
    """Return the second element of a pair.

    Raises an exception if val is not a pair.
    """
    check_type(val, scheme_pairp, 0, 'Pair', 'cdr')
    return val.second


@primitive('list')
def scheme_list(*vals):
    """Construct a list from the given values."""
    result = scheme_core.Nil
    for i in range(len(vals)-1, -1, -1):
        result = scheme_core.Pair(vals[i], result)
    return result


@primitive('append')
def scheme_append(*vals):
    """Append the given lists. The last value need not be a list."""
    if not vals:
        return scheme_core.Nil
    result = vals[-1]
    for i in range(len(vals) - 2, -1, -1):
        val = vals[i]
        if val is not scheme_core.Nil:
            check_type(val, scheme_listp, i, 'List', 'append')
            new_result = pair = scheme_core.Pair(val.first, result)
            val = val.second
            while scheme_pairp(val):
                pair.second = scheme_core.Pair(val.first, result)
                pair = pair.second
                val = val.second
            result = new_result
    return result


# Type predicates

@primitive('string?')
def scheme_stringp(val):
    """Return whether or not the given value is a string."""
    return scheme_core.is_scheme_string(val)


@primitive('symbol?')
def scheme_symbolp(val):
    """Return whether or not the given value is a symbol."""
    return scheme_core.is_scheme_symbol(val)


def _is_int(val):
    """Return whether or not the given value is an integer."""
    return isinstance(val, int) and not scheme_booleanp(val)


@primitive('number?')
def scheme_numberp(val):
    """Return whether or not the given value is a number."""
    return _is_int(val) or isinstance(val, float)


@primitive('integer?')
def scheme_integerp(val):
    """Return whether or not the given value is integral."""
    return _is_int(val) or (isinstance(val, float) and
                            round(val) == val)


@primitive('procedure?')
def scheme_procedurep(val):
    """Return whether or not the given value is a procedure."""
    return scheme_core.is_scheme_procedure(val)


# Arithmetic operations

def _check_nums(*vals):
    """Check that all arguments in VALS are numbers."""
    for i, val in enumerate(vals):
        if not scheme_numberp(val):
            msg = 'operand {0} ({1}) is not a number'
            msg = msg.format(i, scheme_core.scheme_to_string(val))
            raise scheme_core.SchemeError(msg)


def _convert_integral(val):
    """Convert the given value to an int if possible."""
    return round(val) if round(val) == val else val


@primitive('+')
def plus(*args):
    """Return the sum of the arguments, seeded with 0.

    Raises an exception if an argument is not numerical.
    """
    _check_nums(*args)
    return _convert_integral(0 + sum(args))


# define - and * according to the Scheme specification
# define / to produce a float rather than a rational, but
#   otherwise match the Scheme specification
# implement all three forms of - and / in the Scheme spec
# convert the result to an int if it is integral, using the
#   _convert_integral() function above


@primitive('quotient')
def scheme_quo(val0, val1):
    """Perform integral division on the arguments.

    Raises an exception if an argument is not numerical or if val1 is
    0.
    """
    try:
        _check_nums(val0, val1)
        return operator.floordiv(val0, val1)
    except ZeroDivisionError as err:
        raise scheme_core.SchemeError(err)


def _modulo(val0, val1):
    """Perform a Python mod operation on the arguments.

    Raises an exception if an argument is not numerical or if val1 is
    0.
    """
    try:
        _check_nums(val0, val1)
        return operator.mod(val0, val1)
    except ZeroDivisionError as err:
        raise scheme_core.SchemeError(err)


@primitive('modulo')
def scheme_modulo(val0, val1):
    """Perform a mod operation on the arguments, with sign of val1.

    Raises an exception if an argument is not numerical or if val1 is
    0.
    """
    return _modulo(val0, val1)


@primitive('remainder')
def scheme_remainder(val0, val1):
    """Perform a mod operation on the arguments, with sign of val0.

    Raises an exception if an argument is not numerical or if val1 is
    0.
    """
    result = _modulo(val0, val1)
    if math.copysign(1, val0) != math.copysign(1, val1):
        result -= val1
    return result


@primitive('floor')
def scheme_floor(val):
    """Round the given value down to an integer.

    Raises an exception if an argument is not numerical.
    """
    _check_nums(val)
    return math.floor(val)


@primitive('ceiling')
def scheme_ceiling(val):
    """Round the given value up to an integer.

    Raises an exception if an argument is not numerical.
    """
    _check_nums(val)
    return math.ceil(val)


# Numerical comparisons and predicates

@primitive('=')
def scheme_eq(arg0, arg1, *args):
    """Determine if the given values are numerically equal.

    Raises an exception if an argument is not numerical.
    """
    _check_nums(arg0, arg1, *args)
    args = (arg1,) + args
    for arg in args:
        if arg0 != arg:
            return False
    return True


# define <, <=, >, and >= as well


# Numerical predicates

@primitive('even?')
def scheme_evenp(val):
    """Return true if val is numerically even.

    Raises an exception if an argument is not numerical.
    """
    _check_nums(val)
    return val % 2 == 0


@primitive('odd?')
def scheme_oddp(val):
    """Return true if val is numerically odd.

    Raises an exception if an argument is not numerical.
    """
    _check_nums(val)
    return val % 2 == 1


@primitive('zero?')
def scheme_zerop(val):
    """Return true if val is numerically zero.

    Raises an exception if an argument is not numerical.
    """
    _check_nums(val)
    return val == 0


@primitive('positive?')
def scheme_positivep(val):
    """Return true if val is numerically positive.

    Raises an exception if an argument is not numerical.
    """
    _check_nums(val)
    return val > 0


@primitive('negative?')
def scheme_negativep(val):
    """Return true if val is numerically negative.

    Raises an exception if an argument is not numerical.
    """
    _check_nums(val)
    return val < 0


# Eval and apply

# define an R5RS-compliant eval
# it should take an expression and an environment and call
#   scheme_eval() on them
# example: (eval 3 (scheme-report-environment 5))
#          should result in 3
# example: (eval '(+ 1 2) (scheme-report-environment 5))
#          should result in 3


# define an R5RS-compliant apply
# it should take in a procedure and one or more arguments,
#   where the last argument must be a list
# example: (apply + (list 1 2 3)) should result in 6
# example: (apply + 1 2 (list 3)) should result in 6


# Other operations

@primitive('display')
def scheme_display(val):
    """Display the given value to standard out."""
    if scheme_stringp(val):
        val = val[1: -1]
    print(scheme_core.scheme_to_string(val), end='', flush=True)
    return scheme_core.Okay


@primitive('newline')
def scheme_newline():
    """Write a newline on standard out."""
    print()
    sys.stdout.flush()
    return scheme_core.Okay
