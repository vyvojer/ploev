import unittest

from ploev import calc
from ploev.calc import Calc, GameCalc
from ploev.ppt import OddsOracle


class CalcModuleTest(unittest.TestCase):

    def test_close_parenthesis(self):
        self.assertEqual(calc.close_parenthesis('77,KK'), '(77,KK)')
        self.assertEqual(calc.close_parenthesis('(77,KK)'), '(77,KK)')
        self.assertEqual(calc.close_parenthesis('(77,KK):(ss)'), '((77,KK):(ss))')

    def test_create_cumulative_ranges(self):
        ranges = [
            '(77,KK)',
            '(74,K4,K7,44,77,KK)',
            '*',
        ]
        expected = [
            '(77,KK)',
            '(74,K4,K7,44,77,KK)!(77,KK)',
            '*!(74,K4,K7,44,77,KK)!(77,KK)',
        ]
        cumulative_ranges = calc.create_cumulative_ranges(ranges)
        self.assertEqual(cumulative_ranges, expected)


class CalcTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        odds_oracle = OddsOracle()
        odds_oracle.trials = 100000
        odds_oracle.seconds = 1
        cls.odds_oracle = odds_oracle
        cls.calc = Calc(odds_oracle)

    def test_range_distribution(self):
        main_range = '75%'
        board = '7c Kh 4s'
        sub_ranges = [
            '77,KK',
            '74,K4,K7,44,77,KK',
            '*'
        ]
        hero = '8c4h6s4c'
        rd = self.calc.range_distribution(main_range, sub_ranges, board, players=[hero])
        self.assertAlmostEqual(rd[0].fraction, 0.041, delta= 0.01)
        self.assertAlmostEqual(rd[1].fraction, 0.0733, delta=0.01)
        self.assertAlmostEqual(rd[2].fraction, 0.885, delta=0.01)
        self.assertAlmostEqual(rd[0].equity, 0.23, delta= 0.02)
        self.assertAlmostEqual(rd[1].equity, 0.79, delta=0.02)
        self.assertAlmostEqual(rd[2].equity, 0.88, delta=0.02)

    def test_range_distribution_no_cumulative(self):
        main_range = '75%'
        board = '7c Kh 4s'
        sub_ranges = [
            '77,KK',
            '74,K4,K7,44,77,KK',
            '*'
        ]
        players = ['8c4h6s4c']
        rd = self.calc.range_distribution(main_range, sub_ranges, board, players, cumulative=False)
        self.assertAlmostEqual(rd[0].fraction, 0.041, delta= 0.01)
        self.assertAlmostEqual(rd[1].fraction, 0.115, delta=0.01)
        self.assertAlmostEqual(rd[2].fraction, 1, delta=0.01)
        self.assertAlmostEqual(rd[0].equity, 0.23, delta= 0.02)
        self.assertAlmostEqual(rd[1].equity, 0.59, delta=0.02)
        self.assertAlmostEqual(rd[2].equity, 0.84, delta=0.02)

    def test_equity(self):
        players = [ '3s4s5d6d', '10%', 'AA',]
        equities = self.calc.equity(players)
        self.assertAlmostEqual(equities[0], 0.34, delta=0.01)
        self.assertAlmostEqual(equities[1], 0.30, delta=0.01)
        self.assertAlmostEqual(equities[2], 0.36, delta=0.01)

        equity = self.calc.equity(players, hero_only=True)
        self.assertAlmostEqual(equity, 0.34, delta=0.01)

        players = ['As2sTc7h', '60%!$3b10i']
        board = 'Ks3s9d'
        equity = self.calc.equity(players, board=board, hero_only=True)
        self.assertAlmostEqual(equity, 0.52, delta=0.01)



