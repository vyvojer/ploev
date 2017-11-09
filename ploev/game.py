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

from abc import ABC, abstractmethod
from enum import Enum
import copy
from typing import Iterable

import logging

from easy_range import BoardExplorer
from ploev.ppt import OddsOracle
from ploev.cards import Board
from ploev.calc import close_parenthesis, create_cumulative_ranges, Calc
from ploev.settings import CONFIG

logging.getLogger()


class AbstractRange(ABC):
    @abstractmethod
    def ppt(self):
        pass


class PptRange(AbstractRange):
    def __init__(self, range_: str):
        self.range_ = range_

    def ppt(self):
        return self.range_

    def __repr__(self):
        cls_name = self.__class__.__name__
        return "{}({})".format(cls_name, self.range_)


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
    def __init__(self, position: Position, stack: float, ranges: Iterable = None, name: str = None,
                 is_hero: bool = False):
        self.position = position
        self._stack = stack
        self._previous_stack = stack
        if ranges is not None:
            self.ranges = list(ranges)
        else:
            self.ranges = []
        if name is not None:
            self.name = name
        else:
            self.name = position.name
        self._is_hero = True
        self._is_villain = True
        self.is_hero = is_hero
        self.is_active = True
        self.in_action = False
        self.action = None
        self.equity = None
        self.invested_in_bank = 0
        self.game = None

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}(position={self.position}, stack={self.stack}, name='{self.name}')"

    @property
    def stack(self):
        return  self._stack

    @stack.setter
    def stack(self, value):
        self._previous_stack = self._stack
        self._stack = value

    @property
    def previous_stack(self):
        return self._previous_stack

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

    def add_range(self, range_):
        if hasattr(range_, 'board_explorer'):
            range_.board_explorer = self.game.board_explorer(range_.street)
        self.ranges.append(range_)

    def ppt(self):
        return ":".join([close_parenthesis(range_.ppt()) for range_ in self.ranges])

    def clone(self):
        return copy.deepcopy(self)

    def restore(self, state):
        """ Restore state of Player from cloned Player"""
        for key, value in vars(state).items():
            if not key.startswith('_'):
                setattr(self, key, value)
        self._previous_stack = state._previous_stack
        self._stack = state._stack


class Street(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4


class EasyRange(AbstractRange):
    def __init__(self, range_: str, cumulative: bool = True, street: Street = None):
        self.range_ = range_
        self.cumulative = cumulative
        self.street = street
        self.board_explorer = None

    def ppt(self):
        return self.board_explorer.ppt(self.range_)

    def __repr__(self):
        cls_name = self.__class__.__name__
        repr_str = "{}({}, cumulative={}, street={})"
        return repr_str.format(cls_name, self.range_, self.cumulative, self.street)


class GameLeaf(Enum):
    NONE = 0
    ROUND_CLOSED = 1
    FOLD = 2


class Game:
    def __init__(self, players: Iterable, pot: float = 0, board: str='', allin_allowed: bool = False):
        self.players = {player.position: player for player in players}
        if len(list(players)) != len(self.players):
            raise ValueError("More than one player with same position")
        for player in self.players.values():
            player.game = self
        self.pot = pot
        self.allin_allowed = allin_allowed
        self._possible_actions = None
        self.in_action_position = None
        self._board = None
        self.street = None
        self.streets = {}
        self.streets_explorers = {}
        self.board = board
        self.in_action_position = max(self.active_positions, key=lambda position: position.value)
        self._is_round_closed = False
        self._last_aggressor = None
        self._previous_player = None
        self._previous_action = None
        self.next_raise_possible = True
        self.leaf = GameLeaf.NONE
        self.game_over = False

    def __repr__(self):
        cls_name = self.__class__.__name__
        players = [player for player in self.players.values()]
        return f'{cls_name}(players={players}, pot={self.pot}, board={self.board!r})'

    @property
    def board(self) -> Board:
        return self._board

    @board.setter
    def board(self, board_str: str):
        board = Board.from_str(board_str)
        if len(board) not in [0, 3, 4, 5]:
            raise ValueError("Wrong board", board)
        self._board = board

        if len(board) == 0:
            self.street = Street.PREFLOP
        elif len(board) == 3:
            self.street = Street.FLOP
            self.set_street(Street.FLOP, board)
        elif len(board) == 4:
            self.street = Street.TURN
            self.set_street(Street.FLOP, board[0:3])
            self.set_street(Street.TURN, board)
        elif len(board) == 5:
            self.street = Street.RIVER
            self.set_street(Street.FLOP, board[0:3])
            self.set_street(Street.TURN, board[0:4])
            self.set_street(Street.RIVER, board)

    def get_street(self, street):
        board = self.streets.get(street)
        return board

    def set_street(self, street, board: Board):
        if self.get_street(street) is None or self.get_street(street) != board:
            self.streets[street] = board
            self.streets_explorers.pop(street, None)

    def board_explorer(self, street=None):
        if street is None:
            street = self.street
        board = self.get_street(street)
        if board:
            return self.streets_explorers.setdefault(street, BoardExplorer(board))
        else:
            return None

    @property
    def flop(self):
        return self.get_street(Street.FLOP)

    @property
    def turn(self):
        return self.get_street(Street.TURN)

    @property
    def river(self):
        return self.get_street(Street.RIVER)

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
    def previous_action(self):
        return self._previous_action

    @property
    def previous_player(self):
        return self._previous_player

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
        """ Returns list of possible actions for the player in action """
        self._possible_actions = []
        player_in_action = self.player_in_action
        if self._previous_action is None:
            return

        action_raise = None
        action_call = None
        raise_possible = True
        # Raise probably possible
        if self._previous_action.type_ in [ActionType.RAISE, ActionType.CALL, ActionType.BET, ActionType.POST_BLIND]:
            pot_raise = self._count_pot_raise(self._previous_action.size, self.pot)
            call_size = self._previous_action.size - player_in_action.invested_in_bank
            if player_in_action.stack <= call_size:
                raise_possible = False
                call_size = player_in_action.stack
            if raise_possible:
                min_raise_size = self._previous_action.size * 2
                if self.allin_allowed:
                    max_raise_size = player_in_action.stack
                else:
                    max_raise_size = pot_raise
                if player_in_action.stack < min_raise_size:  # All-in
                    min_raise_size = max_raise_size = player_in_action.stack
                if player_in_action.stack < max_raise_size:  # All-n
                    max_raise_size = player_in_action.stack
                action_raise = Action(ActionType.RAISE, size=max_raise_size, min_size=min_raise_size,
                                      max_size=max_raise_size)
            action_call = Action(ActionType.CALL, size=call_size)

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
                if raise_possible:
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

    def get_hero(self):
        for player in self.players.values():
            if player.is_hero:
                return player

    def get_active_players(self):
        """ Return lis of active (yet in play) players """
        return [player for player in self.players.values() if player.is_active]

    def set_player_in_action(self, player: Player):
        for pl in self.players.values():
            pl.in_action = False
        player.in_action = True
        self.in_action_position = player.position
        self._determine_possible_actions()

    def make_action(self, action: Action, player_range=None):
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
        if player_range is not None:
            self.player_in_action.add_range(player_range)

        self._previous_action = action
        self._previous_player = self.player_in_action
        if action.is_sizable:
            self.pot += action.size
            self.player_in_action.stack -= action.size
            self.player_in_action.invested_in_bank = action.size
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
        self._set_leaf_and_activeness()

    def _set_leaf_and_activeness(self):
        self.game_over = False
        if self.previous_action.type_ == ActionType.FOLD:
            self.leaf = GameLeaf.FOLD
            self.previous_player.is_active = False
        elif self._is_round_closed:
            self.leaf = GameLeaf.ROUND_CLOSED
            if self.street == Street.SHOWDOWN:
                self.game_over = True
        else:
            self.leaf = GameLeaf.NONE
        # Check all players in all-in
        if len([player for player in self.get_active_players() if player.stack > 0]) <= 1:
            self.game_over = True

    def clone(self):
        return copy.deepcopy(self)

    def restore_state(self, state):
        for position, player in self.players.items():
            self.players[position].restore(state.players[position])
        self.pot = state.pot
        self._board = state._board
        self._possible_actions = state.possible_actions
        self.in_action_position = state.in_action_position
        self._is_round_closed = state._is_round_closed
        self._last_aggressor = state._last_aggressor
        self._previous_action = state.previous_action


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


class GameNode:
    def __init__(self, game: Game, game_state: Game = None, parent=None, level_id=1, action_id=1):
        self._game = game
        if game_state is not None:
            self.game_state = game_state
        else:
            self.game_state = game.clone()
        self.level_id = level_id
        self.action_id = action_id
        self.parent = parent
        self._lines = []
        self.hero_equity = None
        self.hero_pot_share = None
        self.hero_ev = None
        self.hero_pot_share_relative = None
        self.hero_ev_relative = None

    def __repr__(self):
        player = self.game_state.previous_player.name
        action = self.game_state.previous_action
        return "{} {}".format(player, action)

    def __iter__(self):
        yield self
        for child in self.lines:
            yield from child

    @property
    def id(self):
        return self.level_id, self.action_id

    @property
    def lines(self):
        return self._lines

    @property
    def game(self):
        self._game.restore_state(self.game_state)
        return self._game

    @property
    def player(self):
        """ Return player made node action"""
        return self.game_state.previous_player

    def add_line(self, action: Action):
        line_node = GameNode(game=self._game,
                             game_state=self.game_state.clone(),
                             parent=self,
                             level_id=self.level_id + 1,
                             action_id=len(self.lines) + 1)
        line_node.game_state.make_action(action)
        self.lines.append(line_node)
        return line_node

    def add_standard_lines(self):
        """ Add all possible lines  """
        for possible_action in self.game_state.possible_actions:
            self.add_line(copy.copy(possible_action))


class GameTree:
    def __init__(self, root: GameNode, odds_oracle: OddsOracle):
        self.root = root
        self.calc = Calc(odds_oracle)
        self.hero = root.game.get_hero()
        self._hero_node = None

    def __iter__(self):
        yield from self.root

    def _walk(self, game_node):
        yield game_node
        for child in game_node.lines:
            yield from self._walk(child)

    @staticmethod
    def _get_nodes_of_active_players(node: GameNode) -> (GameNode, list):
        active_players_nodes = []
        hero_node = None
        active_players_position = set(node.game_state.active_positions)
        current_node = node
        while len(active_players_position) > 0 and current_node is not None:
            if current_node.player.position in active_players_position:
                active_players_position.remove(current_node.player.position)
                active_players_nodes.append(current_node)
                if current_node.player.is_hero:
                    hero_node = current_node
            current_node = current_node.parent
        return hero_node, active_players_nodes

    @staticmethod
    def calculate_equity(node: GameNode, active_player_nodes, calc):
        players_ranges = [node.player.ppt() for node in active_player_nodes]
        board = node.game.board.ppt()
        equities = calc.equity(players_ranges, board)
        for node, equity in zip(active_player_nodes, equities):
            node.player.equity = equity

    def calculate_node(self, node: GameNode):
        hero_node, active_player_nodes = self._get_nodes_of_active_players(node)
        self.calculate_equity(node, active_player_nodes, self.calc)
        node.hero_equity = hero_node.player.equity
        node.hero_pot_share = None
        node.hero_ev = None
        node.hero_pot_share_relative = None
        node.hero_ev_relative = None
        if node.game_state.leaf == GameLeaf.ROUND_CLOSED:
            node.hero_pot_share = node.hero_equity * node.game_state.pot
            node.hero_pot_share_relative = node.hero_pot_share - hero_node.player.previous_stack
            if node.game_state.game_over:
                node.hero_ev = node.hero_pot_share
                node.hero_ev_relative = node.hero_pot_share_relative

    def calculate(self):
        pass
