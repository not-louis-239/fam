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
    MethodDecl,
    KeyValuePair,
    MethodParam,
    AttributeDef,
    ImplicitLinkDef,
    LinkDef,
    AttributeDef,
    VariableDef,
    InferredLinkDef,
    Expr
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

def parse_method(self: Parser) -> MethodDecl:
    start_token = self.expect(TokenType.METHOD)

    # Consume and record the method name
    method_name = parse_name(self, "expected method name")

    # Parse params
    params: list[MethodParam] = parse_method_params(self)

    # Return type
    if self.peek().typ == TokenType.COLON:
        return_type = None
        self.advance()
    else:
        self.expect(TokenType.ARROW_RIGHT, err_msg="expected '->' or ':' after method parameters")
        return_type = parse_expr(self)
        self.expect(TokenType.COLON)

    self.expect(TokenType.NEWLINE)

    body = parse_code_block(self)

    return MethodDecl(
        start_token.start_pos, body[-1].end_pos,
        Name(start_token.start_pos, start_token.end_pos, (start_token.string,)),
        method_name, params,return_type, body
    )

def parse_node_or_link_method(self: Parser) -> MethodDecl:
    host_class = self.expect(TokenType.NODE, TokenType.LINK)
    decl_node = parse_method(self)

    decl_node.caller = Name(host_class.start_pos, host_class.end_pos, (host_class.string,))
    decl_node.start_pos = host_class.start_pos

    return decl_node

def parse_link_attribute_defs(self: Parser) -> tuple[list[AttributeDef], int]:
    """Returns (pairs, end_pos). Consumes the surrounding indent and dedent."""

    self.expect(TokenType.INDENT)

    if self.peek().typ == TokenType.PASS:
        tok = self.advance()
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.DEDENT)
        return ([], tok.end_pos)

    attrs: list[AttributeDef] = []
    while not self.eof() and self.peek().typ == TokenType.DEFINE:
        attr_def_node = parse_define(self)
        if not isinstance(attr_def_node, AttributeDef):
            raise FamParseError(
                "expected attribute definitions or 'Pass' under link definition",
                attr_def_node.start_pos, attr_def_node.end_pos
            )
        attrs.append(attr_def_node)

    self.expect(TokenType.DEDENT)
    return (attrs, attrs[-1].end_pos)

def parse_define(self: Parser) -> AttributeDef | VariableDef | LinkDef | InferredLinkDef | ImplicitLinkDef:
    define_tok = self.advance()

    # For attributes or variables, parse type expression
    if self.peek().typ not in (
        TokenType.ATTRIBUTE,
        TokenType.VARIABLE,
        TokenType.LINK,
        TokenType.INFERRED,
        TokenType.IMPLICIT
    ):
        typ_expr = parse_expr(self)
    else:
        typ_expr = None

    if typ_expr is not None:
        if (bad_tok := self.peek()).typ in (
            TokenType.LINK,
            TokenType.INFERRED,
            TokenType.IMPLICIT
        ):
            raise FamParseError(
                "expected attribute or variable definition after type annotation",
                bad_tok.start_pos, bad_tok.end_pos
            )

    kw = self.advance()

    match kw.typ:
        # Node attributes
        case TokenType.ATTRIBUTE:
            attr_name = parse_name(self, "expected attribute name")
            self.expect(TokenType.COLON)

            self.expect(TokenType.NEWLINE)
            self.expect(TokenType.INDENT, err_msg="expected indented block in attribute definition")

            tok = self.expect(TokenType.CONSTRAINTS, TokenType.PASS, err_msg="expected 'Constraints' or 'Pass' in attribute definition")

            if tok.typ == TokenType.PASS:
                self.expect(TokenType.NEWLINE)
                self.expect(TokenType.DEDENT)
                return AttributeDef(define_tok.start_pos, tok.end_pos, typ_expr, attr_name, [])

            self.expect(TokenType.COLON)
            self.expect(TokenType.NEWLINE)
            self.expect(TokenType.INDENT, err_msg="expected indented block in constraints section of attribute definition")
            constraints: list[Expr] = []

            while not self.eof() and self.peek().typ != TokenType.DEDENT:
                constraints.append(parse_expr(self))
                self.expect(TokenType.NEWLINE)

            self.expect(TokenType.DEDENT)
            self.expect(TokenType.DEDENT)

            return AttributeDef(define_tok.start_pos, constraints[-1].end_pos, typ_expr, attr_name, constraints)

        # Variables
        case TokenType.VARIABLE:
            var_name = parse_name(self, "expected variable name")
            self.expect(TokenType.ASSIGNMENT, err_msg="expected '=' after variable name")
            value = parse_expr(self)
            node = VariableDef(define_tok.start_pos, value.end_pos, typ_expr, var_name, value)

        # Links
        case TokenType.LINK:
            name = parse_name(self, "expected link name")
            self.expect(TokenType.COLON)
            self.expect(TokenType.NEWLINE)
            attr_defs, end_pos = parse_link_attribute_defs(self)
            node = LinkDef(define_tok.start_pos, end_pos, name, attr_defs)

        # Inferred Links
        case TokenType.INFERRED:
            self.expect(TokenType.LINK, err_msg="expected 'Link' after link modifier keyword 'Inferred'")
            name = parse_name(self, "expected link name")
            self.expect(TokenType.ARROW_DOUBLE, err_msg="expected '<->' after link name in inferred link declaration")
            inferred_name = parse_name(self, "expected inferred link name")
            self.expect(TokenType.COLON)
            self.expect(TokenType.NEWLINE)
            attr_defs, end_pos = parse_link_attribute_defs(self)
            node = InferredLinkDef(define_tok.start_pos, end_pos, name, attr_defs, inferred_name)

        # Implicit Links
        case TokenType.IMPLICIT:
            self.expect(TokenType.LINK, err_msg="expected 'Link' after link modifier keyword 'Implicit'")

            intermediate_links: list[Name] = [parse_name(self, "expected one or more link names in implicit link definition")]

            while True:
                tok = self.expect(
                    TokenType.ARROW_RIGHT, TokenType.ARROW_IMPLICATION,
                    err_msg="expected '->' or '=>' in implicit link declaration"
                )

                match tok.typ:
                    case TokenType.ARROW_RIGHT:
                        intermediate_links.append(parse_name(self, "expected link name after '->' in implicit link definition"))
                    case TokenType.ARROW_IMPLICATION:
                        implied = parse_name(self, "expected implicit link name")
                        break

            self.expect(TokenType.COLON)
            self.expect(TokenType.NEWLINE)
            attr_defs, _ = parse_link_attribute_defs(self)
            node = ImplicitLinkDef(define_tok.start_pos, implied.end_pos, implied, attr_defs, intermediate_links)

        case _:
            raise FamParseError(f"unexpected token {kw.string!r}", kw.start_pos, kw.end_pos)

    self.expect(TokenType.NEWLINE)
    return node
