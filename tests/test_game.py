import unittest
from ploev.game import *


class RangesTest(unittest.TestCase):

    def test_sub_ranges(self):
        raise_range = SubRange('KK', 'raise range')
        call_range = SubRange('K4', 'raise range')
        ranges = Ranges([raise_range, call_range], 'standard', cumulative=False)
        sub_ranges = ranges.sub_ranges
        self.assertEqual(sub_ranges[0].sub_range, 'KK')
        self.assertEqual(sub_ranges[1].sub_range, 'K4')

    def test_cumulative_ranges(self):
        raise_range = SubRange('KK', 'raise range')
        call_range = SubRange('K4', 'raise range')
        ranges = Ranges([raise_range, call_range], 'standard', cumulative=True)
        sub_ranges = ranges.sub_ranges
        self.assertEqual(sub_ranges[0].sub_range, 'KK')
        self.assertEqual(sub_ranges[1].sub_range, '(K4)!(KK)')
        ranges.cumulative = False
        sub_ranges = ranges.sub_ranges
        self.assertEqual(sub_ranges[0].sub_range, 'KK')
        self.assertEqual(sub_ranges[1].sub_range, 'K4')


class GameTest(unittest.TestCase):

    def test_game_state(self):
        game = Game(players=[1, 2], pot=100)
        game_state = game.save_state()
        self.assertEqual(game_state.pot, 100)
        game.pot = 200
        self.assertEqual(game.pot, 200)
        game.restore_state(game_state)
        self.assertEqual(game.pot, 100)


class GameFlowTest(unittest.TestCase):

    def test_next_and_previous(self):
        state0 = GameState(pot=0)
        state1 = GameState(pot=100)
        state2 = GameState(pot=200)
        flow = GameFlow(states=[state0, state1, state2])
        self.assertEqual(flow.pointer, 0)
        self.assertEqual(flow.get_state(), state0)
        self.assertEqual(flow.pointer, 0)
        self.assertEqual(flow.next(), state1)
        self.assertEqual(flow.pointer, 1)
        self.assertEqual(flow.next(), state2)
        self.assertEqual(flow.pointer, 2)
        self.assertEqual(flow.next(), state2)
        self.assertEqual(flow.previous(), state1)
        self.assertEqual(flow.pointer, 1)
        self.assertEqual(flow.previous(), state0)
        self.assertEqual(flow.pointer, 0)
        self.assertEqual(flow.previous(), state0)
        self.assertEqual(flow.pointer, 0)
