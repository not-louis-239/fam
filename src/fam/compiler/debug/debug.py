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


from fam.compiler.utils.tokens import Token
from fam.utils import pos_to_line_col
from fam.compiler.utils.nodes import AST, ASTNode


def visualise_tokens(tokens: list[Token], src_code: str | None = None) -> None:
    for i, tok in enumerate(tokens, start=1):
        if src_code is not None:
            # Make a representation of the token that is easier to understand:
            line, col = pos_to_line_col(src_code, tok.start_pos)
            print(f"    \033[94m{i: 3d}.\033[0m \033[33m{tok.typ}\033[0m \033[92m{f"'{tok.string.replace('\n', '\\n')}'"}\033[0m at line \033[95m{line + 1}\033[0m, position \033[95m{col + 1}\033[0m")
        else:
            print(f"    \033[94m{i: 3d}.\033[0m \033[33m{tok.typ}\033[0m \033[92m{f"'{tok.string.replace('\n', '\\n')}'"}\033[0m at chars \033[95m{tok.start_pos + 1} - {tok.end_pos + 1}\033[0m")


def _dump_node(node: ASTNode, padding: int = 0, indent: int = 4):
    print(f"\033[94m{' ' * padding}{type(node).__name__}\033[0m @ \033[95m{node.start_pos} - {node.end_pos}\033[0m:")
    for name, value in vars(node).items():
        if name in ("start_pos", "end_pos"):
            continue
        if isinstance(value, ASTNode):
            print(f"\033[93m{' ' * (padding + indent)}{name}\033[0m: ")
            _dump_node(value, padding + 2 * indent)
            continue

        if isinstance(value, list) and all(isinstance(e, ASTNode) for e in value):
            print(f"\033[93m{' ' * (padding + indent)}{name}\033[0m: ")
            dump_ast(value, padding + 2 * indent)
            continue

        print(f"{' ' * (padding + indent)}\033[93m{name}\033[0m: \033[96m{value!r}\033[0m")

def dump_ast(ast: AST, padding: int = 0, indent: int = 4):
    for node in ast:
        _dump_node(node, padding, indent)
