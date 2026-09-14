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
from typing import Callable

from fam.compiler.utils.tokens import Token
from fam.compiler.utils.tokens import TokenType
from fam.errors import FamParseError, FamTabError, FamIndentationError
from fam.utils import unescape_string


# TokenFactory - a function to convert a re.Match into TokenData
type TokenFactory = Callable[[re.Match], Token]


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
    (re.compile(r'\bFrom\b'), lambda m: Token(TokenType.FROM, m.group(0))),
    (re.compile(r'\bVariable\b'), lambda m: Token(TokenType.VARIABLE, m.group(0))),
    (re.compile(r'\bAttribute\b'), lambda m: Token(TokenType.ATTRIBUTE, m.group(0))),
    (re.compile(r'\bConstraints\b'), lambda m: Token(TokenType.CONSTRAINTS, m.group(0))),

    (re.compile(r'\bInferred\b'), lambda m: Token(TokenType.INFERRED, m.group(0))),
    (re.compile(r'\bImplicit\b'), lambda m: Token(TokenType.IMPLICIT, m.group(0))),

    (re.compile(r'\bIs\b'), lambda m: Token(TokenType.BIN_IS, m.group(0))),
    (re.compile(r'\bNot\b'), lambda m: Token(TokenType.BIN_NOT, m.group(0))),

    # Language constants
    (re.compile(r'\bNone\b'), lambda m: Token(TokenType.NONE, m.group(0))),
    (re.compile(r'\bTrue\b'), lambda m: Token(TokenType.TRUE, m.group(0))),
    (re.compile(r'\bFalse\b'), lambda m: Token(TokenType.FALSE, m.group(0))),

    # Title case identifiers - for nodes and links
    (re.compile(r'\b[a-zA-Z]+\b'), lambda m: Token(TokenType.NAME, m.group(0))),

    # Lowercase (lower_snake_case) identifiers
    (re.compile(r'\b[_a-zA-Z][_a-zA-Z0-9]*\b'), lambda m: Token(TokenType.NAME, m.group(0))),

    # Other operators
    (re.compile(r'->'), lambda m: Token(TokenType.ARROW_RIGHT, m.group(0))),
    (re.compile(r'<->'), lambda m: Token(TokenType.ARROW_DOUBLE, m.group(0))),
    (re.compile(r'=>'), lambda m: Token(TokenType.ARROW_IMPLICATION, m.group(0))),
    (re.compile(r'='), lambda m: Token(TokenType.EQUALS, m.group(0))),

    # Binary operators
    (re.compile(r'=='), lambda m: Token(TokenType.BIN_EQ, m.group(0))),
    (re.compile(r'>='), lambda m: Token(TokenType.BIN_GREATER_EQ, m.group(0))),
    (re.compile(r'<='), lambda m: Token(TokenType.BIN_LESS_EQ, m.group(0))),
    (re.compile(r'\+'), lambda m: Token(TokenType.BIN_ADD, m.group(0))),
    (re.compile(r'-'), lambda m: Token(TokenType.BIN_SUB, m.group(0))),
    (re.compile(r'\*'), lambda m: Token(TokenType.BIN_MUL, m.group(0))),
    (re.compile(r'\/'), lambda m: Token(TokenType.BIN_DIV, m.group(0))),
    (re.compile(r'\|'), lambda m: Token(TokenType.BIN_OR, m.group(0))),
    (re.compile(r'>'), lambda m: Token(TokenType.BIN_GREATER_THAN, m.group(0))),
    (re.compile(r'<'), lambda m: Token(TokenType.BIN_LESS_THAN, m.group(0))),

    # Punctuation
    (re.compile(r'\.'), lambda m: Token(TokenType.DOT, m.group(0))),
    (re.compile(r':'), lambda m: Token(TokenType.COLON, m.group(0))),
    (re.compile(r'\('), lambda m: Token(TokenType.L_PAREN, m.group(0))),
    (re.compile(r'\)'), lambda m: Token(TokenType.R_PAREN, m.group(0))),

    # Newlines and indentation - newline + any amount of whitespace except newlines
    (re.compile(r'\n[^\S\n]*'), lambda m: Token(TokenType.NEWLINE, m.group(0))),

    # Skip whitespace
    (re.compile(r'\s+'), None),
]


# Note:
# Source code and positions are stored here as full strings and integers respectively, internally.


class Lexer:
    def lex(self, src_code: str) -> list[Token]:
        # Initialise token list
        tokens: list[Token] = []

        # Run through the source code and extract the tokens
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
                raise FamParseError(f"invalid token '{src_code[pos]}'", pos=pos, src_code=src_code)

        # Remove consecutive newline tokens because they aren't important - only the last newline in
        # a series of newlines matters for indentation
        last_token = None

        # Iteration is reversed because we only want to keep the last token in each chain of
        # NEWLINE tokens. This algorithm by default removes all NEWLINEs after the first,
        # so reversing iteration preserves the last token only out of each chain.
        for tok in tokens[::-1]:
            if tok.typ == TokenType.NEWLINE and last_token and last_token.typ == TokenType.NEWLINE:
                tokens.remove(tok)
            last_token = tok

        # Convert newline tokens to indentation
        indent_stack: list[str] = [""]
        processed_tokens: list[Token] = []

        for tok in tokens:
            # If we're not at a newline, skip past tokens until we get to one.
            if tok.typ != TokenType.NEWLINE:
                processed_tokens.append(tok)
                continue

            # If we see a newline, we split the token into the newline itself
            # and indentation, which we then process.

            # Add a synthetic newline token
            processed_tokens.append(Token(
                typ=TokenType.NEWLINE, string='\n',
                start_pos=tok.start_pos, end_pos=tok.start_pos + 1
            ))

            # Process the indentation
            indent_prefix = tok.string[1:]  # strip away the newline
            last_indent = indent_stack[-1]

            indent_start_pos = tok.start_pos + 1

            # Constant indentation
            if indent_prefix == last_indent:
                pass

            # TabError - Inconsistent prefix
            elif not (last_indent.startswith(indent_prefix) or indent_prefix.startswith(last_indent)):
                raise FamTabError(msg="inconsistent use of tabs and spaces in indentation", pos=indent_start_pos, src_code=src_code)

            # Indent - consistent prefix
            elif indent_prefix.startswith(last_indent):
                indent_stack.append(indent_prefix)
                processed_tokens.append(Token(typ=TokenType.INDENT, string=indent_prefix, start_pos=indent_start_pos, end_pos=indent_start_pos + len(indent_prefix)))

            # Dedent - try to find the outer indentation level
            else:
                while indent_stack:
                    if indent_stack[-1] == indent_prefix:
                        break
                    indent_stack.pop()
                    processed_tokens.append(Token(typ=TokenType.DEDENT, string='', start_pos=indent_start_pos, end_pos=indent_start_pos))
                else:
                    raise FamIndentationError("unindent does not match any outer indentation level", pos=indent_start_pos, src_code=src_code)

        assert not any(tok.start_pos == -1 or tok.end_pos == -1 for tok in processed_tokens), "Missing token metadata!!"

        return processed_tokens
