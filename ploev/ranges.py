# ploev
# Copyright (C) 2017 Alexey Londkevich <vyvojer@gmail.com>

# ploev is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ploev is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Classes implementing ranges. """

from typing import Iterable, Union
from ploev.easy_range import check_range, EasyRangeValueError
import pickle
import os


class Tag:

    def __init__(self, name, parent: 'Tag'=None):
        self.name = name
        self.parent = parent
        self.children = []

    def add_tag(self, tag: 'Tag'):
        self.children.append(tag)
        tag.parent = self

    def add_tags(self, tags: Iterable['Tag']):
        for tag in tags:
            tag.parent = self
        self.children.extend(tags)


class SubRanges:

    def __init__(self, name):
        self.name = name