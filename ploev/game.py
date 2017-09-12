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
from ploev.cards import Board
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
    BB = 8
    SB = 9
    BTN = 0
    CO = 1
    HJ = 2
    UTG = 3


class ActionType(Enum):
    BET = 'Bet'
    RAISE = 'Raise'
    CHECK = 'Check'
    CALL = 'Call'
    FOLD = 'Fold'
    POST_BLIND = 'Post'


class Action:
    def __init__(self, type_: ActionType, size: float = None, min_size: float = None, max_size: float = None):
        self.type_ = type_
        self.size = size
        self._is_sizable = False
        self._is_different_sizes_possible = False
        if min_size is None or max_size is None:
            self.min_size = size
            self.max_size = size
        else:
            self.min_size = min_size
            self.max_size = max_size
        self._set_sizable()
        self._set_different_size_possible()

    @property
    def is_sizable(self):
        return self._is_sizable

    def _set_sizable(self):
        if self.type_ in [ActionType.CHECK, ActionType.FOLD]:
            self._is_sizable = False
        else:
            self._is_sizable = True

    def _set_different_size_possible(self):
        if self.type_ in [ActionType.BET, ActionType.RAISE]:
            self._is_different_sizes_possible = True
        else:
            self._is_different_sizes_possible = False

    def __eq__(self, other):
        return self.type_ == other.type_ and self.size == other.size \
               and self.min_size == other.min_size and self.max_size == other.max_size

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(type_={self.type_}, size={self.size}, min_size={self.min_size}, max_size={self.max_size})'

    def __str__(self):
        if self._is_sizable:
            return f'{self.type_.value} {self.size}'
        else:
            return f'{self.type_.value}'


class Player:
    def __init__(self, position: Position, stack: float, name: str = None, is_hero: bool = False):
        self.position = position
        if name is not None:
            self.name = name
        else:
            self.name = position.name
        self.stack = stack
        self._is_hero = True
        self._is_villain = True
        self.is_hero = is_hero
        self.is_active = True
        self.in_action = False
        self.action = None
        self.invested_in_bank = 0

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
        return f"{cls_name}(position={self.position}, stack={self.stack}, name='{self.name}')"

    def clone(self):
        return copy.deepcopy(self)

    def restore(self, state):
        """ Restore state of Player from cloned Player"""
        for key, value in vars(state).items():
            if not key.startswith('_'):
                setattr(self, key, value)


class Street(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4


class GameState:
    def __init__(self, players: Iterable, pot: float = 0, board: Board = None):
        self.players = {player.position: player for player in players}
        if len(list(players)) != len(self.players):
            raise ValueError("More than one player with same position")
        self.pot = pot
        self._possible_actions = None
        self.in_action_position = None
        self._board = None
        self.street = None
        self._flop = None
        self._turn = None
        self._river = None
        if board is None:
            board = Board()
        self.board = board
        self.in_action_position = max(self.active_positions, key=lambda position: position.value)
        self._is_round_closed = False
        self._last_aggressor = None
        self._previous_action = None

    def __repr__(self):
        cls_name = self.__class__.__name__
        players = [player for player in self.players.values()]
        return f'{cls_name}(players={players}, pot={self.pot}, board={self.board!r})'

    @property
    def board(self) -> Board:
        return self._board

    @board.setter
    def board(self, board: Board):
        if len(board) not in [0, 3, 4, 5]:
            raise ValueError("Wrong board", board)
        self._board = board
        self._flop = None
        self._turn = None
        self._river = None
        if len(board) == 0:
            self.street = Street.PREFLOP
        elif len(board) == 3:
            self.street = Street.FLOP
            self._flop = board
        elif len(board) == 4:
            self.street = Street.TURN
            self._flop = board[0:3]
            self._turn = board
        elif len(board) == 5:
            self.street = Street.RIVER
            self._flop = board[0:3]
            self._turn = board[0:4]
            self._river = board

    @property
    def positions(self):
        return sorted([player.position for player in self.players.values()],
                      key=lambda position: position.value, reverse=True)

    @property
    def active_positions(self):
        return sorted([player.position for player in self.players.values() if player.is_active],
                      key=lambda position: position.value, reverse=True)

    @property
    def last_position_player(self):
        return self.get_player(self.active_positions[-1])

    @property
    def first_position_player(self):
        return self.get_player(self.active_positions[0])

    @property
    def player_in_action(self):
        """ Return the player in action"""
        return self.get_player(self.in_action_position)

    @property
    def possible_actions(self) -> list:
        return self._possible_actions

    def next_street(self):
        st_value = self.street.value
        if st_value < 4:
            st_value += 1
            self.street = Street(st_value)

    @staticmethod
    def _count_pot_raise(call_size: float, pot: float) -> float:
        return call_size * 2 + pot

    def _determine_possible_actions(self):
        self._possible_actions = []
        player_in_action = self.player_in_action
        if self._previous_action is None:
            return

        action_raise = None
        action_call = None
        if self._previous_action.type_ in [ActionType.RAISE, ActionType.CALL, ActionType.BET, ActionType.POST_BLIND]:
            pot_raise = self._count_pot_raise(self._previous_action.size, self.pot)
            action_raise = Action(ActionType.RAISE,
                                  size=pot_raise,
                                  min_size=self._previous_action.size * 2,
                                  max_size=pot_raise)
            action_call = Action(ActionType.CALL, size=self._previous_action.size - player_in_action.invested_in_bank)
        action_bet = Action(ActionType.BET, size=self.pot, min_size=1, max_size=self.pot)
        action_check = Action(ActionType.CHECK)
        action_fold = Action(ActionType.FOLD)
        action_post_bb = Action(ActionType.POST_BLIND, size=1)

        if self.street == Street.PREFLOP and player_in_action.position == Position.BB:
            # Special situations with BB
            if player_in_action.position == Position.BB:
                # SB posted small blind, BB must post big blind
                if self._previous_action.type_ == ActionType.POST_BLIND:
                    self._possible_actions.append(action_post_bb)
                # SB completed, BB can check and close round or reopen round by raise
                elif self._previous_action.type_ == ActionType.CALL and self._previous_action.size == 1:
                    self._possible_actions.append(action_check)
        else:
            if self._previous_action.type_ == ActionType.CHECK or self._is_round_closed:
                self._possible_actions.append(action_bet)
                self._possible_actions.append(action_check)
            elif self._previous_action.type_ in [ActionType.RAISE, ActionType.BET, ActionType.CALL,
                                                 ActionType.POST_BLIND]:
                self._possible_actions.append(action_raise)
                self._possible_actions.append(action_call)
                self._possible_actions.append(action_fold)

    def get_next_action_player(self):
        """ Return the player who is next in action"""
        current_index = self.active_positions.index(self.player_in_action.position)
        if current_index < len(self.active_positions) - 1:
            next_position = self.active_positions[current_index + 1]
        else:
            next_position = self.active_positions[0]
        return self.get_player(next_position)

    def get_player(self, position: Position) -> Player:
        return self.players[position]

    def set_hero(self, position: Position):
        for player in self.players.values():
            player.is_hero = False
        self.get_player(position).is_hero = True

    def set_player_in_action(self, player: Player):
        for pl in self.players.values():
            pl.in_action = False
        player.in_action = True
        self.in_action_position = player.position
        self._determine_possible_actions()

    def make_action(self, action: Action):
        if self.possible_actions:
            for possible_action in self.possible_actions:
                if action.type_ == possible_action.type_:
                    break
            else:
                raise ValueError(f"Action is not possible, only {self.possible_actions} are possible", action)
            if action.is_sizable and (action.size < possible_action.min_size or action.size > possible_action.max_size):
                message = "Action size is not possible, size must be between {} and {}"
                raise ValueError(message.format(possible_action.min_size, possible_action.max_size), action.size)
        for player in self.players.values():
            player.action = None
        self.player_in_action.action = action
        self._is_round_closed = False

        if action.is_sizable:
            self.pot += action.size
            self.player_in_action.stack -= action.size
            self.player_in_action.invested_in_bank = action.size
        if action.type_ != ActionType.FOLD:
            self._previous_action = action
        if action.type_ in [ActionType.RAISE, ActionType.BET]:
            self._last_aggressor = self.player_in_action
        if action.type_ == ActionType.POST_BLIND:
            self._last_aggressor = self.get_next_action_player()
        if action.type_ in [ActionType.CALL, ActionType.FOLD] and self.get_next_action_player() == self._last_aggressor:
            self._is_round_closed = True
        elif action.type_ == ActionType.CHECK:
            if self.player_in_action == self.last_position_player:
                self._is_round_closed = True
            # Special situation: BB close preflop round after SB completing
            elif self.player_in_action.position == Position.BB and self.street == Street.PREFLOP:
                self._is_round_closed = True
        if self._is_round_closed:
            for player in self.players.values():
                player.invested_in_bank = 0
            self.set_player_in_action(self.first_position_player)
            self.next_street()
            self._last_aggressor = None
        else:
            self.set_player_in_action(self.get_next_action_player())

    def clone(self):
        return copy.deepcopy(self)

    def restore_state(self, state):
        for position, player in self.players.items():
            self.players[position].restore(state.players[position])
        self.pot = state.pot
        self.board = state.board
        self._possible_actions = state.possible_actions
        self.in_action_position = state.in_action_position
        self._is_round_closed = state._is_round_closed
        self._last_aggressor = state._last_aggressor
        self._previous_action = state._previous_action


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


class GameTree:
    def __init__(self, game: GameState):
        self.game = game

