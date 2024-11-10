"""The buffer module assists in iterating through lines and tokens.

Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48
"""

import math
import importlib


importlib.import_module('readline')  # for input history


class Buffer:
    """Provides a way of accessing a sequence of tokens across lines.

    The constructor takes an iterator, called "the source", that
    returns the next line of tokens as a list each time it is queried,
    or None to indicate the end of data.

    The Buffer in effect concatenates the sequences returned from its
    source and then supplies the items from them one at a time through
    its pop() method, calling the source for more sequences of items
    only when needed.

    In addition, Buffer provides a current method to look at the next
    item to be supplied, without sequencing past it.

    The __str__ method prints all tokens read so far, up to the end of
    the current line, and marks the current token with >>.

    >>> buf = Buffer(iter([['(', '+'], [15], [12, ')']]))
    >>> buf.pop()
    '('
    >>> buf.pop()
    '+'
    >>> buf.current()
    15
    >>> print(buf)
    1: ( +
    2:  >> 15
    >>> buf.pop()
    15
    >>> buf.current()
    12
    >>> buf.pop()
    12
    >>> print(buf)
    1: ( +
    2: 15
    3: 12 >> )
    >>> buf.pop()
    ')'
    >>> print(buf)
    1: ( +
    2: 15
    3: 12 ) >>
    >>> buf.pop()  # returns None
    """

    def __init__(self, source):
        """Initialize this Buffer with the give source iterable."""
        self.index = 0
        self.lines = []
        self.source = source
        self.current_line = ()
        self.current()

    def pop(self):
        """Remove the next item from self and return it.

        If self has exhausted its source, returns None.
        """
        current = self.current()
        self.index += 1
        return current

    @property
    def more_on_line(self):
        """Return whether more data remains on the current line."""
        return self.index < len(self.current_line)

    def current(self):
        """Return the current element, or None if none exists."""
        while not self.more_on_line:
            self.index = 0
            try:
                self.current_line = next(self.source)
                self.lines.append(self.current_line)
            except StopIteration:
                self.current_line = ()
                return None
        return self.current_line[self.index]

    def __str__(self):
        """Return recently read contents.

        The current element is marked with >>.
        """
        # Format string for right-justified line numbers
        count = len(self.lines)
        msg = '{0:>' + str(math.floor(math.log10(count)) + 1) + '}: '

        # Up to three previous lines and current line are included in
        # output
        result = ''
        for i in range(max(0, count - 4), count - 1):
            result += (msg.format(i + 1) +
                       ' '.join(map(str, self.lines[i])) +
                       '\n')
        result += msg.format(count)
        result += ' '.join(map(str, self.current_line[:self.index]))
        result += ' >> '
        result += ' '.join(map(str, self.current_line[self.index:]))
        return result.strip()


def make_input_reader(prompt):
    """Make an iterable over user input, with the given prompt."""
    while True:
        yield input(prompt)
        prompt = ' ' * len(prompt)


def make_line_reader(lines, prompt, comment=';'):
    """Make an iterable that prints lines after a prompt."""
    while lines:
        line = lines.pop(0).strip('\n')
        if (prompt is not None and line != '' and
                not line.lstrip().startswith(comment)):
            print(prompt + line)
            prompt = ' ' * len(prompt)
        yield line
    raise EOFError
