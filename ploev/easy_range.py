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

""" Classes implementing 'easy' (traditional) ranges for a board. """

from typing import Iterable, Union
from collections import Counter, namedtuple
import itertools
import copy
import pyparsing as pp

from ploev.cards import CardSet, Board, STRING_TO_RANK, Card


def _constants_dict(hand_type):
    constants = [name for name in dir(hand_type) if name[0] != '_' and name[0].isupper()]
    constant_dir = {getattr(hand_type, name): '{}.{}'.format(hand_type.__class__.__name__, name) for name in constants}
    return constant_dir


class MadeHand:
    """ Class representing made hands """

    # Hand types
    STRAIGHT_FLUSH = 9
    QUADS = 8
    FULL_HOUSE = 7
    FLUSH = 6
    STRAIGHT = 5
    SET = 4
    TRIPS = 3
    TWO_PAIR = 2
    PAIR = 1
    NO_PAIR = 0

    # Hand subtypes
    NONE = 10
    POCKET_PAIR = 11
    BOARD_PAIR = 12

    def __init__(self, type_: int, subtype: int, absolute_rank: tuple, relative_rank: tuple,
                 hole: CardSet, hand: CardSet):
        """ Constructor for MadeHand

        Args:
            type_ (int): type of the hand. MadeHand.STRAIGHT_FLUSH ... MaidHand.PAIR
            subtype (int): subtype of the hand if exist.
                For PAIR type_ subtypes are POCKET_PAIR and BOARD_PAIR. For other types subtype is NONE
            absolute_rank (tuple):
            relative_rank (tuple):
            hole (CardSet): 2 hole cards for the hand
            hand (CardSet): made 5-cards the hand
        """
        self.type_ = type_
        self.subtype = subtype
        self.absolute_rank = absolute_rank
        self.relative_rank = relative_rank
        self.hole = hole
        self.hand = hand

    def __eq__(self, other):
        return (self.type_, self.absolute_rank, self.relative_rank, self.hole, self.hand) \
               == (other.type_, other.absolute_rank, other.relative_rank, other.hole, other.hand)

    def __hash__(self):
        return hash(self.type_) ^ hash(self.subtype) ^ hash(self.absolute_rank) ^ hash(self.relative_rank)

    def __lt__(self, other):
        return (self.type_, self.absolute_rank) < (other.type_, other.absolute_rank)

    def __repr__(self):
        constants_dict = _constants_dict(self)
        cls_name = self.__class__.__name__
        msg = '{}({}, {}, {}, {}, {!r}, {!r})'
        return msg.format(cls_name,
                          constants_dict[self.type_], constants_dict[self.subtype],
                          self.absolute_rank, self.relative_rank,
                          self.hole, self.hand)


def _rank_index(rank):
    """ Returns index number of card rank

        Returns 1 for Ace, 13 for deuce
    """
    return 15 - rank


class StraightDraw:
    """Representing a straight draw"""

    NORMAL = 1
    BACKDOOR = 0

    def __init__(self, type_, hole_ranks: tuple, outs: tuple, nut_outs: tuple):
        """ Constructor for StraightDraw

        Args:
            type_ (int): NORMAL or BACKDOOR
            hole_ranks (tuple): ranks of hole cards
            outs (tuple): ranks of outs
            nut_outs (tuple): ranks of nut outs
        """
        self.type_ = type_
        self.hole_ranks = tuple(sorted(hole_ranks, reverse=True))
        self.outs = tuple(sorted(outs, reverse=True))
        self.nut_outs = tuple(sorted(nut_outs, reverse=True))
        self._ranks_card_set = None

    @property
    def hole(self):
        return CardSet.from_ranks(self.hole_ranks)

    @property
    def ranks_card_set(self):
        if self._ranks_card_set is None:
            self._ranks_card_set = CardSet.from_ranks(self.hole_ranks)
        return self._ranks_card_set

    def add_outs(self, *outs):
        self.outs = tuple(sorted((set(self.outs) | set(outs)), reverse=True))

    def add_nut_outs(self, *nut_outs):
        self.add_outs(*nut_outs)
        self.nut_outs = tuple(sorted(self.nut_outs + nut_outs, reverse=True))

    def get_card_set(self):
        return CardSet.from_ranks(self.hole_ranks)

    def __eq__(self, other):
        if not isinstance(other, StraightDraw):
            return NotImplemented
        return (self.type_ == other.type_
                and self.hole_ranks == other.hole_ranks
                and self.outs == other.outs
                and self.nut_outs == other.nut_outs)

    def __lt__(self, other):
        if not isinstance(other, StraightDraw):
            return NotImplemented
        return (self.type_, self.count_outs(), self.count_nut_outs(), self.hole_ranks) < (other.type_,
                                                                                          other.count_outs(),
                                                                                          other.count_nut_outs(),
                                                                                          other.hole_ranks)

    def __repr__(self):
        constants_dict = _constants_dict(self)
        cls_name = self.__class__.__name__
        msg = '{}({}, {}, {}, {})'
        return msg.format(cls_name, constants_dict[self.type_],
                          self.hole_ranks, self.outs, self.nut_outs)

    def __str__(self):
        return "Straight draw:{} ({}, {}) outs:{} nut outs:{}".format(CardSet.from_ranks(self.hole_ranks),
                                                                      CardSet.from_ranks(self.outs),
                                                                      CardSet.from_ranks(self.nut_outs),
                                                                      self.count_outs(),
                                                                      self.count_nut_outs())

    def count_outs(self):
        """ Returns total number of outs"""
        return len(self.outs) * 4 - len(set(self.outs) & set(self.hole_ranks))

    def count_nut_outs(self):
        """ Returns number of nut outs"""
        return len(self.nut_outs) * 4 - len(set(self.nut_outs) & set(self.hole_ranks))

    @classmethod
    def from_str(cls, ranks_str, outs_str, nut_outs_str=''):
        ranks = [STRING_TO_RANK[rank] for rank in ranks_str]
        outs = [STRING_TO_RANK[out] for out in outs_str]
        nut_outs = [STRING_TO_RANK[nut_out] for nut_out in nut_outs_str]
        return cls(StraightDraw.NORMAL, ranks, outs, nut_outs)


class FlushDraw:
    """ Class representing a flush draw """

    # types
    NORMAL = 0
    BACKDOOR = 1

    # subtypes
    FLOPPED = 2
    TURNED = 3
    NONE = 4

    def __init__(self, type_: int, subtype: int, absolute_rank: tuple, relative_rank: tuple, hole: CardSet):
        """ Constructor for FlushDraw

        Args:
            type_ (int): NORMAL of BACKDOOR
            subtype (int): FLOPPED of TURNED
            absolute_rank (tuple): rank of top hole flush draw cards. (14,) for 'Add';
                (12,) for 'Qdd' on 'Ad2d3s' board; (0,) for generic ('dd') draw
            relative_rank (tuple): relative_rank  of draw. (1,) for 1st draw; (2,) for 2nd draw;
                (0,) for generic draw
            hole (CardSet):  hole cards of draw. CardSet.from_str('Add')
        """
        self.type_ = type_
        self.subtype = subtype
        self.absolute_rank = absolute_rank
        self.relative_rank = relative_rank
        self.hole = hole

    def __eq__(self, other):
        if not isinstance(other, FlushDraw):
            return NotImplemented
        return (self.type_ == other.type_
                and self.subtype == other.subtype
                and self.absolute_rank == other.absolute_rank
                and self.relative_rank == other.relative_rank
                and self.hole == other.hole)

    def __lt__(self, other):
        if not isinstance(other, FlushDraw):
            return NotImplemented
        return (self.type_, self.relative_rank, self.subtype, self.hole[0].suit) > (
            other.type_, other.relative_rank, other.subtype, other.hole[0].suit)

    def __repr__(self):
        constants_dict = _constants_dict(self)
        cls_name = self.__class__.__name__
        msg = '{}({}, {}, {}, {}, {!r})'
        return msg.format(cls_name, constants_dict[self.type_],
                          constants_dict[self.subtype],
                          self.absolute_rank, self.relative_rank, self.hole)


class Blocker:
    """ Class representing various blockers """
    # types
    FLUSH_BLOCKER = 0
    STRAIGHT_BLOCKER = 1
    FLUSH_DRAW_BLOCKER = 2
    STRAIGHT_DRAW_BLOCKER = 3

    # sub_types
    NONE = 4
    TWO_CARD = 5
    ONE_CARD = 6
    FLOPPED = 7
    TURNED = 8

    def __init__(self, type_: int, subtype: int, absolute_rank: tuple, relative_rank: tuple, hole: CardSet):
        """ Constructor for Blocker

        Args:
            type_ (int): FLUSH_BLOCKER, STRAIGHT_BLOCKER, FLUSH_DRAW_BLOCKER, STRAIGHT_DRAW_BLOCKER
            subtype (int): FLOPPED, TURNED, ONE_CARD, TWO_CARD
            absolute_rank (Iterable): absolute rank of the blocker
            relative_rank (Iterable): rank of the blocker
            hole (CardSet):
        """
        self.type_ = type_
        self.subtype = subtype
        self.absolute_rank = absolute_rank
        self.relative_rank = relative_rank
        self.hole = hole

    def __eq__(self, other):
        return (self.type_ == other.type_
                and self.subtype == other.subtype
                and self.absolute_rank == other.absolute_rank
                and self.relative_rank == other.relative_rank
                and self.hole == other.hole)

    def __lt__(self, other):
        if not isinstance(other, Blocker):
            return NotImplemented
        if self.type_ == Blocker.FLUSH_DRAW_BLOCKER:
            return (self.type_, self.relative_rank, self.subtype, _rank_index(self.absolute_rank[0])) > (
                other.type_, other.relative_rank, other.subtype, _rank_index(other.absolute_rank[0]))
        else:
            return (self.type_, self.subtype, self.relative_rank, _rank_index(self.absolute_rank[0])) > (
                other.type_, other.subtype, other.relative_rank, _rank_index(other.absolute_rank[0]))

    def __repr__(self):
        constants_dict = _constants_dict(self)
        cls_name = self.__class__.__name__
        msg = '{}({}, {}, {}, {}, {!r})'
        return msg.format(cls_name, constants_dict[self.type_],
                          constants_dict[self.subtype],
                          self.absolute_rank, self.relative_rank, self.hole)


def _is_straight(ranks):
    """ Returns max rank of straight if ranks is straight"""
    if set(ranks) == {14, 5, 4, 3, 2}:
        return 5
    if (max(ranks) - min(ranks) == 4) and len(set(ranks)) == 5:
        return max(ranks)
    return False


class _StraightExplorer:
    """ Class exploring board for straights """

    def __init__(self, board):
        self._board = board
        self._straights = None
        self._straight_blockers = None
        self._is_straighted = None
        self._straights_holes = None
        self._straight_draws = None
        self._remaining_ranks = None

    def __repr__(self):
        class_name = type(self).__name__
        return "{}({!r})".format(class_name, self._board)

    @property
    def is_straighted(self):
        if self._is_straighted is None:
            self.explore()
        return self._is_straighted

    @property
    def straights(self):
        if self._straights is None:
            self.explore()
        return self._straights

    @property
    def straight_blockers(self):
        if self._straight_blockers is None:
            self.explore()
        return self._straight_blockers

    def explore(self):
        if self._straights is None:
            self._straights = []
            self._straight_blockers = []
            unranked_straights = self.get_unranked_straights(self._board)
            # Sorting straights by straight top card rank and set straight number rank
            # First straight will have rank=1, second straight will have rank=2 etc...
            handled_outs = set()
            for index, straight in enumerate(sorted(unranked_straights, key=lambda x: x.hand, reverse=True)):
                straight.relative_rank = (index + 1,)
                self._straights.append(straight)
                straight.hand = CardSet.from_ranks(straight.hand)  # hand was tuple, not CardSet
                straight.hole = CardSet.from_ranks(straight.hole)
                for i in range(2):
                    if straight.hole[i].rank not in handled_outs:
                        handled_outs.add(straight.hole[i].rank)
                        self._straight_blockers.append(
                            Blocker(Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (straight.hole[i].rank,),
                                    straight.relative_rank, CardSet([straight.hole[i]] * 2)))
                        self._straight_blockers.append(
                            Blocker(Blocker.STRAIGHT_BLOCKER, Blocker.ONE_CARD, (straight.hole[i].rank,),
                                    straight.relative_rank, CardSet([straight.hole[i]])))
        if self._straights:
            self._is_straighted = True
        else:
            self._is_straighted = False
        self._straight_blockers.sort(reverse=True)
        return self._straights

    @staticmethod
    def get_unranked_straights(board):
        """ Return list of possible straights without right relative rank
            Note: hole and hand are tuples of rank instead of CardSet
        """
        straights = []
        remaining_ranks = board.remaining_ranks
        remaining_2_card_combos = [sorted(list(combo), reverse=True) for combo
                                   in itertools.combinations(remaining_ranks, 2)]
        boards_3_card_combos = [list(comb) for comb in itertools.combinations(board.unique_ranks, 3)]
        hands = (tuple((tuple(sorted(board + hole, reverse=True)), tuple(hole)))
                 for board in boards_3_card_combos
                 for hole in remaining_2_card_combos)
        for (hand, hole) in hands:
            straight_rank = _is_straight(hand)
            if straight_rank:
                # rank is 1 for all straights yet
                straights.append(
                    MadeHand(type_=MadeHand.STRAIGHT, subtype=MadeHand.NONE, absolute_rank=(straight_rank,),
                             relative_rank=(0,), hole=hole, hand=hand))
        return straights


# noinspection PyTypeChecker
class _StraightDrawExplorer:
    """ Class exploring board for straights draws """

    def __init__(self, board, straights=None):
        self._board = board
        self._remaining_ranks = None
        self._straights = straights
        self._straights_holes = None
        self._straight_draws = None
        self._straight_draw_blockers = None
        self._backdoor_straight_draws = None

    def __repr__(self):
        class_name = type(self).__name__
        return "{}({!r})".format(class_name, self._board)

    def _get_straights(self):
        if self._straights is None:
            self._straights = _StraightExplorer(self._board).straights
            # noinspection PyTypeChecker
            self._straights_holes = [set(straight.hole.ranks) for straight in self._straights]

    @property
    def straight_draws(self):
        if self._straight_draws is None:
            self._explore()
        return self._straight_draws

    @property
    def backdoor_straight_draws(self):
        if self._backdoor_straight_draws is None:
            self._explore()
        return self._backdoor_straight_draws

    @property
    def straight_draw_blockers(self) -> list:
        if self._straight_draw_blockers is None:
            self._explore()
        return self._straight_draw_blockers

    def _explore(self):
        self._straight_draws = []
        self._straight_draw_blockers = []
        self._backdoor_straight_draw_blockers = []
        if len(self._board) == 5:
            return
        # find all two cards straight draws
        board = self._board.ranks
        remaining = self._board.remaining_ranks
        self._get_straights()  # hole cards for the already existing straight
        two_card_draws, ranks_of_all_draw, draws_ranks = self._find_two_card_draws(board, remaining,
                                                                                   self._straights_holes)
        self._straight_draws.extend(two_card_draws)
        # find three and four cards straight draws
        by_ranks, by_outs = self._fill_by_outs_and_by_ranks(two_card_draws, 2)
        for x in range(3, 5):
            draw_x_cards, by_ranks, by_outs = self._find_x_size_card_draws(by_ranks, by_outs, ranks_of_all_draw, x)
            self._straight_draws.extend(draw_x_cards)
        self.straight_draws.sort(reverse=True)
        # Blockers
        for relative_rank, absolute_rank in enumerate(sorted(list(ranks_of_all_draw), reverse=True)):
            self._straight_draw_blockers.append(
                Blocker(Blocker.STRAIGHT_DRAW_BLOCKER, Blocker.TWO_CARD, (absolute_rank,), (relative_rank + 1,),
                        CardSet.from_ranks([absolute_rank] * 2)))
            self._straight_draw_blockers.append(
                Blocker(Blocker.STRAIGHT_DRAW_BLOCKER, Blocker.ONE_CARD, (absolute_rank,),
                        (relative_rank + 1,), CardSet.from_ranks([absolute_rank])))
        self._straight_draw_blockers.sort(reverse=True)
        # Backdoors
        if len(self._board) == 3:
            self._backdoor_straight_draws = self._get_backdoors(self._board, draws_ranks)

    @staticmethod
    def _find_two_card_draws(board, remaining_ranks, straights_holes):
        """ Find all possible two card draws for the board

        Args:
            board(iterable): ranks of a board
            remaining_ranks(iterable): remaining ranks
            straights_holes(iterable): tuples of holes card for possible straights for the board

        """
        draws = {}
        for out in remaining_ranks:  # all cards for next street
            next_street_board = board + [out]
            next_street_remaining = remaining_ranks.copy()
            next_street_remaining.remove(out)
            all_straights = _StraightExplorer.get_unranked_straights(CardSet.from_ranks(next_street_board))
            all_straights.sort(reverse=True)
            for hole in itertools.combinations(next_street_remaining, 2):  # all possible 2 cards draw
                if set(hole) not in straights_holes:
                    for three_card_combination in itertools.combinations(next_street_board, 3):
                        hand = three_card_combination + hole
                        straight_rank = _is_straight(hand)
                        if straight_rank:
                            draw = draws.get(hole)
                            is_nut_out = ((straight_rank,) == all_straights[0].absolute_rank)
                            if is_nut_out:
                                if draw:
                                    draw.add_nut_outs(out)
                                else:
                                    draws[hole] = StraightDraw(StraightDraw.NORMAL, hole, (out,), (out,))

                            else:
                                if draw:
                                    draw.add_outs(out)
                                else:
                                    draws[hole] = StraightDraw(StraightDraw.NORMAL, hole, (out,), ())

        two_card_draws = list(draws.values())
        ranks_of_all_draw = set()
        draws_ranks = set()
        for ranks in draws.keys():
            ranks_of_all_draw |= set(ranks)
            draws_ranks.add(tuple(sorted(ranks, reverse=True)))
        return two_card_draws, ranks_of_all_draw, draws_ranks

    @staticmethod
    def _get_backdoors(board, draws_ranks):
        draws = {}
        remaining = sorted(board.remaining_ranks, reverse=True)
        for card in board.ranks:
            for four_cards in itertools.combinations(remaining, 4):
                possible_straight = (card,) + four_cards
                if _is_straight(possible_straight):
                    for hole in itertools.combinations(four_cards, 2):
                        if hole not in draws_ranks:
                            draw = draws.get(hole)
                            outs = tuple(set(four_cards) - set(hole))
                            if draw:
                                draw.add_outs(*outs)
                            else:

                                draws[hole] = StraightDraw(StraightDraw.BACKDOOR, hole, outs, ())

        return sorted([draw for draw in draws.values()], reverse=True)

    @staticmethod
    def _fill_by_outs_and_by_ranks(draws, size, by_ranks=None, by_outs=None):
        """
        Fill draws dictionaries
        Args:
            draws(iterable): straight draws of certain size
            size: 2, 3 or 4 card straight draw
            by_ranks(dict): dict by hole cards
            by_outs(dict): dict by number outs

        Returns:
            dict: dict by hole cards

        Returns:
            dict: dcit by outs

        """
        if by_ranks is None:
            by_ranks = {}
        if by_outs is None:
            by_outs = {}
        by_ranks[size] = {}
        by_outs[size] = {}
        for draw in draws:
            by_ranks[size][draw.hole_ranks] = draw
            by_outs[size][(draw.outs, draw.nut_outs)] = draw
        return by_ranks, by_outs

    @staticmethod
    def _find_x_size_card_draws(by_ranks, by_outs, all_draw_ranks, size=3):
        draws = []
        higher_level = size - 1
        for x_card_combination in itertools.combinations(sorted(all_draw_ranks, reverse=True), size):
            two_card_combinations = [by_ranks[2][c]
                                     for c in itertools.combinations(x_card_combination, 2)
                                     if c in by_ranks[2]]
            if len(two_card_combinations) > 1:
                x_card_draw = _StraightDrawExplorer._combine_straight_draw(*two_card_combinations)
                if not (x_card_draw.outs, x_card_draw.nut_outs) in by_outs[higher_level]:
                    draws.append(x_card_draw)
                _StraightDrawExplorer._fill_by_outs_and_by_ranks(draws, size, by_ranks, by_outs)
        return draws, by_ranks, by_outs

    @staticmethod
    def _combine_straight_draw(*straight_draws):
        combined_ranks = set()
        combined_outs = set()
        combined_nut_outs = set()
        for sd in straight_draws:
            combined_ranks |= set(sd.hole_ranks)
            combined_outs |= set(sd.outs)
            combined_nut_outs |= set(sd.nut_outs)
        return StraightDraw(StraightDraw.NORMAL, combined_ranks, combined_outs, combined_nut_outs)


class _FlushDrawExplorer:
    """ Class exploring board for flush draws """

    def __init__(self, board: CardSet):
        self._board = board
        self._is_rainbow = None
        self._is_flushed = None
        self._has_flopped_flush_draw = None
        self._has_turned_flush_draw = None
        self._flush_draws = None
        self._backdoor_flush_draws = None
        self._flush_draw_blockers = None

    def __repr__(self):
        class_name = type(self).__name__
        return "{}({!r})".format(class_name, self._board)

    @property
    def is_rainbow(self):
        if self._is_rainbow is None:
            if max(Counter(self._board.suits).values()) == 2:
                self._is_rainbow = False
            else:
                self._is_rainbow = True
        return self._is_rainbow

    @property
    def is_flushed(self):
        if self._is_flushed is None:
            if max(Counter(self._board.suits).values()) >= 3:
                self._is_flushed = True
            else:
                self._is_flushed = False
        return self._is_flushed

    @property
    def has_flopped_flush_draw(self):
        if self._has_flopped_flush_draw is None:
            if max(Counter(self._board[:3].suits).values()) == 2:
                self._has_flopped_flush_draw = True
            else:
                self._has_flopped_flush_draw = False
        return self._has_flopped_flush_draw

    @property
    def has_turned_flush_draw(self):
        if self._has_turned_flush_draw is None:
            # if turn or river
            #  and last three cards (two from flop and one from turn) has two cards of one suit
            # and it's not two cards because flop had flush draw, which was flushed on the turn
            if len(self._board) >= 4 and max(Counter(self._board[1:4].suits).values()) == 2 and max(
                    Counter(self._board[:4].suits).values()) == 2:
                self._has_turned_flush_draw = True
            else:
                self._has_turned_flush_draw = False
        return self._has_turned_flush_draw

    @property
    def flush_draws(self) -> list:
        if self._flush_draws is None:
            self._explore()
        # noinspection PyTypeChecker
        return self._flush_draws

    @property
    def backdoor_flush_draws(self) -> list:
        if self._backdoor_flush_draws is None:
            self._explore()
        # noinspection PyTypeChecker
        return self._backdoor_flush_draws

    @property
    def flush_draw_blockers(self) -> list:
        if self._flush_draw_blockers is None:
            self._explore()
        # noinspection PyTypeChecker
        return self._flush_draw_blockers

    def _explore(self):
        self._flush_draws = []
        self._flush_draw_blockers = []
        if len(self._board) < 5 and not self.is_rainbow:
            if self.has_flopped_flush_draw:
                flop_fd_suit = Counter(self._board[:3].suits).most_common(1)[0][0]
                flush_ranks = self._board.get_ranks_for_suit(flop_fd_suit)
                remaining_flush_ranks = sorted(CardSet.from_ranks(flush_ranks).remaining_ranks, reverse=True)
                for index, rank in enumerate(remaining_flush_ranks):
                    if index + 1 < len(remaining_flush_ranks):  # dont' count lowest flush draw (2ss)
                        flush_draw = FlushDraw(type_=FlushDraw.NORMAL, subtype=FlushDraw.FLOPPED, absolute_rank=(rank,),
                                               relative_rank=(index + 1,),
                                               hole=CardSet([Card(rank, flop_fd_suit), Card(0, flop_fd_suit)]))
                        self._flush_draws.append(flush_draw)
                    flush_draw_blocker = Blocker(type_=Blocker.FLUSH_DRAW_BLOCKER,
                                                 subtype=Blocker.FLOPPED,
                                                 absolute_rank=(rank,),
                                                 relative_rank=(index + 1,),
                                                 hole=CardSet([Card(rank, flop_fd_suit)]))
                    self._flush_draw_blockers.append(flush_draw_blocker)
            if self.has_turned_flush_draw:
                turned_fd_suit = Counter(self._board[1:].suits).most_common(1)[0][0]
                flush_ranks = self._board.get_ranks_for_suit(turned_fd_suit)
                remaining_flush_ranks = sorted(CardSet.from_ranks(flush_ranks).remaining_ranks, reverse=True)
                for index, rank in enumerate(remaining_flush_ranks):
                    if index + 1 < len(remaining_flush_ranks):  # dont' count lowest flush draw (2ss)
                        flush_draw = FlushDraw(type_=FlushDraw.NORMAL, subtype=FlushDraw.TURNED,
                                               absolute_rank=(rank,), relative_rank=(index + 1,),
                                               hole=CardSet([Card(rank, turned_fd_suit), Card(0, turned_fd_suit)]))
                        self._flush_draws.append(flush_draw)
                    flush_draw_blocker = Blocker(type_=Blocker.FLUSH_DRAW_BLOCKER,
                                                 subtype=Blocker.TURNED,
                                                 absolute_rank=(rank,),
                                                 relative_rank=(index + 1,),
                                                 hole=CardSet([Card(rank, turned_fd_suit)]))
                    self._flush_draw_blockers.append(flush_draw_blocker)
                self._flush_draws.sort(reverse=True)
                self._flush_draw_blockers.sort(reverse=True)
        # Backdoors
        self._backdoor_flush_draws = []
        if len(self._board) == 3 and not self.is_flushed:
            for suit in [suit for (suit, count) in Counter(self._board.suits).items() if count == 1]:
                flush_ranks = self._board.get_ranks_for_suit(suit)
                remaining_flush_ranks = sorted(CardSet.from_ranks(flush_ranks).remaining_ranks, reverse=True)
                for index, rank in enumerate(remaining_flush_ranks[:-1]):
                    backdoor = FlushDraw(type_=FlushDraw.BACKDOOR, subtype=FlushDraw.FLOPPED, absolute_rank=(rank,),
                                         relative_rank=(index + 1,), hole=CardSet(
                            [Card(rank, suit), Card(0, suit)]))
                    self._backdoor_flush_draws.append(backdoor)
            self._backdoor_flush_draws.sort(reverse=True)


# noinspection PyTypeChecker
class _MadeHandExplorer:
    """ Class exploring board for made hands """

    def __init__(self, board: CardSet):
        self._board = board
        self._straight_flushes = None
        self._quads = None
        self._full_houses = None
        self._flushes = None
        self._sets = None
        self._trips = None
        self._two_pairs = None
        self._board_pairs = None
        self._pocket_pairs = None
        self._is_paired = None
        self._is_exactly_paired = None
        self._is_exactly_tripsed = None
        self._is_exactly_quaded = None
        self._paired_ranks = None
        self._unpaired_ranks = None
        self._is_flushed = None
        self._straight_explorer = _StraightExplorer(board)
        self._made_hands = None
        self._flush_blockers = None

    def __repr__(self):
        class_name = type(self).__name__
        return "{}({!r})".format(class_name, self._board)

    @property
    def is_paired(self):
        if self._is_paired is None:
            self._check_pairness()
        return self._is_paired

    @property
    def is_exactly_paired(self):
        if self._is_exactly_paired is None:
            self._check_pairness()
        return self._is_exactly_paired

    @property
    def is_exactly_tripsed(self):
        if self._is_exactly_tripsed is None:
            self._check_pairness()
        return self._is_exactly_tripsed

    @property
    def is_exactly_quaded(self):
        if self._is_exactly_quaded is None:
            self._check_pairness()
        return self._is_exactly_quaded

    def _check_pairness(self):
        max_count = Counter(self._board.ranks).most_common(1)[0][1]
        self._is_paired = False
        self._is_exactly_paired = False
        self._is_exactly_tripsed = False
        self._is_exactly_quaded = False
        if max_count >= 2:
            self._is_paired = True
        if max_count == 2:
            self._is_exactly_paired = True
        if max_count == 3:
            self._is_exactly_tripsed = True
        if max_count == 4:
            self._is_exactly_quaded = True

    @property
    def is_flushed(self):
        if self._is_flushed is None:
            if max(Counter(self._board.suits).values()) >= 3:
                self._is_flushed = True
            else:
                self._is_flushed = False
        return self._is_flushed

    @property
    def is_straighted(self):
        return self._straight_explorer.is_straighted

    @property
    def made_hands(self) -> list:
        """ Returns list of made hands, sorted by rank"""
        if self._made_hands is None:
            self._made_hands = []
            self._made_hands.extend(self.flushes)
            self._made_hands.extend(self.straights)
            if self.is_paired:
                self._made_hands.extend(self.trips)
                self._made_hands.extend(self.full_houses)
                self._made_hands.extend(self.quads)
            else:
                self._made_hands.extend(self.sets)
            self._made_hands.extend(self.two_pairs)
            self._made_hands.extend(self.board_pairs)
            self._made_hands.extend(self.pocket_pairs)
            self._made_hands.sort(reverse=True)
        # noinspection PyTypeChecker
        return self._made_hands

    @property
    def straights(self) -> list:
        # noinspection PyTypeChecker
        return self._straight_explorer.straights

    @property
    def straight_blockers(self) -> list:
        # noinspection PyTypeChecker
        return self._straight_explorer.straight_blockers

    @property
    def flushes(self) -> list:
        if self._flushes is None:
            self._get_flushes()
        # noinspection PyTypeChecker
        return self._flushes

    @property
    def flush_blockers(self) -> list:
        if self._flush_blockers is None:
            self._get_flushes()
        # noinspection PyTypeChecker
        return self._flush_blockers

    def _get_flushes(self):
        self._flushes = []
        self._flush_blockers = []
        if self.is_flushed:
            flush_suit = Counter(self._board.suits).most_common(1)[0][0]
            flush_ranks = sorted(self._board.get_ranks_for_suit(flush_suit), reverse=True)
            remaining_flush_ranks = CardSet.from_ranks(flush_ranks).remaining_ranks
            remaining_flush_ranks.sort(reverse=True)
            for index, rank in enumerate(remaining_flush_ranks):
                absolute_rank = (rank,)
                relative_rank = (index + 1,)
                if index + 1 < len(remaining_flush_ranks):  # dont' count lowest flush draw (2ss)
                    hole = CardSet([Card(rank, flush_suit), Card(0, flush_suit)])
                    hand = CardSet(sorted([Card(rank, flush_suit)]
                                          + [Card(flush_rank, flush_suit) for flush_rank in flush_ranks][:3]
                                          + [Card(0, flush_suit)], reverse=True))
                    self._flushes.append(MadeHand(MadeHand.FLUSH, MadeHand.NONE,
                                                  absolute_rank, relative_rank,
                                                  hole, hand))
                blocker_hole = CardSet([Card(rank, flush_suit)])
                self._flush_blockers.append(
                    Blocker(Blocker.FLUSH_BLOCKER, Blocker.NONE, absolute_rank, relative_rank, blocker_hole))

    @property
    def sets(self) -> list:
        if self._sets is None:
            self._get_sets()
        return self._sets

    def _get_sets(self):
        self._sets = []
        if not self.is_paired:
            board_ranks = sorted(self._board.ranks, reverse=True)
            for board_rank in board_ranks:
                absolute_rank = (board_rank,)
                relative_rank = (board_ranks.index(board_rank) + 1,)
                hole = CardSet.from_ranks([board_rank, board_rank])
                hand = CardSet.from_ranks([board_rank, board_rank, board_rank])
                set_hand = MadeHand(MadeHand.SET, MadeHand.NONE, absolute_rank, relative_rank, hole, hand)
                self._sets.append(set_hand)

    @property
    def two_pairs(self) -> list:
        if self._two_pairs is None:
            self._get_two_pairs()
        return self._two_pairs

    def _get_two_pairs(self):
        self._two_pairs = []
        if not self.is_paired:
            ranks_for_two_pairs = sorted(self._board.ranks, reverse=True)
        else:
            ranks_for_two_pairs = [up_rank for up_rank in self.unpaired_ranks if up_rank > max(self.paired_ranks)]
        for two_pair_ranks in itertools.combinations(ranks_for_two_pairs, 2):
            absolute_rank = tuple(two_pair_ranks)
            relative_rank = (ranks_for_two_pairs.index(two_pair_ranks[0]) + 1,
                             ranks_for_two_pairs.index(two_pair_ranks[1]) + 1,)
            hole = CardSet.from_ranks(two_pair_ranks)
            hand = CardSet.from_ranks([two_pair_ranks[0], two_pair_ranks[0],
                                       two_pair_ranks[1], two_pair_ranks[1]])
            two_pair = MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE, absolute_rank, relative_rank, hole, hand)
            self._two_pairs.append(two_pair)

    @property
    def board_pairs(self) -> list:
        if self._board_pairs is None:
            self._get_board_pairs()
        return self._board_pairs

    def _get_board_pairs(self):
        self._board_pairs = []
        if not self.is_paired:
            ranks_for_pairs = sorted(self._board.ranks, reverse=True)
        else:
            ranks_for_pairs = [up_rank for up_rank in self.unpaired_ranks if up_rank not in self.paired_ranks]
        kickers = sorted(self._board.remaining_ranks, reverse=True)
        for pair_relative_rank, pair_absolute_rank in enumerate(ranks_for_pairs):
            for kicker_relative_rank, kicker_absolute_rank in enumerate(kickers):
                absolute_rank = (pair_absolute_rank, kicker_absolute_rank)
                # rank among all pairs, including pocket pairs
                all_pairs_relative_rank = _rank_index(pair_absolute_rank)
                relative_rank = (all_pairs_relative_rank, pair_relative_rank + 1, kicker_relative_rank + 1)
                hole = CardSet.from_ranks([pair_absolute_rank, kicker_absolute_rank])
                hand = CardSet.from_ranks([pair_absolute_rank] * 2 + [kicker_absolute_rank])
                board_pair = MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, absolute_rank, relative_rank, hole,
                                      hand)
                self._board_pairs.append(board_pair)

    @property
    def pocket_pairs(self):
        if self._pocket_pairs is None:
            self._get_pocket_pairs()
        return self._pocket_pairs

    def _get_pocket_pairs(self):
        self._pocket_pairs = []
        second_rank = 1  # 1: overpair, 2: midpair
        third_rank = 1  # rank of pocket pair: 1st best, 2nd best
        for pocket_rank in range(14, 1, -1):
            if pocket_rank not in self._board.ranks:
                absolute_rank = (pocket_rank,)
                relative_rank = (_rank_index(pocket_rank), second_rank, third_rank)
                hole = CardSet.from_ranks([pocket_rank, pocket_rank])
                hand = CardSet.from_ranks([pocket_rank, pocket_rank])
                pocket_pair = MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR, absolute_rank,
                                       relative_rank, hole, hand)
                self._pocket_pairs.append(pocket_pair)
                third_rank += 1
            else:
                if third_rank > 1 or second_rank == 1:  # check if board ranks aren't alongside
                    second_rank += 1
                third_rank = 1

    @property
    def paired_ranks(self):
        if self._paired_ranks is None:
            self._paired_ranks = [rank for rank, count in Counter(self._board.ranks).items() if count == 2]
            self._paired_ranks.sort(reverse=True)
        return self._paired_ranks

    @property
    def unpaired_ranks(self):
        if self._unpaired_ranks is None:
            self._unpaired_ranks = [rank for rank, count in Counter(self._board.ranks).items() if count == 1]
            self._unpaired_ranks.sort(reverse=True)
        return self._unpaired_ranks

    @property
    def trips(self):
        if self._trips is None:
            self._get_trips()
        return self._trips

    def _get_trips(self):
        self._trips = []
        kickers = [rank for rank in CardSet.from_ranks(self.unpaired_ranks).remaining_ranks if
                   rank not in self.paired_ranks]
        kickers.sort(reverse=True)
        # noinspection PyTypeChecker
        for trips_index, trips_rank in enumerate(self.paired_ranks):
            for kicker_index, kicker_rank in enumerate(kickers):
                self._trips.append(MadeHand(MadeHand.TRIPS,
                                            MadeHand.NONE,
                                            (trips_rank, kicker_rank),
                                            (trips_index + 1, kicker_index + 1),
                                            CardSet.from_ranks([trips_rank, kicker_rank]),
                                            CardSet.from_ranks([trips_rank] * 3 + [kicker_rank])))

    @property
    def full_houses(self):
        if self._full_houses is None:
            self._get_full_houses()
        return self._full_houses

    def _get_full_houses(self):
        self._full_houses = []
        if self.is_paired:
            if self.is_exactly_paired:
                relative_rank = 1
                for rank in self._board.unique_ranks:
                    if rank in self.unpaired_ranks:  # 'Sets' full houses
                        for paired_rank in self.paired_ranks:
                            self._full_houses.append(MadeHand(MadeHand.FULL_HOUSE,
                                                              MadeHand.NONE,
                                                              (rank, paired_rank),
                                                              (relative_rank,),
                                                              CardSet.from_ranks([rank] * 2),
                                                              CardSet.from_ranks(
                                                                  [rank] * 3 + [paired_rank] * 2),
                                                              ))
                            relative_rank += 1
                    if rank in self.paired_ranks:
                        for another_rank in self.unpaired_ranks:
                            if another_rank != rank:
                                self._full_houses.append(MadeHand(MadeHand.FULL_HOUSE,
                                                                  MadeHand.NONE,
                                                                  (rank, another_rank),
                                                                  (relative_rank,),
                                                                  CardSet.from_ranks([rank, another_rank]),
                                                                  CardSet.from_ranks(
                                                                      [rank] * 3 + [another_rank] * 2),
                                                                  ))
                                relative_rank += 1
        self._full_houses.sort(reverse=True)

    @property
    def quads(self):
        if self._quads is None:
            self._get_quads()
        return self._quads

    def _get_quads(self):
        self._quads = []
        if self.is_paired:
            if self.is_exactly_paired:
                # noinspection PyTypeChecker
                for index, paired_rank in enumerate(self.paired_ranks):
                    self._quads.append(MadeHand(MadeHand.QUADS,
                                                MadeHand.NONE,
                                                (paired_rank,),
                                                (index + 1,),
                                                CardSet.from_ranks([paired_rank] * 2),
                                                CardSet.from_ranks([paired_rank] * 4),
                                                ))


class Syntax:
    """ Class storing constants for easy_range syntax"""
    MADE_HAND = 'made_hand'
    STRAIGHT_DRAW = 'straight_draw'
    FLUSH_DRAW = 'flush_draw'
    BLOCKER = 'blocker'

    RELATIVE_RANK = 'relative_rank'
    AND_BETTER = 'and_better'

    EasyRange = namedtuple('EasyRange', ['family', 'type_', 'subtype', 'relative_rank',
                                         'rank_prefix', 'and_better', 'digits'])
    syntax = {
        'WRAP': EasyRange(STRAIGHT_DRAW, StraightDraw.NORMAL, None, (13, 0), None, True, [0]),
        'OESD': EasyRange(STRAIGHT_DRAW, StraightDraw.NORMAL, None, (8, 0), None, None, [0]),
        'SD': EasyRange(STRAIGHT_DRAW, StraightDraw.NORMAL, None, None, None, None, [1, 2]),
        'GS': EasyRange(STRAIGHT_DRAW, StraightDraw.NORMAL, None, (4, 0), None, None, [0]),
        'BSD': EasyRange(STRAIGHT_DRAW, StraightDraw.BACKDOOR, None, None, None, None, []),
        'StrF': EasyRange(MADE_HAND, MadeHand.STRAIGHT_FLUSH, MadeHand.NONE, (0,), None, None, []),
        'Q': EasyRange(MADE_HAND, MadeHand.QUADS, MadeHand.NONE, (0,), None, None, [1]),
        'FH': EasyRange(MADE_HAND, MadeHand.FULL_HOUSE, MadeHand.NONE, (0,), None, None, [0, 1]),
        'F': EasyRange(MADE_HAND, MadeHand.FLUSH, MadeHand.NONE, (0,), None, None, [0, 1]),
        'Str': EasyRange(MADE_HAND, MadeHand.STRAIGHT, MadeHand.NONE, None, None, None, [1]),
        'TS': EasyRange(MADE_HAND, MadeHand.SET, MadeHand.NONE, None, (1,), None, [0]),
        'S': EasyRange(MADE_HAND, MadeHand.SET, MadeHand.NONE, None, None, None, [1]),
        'BS': EasyRange(MADE_HAND, MadeHand.SET, MadeHand.NONE, None, (5,), None, [0]),
        'MS': EasyRange(MADE_HAND, MadeHand.SET, MadeHand.NONE, None, (2,), None, [0]),
        'Tr': EasyRange(MADE_HAND, MadeHand.TRIPS, MadeHand.NONE, (0,), None, None, [0, 2]),
        '2P': EasyRange(MADE_HAND, MadeHand.TWO_PAIR, MadeHand.NONE, None, None, None, [0, 2]),
        'T2P': EasyRange(MADE_HAND, MadeHand.TWO_PAIR, MadeHand.NONE, (1, 2), None, None, [0]),
        'TB2P': EasyRange(MADE_HAND, MadeHand.TWO_PAIR, MadeHand.NONE, (1, 3), None, None, [0]),
        'MP': EasyRange(MADE_HAND, MadeHand.PAIR, MadeHand.BOARD_PAIR, None, (2,), None, [0, 1]),
        'PB': EasyRange(MADE_HAND, MadeHand.PAIR, MadeHand.BOARD_PAIR, None, None, None, [1, 2]),
        'P': EasyRange(MADE_HAND, MadeHand.PAIR, MadeHand.NONE, None, None, None, [1]),
        'PP': EasyRange(MADE_HAND, MadeHand.PAIR, MadeHand.POCKET_PAIR, None, None, None, [1, 2]),
        'BP': EasyRange(MADE_HAND, MadeHand.PAIR, MadeHand.BOARD_PAIR, None, (3,), None, [0, 1]),
        'TP': EasyRange(MADE_HAND, MadeHand.PAIR, MadeHand.BOARD_PAIR, None, (1,), None, [0, 1]),
        'OP': EasyRange(MADE_HAND, MadeHand.PAIR, MadeHand.POCKET_PAIR, None, (1,), None, [0, 1]),
        'NBFD': EasyRange(FLUSH_DRAW, FlushDraw.BACKDOOR, None, (1,), None, None, [0]),
        'BFD': EasyRange(FLUSH_DRAW, FlushDraw.BACKDOOR, None, None, None, None, [1]),
        'FDF': EasyRange(FLUSH_DRAW, FlushDraw.NORMAL, FlushDraw.FLOPPED, None, None, None, [0, 1]),
        'NFD': EasyRange(FLUSH_DRAW, FlushDraw.NORMAL, None, (1,), None, None, [0]),
        'FD': EasyRange(FLUSH_DRAW, FlushDraw.NORMAL, None, None, None, None, [0, 1]),
        'FDT': EasyRange(FLUSH_DRAW, FlushDraw.NORMAL, FlushDraw.TURNED, None, None, None, [0, 1]),
        'SDB': EasyRange(BLOCKER, Blocker.STRAIGHT_DRAW_BLOCKER, Blocker.TWO_CARD, None, None, None, [1]),
        'SDBO': EasyRange(BLOCKER, Blocker.STRAIGHT_DRAW_BLOCKER, Blocker.ONE_CARD, None, None, None, [1]),
        'NFDB': EasyRange(BLOCKER, Blocker.FLUSH_DRAW_BLOCKER, None, (1,), None, None, [0]),
        'FDB': EasyRange(BLOCKER, Blocker.FLUSH_DRAW_BLOCKER, None, None, None, None, [1]),
        'SB': EasyRange(BLOCKER, Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, None, None, None, [1]),
        'NSB': EasyRange(BLOCKER, Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (1,), None, None, [1]),
        'NFB': EasyRange(BLOCKER, Blocker.FLUSH_BLOCKER, None, (1,), None, None, [0]),
        'FB': EasyRange(BLOCKER, Blocker.FLUSH_BLOCKER, None, None, None, None, [1]),
    }


class BoardExplorer:
    """ Class explorers a board for all possible made hands and draws. """

    MADE_HAND = 'made_hand'
    STRAIGHT_DRAW = 'straight_draw'
    FLUSH_DRAW = 'flush_draw'
    BLOCKER = 'blocker'

    ONLY_THAT = 'only_that'
    THAT_AND_BETTER = 'that_and_better'
    THAT_AND_WORSE = 'that_and_worse'
    ALL_BUT_THAT = 'all_but_that'

    def __init__(self, board: CardSet):
        """ Constructor for BoardExplorer

        Args:
            board (Board): board
        """
        self._board = board
        self._straight_draw_explorer = _StraightDrawExplorer(self._board)
        self._flush_draw_explorer = _FlushDrawExplorer(self._board)
        self._made_hand_explorer = _MadeHandExplorer(self._board)

    @classmethod
    def from_str(cls, board):
        """ String counstructor for BoardExlorer"""
        return cls(Board.from_str(board))

    @property
    def is_paired(self):
        return self._made_hand_explorer.is_paired

    @property
    def is_straighted(self):
        return self._made_hand_explorer.is_straighted

    @property
    def straight_draws(self):
        return self._straight_draw_explorer.straight_draws

    @property
    def backdoor_straight_draws(self):
        return self._straight_draw_explorer.backdoor_straight_draws

    @property
    def is_flushed(self):
        return self._made_hand_explorer.is_flushed

    @property
    def flush_draws(self):
        return self._flush_draw_explorer.flush_draws

    @property
    def backdoor_flush_draws(self):
        return self._flush_draw_explorer.backdoor_flush_draws

    @property
    def is_rainbow(self):
        return self._flush_draw_explorer.is_rainbow

    @property
    def has_turned_flush_draw(self):
        return self._flush_draw_explorer.has_turned_flush_draw

    @property
    def made_hands(self):
        return self._made_hand_explorer.made_hands

    @property
    def flush_blockers(self):
        return self._made_hand_explorer.flush_blockers

    @property
    def straight_blockers(self):
        return self._made_hand_explorer.straight_blockers

    @property
    def flush_draw_blockers(self):
        return self._flush_draw_explorer.flush_draw_blockers

    @property
    def straight_draw_blockers(self):
        return self._straight_draw_explorer.straight_draw_blockers

    @staticmethod
    def _generalize_hands(made_hands: Iterable, types: Iterable) -> list:
        """ Removes non-generic hands.

        Args:
            made_hands (list): list of MadeHand
            types (list): list of MadeHand type_s: MadeHand.PAIR, MadeHand.FLUSH, MadeHand.TRIPS

            Removes hands with kickers if finding for generic hands without kickers (Pairs, Trips)
            Removes flushes with rank if finding for generic flushes
        Returns:
            list: list of  generalized MadeHands
        """

        must_generalize_pairs = False
        must_generalize_trips = False
        must_generalize_flushes = False
        hands = copy.deepcopy(made_hands)
        if MadeHand.PAIR in types:
            must_generalize_pairs = True
        if MadeHand.FLUSH in types:
            must_generalize_flushes = True
        if MadeHand.TRIPS in types:
            must_generalize_trips = True

        for hand in hands:
            if must_generalize_pairs and hand.type_ == MadeHand.PAIR and hand.subtype == MadeHand.BOARD_PAIR:
                hand.absolute_rank = hand.absolute_rank[:1]
                hand.relative_rank = hand.relative_rank[:2]
                hand.hole.pop()
                hand.hand.pop()
            if must_generalize_trips and hand.type_ == MadeHand.TRIPS:
                hand.absolute_rank = hand.absolute_rank[:1]
                hand.relative_rank = hand.relative_rank[:1]
                hand.hole.pop()
                hand.hand.pop()
            if must_generalize_flushes and hand.type_ == MadeHand.FLUSH:
                hand.absolute_rank = (0,)
                hand.relative_rank = (0,)
                suit = hand.hole[0].suit
                generalised_card_index = hand.hand.index(hand.hole[0])
                hand.hole[0] = Card(0, suit)
                hand.hand[generalised_card_index] = Card(0, suit)
                hand.hand.cards.sort(reverse=True)

        return sorted(list(set(hands)), reverse=True)

    def find_made_hands(self, type_: int, sub_type: int = MadeHand.NONE,
                        relative_rank: tuple = None, strictness: str = 'only_that') -> list:
        """ Returns list of hands (or that hands and better hands) of specified type, sub_type and relative rank

            If appropriate hand doesn't exist returns hand one rank higher.
            If appropriate hand doesn't exist and there are not better hands returns empty list
        Args:
            type_ (int): MadeHand type_
            sub_type (int): MadeHand sub_type
            relative_rank (tuple): MadeHand relative_rank.
            strictness (str): one of BoardExplorer.ONLY_THAT, .THAT_AND_BETTER, .ALL_BUT_THAT
            if THAT_AND_BETTER returns not only the found hand, but all the hands better

        Returns:
            list: list of MadeHand
        """

        two_digit_hand_types = [MadeHand.TRIPS,
                                MadeHand.TWO_PAIR,
                                MadeHand.BOARD_PAIR,
                                MadeHand.POCKET_PAIR
                                ]
        must_generalize = False
        if (type_ in two_digit_hand_types or sub_type in two_digit_hand_types) and relative_rank is not None and len(
                relative_rank) < 2:
            must_generalize = True
        elif type_ == MadeHand.PAIR and sub_type == MadeHand.NONE:
            must_generalize = True
        if relative_rank == (0,):
            must_generalize = True
            relative_rank = None

        condition_equal = 0
        condition_equal_or_less = 1
        condition_doesnt_equal = 3

        def relative_rank_condition(made_hand, condition=condition_equal_or_less):
            rank_is_none = relative_rank is None
            specified_rank = relative_rank
            if type_ == MadeHand.PAIR and sub_type == MadeHand.NONE:
                specified_hand_rank = made_hand.relative_rank[:1]
            elif type_ == MadeHand.PAIR and sub_type == MadeHand.BOARD_PAIR:
                if must_generalize:
                    specified_hand_rank = made_hand.relative_rank[1:2]
                else:
                    specified_hand_rank = made_hand.relative_rank[1:]
            elif type_ == MadeHand.PAIR and sub_type == MadeHand.POCKET_PAIR:
                if must_generalize:
                    specified_hand_rank = made_hand.relative_rank[1:2]
                else:
                    specified_hand_rank = made_hand.relative_rank[1:]
            else:
                specified_hand_rank = made_hand.relative_rank
            if condition == condition_equal_or_less:
                return rank_is_none or specified_hand_rank <= specified_rank
            elif condition == condition_equal:
                return rank_is_none or specified_hand_rank == specified_rank

        def that_hands_and_better(made_hand):
            upper_hands = (made_hand.type_ > type_)
            type_matches = (made_hand.type_ == type_)
            that_hands = type_matches and relative_rank_condition(made_hand, condition_equal_or_less)
            return upper_hands or that_hands

        def only_that_hands(made_hand):
            type_matches = (made_hand.type_ == type_)
            subtype_matches = (sub_type is None or made_hand.subtype == sub_type)
            relative_rank_matches = relative_rank_condition(made_hand, condition_equal)
            return type_matches and subtype_matches and relative_rank_matches

        if sub_type == MadeHand.BOARD_PAIR:
            searchable = itertools.takewhile(that_hands_and_better,
                                             filter(lambda x: x.subtype != MadeHand.POCKET_PAIR, self.made_hands))
        elif sub_type == MadeHand.POCKET_PAIR:
            searchable = itertools.takewhile(that_hands_and_better,
                                             filter(lambda x: x.subtype != MadeHand.BOARD_PAIR, self.made_hands))
        else:
            searchable = itertools.takewhile(that_hands_and_better, self.made_hands)

        last_hand = None
        for hand in searchable:
            last_hand = hand
        if last_hand:
            founded_hands = copy.deepcopy(self.made_hands[:self.made_hands.index(last_hand) + 1])
        else:
            founded_hands = []

        if strictness == self.THAT_AND_BETTER:
            ungeneralized_hands = founded_hands
        else:
            hands = list(itertools.takewhile(only_that_hands, sorted(founded_hands)))
            if founded_hands:
                if hands:
                    ungeneralized_hands = sorted(hands, reverse=True)  # Returns exact matches
                else:
                    ungeneralized_hands = [founded_hands[-1]]  # There are no exact matches, returns the better hand
            else:
                ungeneralized_hands = []  # There are no even better hands

        if ungeneralized_hands and must_generalize:
            generalized_hands = self._generalize_hands(ungeneralized_hands, [type_])
        else:
            generalized_hands = ungeneralized_hands
        if strictness == BoardExplorer.ALL_BUT_THAT:
            all_hands = copy.deepcopy(self.made_hands)
            for hand in generalized_hands:
                all_hands.remove(hand)
            return all_hands
        else:
            return generalized_hands

    def find_straight_draws(self, type_: int = StraightDraw.NORMAL, relative_rank: tuple = (0, 0),
                            strictness: str = 'only_that') -> list:
        """ Returns list of StraightDraw with required number of outs and nut outs

        Args:
            type_ (int): type of straight draw on of StraightDraw.NORMAL, StraightDraw.BACKDOOR
            relative_rank (tuple): (number outs, number nut outs). Use 0 if number not required
            strictness (str): if BoardExplorer.THAT_AND_BETTER, but all the draw better

        Returns:
            list: list of found draws
        """
        outs = relative_rank[0]
        try:
            nut_outs = relative_rank[1]
        except IndexError:
            nut_outs = 0

        if type_ == StraightDraw.BACKDOOR:
            searchable = self.backdoor_straight_draws
        else:
            searchable = self.straight_draws
        if nut_outs:
            searchable = sorted(searchable, reverse=True, key=lambda x: (x.count_nut_outs(), x.count_outs()))
        draws = {}
        index = self._get_first_suitable_straight_draw_index(type_, outs, nut_outs)
        if index == -1:
            return []
        if strictness == BoardExplorer.THAT_AND_BETTER:
            draws = {draw.hole_ranks: draw for draw in searchable[0:index + 1]}
        else:
            first_suitable_outs = searchable[index].count_outs()
            first_suitable_nut_outs = searchable[index].count_nut_outs()
            for draw in reversed(searchable[0:index + 1]):
                if draw.count_outs() == first_suitable_outs \
                        and (not nut_outs or draw.count_nut_outs() == first_suitable_nut_outs):
                    draws[draw.hole_ranks] = draw
                else:
                    break
        self._remove_excess_straight_draws(draws)
        return sorted(list(draws.values()), reverse=True)

    def _get_first_suitable_straight_draw_index(self, draw_type: int = StraightDraw.NORMAL,
                                                outs: int = 0, nut_outs: int = 0) -> int:
        if draw_type == StraightDraw.BACKDOOR:
            searchable = self.backdoor_straight_draws
        else:
            searchable = self.straight_draws
        if nut_outs:
            searchable = sorted(searchable, reverse=True, key=lambda x: (x.count_nut_outs(), x.count_outs()))
        index = -1
        for draw in reversed(searchable):
            if draw.count_outs() >= outs:
                if not nut_outs or draw.count_nut_outs() >= nut_outs:
                    index = searchable.index(draw)
                    break
        return index

    @staticmethod
    def _remove_excess_straight_draws(draws: dict):
        """ Remove excess higher cards draw, if they contains lower cards draw

            For example for [KQJ, QJ, JT] KQJ is excess

            Args:
                draws: dict of draw
        """
        ranks = {}
        remove_it = set()
        for size in range(2, 5):
            ranks[size] = {ranks for ranks in draws.keys() if len(ranks) == size}

        for four_card_draw in ranks[4]:
            for three_card_comb in itertools.combinations(four_card_draw, 3):
                if three_card_comb in ranks[3]:
                    remove_it.add(four_card_draw)
                    break

            for two_card_comb in itertools.combinations(four_card_draw, 2):
                if two_card_comb in ranks[2]:
                    remove_it.add(four_card_draw)
                    break

        for three_card_draw in ranks[3]:
            for two_card_comb in itertools.combinations(three_card_draw, 2):
                if two_card_comb in ranks[2]:
                    remove_it.add(three_card_draw)
                    break
        for rank in remove_it:
            del draws[rank]

    def find_flush_draws(self, type_: int = FlushDraw.NORMAL, sub_type: int = None,
                         relative_rank: tuple = None, strictness: str = 'only_that'):
        """ Returns list flush draws for the board

        Args:
            type_ (int): type of draw, FlushDraw.FLOPPED or FlushDraw.TURNED
            sub_type (int): sub type of draw: FlushDraw.NORMAL, FlushDraw.BACKDOOR, FlushDraw.NONE (for both sub types)
            relative_rank (tuple):  relative rank of draw. (1,) for 1st draw, (2,) for 2nd.
                If relative_rank is None, than returns list of generic draws
                (1 or 2 draws, if turned flush draws are possible)
            strictness (str):  if BoardExplorer.THAT_AND_BETTER returns not only the found draw, but all the draw better

        Returns:
            list:  list of draws
        """

        if sub_type is None:
            sub_type = FlushDraw.NONE
        if type_ == FlushDraw.NORMAL:
            searchable = self.flush_draws
        else:
            searchable = self.backdoor_flush_draws

        if relative_rank is None:  # Generics draws
            draws = []
            if sub_type == FlushDraw.NONE or sub_type == FlushDraw.FLOPPED:
                flopped_draws = [draw for draw in searchable if draw.subtype == FlushDraw.FLOPPED]
                if flopped_draws:
                    draws.append(flopped_draws[0])
            if sub_type == FlushDraw.NONE or sub_type == FlushDraw.TURNED:
                turned_draws = [draw for draw in searchable if draw.subtype == FlushDraw.TURNED]
                if turned_draws:
                    draws.append(turned_draws[0])
            return [FlushDraw(draw.type_, draw.subtype, (0,), (0,), CardSet([Card(0, draw.hole[0].suit)] * 2))
                    for draw in draws]
        else:  # Concrete draws
            if strictness == BoardExplorer.THAT_AND_BETTER:
                if sub_type == FlushDraw.NONE:
                    return [draw for draw in searchable if draw.relative_rank <= relative_rank]
                else:
                    return [draw for draw in searchable
                            if draw.relative_rank <= relative_rank and draw.subtype == sub_type]
            else:
                if sub_type == FlushDraw.NONE:
                    return [draw for draw in searchable if draw.relative_rank == relative_rank]
                else:
                    return [draw for draw in searchable
                            if draw.relative_rank == relative_rank and draw.subtype == sub_type]

    def find_blockers(self, type_: int, subtype: int = None, relative_rank: tuple = None,
                      strictness: str = 'only_that') -> list:
        """ Returns list of blockers for the board

        Args:
            type_ (int): type of blocker: Blocker.FLUSH_BLOCKER, Blocker.STRAIGHT_BLOCKER,
                Blocker.FLUSH_DRAW_BLOCKER,  Blocker.STRAIGHT_DRAW_BLOCKER
            subtype (int): sub type of blocker: Blocker.FLOPPED, Blocker.TURNED, Blocker.ONE_CARD, Blocker.TWO_CARD
            relative_rank (tuple): rank of blocker
            strictness (str):  if 'that_and_better' returns not only the found blocker, but all the blockers better

        Returns:
            list: list of blockers
        """
        searchable = []
        if type_ == Blocker.FLUSH_BLOCKER:
            searchable = self.flush_blockers
        elif type_ == Blocker.STRAIGHT_BLOCKER:
            searchable = self.straight_blockers
        elif type_ == Blocker.FLUSH_DRAW_BLOCKER:
            searchable = self.flush_draw_blockers
        elif type_ == Blocker.STRAIGHT_DRAW_BLOCKER:
            searchable = self.straight_draw_blockers

        if relative_rank is None:  # Generic draw
            if subtype:
                all_blockers = [blocker for blocker in searchable if blocker.type_ == type_
                                and blocker.subtype == subtype]
            else:
                all_blockers = [blocker for blocker in searchable if blocker.type_ == type_]
            return all_blockers
        else:  # Concrete draw
            if strictness == BoardExplorer.THAT_AND_BETTER:
                if subtype:
                    return [blocker for blocker in searchable
                            if blocker.type_ == type_ and blocker.subtype == subtype
                            and blocker.relative_rank <= relative_rank]
                else:
                    return [blocker for blocker in searchable
                            if blocker.type_ == type_ and blocker.relative_rank <= relative_rank]
            else:
                if subtype:
                    return [blocker for blocker in searchable
                            if blocker.type_ == type_ and blocker.subtype == subtype
                            and blocker.relative_rank == relative_rank]
                else:
                    return [blocker for blocker in searchable
                            if blocker.type_ == type_ and blocker.relative_rank == relative_rank]

    def find(self, family: int, type_: int, sub_type: int = None, relative_rank: tuple = None,
             strictness: str = 'only_that') -> list:
        """ Returns found hands for one of family of hands: made hands, flush draws, straight draws, blockers

        Args:
            family (int): family of finding hands: BoardExplorer.MADE_HAND, BoardExplorer.FLUSH_DRAW,
                BoardExplorer.STRAIGHT_DRAW, BoardExplorer.BLOCKER
            type_ (int): type of hands
            sub_type (int): sub_type of hands
            relative_rank (tuple): relative rank of hands
            strictness (bool): if 'that_and_better' returns not only the found hands, but all the hands better

        Returns:
            list: list of found hands
        """
        if family == BoardExplorer.MADE_HAND:
            return self.find_made_hands(type_, sub_type, relative_rank, strictness)
        elif family == BoardExplorer.FLUSH_DRAW:
            return self.find_flush_draws(type_, sub_type, relative_rank, strictness)
        elif family == BoardExplorer.STRAIGHT_DRAW:
            return self.find_straight_draws(type_=type_, relative_rank=relative_rank, strictness=strictness)
        elif family == BoardExplorer.BLOCKER:
            return self.find_blockers(type_, sub_type, relative_rank, strictness)

    def _easy_range2hands(self, family: str, easy_range: str, relative_rank: tuple = None,
                          strictness: str = 'only_that') -> list:
        """ Returns found hands for easy range

        Args:
            family (int):  family of finding hands: BoardExplorer.MADE_HAND, BoardExplorer.FLUSH_DRAW,
                BoardExplorer.STRAIGHT_DRAW, BoardExplorer.BLOCKER
            easy_range (str): easy range
            relative_rank (tuple): relative rank of hand
            strictness (str):  if 'that_and_better' returns not only the found hands, but all the hands better

        Returns:
            list: list of found hands
        """
        FAMILY = 'family'
        TYPE_ = 'type_'
        SUBTYPE = 'sub_type'
        RELATIVE_RANK = 'relative_rank'
        STRICTNESS = 'strictness'

        params = {FAMILY: family,
                  TYPE_: Syntax.syntax[easy_range].type_}
        if relative_rank is None:
            if Syntax.syntax[easy_range].relative_rank:
                params[RELATIVE_RANK] = Syntax.syntax[easy_range].relative_rank
            elif Syntax.syntax[easy_range].rank_prefix:
                params[RELATIVE_RANK] = Syntax.syntax[easy_range].rank_prefix
        else:
            params[RELATIVE_RANK] = relative_rank
            if Syntax.syntax[easy_range].rank_prefix:
                params[RELATIVE_RANK] = Syntax.syntax[easy_range].rank_prefix + params[RELATIVE_RANK]
        if Syntax.syntax[easy_range].subtype:
            params[SUBTYPE] = Syntax.syntax[easy_range].subtype
        if Syntax.syntax[easy_range].and_better:
            params[STRICTNESS] = Syntax.syntax[easy_range].and_better
        else:
            params[STRICTNESS] = strictness
        return self.find(**params)

    @staticmethod
    def _hands2ppt(hands: list):
        """ Returns ppt ranges for list of hands"""
        return ','.join([str(hand.hole) for hand in hands])

    def ppt(self, easy_ranges: str) -> str:
        """ Returns PPT range for easy range

        Args:
            easy_ranges (str):

        Returns:
            str: PPT range
        """
        """ Returns PPT range for easy_range string"""
        if easy_ranges.strip() == '*':
            return '*'

        parser = _parser

        results = None
        try:
            results = parser.parseString(easy_ranges, parseAll=True)
        except pp.ParseException as pe:
            raise EasyRangeValueError.from_pe(pe)

        ppt_range = ''
        for result in results:
            if isinstance(result, str):
                if result != 'K':  # The kicker symbol isn't needed
                    ppt_range += result
            else:
                res_dict = result.asDict()
                family = None
                if BoardExplorer.MADE_HAND in res_dict:
                    family = BoardExplorer.MADE_HAND
                elif BoardExplorer.STRAIGHT_DRAW in res_dict:
                    family = BoardExplorer.STRAIGHT_DRAW
                elif BoardExplorer.FLUSH_DRAW in res_dict:
                    family = BoardExplorer.FLUSH_DRAW
                elif BoardExplorer.BLOCKER in res_dict:
                    family = BoardExplorer.BLOCKER
                easy_range = res_dict[family]
                relative_rank = res_dict.get(Syntax.RELATIVE_RANK)
                if relative_rank is not None:
                    if isinstance(relative_rank, str):
                        relative_rank = (int(relative_rank),)
                    else:
                        relative_rank = tuple([int(rank) for rank in relative_rank if rank != '_'])
                pp_and_better = res_dict.get(Syntax.AND_BETTER)
                if pp_and_better:
                    strictness = self.THAT_AND_BETTER
                else:
                    strictness = self.ONLY_THAT
                hands = self._easy_range2hands(family, easy_range, relative_rank, strictness)
                if  len(hands) > 1:
                    ppt_range += '(' + BoardExplorer._hands2ppt(hands) + ')'
                else:
                    ppt_range += BoardExplorer._hands2ppt(hands)

        return ppt_range

    def __repr__(self):
        class_name = type(self).__name__
        return "{}({!r})".format(class_name, self._board)


def _generate_parser() -> pp.ParserElement:
    """ Generates pyparsing parser for easy ranges

    Returns:
        pyparsing.ParserElement: generated parser
    """
    digits = [0, 1, 2]
    families = [Syntax.MADE_HAND, Syntax.STRAIGHT_DRAW, Syntax.FLUSH_DRAW, Syntax.BLOCKER]
    hands_digits = {0: {}, 1: {}, 2: {}}
    for (key, value) in Syntax.syntax.items():
        for digit in value.digits:
            family_list = hands_digits[digit].setdefault(value.family, [])
            family_list.append(key)

    pp_and_better = pp.Optional(pp.Literal('+')).setResultsName(Syntax.AND_BETTER)
    pp_kicker = pp.Optional(pp.Literal('K'))

    pp_one_or_more = None

    for digit in digits:
        for family in families:
            if hands_digits[digit].get(family):
                pp_hand = pp.oneOf(hands_digits[digit][family], caseless=True).setResultsName(family)
                if digit != 0:
                    pp_number = pp.Word(pp.nums, min=1, max=2)
                    if digit == 1:
                        pp_relative_rank = pp_number.setResultsName(Syntax.RELATIVE_RANK)
                    else:
                        pp_relative_rank = pp.Group(pp_number + '_' + pp_number).setResultsName(Syntax.RELATIVE_RANK)
                    pp_hand_group = pp.Group(pp_hand + pp_relative_rank + pp_kicker + pp_and_better)
                else:
                    pp_hand_group = pp.Group(pp_hand + pp_and_better)
                if pp_one_or_more is None:
                    pp_one_or_more = pp_hand_group
                else:
                    pp_one_or_more = pp_one_or_more ^ pp_hand_group

    operator = pp.oneOf(", : ! ( )").setResultsName('operator')
    parser = pp.OneOrMore(pp_one_or_more ^ operator ^ '*')
    return parser


_parser = _generate_parser()


class EasyRangeValueError(Exception):
    def __init__(self, *args, easy_range, column):
        self.easy_range = easy_range
        self.column = column

    @classmethod
    def from_pe(cls, pe: pp.ParseException):
        message = "Unexpected symbol '{}' at column {}: {}"
        return cls(message.format(pe.line[pe.col - 1], pe.col, pe.line),
                   easy_range=pe.line,
                   column=pe.col)


def check_range(range_):
    """ Checks easy range for errors

    Args:
        range_ (str): easy range

    Returns:
        bool: True if no errors was found
    """
    try:
        _parser.parseString(range_, parseAll=True)
    except pp.ParseException as pe:
        raise EasyRangeValueError.from_pe(pe) from None
    else:
        return True


class PureHand:
    def __init__(self, name, include: Union[CardSet, Iterable[CardSet]],
                 exclude: Union[CardSet, Iterable[CardSet]]):
        self.name = name
        if isinstance(include, CardSet):
            self.include = [include]
        else:
            self.include = list(include)
        if isinstance(exclude, CardSet):
            self.exclude = [exclude]
        else:
            self.exclude = list(exclude)

    def __str__(self):
        return self.name

    def __add__(self, other):
        name = self.name + ':' + other.name
        include = self.include + other.include
        exclude = [card_set for card_set in self.exclude if card_set not in other.include]
        exclude += [card_set for card_set in other.exclude if card_set not in self.include and card_set not in exclude]
        return PureHand(name, include, exclude)

    def ppt(self):
        include_ppt = ",".join(str(card_set) for card_set in self.include)
        if len(self.include) > 1:
            include_ppt = "(" + include_ppt + ")"
        exclude_ppt = ",".join(str(card_set) for card_set in self.exclude)
        if len(self.exclude) > 1:
            exclude_ppt = "(" + exclude_ppt + ")"
        return "{}!{}".format(include_ppt, exclude_ppt)


class Combinations:
    pass