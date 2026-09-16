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


from fam.compiler.utils.tokens import TokenType

NESTING_INC_TOKENS = (TokenType.L_BRACE, TokenType.L_PAREN, TokenType.L_SQ_BRAC)
NESTING_DEC_TOKENS = (TokenType.R_BRACE, TokenType.R_PAREN, TokenType.R_SQ_BRAC)

NESTING_PAIRS = {
    TokenType.L_BRACE: TokenType.R_BRACE,
    TokenType.L_PAREN: TokenType.R_PAREN,
    TokenType.L_SQ_BRAC: TokenType.R_SQ_BRAC,
}

BRACKET_CHARS = {
    TokenType.L_BRACE: '{',
    TokenType.R_BRACE: '}',
    TokenType.L_PAREN: '(',
    TokenType.R_PAREN: ')',
    TokenType.L_SQ_BRAC: '[',
    TokenType.R_SQ_BRAC: ']',
}