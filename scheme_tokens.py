"""Lexer for Scheme.

This module provides a Tokenizer class with tokenize_line and
tokenize_lines methods for converting (iterators producing) strings
into (iterators producing) lists of tokens. A token may be:

  * A number (represented as an int, float, complex, or Fraction)
  * A boolean (represented as a bool)
  * A character (represented as a string)
  * A symbol (represented as a string)
  * A string (represented as a quoted string)
  * A punctuator, including parentheses, dots, and single quotes

Author: Amir Kamil
Small portions of code were derived from the Scheme interpreter
project in the Composing Programs text by John DeNero.

Project UID 2d6261568f83a98aa474c0a2b04179ce000b9a48
"""

import re
import sys
import cmath
import itertools
import fractions


_WHITESPACE = set(' \t\n\r')
PUNCTUATORS = set("()'`,.") | {',@', '#('}
DELIMITERS = _WHITESPACE | {'(', ')', '"', ';'}

# Simple tokens
STRING_CHARS = r'(\\\\|\\"|[^\\])'
RAW_STRING = re.compile(fr'"{STRING_CHARS}*?"')
STRING_START = re.compile(fr'"{STRING_CHARS}*\n')
STRING_END = re.compile(fr'{STRING_CHARS}*?"')
STRING_ESCAPE = re.compile(r'\\(.)', flags=re.DOTALL)
BOOLEAN = re.compile(r'#[tTfF]')
CHARACTER = re.compile(r'#\\[sS][pP][aA][cC][eE]|'
                       r'#\\[nN][eE][wW][lL][iI][nN][eE]|'
                       r'#\\.', flags=re.DOTALL)
INITIAL = r'a-zA-Z!\$%&\*/:<=>\?\^_~'
SUBSEQUENT = INITIAL + r'0-9\+\-\.@'
IDENTIFIER = re.compile(fr'[{INITIAL}][{SUBSEQUENT}]*|\+|\-|\.\.\.')
PUNCTUATOR = re.compile(r"#\(|,@|[()'`,.]")
COMMENT = re.compile(r';.*')


# Numbers
EXACTNESS = r'(#[eEiI])'
PREFIX_2 = fr'(#[bB]{EXACTNESS}?|{EXACTNESS}#[bB])'
PREFIX_8 = fr'(#[oO]{EXACTNESS}?|{EXACTNESS}#[oO])'
PREFIX_10 = fr'({EXACTNESS}#[dD]|(#[dD])?{EXACTNESS}?)'
PREFIX_16 = fr'(#[xX]{EXACTNESS}?|{EXACTNESS}#[xX])'
EXPONENT_MARKER = r'[eEsSfFdDlL]'
SIGN = r'[+-]?'
SUFFIX = fr'({EXPONENT_MARKER}{SIGN}[0-9]+)?'
UINTEGER_2 = r'[01]+#*'
UINTEGER_8 = r'[0-7]+#*'
UINTEGER_10 = r'[0-9]+#*'
UINTEGER_16 = r'[0-9a-fA-F]+#*'
DECIMAL_10 = (fr'(\.[0-9]+#*{SUFFIX}|'
              fr'[0-9]+\.[0-9]*#*{SUFFIX}|'
              fr'[0-9]+#+\.#*{SUFFIX}|'
              fr'{UINTEGER_10}{SUFFIX})')
UREAL_2 = fr'({UINTEGER_2}/{UINTEGER_2}|{UINTEGER_2})'
UREAL_8 = fr'({UINTEGER_8}/{UINTEGER_8}|{UINTEGER_8})'
UREAL_10 = (fr'({UINTEGER_10}/{UINTEGER_10}|{DECIMAL_10}|'
            fr'{UINTEGER_10})')
UREAL_16 = fr'({UINTEGER_16}/{UINTEGER_16}|{UINTEGER_16})'
REAL_2 = fr'{SIGN}{UREAL_2}'
REAL_8 = fr'{SIGN}{UREAL_8}'
REAL_10 = fr'{SIGN}{UREAL_10}'
REAL_16 = fr'{SIGN}{UREAL_16}'
COMPLEX_2 = (fr'({REAL_2}@{REAL_2}|{REAL_2}[+-]{UREAL_2}?i|'
             fr'[+-]{UREAL_2}?i|{REAL_2})')
COMPLEX_8 = (fr'({REAL_8}@{REAL_8}|{REAL_8}[+-]{UREAL_8}?i|'
             fr'[+-]{UREAL_8}?i|{REAL_8})')
COMPLEX_10 = (fr'({REAL_10}@{REAL_10}|{REAL_10}[+-]{UREAL_10}?i|'
              fr'[+-]{UREAL_10}?i|{REAL_10})')
COMPLEX_16 = (fr'({REAL_16}@{REAL_16}|{REAL_16}[+-]{UREAL_16}?i|'
              fr'[+-]{UREAL_16}?i|{REAL_16})')
NUMBER = re.compile(fr'({PREFIX_2}{COMPLEX_2}|'
                    fr'{PREFIX_8}{COMPLEX_8}|'
                    fr'{PREFIX_10}{COMPLEX_10}|'
                    fr'{PREFIX_16}{COMPLEX_16})')

# Number utilities
PREFIX = re.compile(r'#[bodx](#[ei])?|#[ei](#[bodx])?')
RADIX = re.compile(r'#[bodx]')
RADIX_MAP = {'#b': 2, '#o': 8, '#d': 10, '#x': 16}
EXACTNESS_LOWER = re.compile(r'#[ei]')
EXPONENT = re.compile(r'[esdfl]')

# Token precedence order
TOKEN_PATTERNS = (RAW_STRING, STRING_START, BOOLEAN, CHARACTER,
                  NUMBER, IDENTIFIER, PUNCTUATOR, COMMENT)


def process_rational(token_text, radix=10, inexact=False):
    """Convert a rational or integer literal to a number.

    If inexact is true, returns a float. Otherwise returns an int
    or Fraction.
    """
    # Fractions
    if '/' in token_text:
        value = fractions.Fraction(*(int(num, radix)
                                     for num in
                                     token_text.split('/')))
        if inexact:
            return float(value)
        return (value.numerator if value.denominator == 1
                else value)

    # Integers
    value = int(token_text, radix)
    return float(value) if inexact else value


def process_number(token_text):
    """Convert a numeric literal to its associated value.

    Handles floating-point numbers in base 10 and fractions and
    integers in bases 2, 8, 10, and 16. Handles exact and inexact
    prefixes. Returns a float for inexact literals and an int or
    Fraction for an exact literal.
    """
    token_text = token_text.lower()

    prefix_match = PREFIX.match(token_text)
    prefix = ''
    if prefix_match:
        # Strip prefix
        token_text = token_text[prefix_match.span()[1]:]
        prefix = prefix_match.group()

    # Determine exactness and strip it
    inexact = '#i' in prefix
    exact = '#e' in prefix
    prefix = EXACTNESS_LOWER.sub('', prefix)

    # Determine radix
    radix_match = RADIX.match(prefix)
    radix = 10
    if radix_match:
        radix = RADIX_MAP[radix_match.group()]

    # Convert all remaining hash symbols to zeros
    token_text = token_text.replace('#', '0')

    # Floating-point literals
    if '.' in token_text or 'e' in token_text:
        # Convert all (now lower-case) exponent markers to e
        token_text = EXPONENT.sub('e', token_text)

        # Complex numbers, always inexact
        if token_text[-1] == 'i':
            return complex(token_text[:-1] + 'j')
        # Polar notation
        if '@' in token_text:
            partitioned = token_text.partition('@')
            return cmath.rect(float(partitioned[0]),
                              float(partitioned[2]))

        # Real numbers
        return (fractions.Fraction(token_text) if exact
                else float(token_text))

    # Complex numbers
    if token_text[-1] == 'i':
        # Find rightmost sign
        split = max(token_text.rfind('+'), token_text.rfind('-'))
        real_text = token_text[:split]
        imag_text = token_text[split: -1]
        if not real_text:
            real_text = '0'
        if len(imag_text) == 1:
            imag_text += '1'
        return complex(process_rational(real_text, radix),
                       process_rational(imag_text, radix))
    # Polar notation
    if '@' in token_text:
        partitioned = token_text.partition('@')
        return cmath.rect(process_rational(partitioned[0], radix),
                          process_rational(partitioned[2], radix))

    # Rationals and integers
    return process_rational(token_text, radix, inexact)


def check_termination(token_text, pattern, next_char):
    """Check if token must be implicitly terminated but is not."""
    undelimited = False
    if pattern in (IDENTIFIER, NUMBER):
        undelimited = next_char not in DELIMITERS
    elif pattern is CHARACTER:
        undelimited = (len(token_text) == 3 and
                       token_text[2].isalpha() and
                       next_char not in DELIMITERS)
    elif pattern is PUNCTUATOR:
        undelimited = (token_text == '.' and
                       next_char not in DELIMITERS)
    if undelimited:
        print(f'warning: token {token_text} should be terminated by '
              f'a delimiter instead of {next_char}', file=sys.stderr)


class Tokenizer:
    """Lexes input data representing Scheme source code."""

    def __init__(self):
        """Initialize this tokenizer to be empty."""
        self.partial_string = None

    def _process_token(self, token_text, pattern):
        """Process the token, where pattern is what the text matched.

        For strings, replaces escape sequences.
        For booleans, converts them to the corresponding Python value/
        For decimals, coverts them to number format.
        For fractions, converts them to Fraction objects.
        For identifiers, converts them to lowercase.
        For comments, discards them.
        """
        processed_token = token_text
        if pattern is RAW_STRING:
            processed_token = STRING_ESCAPE.sub(r'\1', token_text)
        elif pattern is STRING_START:
            self.partial_string = token_text
            processed_token = ''
        elif pattern is BOOLEAN:
            processed_token = token_text.lower() == '#t'
        elif pattern is CHARACTER:
            if len(processed_token) > 3:  # space and newline escapes
                processed_token = processed_token.lower()
        elif pattern is NUMBER:
            processed_token = process_number(token_text)
        elif pattern is IDENTIFIER:
            processed_token = token_text.lower()
        elif pattern is COMMENT:
            processed_token = ''
        return processed_token

    def _next_token(self, line, position):
        """Return the next token in line after the given position.

        Produces a tuple (token, position'), where token is the next
        substring of line at or after the given position that could be
        a token (assuming it passes a validity check), and position'
        is the position in line following that token. Returns ('',
        len(line)) when there are no more tokens.

        For multiline strings, the string read so far is in
        self.partial_string.
        """
        # Check for and handle multiline string
        if self.partial_string:
            assert position == 0, line + f' ({position})'
            match = STRING_END.match(line)
            if match:
                token_text = self.partial_string + match.group()
                self.partial_string = None
                return (self._process_token(token_text, RAW_STRING),
                        match.span()[1])
            self.partial_string += line
            return '', len(line)

        # Discard leading whitespace
        while position < len(line) and line[position] in _WHITESPACE:
            position += 1

        if position == len(line):
            return '', position

        text = line[position:]
        # Attempt to match each token type in order
        for pattern in TOKEN_PATTERNS:
            match = pattern.match(text)
            if match:
                token = self._process_token(match.group(), pattern)
                position += match.span()[1]
                check_termination(match.group(), pattern,
                                  line[position: position+1])
                return token, position

        # Did not match any token type
        raise SyntaxError(f'invalid token: {text}')

    def tokenize_line(self, line):
        """Return a list of the Scheme tokens on line.

        Excludes comments and whitespace.
        """
        # Some forms of input strip the trailing newline
        if line[-1:] != '\n':
            line += '\n'

        result = []
        token, i = self._next_token(line, 0)
        while token != '':
            result.append(token)
            token, i = self._next_token(line, i)

        return result

    def tokenize_lines(self, input_data):
        """Produce an iterator over lists of the tokens in the input.

        A list is returned for each line of the iterable input
        sequence.
        """
        return map(self.tokenize_line, input_data)


def count_tokens(input_data):
    """Count the number of non-punctuator tokens in the input."""
    return len(list(filter(lambda x: x not in PUNCTUATORS,
                           itertools.chain(
                               *Tokenizer().tokenize_lines(input_data)
                           ))))


def main():
    """Count the tokens in standard input."""
    file = sys.stdin
    if len(sys.argv) > 1:
        file = open(sys.argv[1], 'r')
    print('counted', count_tokens(file), 'non-punctuator tokens')


if __name__ == '__main__':
    main()
