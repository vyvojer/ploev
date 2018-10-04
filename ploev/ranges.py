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

from typing import Iterable
from ploev.easy_range import check_range, EasyRangeValueError
from ploev.game import SubRange
import pickle
import os


class Tag:

    def __init__(self, name=None, parent: 'Tag' = None):
        if name is not None:
            self.name = name
        else:
            self.name = ''
        self.parent = parent
        self.children = []

    def add_tag(self, tag: 'Tag'):
        self.children.append(tag)
        tag.parent = self

    def add_tags(self, tags: Iterable['Tag']):
        for tag in tags:
            tag.parent = self
        self.children.extend(tags)

    def is_leaf(self) -> bool:
        return not bool(self.children)

    def is_root(self) -> bool:
        return self.parent is None


class SubRanges:

    def __init__(self, name,
                 sub_ranges: Iterable[SubRange] = None,
                 tags: Iterable[Tag] = None):
        self.name = name
        if sub_ranges is not None:
            self.sub_ranges = list(sub_ranges)
        else:
            self.sub_ranges = []
        if tags is not None:
            self.tags = list(tags)
        else:
            self.tags = []

    def add_sub_range(self, sub_range: SubRange):
        self.sub_ranges.append(sub_range)


class RangesList:

    def __init__(self, root_tag: Tag):
        self.root_tag = root_tag
        self.sub_ranges = []

    def add_sub_ranges(self, sub_ranges: SubRanges):
        self.sub_ranges.append(sub_ranges)
