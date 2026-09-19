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


from __future__ import annotations

import itertools

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fam.compiler.stages.parser import Parser

from fam.compiler.utils.nodes import (
    AddOp,
    AndOp,
    AttributeAccess,
    BitAndOp,
    BitLShift,
    BitNotOp,
    BitOrOp,
    BitRShift,
    BitXorOp,
    Boolean,
    Date,
    DivOp,
    Duration,
    EqOp,
    Expr,
    FloorDivOp,
    GtEqOp,
    GtOp,
    IndexOp,
    Integer,
    LtEqOp,
    LtOp,
    MethodCall,
    ModuloOp,
    MultOp,
    Name,
    NegOp,
    NoneItem,
    NotEqOp,
    NotOp,
    OrOp,
    PosOp,
    PowOp,
    Real,
    Sequence,
    String,
    SubOp,
    IsOp,
    InOp,
    IsNotOp,
    NotInOp
)
from fam.compiler.utils.regex import DATE_RE, DURATION_RE, DateKeys, DurationKeys
from fam.compiler.utils.tokens import Token, TokenType
from fam.errors import FamParseError
from fam.utils import get_days_in_month


# In descending order of precedence for expression parsing:
# - parentheses for grouping
# - subprimitives: indexing, method calls, attribute access
# - dates and durations (special parsing functions are dedicated to these)
# - integers, real numbers, strings, booleans, sequences, Nones, other primitives
# - unary operators: +, -
# - indices (exponentiation)
# - multiplication, division, floor division, modulo
# - addition, subtraction
# - bit shifts: <<, >>
# - chainable comparators (==, !=, >, <, >=, <=)
# - bitwise operators: ~ -> & -> ^ -> |
# - identity and membership operators: is, is not, in, not in
# - logical operators: 'not' -> 'and' -> 'or'


# Date and duration parsing

# I assume that only date or duration strings validated by the
# lexer could get here.
# So they shouldn't throw errors...hopefully.

# For non-optional fields, type-cast the regex group
# directly because we know they'll be there.

# For optional fields, they could be None,
# and type casting None would go boom.
# So extract from the group first,
# then type-cast if it's not None,
# else use a default value.

def parse_date_literal(tok: Token) -> Date:
    m = DATE_RE.match(tok.string)
    assert m is not None

    hour = m.group(DateKeys.HOUR)
    minute = m.group(DateKeys.MINUTE)
    second = m.group(DateKeys.SECOND)
    frac_seconds = m.group(DateKeys.FRAC_SECONDS)
    am_pm_suffix = m.group(DateKeys.AM_PM_SUFFIX)
    day = int(m.group(DateKeys.DAY))
    month = int(m.group(DateKeys.MONTH))
    year = int(m.group(DateKeys.YEAR))

    # Fill in missing fields
    hour = int(hour) if hour is not None else 0
    minute = int(minute) if minute is not None else 0
    second = int(second) if second is not None else 0
    frac_seconds = float(frac_seconds) if frac_seconds is not None else 0.0

    # Validate seconds
    if not 0 <= second <= 59:
        raise FamParseError(f"invalid second value '{second}' (must be 0-59)", tok.start_pos, tok.end_pos)

    # Validate minute
    if not 0 <= minute <= 59:
        raise FamParseError(f"invalid minute value '{minute}' (must be 0-59)", tok.start_pos, tok.end_pos)

    # Validate hour
    if am_pm_suffix is None:
        if not 0 <= hour < 24:
            raise FamParseError(f"invalid hour for 24-hour time: '{hour}'", tok.start_pos, tok.end_pos)
    else:
        # Convert 12-hour to 24-hour time
        if not 1 <= hour <= 12:
            raise FamParseError(f"invalid hour for 12-hour time: '{hour}'", tok.start_pos, tok.end_pos)

        if hour == 12 and am_pm_suffix == 'am':
            hour = 0
        if hour != 12 and am_pm_suffix == 'pm':
            hour += 12

    # Validate day of month
    if not 1 <= day <= get_days_in_month(month, year):
        raise FamParseError(f"invalid day of month '{day}' for month '{month}' of year '{year}'", tok.start_pos, tok.end_pos)

    # Validate month
    if not 1 <= month <= 12:
        raise FamParseError(f"invalid month '{month}' (must be 1-12)", tok.start_pos, tok.end_pos)

    return Date(
        tok.start_pos, tok.end_pos,
        year, month, day,
        hour, minute, second, frac_seconds
    )

def parse_duration_literal(tok: Token) -> Duration:
    m = DURATION_RE.match(tok.string)
    assert m is not None

    days = m.group(DurationKeys.DAYS)
    hours = int(m.group(DurationKeys.HOURS))
    minutes = int(m.group(DurationKeys.MINUTES))
    seconds = m.group(DurationKeys.SECONDS)
    frac_seconds = m.group(DurationKeys.FRAC_SECONDS)

    # If seconds don't exist, but frac_seconds do,
    # treat the hours column as minutes and the minutes column as seconds.
    if seconds is None and frac_seconds is not None:
        seconds = minutes
        minutes = hours
        hours = 0

        # If this results in minutes >= 60,
        # carry them over to hours
        # Then if this results in hours >= 24, carry them over to days
        if minutes >= 60:
            hours += minutes // 60
            minutes = minutes % 60
        if hours >= 24:
            days = (int(days) or 0) + hours // 24
            hours = hours % 24

    # If days doesn't exist, carry over hours
    # in groups of 24 to days.
    # If days exists, throw errors for hours >= 24.
    if days is None:
        days = hours // 24
        hours = hours % 24
    else:
        if hours >= 24:
            raise FamParseError(f"invalid hours '{hours}' in duration (must be 0-23 if days are specified)", tok.start_pos, tok.end_pos)

    # Fill in missing fields
    days = int(days) if days is not None else 0
    seconds = int(seconds) if seconds is not None else 0
    frac_seconds = float(frac_seconds) if frac_seconds is not None else 0.0

    # Validate seconds
    if not 0 <= seconds <= 59:
        raise FamParseError(f"invalid seconds '{seconds}' in duration", tok.start_pos, tok.end_pos)

    # Validate minutes
    if not 0 <= minutes <= 59:
        raise FamParseError(f"invalid minutes '{minutes}' in duration", tok.start_pos, tok.end_pos)

    return Duration(
        tok.start_pos, tok.end_pos,
        days, hours, minutes, seconds, frac_seconds
    )

# Parsers for other primitives

def parse_name(self: Parser) -> Name:
    token = self.expect(TokenType.NAME)

    # Normalise for identifiers in parentheses
    # and for names with spaces, normalise whitespace
    # to one space per whitespace section

    no_parens = token.string.strip('()')
    components = tuple(no_parens.split())

    return Name(token.start_pos, token.end_pos, components)

# TODO: use this function in special cases where name streaks are allowed
# TODO: in here, if parsed as a name streak, keywords like 'Node' should be
# allowed to be treated as names
def parse_name_streak(self: Parser) -> Name:
    # This is for when the parser allows a name with spaces
    # to be included somewhere without surrounding parentheses,
    # so the name tokens will be parsed and then joined
    # by a space internally.
    sub_nodes: list[Name] = [parse_name(self)]

    while not self.eof() and self.peek().typ == TokenType.NAME:
        sub_nodes.append(parse_name(self))

    start_pos = sub_nodes[0].start_pos
    end_pos = sub_nodes[-1].end_pos
    name_components = tuple(comp for node in sub_nodes for comp in node.components)

    return Name(start_pos, end_pos, name_components)

def parse_comma_separated_exprs(self: Parser, start_tok: TokenType, end_tok: TokenType) -> Sequence:
    elems: list[Expr] = []

    start = self.expect(start_tok)

    while not self.eof():
        tok = self.advance()

        if tok.typ == end_tok:
            return Sequence(start.start_pos, tok.end_pos, elems)

        self.retreat()
        elems.append(parse_expr(self))

        next_tok = self.peek()

        if next_tok.typ == TokenType.COMMA:
            self.advance()
        elif next_tok.typ == end_tok:
            continue
        else:
            raise FamParseError("expected ',' after sequence element", next_tok.start_pos, next_tok.end_pos)

    raise FamParseError("unexpected EOF in sequence", self.tokens[-1].start_pos, self.tokens[-1].end_pos)

# Expression parsing

def parse_primary(self: Parser) -> Expr:
    token = self.advance()

    match token.typ:
        # Parentheses
        # If we see parentheses, any random mixed bag of
        # operations could have been shoved in there, so we have
        # to start from the very top again.
        case TokenType.L_PAREN:
            expr = parse_expr(self)
            end_tok = self.expect(TokenType.R_PAREN)
            expr.start_pos = token.start_pos
            expr.end_pos = end_tok.end_pos
            node = expr

        # Sequences
        case TokenType.L_BRACE:
            self.retreat()
            node = parse_comma_separated_exprs(self, TokenType.L_BRACE, TokenType.R_BRACE)

        # Integers and real numbers
        case TokenType.INTEGER:
            node = Integer(token.start_pos, token.end_pos, int(token.string))
        case TokenType.REAL:
            node = Real(token.start_pos, token.end_pos, float(token.string))

        # Strings
        case TokenType.STRING:
            node = String(token.start_pos, token.end_pos, token.string)

        # Dates and durations
        case TokenType.DATE:
            node = parse_date_literal(token)
        case TokenType.DURATION:
            node = parse_duration_literal(token)

        # Booleans and None
        case TokenType.TRUE:
            node = Boolean(token.start_pos, token.end_pos, True)
        case TokenType.FALSE:
            node = Boolean(token.start_pos, token.end_pos, False)
        case TokenType.NONE:
            node = NoneItem(token.start_pos, token.end_pos)

        # Names
        case TokenType.NAME:
            # Normalise for identifiers in parentheses
            self.retreat()
            node = parse_name(self)

        # Unexpected token
        case _:
            raise FamParseError(f"unexpected token {token.string!r}", start_pos=token.start_pos, end_pos=token.end_pos)

    # Parse subprimitives: indexing, method calls, attribute access
    while not self.eof() and (tok_typ := self.peek().typ) in (
        TokenType.DOT,
        TokenType.L_SQ_BRAC,
        TokenType.L_PAREN
    ):
        match tok_typ:
            # Attribute
            case TokenType.DOT:
                self.advance()
                attr_name = parse_name(self)

                node = AttributeAccess(
                    node.start_pos, attr_name.end_pos,
                    node, attr_name
                )

            # Indexing
            case TokenType.L_SQ_BRAC:
                self.advance()
                index_expr = parse_expr(self)
                r_bracket = self.expect(TokenType.R_SQ_BRAC)

                node = IndexOp(
                    node.start_pos, r_bracket.end_pos,
                    container=node,
                    index=index_expr
                )

            # Methods
            case TokenType.L_PAREN:
                args = parse_comma_separated_exprs(self, TokenType.L_PAREN, TokenType.R_PAREN)

                node = MethodCall(
                    node.start_pos, args.end_pos,
                    node, args.elems
                )

    return node

def parse_unary(self: Parser) -> Expr:
    # The '+' and '-' unary operators
    # need to be handled here.

    op_tok = self.advance()

    match op_tok.typ:
        case TokenType.BIN_ADD:
            operand = parse_unary(self)
            return PosOp(op_tok.start_pos, operand.end_pos, operand)
        case TokenType.BIN_SUB:
            operand = parse_unary(self)
            return NegOp(op_tok.start_pos, operand.end_pos, operand)
        case _:
            self.retreat()
            return parse_primary(self)

def parse_indices(self: Parser) -> Expr:
    terms = [parse_unary(self)]

    # Hold up...indices are weird. They're parsed from right to left.

    # Eat up the terms...
    while not self.eof() and self.peek().typ == TokenType.BIN_POW:
        self.advance()
        terms.append(parse_unary(self))

    # then build the tree from the right.
    node = terms.pop()
    for term in reversed(terms):
        node = PowOp(term.start_pos, node.end_pos, term, node)

    return node

def parse_multiplication(self: Parser) -> Expr:
    node = parse_indices(self)

    while not self.eof() and self.peek().typ in (TokenType.BIN_MUL, TokenType.BIN_DIV, TokenType.BIN_MODULO):
        op_tok = self.advance()
        right = parse_indices(self)

        match op_tok.typ:
            case TokenType.BIN_MUL:
                node = MultOp(node.start_pos, right.end_pos, node, right)
            case TokenType.BIN_DIV:
                node = DivOp(node.start_pos, right.end_pos, node, right)
            case TokenType.BIN_FLOOR_DIV:
                node = FloorDivOp(node.start_pos, right.end_pos, node, right)
            case TokenType.BIN_MODULO:
                node = ModuloOp(node.start_pos, right.end_pos, node, right)

    return node

def parse_addition(self: Parser) -> Expr:
    node = parse_multiplication(self)

    while not self.eof() and self.peek().typ in (TokenType.BIN_ADD, TokenType.BIN_SUB):
        op_tok = self.advance()
        right = parse_multiplication(self)

        match op_tok.typ:
            case TokenType.BIN_ADD:
                node = AddOp(node.start_pos, right.end_pos, node, right)
            case TokenType.BIN_SUB:
                node = SubOp(node.start_pos, right.end_pos, node, right)

    return node

def parse_bit_shifts(self: Parser) -> Expr:
    node = parse_addition(self)

    while not self.eof() and self.peek().typ in (TokenType.BIN_BIT_LSHIFT, TokenType.BIN_BIT_RSHIFT):
        op_tok = self.advance()
        right = parse_addition(self)

        match op_tok.typ:
            case TokenType.BIN_BIT_LSHIFT:
                node = BitLShift(node.start_pos, right.end_pos, node, right)
            case TokenType.BIN_BIT_RSHIFT:
                node = BitRShift(node.start_pos, right.end_pos, node, right)

    return node

def parse_chainable_comparators(self: Parser) -> Expr:
    terms: list[Expr] = [parse_bit_shifts(self)]
    ops: list[Token] = []

    # Chained comparisons like a >= b >= c are treated as a >= b and b >= c,
    # so eat all the terms then build a tree from the left.

    # Eat all the terms
    while not self.eof() and self.peek().typ in (
        TokenType.BIN_EQ,
        TokenType.BIN_NOT_EQ,
        TokenType.BIN_GREATER_THAN,
        TokenType.BIN_LESS_THAN,
        TokenType.BIN_GREATER_EQ,
        TokenType.BIN_LESS_EQ
    ):
        op_tok = self.advance()
        right = parse_bit_shifts(self)

        terms.append(right)
        ops.append(op_tok)

    # No ops recorded - return the first term
    if not ops:
        return terms[0]

    # Ops recorded - start building each of
    # the comparison nodes
    # len(terms) should be 1 more than len(ops)
    comparators: list[Expr] = []

    for lhs, rhs in itertools.pairwise(terms):
        op_tok = ops.pop(0)

        match op_tok.typ:
            case TokenType.BIN_EQ:
                node = EqOp(lhs.start_pos, rhs.end_pos, lhs, rhs)
            case TokenType.BIN_NOT_EQ:
                node = NotEqOp(lhs.start_pos, rhs.end_pos, lhs, rhs)
            case TokenType.BIN_GREATER_THAN:
                node = GtOp(lhs.start_pos, rhs.end_pos, lhs, rhs)
            case TokenType.BIN_LESS_THAN:
                node = LtOp(lhs.start_pos, rhs.end_pos, lhs, rhs)
            case TokenType.BIN_GREATER_EQ:
                node = GtEqOp(lhs.start_pos, rhs.end_pos, lhs, rhs)
            case TokenType.BIN_LESS_EQ:
                node = LtEqOp(lhs.start_pos, rhs.end_pos, lhs, rhs)
            case _:
                raise FamParseError(f"unexpected token {op_tok.string!r}", op_tok.start_pos, op_tok.end_pos)

        # Replace the left-hand side with the new node
        comparators.append(node)

    # At this point len(comparators) should be equal to len(ops)
    # Finally, join all the comparison
    # nodes using AndOps
    node = comparators.pop(0)

    for comp in comparators:
        node = AndOp(node.start_pos, comp.end_pos, node, comp)

    return node

# Bitwise operators
# Precedence order is ~ -> & -> ^ -> |

def parse_bitwise_unary_not(self: Parser) -> Expr:
    if not self.eof() and self.peek().typ == TokenType.BIN_BIT_NOT:
        op_tok = self.advance()
        operand = parse_bitwise_unary_not(self)
        return BitNotOp(op_tok.start_pos, operand.end_pos, operand)

    return parse_chainable_comparators(self)

def parse_bitwise_and(self: Parser) -> Expr:
    node = parse_bitwise_unary_not(self)

    while not self.eof() and self.peek().typ == TokenType.BIN_BIT_AND:
        self.advance()
        right = parse_bitwise_unary_not(self)
        node = BitAndOp(node.start_pos, right.end_pos, node, right)

    return node

def parse_bitwise_xor(self: Parser) -> Expr:
    node = parse_bitwise_and(self)

    while not self.eof() and self.peek().typ == TokenType.BIN_BIT_XOR:
        self.advance()
        right = parse_bitwise_and(self)
        node = BitXorOp(node.start_pos, right.end_pos, node, right)

    return node

def parse_bitwise_or(self: Parser) -> Expr:
    node = parse_bitwise_xor(self)

    while not self.eof() and self.peek().typ == TokenType.BIN_BIT_OR:
        self.advance()
        right = parse_bitwise_xor(self)
        node = BitOrOp(node.start_pos, right.end_pos, node, right)

    return node

# Identity and membership operators

def parse_identity_and_membership(self: Parser) -> Expr:
    node = parse_bitwise_or(self)

    while not self.eof() and self.peek().typ in (
        TokenType.BIN_IS,
        TokenType.BIN_IS_NOT,
        TokenType.IN,
        TokenType.BIN_NOT_IN
    ):
        op_tok = self.advance()
        right = parse_bitwise_or(self)

        match op_tok.typ:
            case TokenType.BIN_IS:
                node = IsOp(node.start_pos, right.end_pos, node, right)
            case TokenType.BIN_IS_NOT:
                node = IsNotOp(node.start_pos, right.end_pos, node, right)
            case TokenType.IN:
                node = InOp(node.start_pos, right.end_pos, node, right)
            case TokenType.BIN_IS:
                node = NotInOp(node.start_pos, right.end_pos, node, right)

    return node

# Logical operators
# Precedence order is not -> and -> or,
# in descending order for logical expressions.

def parse_unary_not(self: Parser) -> Expr:
    if not self.eof() and self.peek().typ == TokenType.UN_NOT:
        op_tok = self.advance()
        operand = parse_unary_not(self)
        return NotOp(op_tok.start_pos, operand.end_pos, operand)

    return parse_identity_and_membership(self)

def parse_logical_and(self: Parser) -> Expr:
    node = parse_unary_not(self)

    while not self.eof() and self.peek().typ == TokenType.BIN_AND:
        self.advance()
        right = parse_unary_not(self)
        node = AndOp(node.start_pos, right.end_pos, node, right)

    return node

def parse_logical_or(self: Parser) -> Expr:
    node = parse_logical_and(self)

    while not self.eof() and self.peek().typ == TokenType.BIN_OR:
        self.advance()
        right = parse_logical_and(self)
        node = OrOp(node.start_pos, right.end_pos, node, right)

    return node

def parse_expr(self: Parser) -> Expr:
    return parse_logical_or(self)
