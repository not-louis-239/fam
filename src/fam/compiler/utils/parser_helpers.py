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

from fam.compiler.utils.expression_parsers import parse_expr, parse_name
from fam.compiler.utils.nodes import (
    AST,
    Name,
    KeyValuePair
)
from fam.compiler.utils.tokens import TokenType


# Helper parser functions

def parse_attribute(self: Parser) -> KeyValuePair:
    attribute_name = self.expect(TokenType.NAME)
    self.expect(TokenType.COLON)
    expr = parse_expr(self)
    self.expect(TokenType.NEWLINE)

    return KeyValuePair(
        attribute_name.start_pos,
        expr.end_pos,
        Name(
            attribute_name.start_pos,
            attribute_name.end_pos,
            attribute_name.string
        ),
        expr
    )

def parse_code_block(self: Parser) -> AST:
    ...
