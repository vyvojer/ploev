"""
Classes implementing various calculations.
"""
import itertools
from collections import namedtuple
from ploev.ppt import Pql, OddsOracle
from typing import Iterable

SubRange = namedtuple("SubRange", "range fraction equity")


def _create_cumulative_ranges(sub_ranges: Iterable) -> list:
    """ Creates cumulative ranges from ranges """
    return list(itertools.accumulate(sub_ranges, lambda sr1, sr2: sr2 + '!' + sr1))


def _close_parenthesis(range_: str) -> str:
    if range_[0] != '(' and range_[-1] != ')':
        return '(' + range_ + ')'
    else:
        parentheses = [symbol for symbol in range_[1:-1] if symbol == '(' or symbol == ')']
        for index, parenthesis in enumerate(parentheses):
            if parentheses[index - 1] == '(' and parentheses == ')':
                parentheses.pop(index)
                parentheses.pop(index-1)
        if parentheses:
            return '(' + range_ + ')'
        else:
            return range_


class Calc:
    """
    Class to make various general calculations
    """
    def __init__(self, odds_oracle: OddsOracle):
        """

        Args:
            odds_oracle (OddsOracle): OddsOracle
        """
        self.odds_oracle = odds_oracle
        self.pql = Pql(self.odds_oracle)

    def equity(self, players, board=None, dead=None, hero_only=False):
        """ Calculates equities

        For intensive computations set 'hero_only' to True if you need only hero equity. It's faster.
        If hero_only is True return float (hero_equity), otherwise returns list of equities.

        Args:
            players (list): players ranges. If hero_only is True calculates equity only for first player
            board (str): board (optional)
            dead (str): dead cards (optional)
            hero_only (bool): If True calculate equity only for the hero (faster)

        Returns:
            list: if hero_only is False, returns list of equities

        Returns:
            float: if hero_only is True, returns hero's equity
        """
        if hero_only:
            return self.pql.hero_equity(players[0], players[1:], board, dead)
        else:
            if board is None:
                board = ''
            if dead is None:
                dead = ''
            return self.pql.equity(players, board, dead)

    def range_distribution(self, main_range: str, sub_ranges: Iterable, board: str,
                           hero: str=None, equity: bool=True, cumulative: bool=True):
        """ Calculates how often sub_ranges are in main_range and what is hero's equity vs sub_ranges

        Args:
            main_range (str): main range
            sub_ranges (Iterable): sub ranges
            board (str): board
            hero (str): hero range (optional)
            equity (bool): if True calculate equity
            cumulative (bool): if True takes sub ranges, as cumulative

        Returns:
            list: list of namedtuple (SubRange). Fields are:
            'equity' - equity of sub range (0 if 'equity' argument is False;
            'fraction' - fraction of sub range;
            'range' - sub range.

        """
        sub_ranges = map(_close_parenthesis, sub_ranges)
        if cumulative:
            sub_ranges = _create_cumulative_ranges(sub_ranges)
        fractions = self.pql.count_in_range(main_range, sub_ranges, board, hero)
        distribution = []
        for subrange, fraction in zip(sub_ranges, fractions):
            if equity:
                villain_range = main_range + ":" + subrange
                equity = self.pql.hero_equity(hero, [villain_range], board)
            else:
                equity = 0
            distribution.append(SubRange(subrange, fraction, equity))
        return distribution


class GameCalc:
    pass
