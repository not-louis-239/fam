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


from collections.abc import Callable

from fam.compiler.utils.nodes import (
    AST,
    KeyValuePair,
    ASTNode,
    NodeDecl,
    MethodDecl,
    MethodParam,
    Name,
    Break,
    Continue,
    Pass,
    ForLoop,
    WhileLoop,
    Return,
    LinkDef,
    ImplicitLinkDef,
    Import,
    InferredLinkDef,
    VariableDef,
    AttributeDef,
    Expr,
    String,
    LinkDecl,
    IfStmt,
    DisplayStmt
)
from fam.compiler.utils.parser_helpers import parse_method_params, parse_code_block, parse_key_value_pair
from fam.compiler.utils.expression_parsers import parse_name_streak, parse_name, parse_expr
from fam.compiler.utils.tokens import Token, TokenType
from fam.errors import FamParseError, FamIndentationError

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

    def expect(self, *acceptable_types: TokenType, err_msg: str | None = None) -> Token:
        """Consume and return the current token and raise an error if it
        is not one of a set of accepted types.
        Dynamically create a message based on acceptable types and the provided type."""
        tok = self.advance()
        if tok.typ not in acceptable_types:
            if TokenType.INDENT in acceptable_types:
                raise FamIndentationError("expected indented block", tok.start_pos, tok.end_pos)
            elif tok.typ == TokenType.INDENT:
                raise FamIndentationError("unexpected indent", tok.start_pos, tok.end_pos)
            elif TokenType.NEWLINE in acceptable_types:
                msg = "expected newline after statement"
            elif TokenType.L_PAREN in acceptable_types:
                msg = "expected '('"
            elif TokenType.L_BRACE in acceptable_types:
                msg = "expected '{'"
            elif TokenType.L_SQ_BRAC in acceptable_types:
                msg = "expected '['"
            elif TokenType.R_PAREN in acceptable_types:
                msg = "missing closing ')'"
            elif TokenType.R_BRACE in acceptable_types:
                msg = "missing closing '}'"
            elif TokenType.R_SQ_BRAC in acceptable_types:
                msg = "missing closing ']'"
            elif TokenType.COLON in acceptable_types:
                msg = "expected ':'"
            else:
                msg = "invalid syntax"

            raise FamParseError(msg, start_pos=tok.start_pos, end_pos=tok.end_pos)
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


# Parse control flow keywords

@Parser.register(TokenType.BREAK)
def parse_break(self: Parser) -> Break:
    tok = self.advance()
    self.expect(TokenType.NEWLINE)
    return Break(tok.start_pos, tok.end_pos)

@Parser.register(TokenType.CONTINUE)
def parse_continue(self: Parser) -> Continue:
    tok = self.advance()
    self.expect(TokenType.NEWLINE)
    return Continue(tok.start_pos, tok.end_pos)

@Parser.register(TokenType.PASS)
def parse_pass(self: Parser) -> Pass:
    tok = self.advance()
    self.expect(TokenType.NEWLINE)
    return Pass(tok.start_pos, tok.end_pos)

@Parser.register(TokenType.RETURN)
def parse_return(self: Parser) -> Return:
    tok = self.advance()
    if self.peek().typ != TokenType.NEWLINE:
        expr = parse_expr(self)
        end_pos = expr.end_pos
    else:
        expr = None
        end_pos = tok.end_pos
    self.expect(TokenType.NEWLINE)
    return Return(tok.start_pos, end_pos, expr)

# Parse node declarations

@Parser.register(TokenType.NODE)
def parse_node_decl(self: Parser) -> NodeDecl | MethodDecl:

    # Consume the 'Node' token
    start_token = self.expect(TokenType.NODE)

    if self.peek().typ == TokenType.METHOD:
        # Consume the 'Method' token
        self.advance()

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
            Name(start_token.start_pos, start_token.end_pos, (start_token.string,)), method_name, params,return_type, body)

    else:
        # Consume the name token(s) and save it
        name_token = parse_name_streak(self, "expected node name or 'Method'")
        self.expect(TokenType.COLON)

        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT, err_msg="expected indented block in node declaration")

        # Parse attributes
        if self.peek().typ == TokenType.PASS:
            attributes = []
            end_pos = self.advance().end_pos
        else:
            attributes: list[KeyValuePair] = []
            while self.peek().typ == TokenType.NAME:
                attributes.append(parse_key_value_pair(self))
            end_pos = attributes[-1].end_pos

        # Dedent
        self.expect(TokenType.DEDENT)

        return NodeDecl(start_token.start_pos, end_pos, name_token, attributes)

# Parse link declarations

@Parser.register(TokenType.LINK)
def parse_link_decl(self: Parser) -> LinkDecl:
    start = self.expect(TokenType.LINK)
    link_name = parse_name_streak(self, "expected link name")
    self.expect(TokenType.FROM, err_msg="expected 'From' after link name")
    src = parse_name_streak(self, "expected source node name")
    self.expect(TokenType.ARROW_RIGHT, err_msg="expected '->' after source node")
    dest = parse_name_streak(self, "expected destination node name")
    self.expect(TokenType.NEWLINE)
    return LinkDecl(start.start_pos, dest.end_pos, link_name, src, dest, [])
    # TODO: eventually parse link methods

# Define keyword

@Parser.register(TokenType.DEFINE)
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
        # Attributes
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
        # TODO: eventually allow links to have attributes defined
        # under their definitions
        case TokenType.LINK:
            name = parse_name(self, "expected link name")
            node = LinkDef(define_tok.start_pos, name.end_pos, name)

        # Inferred Links
        case TokenType.INFERRED:
            self.expect(TokenType.LINK, err_msg="expected 'Link' after link modifier keyword 'Inferred'")
            name = parse_name(self, "expected link name")
            self.expect(TokenType.ARROW_DOUBLE, err_msg="expected '<->' after link name in inferred link declaration")
            inferred_name = parse_name(self, "expected inferred link name")
            node = InferredLinkDef(define_tok.start_pos, inferred_name.end_pos, name, inferred_name)

        # Implicit Links
        case TokenType.IMPLICIT:
            self.expect(TokenType.LINK, err_msg="expected 'Link' after link modifier keyword 'Implicit'")

            links: list[Name] = [parse_name(self, "expected one or more link names in implicit link definition")]

            while True:
                tok = self.expect(
                    TokenType.ARROW_RIGHT, TokenType.ARROW_IMPLICATION,
                    err_msg="expected '->' or '=>' in implicit link declaration"
                )

                match tok.typ:
                    case TokenType.ARROW_RIGHT:
                        links.append(parse_name(self, "expected link name after '->' in implicit link definition"))
                    case TokenType.ARROW_IMPLICATION:
                        implied = parse_name(self, "expected implicit link name")
                        break

            node = ImplicitLinkDef(define_tok.start_pos, implied.end_pos, implied, links)

        case _:
            raise FamParseError(f"unexpected token {kw.string!r}", kw.start_pos, kw.end_pos)

    self.expect(TokenType.NEWLINE)
    return node

# Conditionals

@Parser.register(TokenType.IF)
def parse_if_stmt(self: Parser) -> IfStmt:
    if_tok = self.expect(TokenType.IF, TokenType.ELSE_IF)
    cond = parse_expr(self)
    self.expect(TokenType.COLON)
    self.expect(TokenType.NEWLINE)
    body = parse_code_block(self)

    while not self.eof() and self.peek().typ in (TokenType.ELSE, TokenType.ELSE_IF):
        next_tok = self.advance()
        match next_tok.typ:
            case TokenType.ELSE:
                else_body = parse_code_block(self)
                return IfStmt(if_tok.start_pos, body[-1].end_pos, cond, body, else_body)
            case TokenType.ELSE_IF:
                sub_if_stmt = parse_if_stmt(self)
                return IfStmt(if_tok.start_pos, sub_if_stmt.end_pos, cond, body, [sub_if_stmt])

    return IfStmt(if_tok.start_pos, body[-1].end_pos, cond, body, None)

# Parse for loop

@Parser.register(TokenType.FOR)
def parse_for(self: Parser) -> ForLoop:
    start = self.expect(TokenType.FOR)
    var = parse_name(self, "expected loop variable name")
    self.expect(TokenType.IN)
    iterable = parse_expr(self)
    self.expect(TokenType.COLON)
    self.expect(TokenType.NEWLINE)
    block = parse_code_block(self)
    self.expect(TokenType.NEWLINE)

    return ForLoop(
        start.start_pos, block[-1].end_pos,
        var, iterable, block
    )

# Parse while loop

@Parser.register(TokenType.WHILE)
def parse_while(self: Parser) -> WhileLoop:
    start = self.expect(TokenType.WHILE)
    cond = parse_expr(self)
    self.expect(TokenType.COLON)
    self.expect(TokenType.NEWLINE)
    block = parse_code_block(self)
    self.expect(TokenType.NEWLINE)
    return WhileLoop(start.start_pos, block[-1].end_pos, cond, block)

# Parse imports

@Parser.register(TokenType.IMPORT)
def parse_import(self: Parser) -> Import:
    start = self.expect(TokenType.IMPORT)
    fp = self.expect(TokenType.STRING)

    return Import(
        start.start_pos, fp.end_pos,
        String(fp.start_pos, fp.end_pos, fp.string)
    )

# Parse display

@Parser.register(TokenType.DISPLAY)
def parse_display(self: Parser) -> DisplayStmt:
    start = self.advance()
    expr = parse_expr(self)
    self.expect(TokenType.NEWLINE)
    return DisplayStmt(start.start_pos, expr.end_pos, expr)
