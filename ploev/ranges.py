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

from easy_range import check_range
import json

class _ChildMixin:
    def __init__(self, parent):
        self._parent = None
        self.parent = parent

    @property
    def parent(self):
        return self._parent

    @parent.deleter
    def parent(self):
        if self.parent is not None:
            self.parent.remove_child(self)

    @parent.setter
    def parent(self, parent):
        del self.parent
        self._parent = parent
        if parent is not None:
            parent.add_child(self)


class PostflopRanges(_ChildMixin):
    def __init__(self, name: str, parent=None, descriptions: list = None):
        self.name = name
        _ChildMixin.__init__(self, parent)
        self.children = []
        self._descriptions = descriptions

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(name="{self.name}", parent={self.parent}, descriptions={self.descriptions})'

    def __eq__(self, other):
        return self.name == other.name \
               and self._descriptions == other._descriptions \
               and self.children == other.children

    def add_child(self, child):
        self.children.append(child)
        child._parent = self
        setattr(self, child.name, child)

    def remove_child(self, child):
        self.children.remove(child)

    @property
    def has_children(self):
        return len(self.children) > 0

    @property
    def descriptions(self):
        if self._descriptions is not None:
            return self._descriptions
        else:
            if self.parent is None:
                return None
            else:
                return self.parent.descriptions

    @staticmethod
    def _to_dict(postflop_ranges):
        pf_ranges = dict()
        pf_ranges['name'] = postflop_ranges.name
        if postflop_ranges._descriptions is not None:
            pf_ranges['descriptions'] = postflop_ranges._descriptions
        if isinstance(postflop_ranges, PostflopRanges):
            ranges = []
            if postflop_ranges.has_children:
                for child in postflop_ranges.children:
                    ranges.append(PostflopRanges._to_dict(child))
            pf_ranges['ranges'] = ranges
        else:  # PosflopRange
            pf_ranges['sub_ranges'] = postflop_ranges.sub_ranges
        return pf_ranges

    @staticmethod
    def _from_dict(ranges_dict: dict, parent=None):
        descriptions = ranges_dict.get('descriptions')
        if ranges_dict.get('ranges') is not None:  # PosflopRanges
            postflop_ranges = PostflopRanges(ranges_dict['name'], parent=parent, descriptions=descriptions)
            if ranges_dict.get('ranges'):  # has children
                for child_dict in ranges_dict.get('ranges'):
                    PostflopRanges._from_dict(child_dict, postflop_ranges)
            return postflop_ranges
        if ranges_dict.get('sub_ranges') is not None:  # PoslfopRange
            posflop_range = PostflopRange(ranges_dict['name'],
                                          parent=parent,
                                          sub_ranges=ranges_dict.get('sub_ranges'),
                                          descriptions=descriptions)
            return posflop_range

    def save(self, file_name: str):
        pr_dict = self._to_dict(self)
        with open(file_name, 'w') as file:
            json.dump(pr_dict, file, indent=4)

    @staticmethod
    def load(file_name: str):
        with open(file_name) as file:
            pr_dict = json.load(file)
            return PostflopRanges._from_dict(pr_dict)

class PostflopRange(_ChildMixin):
    def __init__(self, name, sub_ranges: list, parent: PostflopRanges = None, descriptions: list = None):
        self.name = name
        _ChildMixin.__init__(self, parent)
        self._sub_ranges = sub_ranges
        self._descriptions = descriptions
        self._set_descriptions_attrs()

    def __eq__(self, other):
        return self.name == other.name\
               and self.sub_ranges == other.sub_ranges\
               and self._descriptions == other._descriptions

    @property
    def sub_ranges(self):
        return self._sub_ranges

    @property
    def descriptions(self):
        if self._descriptions is not None:
            return self._descriptions
        elif self.parent is not None and self.parent.descriptions is not None:
            return self.parent.descriptions
        else:
            return ["r_{}".format(range_number) for range_number in range(len(self.sub_ranges))]

    def _set_descriptions_attrs(self):
        for description, sub_range in zip(self.descriptions, self.sub_ranges):
            setattr(self, description, sub_range)
