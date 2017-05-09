import itertools
from collections import namedtuple
from ploev.ppt import Pql, OddsOracle

SubRange = namedtuple("SubRange", "range fraction equity")


def _create_cumulative_ranges(sub_ranges):
    return list(itertools.accumulate(sub_ranges, lambda sr1, sr2: sr2 + '!' + sr1))


def _close_parenthesis(range_: str):
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
    def __init__(self, odds_oracle: OddsOracle):
        self.odds_oracle = odds_oracle
        self.pql = Pql(self.odds_oracle)

    def equity(self, players, board=None, dead=None, hero_only=False):
        if hero_only:
            return self.pql.hero_equity(players[0], players[1:], board, dead)
        else:
            if board is None:
                board = ''
            if dead is None:
                dead = ''
            return self.pql.equity(players, board, dead)

    def range_distribution(self, main_range, sub_ranges, board, hero=None, equity=True, cumulative=True):
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
