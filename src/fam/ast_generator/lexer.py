# Fam - query and storage language specialised in modelling family trees
# repo at: https://github.com/not-louis-239/fam
# Copyright (C) 2026  Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable

from fam.errors import FamParseError


class TokenType(StrEnum):
    # In order of priority...

    # Keywords
    DEFINE = "Define"
    METHOD = "Method"
    RETURN = "Return"
    DISPLAY = "Display"
    IF = "If"
    ELSE = "Else"

    # Core type keywords
    NODE = "Node"
    LINK = "Link"
    VARIABLE = "Variable"
    ATTRIBUTE = "Attribute"
    CONSTRAINTS = "Constraints"

    # Language constants
    NONE = "None"
    TRUE = "True"
    FALSE = "False"

    # Modifier keywords
    INFERRED = "Inferred"
    IMPLICIT = "Implicit"

    # Names
    NAME = "Name"

    # Literals
    STRING = "String"
    DATE = "Date"
    DURATION = "Duration"
    INTEGER = "Integer"
    REAL = "Real"

    # Operations
    ARROW_RIGHT = "ArrowRight"
    ARROW_DOUBLE = "ArrowDouble"
    ARROW_IMPLICATION = "ArrowImplication"
    EQUALS = "Equals"

    # Binary operations
    BIN_ADD = "BinAdd"
    BIN_SUB = "BinSub"
    BIN_MUL = "BinMul"
    BIN_DIV = "BinDiv"
    BIN_OR = "BinOr"
    BIN_EQ = "BinEq"
    BIN_GREATER_THAN = "BinGreaterThan"
    BIN_LESS_THAN = "BinLessThan"
    BIN_GREATER_EQ = "BinGreaterEq"
    BIN_LESS_EQ = "BinLessEq"
    BIN_IS = "BinIs"

    # Whitespace
    NEWLINE = "Newline"
    INDENT = "Indent"
    DEDENT = "Dedent"

    # Punctuation
    DOT = "Dot"
    COLON = "Colon"
    L_PAREN = "LParen"
    R_PAREN = "RParen"


@dataclass
class Token:
    typ: TokenType
    string: str

    # Metadata is attached by the lexer, not the compiler itself
    start_pos: int = -1
    end_pos: int = -1


# TokenFactory - a function to convert a re.Match into TokenData
type TokenFactory = Callable[[re.Match], Token]


def unescape_string(s: str) -> str:
    """Unescape escape sequences in a string literal and remove the string's surrounding quotes."""

    # Remove surrounding quotes
    content = s[1:-1]

    # Handle common escape sequences
    SEQUENCES = [
        ('\\n', '\n'),
        ('\\t', '\t'),
        ('\\r', '\r'),
        ('\\"', '"'),
        ('\\\\', '\\'),
    ]

    for seq in SEQUENCES:
        content = content.replace(seq[0], seq[1])

    # Handle escapes like "\xHH" for hex values
    def replace_hex(match: re.Match) -> str:
        return chr(int(match.group(1), 16))
    return re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex, content)


# Patterns - a list of regex patterns, and the token factory to use when it finds that pattern, or None if it is to be skipped
PATTERNS: list[tuple[re.Pattern, TokenFactory | None]] = [
    # Strings
    # TODO: this should have support for single-quoted strings as well...
    (re.compile(r'"(?:[^"\\]|\\.)*"'), lambda m: Token(TokenType.STRING, unescape_string(m.group(0)))),

    # Comments
    (re.compile(r'#.*'), None),

    # Literals
    (re.compile(r'[0-2][0-9]:[0-5][0-9]\s+[0-3][0-9]-[0-1][0-9]-[0-2][0-9][0-9][0-9]'), lambda m: Token(TokenType.DATE, m.group(0))),  # hh:mm DD/MM/YYYY Dates
    (re.compile(r'[0-3][0-9]-[0-1][0-9]-[0-2][0-9][0-9][0-9]'), lambda m: Token(TokenType.DATE, m.group(0))),  # DD/MM/YYYY Dates
    (re.compile(r'[0-9]+d [0-2][0-9]:[0-5][0-9]'), lambda m: Token(TokenType.DURATION, m.group(0))),  # Xd hh:mm durations
    (re.compile(r'[0-2][0-9]:[0-5][0-9]'), lambda m: Token(TokenType.DURATION, m.group(0))),  # hh:mm durations
    (re.compile(r'\d+\.?\d*'), lambda m: Token(TokenType.REAL, m.group(0))),  # Real numbers
    (re.compile(r'\d+'), lambda m: Token(TokenType.INTEGER, m.group(0))),  # Integers

    # Keywords
    (re.compile(r'\bDefine\b'), lambda m: Token(TokenType.DEFINE, m.group(0))),
    (re.compile(r'\bMethod\b'), lambda m: Token(TokenType.METHOD, m.group(0))),
    (re.compile(r'\bReturn\b'), lambda m: Token(TokenType.RETURN, m.group(0))),
    (re.compile(r'\bDisplay\b'), lambda m: Token(TokenType.DISPLAY, m.group(0))),
    (re.compile(r'\bIf\b'), lambda m: Token(TokenType.IF, m.group(0))),
    (re.compile(r'\bElse\b'), lambda m: Token(TokenType.ELSE, m.group(0))),

    (re.compile(r'\bNode\b'), lambda m: Token(TokenType.NODE, m.group(0))),
    (re.compile(r'\bLink\b'), lambda m: Token(TokenType.LINK, m.group(0))),
    (re.compile(r'\bVariable\b'), lambda m: Token(TokenType.VARIABLE, m.group(0))),
    (re.compile(r'\bAttribute\b'), lambda m: Token(TokenType.ATTRIBUTE, m.group(0))),
    (re.compile(r'\bConstraints\b'), lambda m: Token(TokenType.CONSTRAINTS, m.group(0))),

    (re.compile(r'\bInferred\b'), lambda m: Token(TokenType.INFERRED, m.group(0))),
    (re.compile(r'\bImplicit\b'), lambda m: Token(TokenType.IMPLICIT, m.group(0))),

    # Language constants
    (re.compile(r'\bNone\b'), lambda m: Token(TokenType.DEFINE, m.group(0))),
    (re.compile(r'\bTrue\b'), lambda m: Token(TokenType.TRUE, m.group(0))),
    (re.compile(r'\bFalse\b'), lambda m: Token(TokenType.FALSE, m.group(0))),

    # Title case identifiers - for nodes and links
    (re.compile(r'[a-zA-Z]+( [a-zA-Z]+)*'), lambda m: Token(TokenType.NAME, m.group(0))),

    # Lowercase (lower_snake_case) identifiers
    (re.compile(r'\b[_a-zA-Z][_a-zA-Z0-9]*\b'), lambda m: Token(TokenType.NAME, m.group(0))),

    # Binary operators
    (re.compile(r'\+'), lambda m: Token(TokenType.BIN_ADD, m.group(0))),
    (re.compile(r'-'), lambda m: Token(TokenType.BIN_SUB, m.group(0))),
    (re.compile(r'\*'), lambda m: Token(TokenType.BIN_MUL, m.group(0))),
    (re.compile(r'\/'), lambda m: Token(TokenType.BIN_DIV, m.group(0))),
    (re.compile(r'\|'), lambda m: Token(TokenType.BIN_OR, m.group(0))),
    (re.compile(r'=='), lambda m: Token(TokenType.BIN_EQ, m.group(0))),
    (re.compile(r'>='), lambda m: Token(TokenType.BIN_GREATER_EQ, m.group(0))),
    (re.compile(r'<='), lambda m: Token(TokenType.BIN_LESS_EQ, m.group(0))),
    (re.compile(r'>'), lambda m: Token(TokenType.BIN_GREATER_THAN, m.group(0))),
    (re.compile(r'<'), lambda m: Token(TokenType.BIN_LESS_THAN, m.group(0))),
    (re.compile(r'Is'), lambda m: Token(TokenType.BIN_IS, m.group(0))),

    # Other operators
    (re.compile(r'->'), lambda m: Token(TokenType.ARROW_RIGHT, m.group(0))),
    (re.compile(r'<->'), lambda m: Token(TokenType.ARROW_DOUBLE, m.group(0))),
    (re.compile(r'=>'), lambda m: Token(TokenType.ARROW_IMPLICATION, m.group(0))),
    (re.compile(r'='), lambda m: Token(TokenType.EQUALS, m.group(0))),

    # Punctuation
    (re.compile(r'\.'), lambda m: Token(TokenType.DOT, m.group(0))),
    (re.compile(r':'), lambda m: Token(TokenType.COLON, m.group(0))),
    (re.compile(r'\('), lambda m: Token(TokenType.L_PAREN, m.group(0))),
    (re.compile(r'\)'), lambda m: Token(TokenType.R_PAREN, m.group(0))),

    # Whitespace
    # TODO: How does Python pick up on these, and error out if whitespace is incorrect?

    # Skip whitespace
    (re.compile(r'\s+'), None)
]


# Note:
# Source code and positions are stored here as full strings and integers respectively, internally.


class Lexer:
    def lex(self, src_code: str) -> list[Token]:
        tokens: list[Token] = []

        code_len = len(src_code)
        pos = 0

        while pos < code_len:
            for pat, tok_factory in PATTERNS:
                match = pat.match(src_code, pos)

                if not match:
                    continue

                if tok_factory is not None:
                    tok = tok_factory(match)
                    tok.start_pos = pos
                    tok.end_pos = match.end()
                    tokens.append(tok)

                pos = match.end()
                break
            else:
                raise FamParseError(f"Unexpected token near position {pos}", pos=pos, src_code=src_code)

        return tokens


class FamCompiler:
    pass
