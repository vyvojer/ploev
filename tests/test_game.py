import unittest
from ploev.game import *
from ploev.game import _Street


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
        player = Player(Position.bb, 100, "John", is_hero=True)
        self.assertEqual(player.is_hero, True)
        self.assertEqual(player.is_villain, False)
        player.is_villain = True
        self.assertEqual(player.is_hero, False)
        self.assertEqual(player.is_villain, True)


class ActionTest(unittest.TestCase):

    def test__init__(self):
        action = Action(ActionType.bet, 100)
        self.assertEqual(action.type_, ActionType.bet)
        self.assertEqual(action.size, 100)
        self.assertEqual(action.is_sizable, True)
        self.assertEqual(action._is_different_sizes_possible, True)

        action = Action(ActionType.check)
        self.assertEqual(action.type_, ActionType.check)
        self.assertEqual(action.size, None)
        self.assertEqual(action.is_sizable, False)
        self.assertEqual(action._is_different_sizes_possible, False)


class GameTest(unittest.TestCase):

    def setUp(self):
        self.bb = Player(Position.bb, 100, "Hero")
        self.sb = Player(Position.sb, 100, "SB")
        self.btn = Player(Position.btn, 100, "BTN")
        self.players = [self.bb, self.sb, self.btn]
        self.game = Game(players = self.players)

    def test__init__(self):
        game = self.game
        self.assertEqual(game.players[Position.bb], self.bb)
        self.assertEqual(game.players[Position.sb], self.sb)
        self.assertEqual(game._in_action_position, Position.sb)

    def test__init__with_same_position(self):
        hero = Player(position=Position.bb, name="Hero", stack=100)
        villain = Player(position=Position.bb, name="Villain", stack=100)
        with self.assertRaises(ValueError) as raised:
            game = Game(players=[hero, villain])

    def test_get_player(self):
        self.assertEqual(self.game.get_player(Position.btn), self.btn)

    def test_positions_and_active_positions(self):
        position = self.game.positions
        self.assertEqual(position, [Position.sb, Position.bb, Position.btn])

    def test_set_hero(self):
        game = self.game
        game.set_hero(Position.sb)
        self.assertEqual(game.get_player(Position.bb).is_hero, False)
        self.assertEqual(game.get_player(Position.sb).is_hero, True)
        self.assertEqual(game.get_player(Position.btn).is_hero, False)

    def test_set_player_in_action(self):
        game = self.game
        game.set_player_in_action(self.btn)
        self.assertEqual(game.get_player(Position.bb).in_action, False)
        self.assertEqual(game.get_player(Position.sb).in_action, False)
        self.assertEqual(game.get_player(Position.btn).in_action, True)
        self.assertEqual(game.player_in_action, self.btn)

    def test_board(self):
        game = self.game
        game.board = Board()
        self.assertEqual(game._board, Board())
        self.assertEqual(game._street, _Street.preflop)
        self.assertEqual(game._flop, None)
        self.assertEqual(game._turn, None)
        self.assertEqual(game._river, None)

        game.board = Board.from_str('AsKd8h')
        self.assertEqual(game._board, Board.from_str('AsKd8h'))
        self.assertEqual(game._street, _Street.flop)
        self.assertEqual(game._flop, Board.from_str('AsKd8h'))
        self.assertEqual(game._turn, None)
        self.assertEqual(game._river, None)

        game.board = Board.from_str('AsKd8h2h')
        self.assertEqual(game._street, _Street.turn)
        self.assertEqual(game._flop, Board.from_str('AsKd8h'))
        self.assertEqual(game._turn, Board.from_str('AsKd8h2h'))
        self.assertEqual(game._river, None)

        game.board = Board.from_str('AsKd8h2hQc')
        self.assertEqual(game._street, _Street.river)
        self.assertEqual(game._flop, Board.from_str('AsKd8h'))
        self.assertEqual(game._turn, Board.from_str('AsKd8h2h'))
        self.assertEqual(game._river, Board.from_str('AsKd8h2hQc'))

    def test_get_previous_action_player(self):
        game = self.game
        game.set_player_in_action(self.btn)
        self.assertEqual(game.get_previous_action_player(), self.bb)  # BB
        game.set_player_in_action(self.bb)
        self.assertEqual(game.get_previous_action_player(), self.sb)
        game.set_player_in_action(self.sb)
        self.assertEqual(game.get_previous_action_player(), self.btn)

    def test_get_next_action_player(self):
        game = self.game
        game.set_player_in_action(self.btn)
        self.assertEqual(game.get_next_action_player(), self.sb)
        game.set_player_in_action(self.bb)
        self.assertEqual(game.get_next_action_player(), self.btn)
        game.set_player_in_action(self.sb)
        self.assertEqual(game.get_next_action_player(), self.bb)

    def test_possible_actions(self):
        game = self.game
        self.sb.action = Action(ActionType.post_blind, size=0.5)
        game.set_player_in_action(self.bb)
        self.assertEqual(game.possible_actions[0].type_, ActionType.post_blind)
        self.assertEqual(game.possible_actions[0].size, 1)

        self.bb.action = Action(ActionType.post_blind, size=1)
        game.pot = 1.5
        game.set_player_in_action(self.btn)
        self.assertEqual(game.possible_actions[0].type_, ActionType.raise_)
        self.assertEqual(game.possible_actions[0].size, 3.5)
        self.assertEqual(game.possible_actions[0].min_size, 2)
        self.assertEqual(game.possible_actions[0].max_size, 3.5)
        self.assertEqual(game.possible_actions[1].type_, ActionType.call)
        self.assertEqual(game.possible_actions[1].size, 1)
        game.make_action(game.possible_actions[0])
        self.assertEqual(game.pot, 5)

    def test_count_pot_bet(self):
        self.assertEqual(Game._count_pot_bet(call_size=1, pot=1.5), 3.5)
        self.assertEqual(Game._count_pot_bet(call_size=1, pot=2.5), 4.5)

    def test_make_action(self):
        game = self.game
        self.assertEqual(game.player_in_action, self.sb)
        game.make_action(Action(ActionType.post_blind, 0.5))
        self.assertEqual(self.sb.action.type_, ActionType.post_blind)
        self.assertEqual(game.player_in_action, self.bb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.sb)

    def test_game_state(self):
        game = Game(players=self.players, pot=100)
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
