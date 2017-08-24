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


class PlayerTest(unittest.TestCase):

    def test_villain_and_hero(self):
        player = Player(Position.bb, 100, "John")
        self.assertEqual(player.is_hero, True)
        self.assertEqual(player.is_villain, False)
        player.is_villain = True
        self.assertEqual(player.is_hero, False)
        self.assertEqual(player.is_villain, True)


class PlayerListTest(unittest.TestCase):

    def setUp(self):
        self.hero = Player(Position.bb, 100, "Hero")
        self.villain1 = Player(Position.sb, 100, "Villain 1")
        self.villain2 = Player(Position.btn, 100, "Villain 2")
        players = [self.hero, self.villain1, self.villain2]
        self.player_list = PlayerList(players = players)

    def test__init__(self):
        self.assertEqual(self.player_list.players[Position.bb], self.hero)
        self.assertEqual(self.player_list.players[Position.sb], self.villain1)

    def test__init__with_same_position(self):
        hero = Player(position=Position.bb, name="Hero", stack=100)
        villain = Player(position=Position.bb, name="Villain", stack=100)
        with self.assertRaises(ValueError) as raised:
            player_list = PlayerList(players=[hero, villain])

    def test_get_player(self):
        self.assertEqual(self.player_list.get_player(Position.btn), self.villain2)

    def test_positions_and_active_positions(self):
        position = self.player_list.positions
        self.assertEqual(position, [Position.bb, Position.sb, Position.btn])


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
