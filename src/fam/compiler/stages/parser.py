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

from fam.compiler.utils.parser_helpers import parse_name
from fam.compiler.utils.tokens import Token, TokenType
from fam.compiler.utils.nodes import NodeDecl, ASTNode, AST
from fam.errors import FamParseError


type _ParseCallable = Callable[["Parser"], ASTNode]


class Parser:
    PARSE_REGISTRY: dict[TokenType, _ParseCallable] = {}

    @classmethod
    def register(cls, *types: TokenType):
        def wrapper(fn: Callable[[Parser], ASTNode]) -> _ParseCallable:
            for typ in types:
                cls.PARSE_REGISTRY[typ] = fn
            return fn
        return wrapper

    def eof(self) -> bool:
        """Return True if there are no more tokens to be consumed."""
        return self.pos >= self.num_tokens

    def peek(self) -> Token:
        """Return the current token without eating it."""
        try:
            return self.tokens[self.pos]
        except IndexError:
            raise FamParseError("unexpected end of input", self.tokens[-1].start_pos, self.tokens[-1].end_pos)

    def advance(self) -> Token:
        """Eats and returns the current token."""
        token = self.peek()
        self.pos += 1
        return token

    def retreat(self) -> None:
        """Moves back by one token and returns None."""
        if self.pos == 0:
            raise FamParseError("cannot retreat to before start of input", self.tokens[0].start_pos, self.tokens[0].end_pos)
        self.pos -= 1

    def expect(self, *acceptable_types: TokenType) -> Token:
        """Consume and return the current token and raise an error if it
        is not one of a set of accepted types."""
        tok = self.advance()
        if tok.typ not in acceptable_types:
            raise FamParseError(f"expected one of {acceptable_types}, got token {tok.string!r} of type {tok.typ!r}", start_pos=tok.start_pos, end_pos=tok.end_pos)
        return tok

    def parse_stmt(self) -> ASTNode:
        """Parse an individual statement."""
        token = self.peek()
        try:
            return self.PARSE_REGISTRY[token.typ](self)
        except KeyError:
            raise FamParseError(f"unexpected token {token.string!r}", start_pos=token.start_pos, end_pos=token.end_pos)
        except RecursionError:
            raise FamParseError("control structure is too deeply nested", start_pos=token.start_pos, end_pos=token.end_pos)

    def parse(self, tokens: list[Token]) -> AST:
        """Parse a list of tokens and generate an AST (Abstract Syntax Tree)
        consisting of nodes."""

        self.tokens: list[Token] = tokens
        self.num_tokens = len(self.tokens)
        self.pos = 0
        ast: AST = []

        while not self.eof():
            # Ignore empty newlines
            if self.peek().typ == TokenType.NEWLINE:
                self.advance()
                continue

            ast.append(self.parse_stmt())

            # Skip newlines before the next statement
            while not self.eof() and self.peek().typ == TokenType.NEWLINE:
                self.advance()

        return ast


# Main parse functions

@Parser.register(TokenType.NODE)
def parse_node_decl(self: Parser) -> NodeDecl:

    # Consume the 'Node' token
    node_token = self.expect(TokenType.NODE)

    if self.peek().typ == TokenType.METHOD:
        # Consume the 'Method' token
        self.advance()

        # Consume and record the method name
        method_name = parse_name(self)

    else:
        # Consume the name token and save it
        name_token = self.expect(TokenType.NAME)
        self.expect(TokenType.COLON)

        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT)

        # Parse attributes


        # Dedent
        self.expect(TokenType.DEDENT)
