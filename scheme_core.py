"""This file implements the core of the Scheme interpreter.

Implements internal data types, special forms, and scheme_eval().

Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48
"""


class SchemeError(Exception):
    """Exception indicating an error in a Scheme program."""


# Scheme representations

class SchemeExpr:
    """Base class for all non-primitive Scheme expressions."""

    @staticmethod
    def is_procedure():
        """Return whether this represents a Scheme procedure.

        Returns true for both primitive and user-defined Scheme
        procedures.
        """
        return False

    @staticmethod
    def is_special_form():
        """Return true if this represents a special form."""
        return False

    # add whatever you need here


def scheme_to_string(obj):
    """Convert a Scheme object to a string."""
    if isinstance(obj, bool):
        return '#t' if obj else '#f'
    return str(obj)


def is_scheme_true(val):
    """Return whether val is a true Scheme value.

    All values in Scheme are true except False.
    """
    return val is not False


def is_scheme_false(val):
    """Return whether val is a false Scheme value.

    Only False is false in Scheme.
    """
    return val is False


def is_scheme_string(expr):
    """Return whether expr represents a Scheme string.

    Scheme strings are Python strings that begin and end with quotes.
    """
    return isinstance(expr, str) and expr.startswith('"')


def is_scheme_symbol(expr):
    """Return wether expr represents a Scheme symbol.

    Any Python string that is not quoted is a symbol.
    """
    return isinstance(expr, str) and not is_scheme_string(expr)


def is_scheme_list(expr):
    """Return whether expr is a well-formed list. Assumes no cycles."""
    return expr is Nil or (isinstance(expr, Pair) and expr.is_list())


def is_scheme_procedure(expr):
    """Return whether expr is a Scheme procedure.

    Returns true for both primitive and user-defined Scheme
    procedures.
    """
    return isinstance(expr, SchemeExpr) and expr.is_procedure()


def is_special_form(expr):
    """Return true if expr is a special form."""
    return isinstance(expr, SchemeExpr) and expr.is_special_form()


def is_scheme_value(expr):
    """Return true if expr is a Scheme value that evaluates to itself."""
    return (isinstance(expr, (int, float, bool)) or
            expr is Okay or
            is_scheme_string(expr) or
            is_special_form(expr) or
            is_scheme_procedure(expr))


# Evaluation

def scheme_eval(expr, env):
    """Evaluate the expression in the given environment.

    expr must represent a Scheme expression. Returns the result of
    evaluation.
    """
    if is_scheme_value(expr):
        return expr  # values evaluate to themselves
    return None  # replace with your solution


# Environments

def create_environment():
    """Return a new environment consisting of a single empty frame.

    >>> env = create_environment()
    >>> env['x'] = 3
    >>> env['lst'] = Pair(4, Nil)
    >>> subenv1 = env.extend()
    >>> subenv1['x']
    3
    >>> env['lst'] is subenv1['lst']
    True
    >>> subenv1['lst'] = Pair(4, Nil)
    >>> env['lst'] is subenv1['lst']
    False
    >>> subenv1['y'] = 5
    >>> 'y' in env, 'y' in subenv1
    (False, True)
    >>> subenv2 = env.extend()
    >>> 'y' in env, 'y' in subenv1, 'y' in subenv2
    (False, True, False)
    >>> env['lst'] is subenv2['lst']
    True
    >>> subenv2['y'] = 6
    >>> subenv1['y'], subenv2['y']
    (5, 6)
    >>> subenv3 = subenv2.extend()
    >>> subenv3['x'], subenv3['y']
    (3, 6)
    >>> subenv3['z'] = 7
    >>> 'z' in env, 'z' in subenv1, 'z' in subenv2, 'z' in subenv3
    (False, False, False, True)
    >>> subenv3['y'] = 8
    >>> subenv1['y'], subenv2['y'], subenv3['y']
    (5, 6, 8)
    >>> subenv3['y'] = 9
    >>> subenv1['y'], subenv2['y'], subenv3['y']
    (5, 6, 9)
    """
    return None  # replace with your solution


# Special Forms

def add_special_forms(env):
    """Add the set of special forms to the given environment."""
    pass  # fill in with your solution


# Pairs and Scheme lists

def python_to_scheme_list(plist):
    """Construct a Scheme list from a Python sequence."""
    slist = Nil
    for i in range(len(plist)):
        slist = Pair(plist[-1 - i], slist)
    return slist


class Pair(SchemeExpr):
    """Represents a Scheme pair.

    A Pair has two instance attributes: first and second. For a Pair
    to be a well-formed list, second is either a well-formed list or
    Nil. Some methods only apply to well-formed lists.

    >>> s = Pair(1, Pair(2, Nil))
    >>> s
    Pair(1, Pair(2, Nil))
    >>> print(s)
    (1 2)
    >>> len(s)
    2
    >>> s.second.first
    2
    >>> for item in s: print(item)
    1
    2
    >>> print(s.map(lambda x: x+4))
    (5 6)
    """

    def __init__(self, first, second):
        """Initialize this pair with the given first and second."""
        self.first = first
        self.second = second

    def __repr__(self):
        """Return a canonical representation of this pair."""
        return 'Pair({0}, {1})'.format(repr(self.first),
                                       repr(self.second))

    def __str__(self):
        """Return a string representation of this pair."""
        result = '(' + scheme_to_string(self.first)
        second = self.second
        while isinstance(second, Pair):
            result += ' ' + scheme_to_string(second.first)
            second = second.second
        if second is not Nil:
            result += ' . ' + scheme_to_string(second)
        return result + ')'

    def __len__(self):
        """Return the length of this list.

        Raises an exception of this is not a well-formed list.
        """
        result, second = 1, self.second
        while isinstance(second, Pair):
            result += 1
            second = second.second
        if second is not Nil:
            raise TypeError('length attempted on improper list')
        return result

    def __iter__(self):
        """Return an iterator over this list."""
        current = self
        while isinstance(current, Pair):
            yield current.first
            current = current.second
        if current is not Nil:
            yield current

    def __eq__(self, pair):
        """Return whether the given pair is equal to this one.

        Compares the contents of the two pairs.
        """
        if not isinstance(pair, Pair):
            return False
        return self.first == pair.first and self.second == pair.second

    def map(self, func):
        """Map the given function across the items in this list.

        Raises an exception of this is not a well-formed list. Returns
        a new list for the result; does not mutate this list.
        """
        mapped = func(self.first)
        if self.second is Nil or isinstance(self.second, Pair):
            return Pair(mapped, self.second.map(func))
        raise TypeError('ill-formed list')

    def is_list(self):
        """Return whether this is a well-formed list.

        Assumes no cycles.
        """
        pair = self
        while pair is not Nil:
            if not isinstance(pair, Pair):
                return False
            pair = pair.second
        return True


def singleton(class_):
    """Rebind the class name to an instance of it, hiding the class."""
    return class_()


@singleton  # Rebinds the name Nil to an instance of this class.
class Nil(SchemeExpr):
    """Represents the Scheme empty list.

    There is only one instance of this class, called Nil.
    """

    def __repr__(self):
        """Return a canonical representation of this object."""
        return 'Nil'

    def __str__(self):
        """Return a string representation of this object."""
        return '()'

    def __len__(self):
        """Return the length of this Scheme list."""
        return 0

    def __iter__(self):
        """Return an iterator over this Scheme list."""
        return self

    @staticmethod
    def __next__():
        """Return the next item in the underlying Scheme list."""
        raise StopIteration

    def map(self, _):
        """Map the given function across the items in this list."""
        return self


@singleton  # Rebinds the name Okay to an instance of this class.
class Okay(SchemeExpr):
    """Signifies an undefined value.

    There is only one instance of this class, called Okay.
    """

    def __repr__(self):
        """Return a canonical representation of this object."""
        return 'Okay'

    def __str__(self):
        """Return a string representation of this object."""
        return 'okay'
