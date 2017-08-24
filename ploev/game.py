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
from typing import Iterable


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
    bb = 0
    sb = 1
    btn = 2
    co = 3
    hj = 4
    utg = 5


class Player:

    def __init__(self, position: Position, stack: float, name: str=None, is_hero=True):
        self.name = name
        self.position = position
        self.stack = stack
        self._is_hero = True
        self._is_villain = True
        self.is_hero = is_hero
        self.is_active = True
        self.players = None

    @property
    def is_hero(self):
        return self._is_hero

    @is_hero.setter
    def is_hero(self, value: bool):
        self._is_hero = value
        self._is_villain = not value

    @property
    def is_villain(self):
        return self._is_villain

    @is_villain.setter
    def is_villain(self, value: bool):
        self._is_villain = value
        self._is_hero = not value

    def __repr__(self):
        cls_name = self.__class__.__name__
        repr = f"{cls_name}(position={self.position}, stack={self.stack}, name='{self.name}')"
        return repr


class PlayerList:

    def __init__(self, players: Iterable):
        self.players = {player.position: player for player in players}
        if len(list(players)) != len(self.players):
            raise ValueError("More than one player with same position")

    def get_player(self, position: Position):
        return self.players[position]

    @property
    def positions(self):
        return sorted([player.position for player in self.players.values()],
                      key=lambda position: position.value)

    @property
    def active_positions(self):
        return sorted([player.position for player in self.players.values() if player.is_active],
                      key=lambda position: position.value)


class PlayerState:
    pass


class PlayersState:
    pass


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


class GameState:

    def __init__(self, pot):
        self.pot = pot

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(pot={self.pot})'


class Game:

    def __init__(self, players: Iterable, pot):
        self.players = list(players)
        self.pot = pot

    def save_state(self):
        game_state = GameState(pot=self.pot)
        return game_state

    def restore_state(self, state: GameState):
        self.pot = state.pot


class GameFlow:

    def __init__(self, states: Iterable):
        self.states = list(states)
        self._pointer = 0
        self.pointer = 0

    @property
    def pointer(self):
        return self._pointer

    @pointer.setter
    def pointer(self, value):
        min_value = 0
        max_value = len(self.states) - 1
        if value < 0:
            self._pointer = 0
        elif value > max_value:
            self._pointer = max_value
        else:
            self._pointer = value

    def get_state(self):
        return self.states[self.pointer]

    def next(self):
        self.pointer += 1
        return self.get_state()

    def previous(self):
        self.pointer -= 1
        return self.get_state()
