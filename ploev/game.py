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

from enum import Enum
import copy


class SubRange:
    def __init__(self, sub_range, name=''):
        self.sub_range = sub_range
        self.name = name

    def __repr__(self):
        class_name = type(self).__name__
        return '{}(sub_range={}, name={})'.format(
            class_name,
            repr(self.sub_range), repr(self.name))


class Ranges:
    def __init__(self, sub_ranges, name='', cumulative=True):
        self._sub_ranges = list(sub_ranges)
        self.name = name
        self.cumulative = cumulative
        self._cumulative_ranges = None

    @property
    def sub_ranges(self):
        if self.cumulative:
            if self._cumulative_ranges is None:
                self.create_cumulative_ranges()
            return self._cumulative_ranges
        else:
            return self._sub_ranges

    @sub_ranges.setter
    def sub_ranges(self, value):
        self._sub_ranges = value
        self._cumulative_ranges = None

    def create_cumulative_ranges(self):
        cum_ranges = []
        for i, r in enumerate(self._sub_ranges):
            cum_range = copy.copy(r)
            exclusion = "!".join(['(' + er.sub_range + ')' for er in self._sub_ranges[:i]])
            if exclusion:
                cum_range.sub_range = '(' + r.sub_range + ')!' + exclusion
            cum_ranges.append(cum_range)
        self._cumulative_ranges = cum_ranges

    def __repr__(self):
        class_name = type(self).__name__
        return '{}(sub_ranges={}, name={}, cumulative={})'.format(
            class_name,
            repr(self.sub_ranges),
            repr(self.name),
            repr(self.cumulative)
        )


class LineType(Enum):
    unknown = 0
    check_call = 1
    check_fold = 2
    check_raise = 3


class Line:
    def __init__(self, sub_range, name='', line=LineType.unknown, equity=0, percentage=0):
        self.sub_range = sub_range
        self.line = line
        self.name = name
        self.equity = equity
        self.percentage = percentage

    def __repr__(self):
        class_name = type(self).__name__
        return '{class_name}(sub_range={sr}, name={n}, line={l}, equity={e}, percentage={p})'.format(
            class_name=class_name,
            sr=repr(self.sub_range), n=repr(self.name), l=self.line, e=self.equity, p=self.percentage
        )


class PlayerLines:
    def __init__(self, ranges, main_range=None):
        self.ranges = list(ranges)
        self.main_range = main_range

    def normalize_lines(self):
        pass


class Position(Enum):
    utg = 0
    mp = 1
    co = 2
    btn = 3
    sb = 4
    bb = 5


class Player:

    def __init__(self, name, position, stack, hero=True, villain=False, active=True):
        self.name = name
        self.position = position
        self.stack = stack
        self.hero = hero
        self.villain = villain
        self.active = active


class Pot:

    def __init__(self, size):
        self.size = size

    def add(self, chips):
        self.size =+ chips


class PlayerActionType(Enum):
    bet = 0
    raise_ = 1
    check = 2
    call = 3
    fold = 4


class PlayerAction:

    def __init__(self, type, size):
        self.type = type
        self.size = size


class Game:

    def __init__(self, players, pot):
        self.players = list(players)
        self.pot = pot

    @property
    def spr(self):
        return 0
