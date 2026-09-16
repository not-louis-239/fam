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



import re

# Regex for splitting lexed tokens for DATE and DURATION

# Dates
DATE_RE = re.compile(r'(?:(?P<hour>[0-2]?[0-9]):(?P<minute>[0-5][0-9])(?::(?P<second>[0-5][0-9])(?P<fracSeconds>\.[0-9]*)?)?\s+(?:(?P<amPmSuffix>am|pm)\s+)?)?(?P<day>[0-3]?[0-9])-(?P<month>[0-1]?[0-9])-(?P<year>[0-9]+)')

# Durations
DURATION_RE = re.compile(r'(?:(?P<days>[0-9]+)d\s+)?(?P<hours>[0-9]+):(?P<minutes>[0-5][0-9])(:(?P<seconds>[0-5][0-9]))?(?P<fracSeconds>\.[0-9]*)?')
