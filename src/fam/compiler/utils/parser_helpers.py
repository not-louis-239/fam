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


# Parser functions specialised for parsing expressions


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fam.compiler.stages.parser import Parser

from fam.errors import FamParseError
from fam.compiler.utils.expression_parsers import parse_expr, parse_name
from fam.compiler.utils.nodes import (
    AST,
    Name,
    KeyValuePair,
    MethodParam,
    AttributeDef
)
from fam.compiler.utils.tokens import TokenType
from fam.compiler.utils.expression_parsers import parse_name


# Helper parser functions

def parse_key_value_pair(self: Parser) -> KeyValuePair:
    attribute_name = parse_name(self, "expected attribute name")
    self.expect(TokenType.COLON)
    expr = parse_expr(self)
    self.expect(TokenType.NEWLINE)

    return KeyValuePair(
        attribute_name.start_pos,
        expr.end_pos,
        attribute_name,
        expr
    )

def parse_method_param(self: Parser) -> MethodParam:
    names: list[Name] = []
    while not self.eof() and self.peek().typ == TokenType.NAME:
        names.append(parse_name(self))

    if not names:
        raise FamParseError("expected method parameter name", self.peek().start_pos, self.peek().end_pos)
    elif len(names) == 1:
        typ, name = None, names[0]
    elif len(names) == 2:
        typ, name = names
    else:
        raise FamParseError("too many names in method parameter", names[0].start_pos, names[-1].end_pos)

    if self.peek().typ != TokenType.DEFAULT:
        default = None
        end_pos = name.end_pos
    else:
        self.advance()
        default = parse_expr(self)
        end_pos = default.end_pos

    return MethodParam(names[0].start_pos, end_pos, typ, name, default)

def parse_method_params(self: Parser) -> list[MethodParam]:
    params: list[MethodParam] = []
    default_found = False

    self.expect(TokenType.L_PAREN, err_msg="expected '(' after method name")

    while not self.eof():
        tok = self.advance()

        if tok.typ == TokenType.R_PAREN:
            return params

        self.retreat()

        param = parse_method_param(self)

        if param.default:
            default_found = True
        elif not param.default and default_found:
            raise FamParseError("parameter with default cannot follow parameters without default", param.start_pos, param.end_pos)

        params.append(param)

        next_tok = self.peek()

        if next_tok.typ == TokenType.COMMA:
            self.advance()
        elif next_tok == TokenType.R_PAREN:
            continue
        else:
            raise FamParseError("expected ',' or ')' after method parameter", next_tok.start_pos, next_tok.end_pos)

    raise FamParseError("unexpected EOF in method parameters", self.tokens[-1].start_pos, self.tokens[-1].end_pos)

def parse_code_block(self: Parser) -> AST:
    """Note: this also consumes the surrounding indent and dedent."""

    self.expect(TokenType.INDENT)

    stmts: AST = []

    while not self.eof() and self.peek().typ != TokenType.DEDENT:
        stmts.append(self.parse_stmt())

    self.expect(TokenType.DEDENT)

    return stmts

def parse_attribute_block(self: Parser) -> tuple[list[KeyValuePair], int]:
    """Returns (pairs, end_pos). Also consumes the surrounding indent and dedent."""
    self.expect(TokenType.INDENT, err_msg="expected indented block of 'key: value' pairs separated by lines")

    if self.peek().typ == TokenType.PASS:
        attributes = []
        end_pos = self.advance().end_pos
    else:
        attributes: list[KeyValuePair] = []
        while self.peek().typ == TokenType.NAME:
            attributes.append(parse_key_value_pair(self))
        end_pos = attributes[-1].end_pos

    self.expect(TokenType.DEDENT)
    return (attributes, end_pos)

# TODO: Parse node or link methods
def parse_node_or_link_method(self: Parser) -> MethodDecl:
    host_class = self.expect(TokenType.NODE, TokenType.LINK)

def parse_attribute_def(self: Parser) -> AttributeDef:
    ...
