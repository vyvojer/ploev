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
from easy_range import check_range, EasyRangeValueError
from abc import ABC
import json


class _ChildMixin(ABC):
    """ Abstract mixin implementing class having parent """
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


class RangeGroup(_ChildMixin):
    """ Class implementing postflop (easy_range) range group"""
    def __init__(self, name: str, parent=None, children: Iterable=None, descriptions: list=None):
        """ Counstructor for PostflopRanges

        Args:
            name(str): name of group
            parent(RangeGroup): parent group
            children(Iterable): list of range group(RangeGroup) or concrete ranges(PostflopRange)
            descriptions(list): list of descriptions for children's sub_ranges. For example: ['raise', 'call', 'fold'].
                If description isn't set then uses one of parent's description
        """
        self.name = name
        _ChildMixin.__init__(self, parent)
        if children is None:
            self.children = []
        else:
            self.children = list(children)
        self._descriptions = descriptions
        self._has_error = False

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(name="{self.name}", parent={self.parent}, descriptions={self._descriptions})'

    def __eq__(self, other):
        return self.name == other.name \
               and self._descriptions == other._descriptions \
               and self.children == other.children

    def str_ancestors(self):
        """ Return str of all ancestors"""
        if self.parent is not None:
            return f'{self.parent.str_ancestors()} > {self.name}'
        else:
            return f'{self.name}'

    def __getattr__(self, attr):
        children_by_name = {child.name: child for child in self.children}
        child = children_by_name.get(attr)
        if child:
            return child
        else:
            raise AttributeError(attr)

    def add_child(self, child):
        """ Add child """
        self.children.append(child)
        child._parent = self

    def remove_child(self, child):
        """ Remove child """
        self.children.remove(child)

    @property
    def has_children(self):
        """ True if has children  """
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

    @property
    def has_error(self):
        """ True if checked (by check_sub_ranges())children sub ranges has errors"""
        return self._has_error

    def check_sub_ranges(self, print_error: bool=True):
        """ Check children's sub_ranges for error

        Args:
            print_error(bool): if True (default) print error message

        """
        self._has_error = False
        for child in self.children:
            child.check_sub_ranges(print_error)
            if child.has_error:
                self._has_error = True

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
        """ Save the range group to json file """
        with open(file_name, 'w') as file:
            json.dump(self, file, indent=2, default=_json_default)

    @staticmethod
    def load(file_name: str):
        """ Load new range group from json file """
        with open(file_name) as file:
            return json.load(file, object_hook=_json_object_hook)

    @staticmethod
    def load_and_check(file_name: str, print_error=True):
        """ Load new ragne group from json file and check for sub ranges error """
        ranges = RangeGroup.load(file_name)
        ranges.check_sub_ranges(print_error)
        return ranges


class PostflopRange(_ChildMixin):
    """ Class implementing concrete postflop ranges"""
    def __init__(self, name, sub_ranges: list, parent: RangeGroup=None, descriptions: list=None):
        """

        Args:
            name(str): name of the range
            sub_ranges(list): list of sub_ranges
            parent(RangeGroup): parent range group
            descriptions(list): list of descriptions for the sub_ranges. For example: ['raise', 'call', 'fold'].
                If description isn't set then uses one of parent's description
        """
        self.name = name
        _ChildMixin.__init__(self, parent)
        self._sub_ranges = sub_ranges
        self._descriptions = descriptions
        self._has_error = False
        self._errors = []

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(name="{self.name}, parent={self.parent}, descriptions={self._descriptions}'

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
            return ["r_{}".format(range_number + 1) for range_number in range(len(self.sub_ranges))]

    @property
    def has_error(self):
        """ True if the sub_ranges has error"""
        return self._has_error

    @property
    def errors(self):
        """ Appropriate List of EasyRangeValueError for the sub_ranges"""
        return self._errors

    def __getattr__(self, attr):
        try:
            index = self.descriptions.index(attr)
        except ValueError:
            raise AttributeError(attr)
        else:
            return self.sub_ranges[index]

    def str_ancestors(self):
        if self.parent is not None:
            return f'{self.parent.str_ancestors()} > {self.name}'
        else:
            return f'{self.name}'

    def check_sub_ranges(self, print_error=True):
        """ Check the sub_ranges for error

        Args:
            print_error(bool): if True (default) print error message

        """
        self._errors = []
        self._has_error = False
        for description, sub_range in zip(self.descriptions, self.sub_ranges):
            try:
                check_range(sub_range)
            except EasyRangeValueError as error:
                self._errors.append(error)
                self._has_error = True
                if print_error:
                    print(f'{self.str_ancestors()}\n {description} = {sub_range}\n {error}')
            else:
                self._errors.append(None)

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
        posflop_ranges = RangeGroup(ranges_dict['name'],
                                    children=ranges_dict.get('ranges'),
                                    descriptions=descriptions)
        for child in posflop_ranges.children:
            child._parent = posflop_ranges
        return posflop_ranges
    if ranges_dict.get('sub_ranges') is not None:  # PoslfopRange
        return PostflopRange(ranges_dict['name'],
                             sub_ranges=ranges_dict.get('sub_ranges'),
                             descriptions=descriptions)


def _name_to_attr(name: str):
    if name == 'parent':
        return 'parent_'
    elif name == 'name':
        return 'name_'
    elif name == 'descriptions':
        return 'descriptions_'
    else:
        return name.replace(' ', '_')