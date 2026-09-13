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


class FamException(Exception):
    pass


class FamParseError(FamException):
    def __init__(self, msg: str, pos: int, src_code: str):
        super().__init__(msg)
        self.msg = msg
        self.pos = pos
        self.src_code = src_code


class FamIndentationError(FamParseError):
    pass


class FamTabError(FamIndentationError):
    pass


class FamTypeError(FamException):
    pass


class FamConstraintError(FamException):
    pass


class FamIndexError(FamException):
    pass


class FamReferenceError(FamException):
    pass


class FamAttributeError(FamException):
    pass


class FamAmbiguityError(FamException):
    pass


class FamMissingModuleError(FamException):
    pass
