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

""" Classes implementing cards """

import re
import itertools
from collections import namedtuple
from typing import Iterable

Card = namedtuple('Card', ['rank', 'suit'])

SUIT_TO_STRING = {1: "s", 2: "h", 3: "d", 4: "c"}
RANK_TO_STRING = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "T", 11: "J", 12: "Q",
                  13: "K", 14: "A"}

STRING_TO_SUIT = dict([(v, k) for k, v in SUIT_TO_STRING.items()])
STRING_TO_RANK = dict([(v, k) for k, v in RANK_TO_STRING.items()])


def card_from_str(card: str) -> Card:
    """ Returns Card from string representation of card

    Args:
        card (str): string representation of card

    Returns:
        Card: card
    """
    if not (len(card) == 2 or len(card) == 1):
        raise ValueError("card must contain two or one symbol")

    if len(card) == 2:
        try:
            rank = STRING_TO_RANK[card[0].upper()]
        except KeyError:
            raise ValueError('Non existent rank "{}"'.format(card[0]), card[0], 0)
        try:
            suit = STRING_TO_SUIT[card[1].lower()]
        except KeyError:
            raise ValueError('Non existent suit "{}"'.format(card[1]), card[1], 1)
    elif card.upper() in STRING_TO_RANK:
        rank = STRING_TO_RANK[card.upper()]
        suit = 0
    elif card.lower() in STRING_TO_SUIT:
        rank = 0
        suit = STRING_TO_SUIT[card.lower()]
    elif card == '*':
        rank = 0
        suit = 0
    else:
        raise ValueError("Wrong symbol '{}'".format(card))

    return Card(rank, suit)


def card_to_str(card: Card) -> str:
    """ Returns string representation of card

    Args:
        card (Card): card

    Returns:
        str: string representation of the card
    """
    if card == Card(0, 0):
        return '*'
    else:
        return RANK_TO_STRING.get(card.rank, '') + SUIT_TO_STRING.get(card.suit, '')


def cards_to_str(cards: Iterable) -> str:
    """ Return string representation of cards

    Args:
        cards (Iterable): cards

    Returns:
        str: string representation of the card
    """
    return "".join([card_to_str(card) for card in cards])


class Deck:
    """ Class representing a standard deck"""

    def __init__(self, dead_cards: Iterable=None):
        """ Constructor for Deck

        Args:
            dead_cards (Iterable): dead cards, that will be removed from the Deck
        """
        self.cards = [Card(rank, suit) for rank in range(2, 15) for suit in range(1, 5)]
        if dead_cards:
            self.remove_cards(dead_cards)

    def __getitem__(self, item):
        return self.cards[item]

    def __len__(self):
        return len(self.cards)

    def remove_cards(self, cards: Iterable):
        """ Removes cards from the Deck

        Args:
            cards (Iterable): cards to remove
        """
        for card in cards:
            self.cards.remove(card)


class CardSet:
    """ Class representing set of card """

    def __init__(self, cards: Iterable=None):
        """ Constructor for CardSet

        Args:
            cards (Iterable): cards
        """
        if cards is None:
            self.cards = []
        else:
            self.cards = list(cards)
        self._ranks = None
        self._unique_ranks = None
        self._suits = None
        self._unique_suits = None
        self._remaining_ranks = None

    def __getitem__(self, item):
        cls = type(self)
        if isinstance(item, int):
            return self.cards[item]
        elif isinstance(item, slice):
            return cls(self.cards[item])
        else:
            msg = '{cls.__name__} idices must be integers'
            raise TypeError(msg.format(cls=cls))

    def __setitem__(self, key, value):
        self.cards[key] = value

    def __len__(self):
        return len(self.cards)

    def __eq__(self, other):
        return sorted(self.cards) == sorted(other.cards)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return "{}.from_str('{!s}')".format(cls_name, self)

    def __str__(self):
        return ''.join([card_to_str(card) for card in self.cards])

    def ppt(self):
        return self.__str__()

    def __add__(self, other):
        cards = self.cards + other.cards
        self._ranks = None
        return CardSet(cards)

    def index(self, x):
        return self.cards.index(x)

    def remove(self, x):
        self.cards.remove(x)

    def pop(self, *args):
        self.cards.pop(*args)

    @property
    def ranks(self) -> list:
        """ Returns a list of the ranks"""
        if self._ranks is None:
            self._ranks = [card.rank for card in self.cards]
        # noinspection PyTypeChecker
        return self._ranks

    @property
    def unique_ranks(self) -> list:
        """ Returns a list of the unique ranks. Sorted descending"""
        if self._unique_ranks is None:
            self._unique_ranks = sorted(list(set(self.ranks)), reverse=True)
        # noinspection PyTypeChecker
        return self._unique_ranks

    @property
    def remaining_ranks(self) -> list:
        """ Returns remaining ranks"""
        if self._remaining_ranks is None:
            self._remaining_ranks = [rank for rank in range(2, 15) if rank not in self.unique_ranks]
        # noinspection PyTypeChecker
        return self._remaining_ranks

    @property
    def suits(self) -> list:
        """ Returns a list of the suits"""
        if self._suits is None:
            self._suits = [card.suit for card in self.cards]
        # noinspection PyTypeChecker
        return self._suits

    @property
    def unique_suits(self) -> list:
        """ Return list of the unique suits. Sorted descending """
        if self._unique_suits is None:
            self._unique_suits = sorted(list(set(self.suits)), reverse=True)
        # noinspection PyTypeChecker
        return self._unique_suits

    def get_concrete_cards(self) -> list:
        """ Returns list of concrete cards """
        return [card for card in self.cards if (card.suit != 0 and card.rank != 0)]

    def get_rank_jokers(self) -> list:
        """ Returns list of rank jokers """
        return [card.rank for card in self.cards if (card.suit == 0 and card.rank != 0)]

    def get_suit_jokers(self) -> list:
        """ Returns list of suit jokers """
        return [card.suit for card in self.cards if (card.suit != 0 and card.rank == 0)]

    def count_full_jokers(self) -> int:
        """ Returns list of full jokers """
        return len([card.rank for card in self.cards if (card.rank == 0 and card.suit == 0)])

    def get_combinations(self, size: int) -> list:
        """ Return a list of all combinations of a given size """
        return [CardSet(cards) for cards in itertools.combinations(self, size)]

    def get_rank_combinations(self, size: int) -> list:
        """ Return a list of all combinations of unique ranks of a given size """
        return [list(ranks) for ranks in itertools.combinations(sorted(self.unique_ranks, reverse=True), size)]

    def get_ranks_for_suit(self, suit: int) -> list:
        """ Returns list of ranks for certain suit"""
        return [card.rank for card in self.cards if card.suit == suit]

    @classmethod
    def from_str(cls, card_set=''):
        """
        Create CardSet from string representation of cards.

        Spaces are ignored ('As Js') = ('AsJs')

        Args:
            card_set (str): string representation of cards.

        Returns:
            CardSet: created CardSet
        """
        if card_set == '' or card_set is None:
            return cls([])
        card_set = card_set.replace(' ', '')
        card_set = card_set.upper()
        p = re.compile(r'(\*|[AKQJT2-9]?[SHDC]?)')
        card_str_list = p.findall(card_set)
        card_str_list.remove('')
        card_list = [card_from_str(card) for card in card_str_list]

        return cls(card_list)

    @classmethod
    def from_ranks(cls, ranks: Iterable):
        """ Create CardSet from tuple of ranks"""
        cards = [Card(rank, 0) for rank in ranks]
        return cls(cards)

    @classmethod
    def from_card_sets(cls, *card_sets):
        cs = cls()
        for card_set in card_sets:
            cs = cs + card_set
        return cs


class Board(CardSet):
    """
    Class representing board. Just CardSet with 0, 3, 4 or 5 cards
    """

    def __init__(self, cards: Iterable=None):
        super(Board, self).__init__(cards)
        if not (len(self) in [0, 3, 4, 5]):
            raise ValueError("Board must contains 0, 3, 4 or 5 cards, was {}".format(len(self)))
