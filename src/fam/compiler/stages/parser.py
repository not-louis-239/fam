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
    AddOp,
    SubOp,
    MultOp,
    DivOp,
    FloorDivOp,
    ModuloOp,
    PowOp,
    BitAndOp,
    BitOrOp,
    BitXorOp,
    BitNotOp,
    BitLShift,
    BitRShift,
    ASTNode,
    NodeDecl,
    MethodDecl,
    IndexOp,
    AttributeAccess,
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
    VariableAssign,
    Expr,
    String,
    LinkDecl,
    IfStmt,
    DisplayStmt
)
from fam.compiler.utils.parser_helpers import parse_link_attribute_defs, parse_node_or_link_method, parse_attribute_block, parse_code_block, parse_key_value_pair, parse_define as _parse_define
from fam.compiler.utils.expression_parsers import parse_primary, parse_name_streak, parse_name, parse_expr
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
                if TokenType.NEWLINE in acceptable_types:
                    msg = "expected ':' or newline after statement"
                else:
                    msg = "expected ':'"
            else:
                msg = err_msg or "invalid syntax"

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
        # Re-parse as method if 'Method' token present
        self.retreat()
        return parse_node_or_link_method(self)

    else:
        # Consume the name token(s) and save it
        name_token = parse_name_streak(self, "expected node name or 'Method'")
        self.expect(TokenType.COLON)

        self.expect(TokenType.NEWLINE)

        # Parse attributes
        attributes, end_pos = parse_attribute_block(self)
        return NodeDecl(start_token.start_pos, end_pos, name_token, attributes)

# Parse link declarations

@Parser.register(TokenType.LINK)
def parse_link_decl(self: Parser) -> LinkDecl | MethodDecl:
    start = self.expect(TokenType.LINK)

    if self.peek().typ == TokenType.METHOD:
        self.retreat()
        return parse_node_or_link_method(self)

    link_name = parse_name_streak(self, "expected link name")

    self.expect(TokenType.FROM, err_msg="expected 'From' after link name")
    src = parse_name_streak(self, "expected source node name")
    self.expect(TokenType.ARROW_RIGHT, err_msg="expected '->' after source node")
    dest = parse_name_streak(self, "expected destination node name")
    tok = self.expect(TokenType.COLON, TokenType.NEWLINE)

    if tok.typ == TokenType.NEWLINE:
        return LinkDecl(start.start_pos, dest.end_pos, link_name, src, dest, [])

    link_attrs = parse_attribute_block(self)
    return LinkDecl(start.start_pos, link_attrs[1], link_name, src, dest, link_attrs[0])

# Define keyword

@Parser.register(TokenType.DEFINE)
def parse_define(self: Parser) -> AttributeDef | VariableDef | LinkDef | InferredLinkDef | ImplicitLinkDef:
    return _parse_define(self)

# Conditionals

@Parser.register(TokenType.IF)
def parse_if_stmt(self: Parser) -> IfStmt:
    if_tok = self.expect(TokenType.IF, TokenType.ELSE_IF)
    cond = parse_expr(self)
    self.expect(TokenType.COLON)
    self.expect(TokenType.NEWLINE)
    body = parse_code_block(self)

    while not self.eof() and self.peek().typ in (TokenType.ELSE, TokenType.ELSE_IF):
        next_tok = self.peek()
        match next_tok.typ:
            case TokenType.ELSE:
                self.advance()
                self.expect(TokenType.COLON)
                self.expect(TokenType.NEWLINE)
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
    return WhileLoop(start.start_pos, block[-1].end_pos, cond, block)

# Parse imports

@Parser.register(TokenType.IMPORT)
def parse_import(self: Parser) -> Import:
    start = self.expect(TokenType.IMPORT)
    fp = self.expect(TokenType.STRING)
    self.expect(TokenType.NEWLINE)

    return Import(
        start.start_pos, fp.end_pos,
        String(fp.start_pos, fp.end_pos, fp.string)
    )

# Statements that start with a name
AUGMENTED_ASSIGNMENT_OPS: list[TokenType] = [
    TokenType.BIN_ADD,
    TokenType.BIN_SUB,
    TokenType.BIN_MUL,
    TokenType.BIN_DIV,
    TokenType.BIN_FLOOR_DIV,
    TokenType.BIN_MODULO,
    TokenType.BIN_POW,
    TokenType.BIN_BIT_AND,
    TokenType.BIN_BIT_OR,
    TokenType.BIN_BIT_XOR,
    TokenType.BIN_BIT_LSHIFT,
    TokenType.BIN_BIT_RSHIFT
]

@Parser.register(TokenType.NAME)
def parse_open_name(self: Parser) -> VariableAssign | Expr:
    var = parse_primary(self)

    next_tok = self.peek()

    if next_tok.typ == TokenType.NEWLINE:
        self.advance()
        return var

    # Assignment
    elif next_tok.typ == TokenType.ASSIGNMENT:
        if not isinstance(var, (Name, IndexOp, AttributeAccess)):
            raise FamParseError("illegal left-hand side of assignment", var.start_pos, var.end_pos)

        self.advance()
        rhs = parse_expr(self)
        self.expect(TokenType.NEWLINE)
        return VariableAssign(var.start_pos, rhs.end_pos, var, rhs)

    # Augmented assignment
    if next_tok.typ not in AUGMENTED_ASSIGNMENT_OPS:
        raise FamParseError(f"invalid syntax", next_tok.start_pos, next_tok.end_pos)

    if not isinstance(var, (Name, IndexOp, AttributeAccess)):
        raise FamParseError("illegal left-hand side of augmented assignment", var.start_pos, var.end_pos)

    augmented_op = self.advance()
    self.expect(TokenType.ASSIGNMENT)

    rhs = parse_expr(self)
    self.expect(TokenType.NEWLINE)

    match augmented_op.typ:
        case TokenType.BIN_ADD:
            node = AddOp(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_SUB:
            node = SubOp(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_MUL:
            node = MultOp(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_DIV:
            node = DivOp(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_FLOOR_DIV:
            node = FloorDivOp(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_MODULO:
            node = ModuloOp(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_POW:
            node = PowOp(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_BIT_AND:
            node = BitAndOp(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_BIT_OR:
            node = BitOrOp(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_BIT_XOR:
            node = BitXorOp(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_BIT_LSHIFT:
            node = BitLShift(var.start_pos, rhs.end_pos, var, rhs)
        case TokenType.BIN_BIT_RSHIFT:
            node = BitRShift(var.start_pos, rhs.end_pos, var, rhs)
        case uncaught:
            raise RuntimeError(f"missing handler for augmented assignment operator: {uncaught!r}")

    return VariableAssign(
        var.start_pos, rhs.end_pos,
        var, node
    )



# Parse display

@Parser.register(TokenType.DISPLAY)
def parse_display(self: Parser) -> DisplayStmt:
    start = self.advance()
    expr = parse_expr(self)
    self.expect(TokenType.NEWLINE)
    return DisplayStmt(start.start_pos, expr.end_pos, expr)
