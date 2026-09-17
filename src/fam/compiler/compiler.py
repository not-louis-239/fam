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


from fam.compiler.stages.lexer import Lexer
from fam.compiler.stages.parser import Parser
from fam.compiler.utils.nodes import AST


class FamCompiler:
    def __init__(self) -> None:
        self.lexer = Lexer()
        self.parser = Parser()

    def compile_src(self, src_code: str) -> AST:
        tokens = self.lexer.lex(src_code)
        ast = self.parser.parse(tokens)
        return ast
