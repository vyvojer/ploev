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
    def __init__(self, name: str, parent=None, children=None, descriptions: list = None):
        self.name = name
        _ChildMixin.__init__(self, parent)
        if children is None:
            self.children = []
        else:
            self.children = children
            self._set_descriptions_attrs()
        self._descriptions = descriptions

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(name="{self.name}", parent={self.parent}, descriptions={self.descriptions})'

    def __eq__(self, other):
        return self.name == other.name \
               and self._descriptions == other._descriptions \
               and self.children == other.children

    def _set_descriptions_attrs(self):
        for child in self.children:
            setattr(self, child.name, child)

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
    def _json_default(preflop_ranges):
        if preflop_ranges._descriptions:
            return {'name': preflop_ranges.name,
                    'descriptions': preflop_ranges._descriptions,
                    'ranges': preflop_ranges.children}
        else:
            return {'name': preflop_ranges.name,
                    'ranges': preflop_ranges.children}

    def save(self, file_name: str):
        with open(file_name, 'w') as file:
            json.dump(self, file, indent=4, default=_json_default)

    @staticmethod
    def load(file_name: str):
        with open(file_name) as file:
            return json.load(file, object_hook=_json_object_hook)


class PostflopRange(_ChildMixin):
    def __init__(self, name, sub_ranges: list, parent: PostflopRanges = None, descriptions: list = None):
        self.name = name
        _ChildMixin.__init__(self, parent)
        self._sub_ranges = sub_ranges
        self._descriptions = descriptions
        self._set_descriptions_attrs()

    def __eq__(self, other):
        return self.name == other.name \
               and self.sub_ranges == other.sub_ranges \
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

    @staticmethod
    def _json_default(preflop_range):
        if preflop_range._descriptions:
            return {'name': preflop_range.name,
                    'descriptions': preflop_range._descriptions,
                    'sub_ranges': preflop_range.sub_ranges}
        else:
            return {'name': preflop_range.name,
                    'sub_ranges': preflop_range.sub_ranges}


def _json_default(object):
    return object._json_default(object)


def _json_object_hook(ranges_dict):
    descriptions = ranges_dict.get('descriptions')
    if ranges_dict.get('ranges') is not None:  # PosflopRanges
        posflop_ranges = PostflopRanges(ranges_dict['name'],
                              children=ranges_dict.get('ranges'),
                              descriptions=descriptions)
        for child in posflop_ranges.children:
            child._parent = posflop_ranges
        return posflop_ranges
    if ranges_dict.get('sub_ranges') is not None:  # PoslfopRange
        return PostflopRange(ranges_dict['name'],
                             sub_ranges=ranges_dict.get('sub_ranges'),
                             descriptions=descriptions)
