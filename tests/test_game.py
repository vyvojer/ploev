import unittest
from ploev.game import *
from ploev.game import Street


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
        self.game = Game(players=self.players)

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
        self.assertEqual(game.street, Street.preflop)
        self.assertEqual(game._flop, None)
        self.assertEqual(game._turn, None)
        self.assertEqual(game._river, None)

        game.board = Board.from_str('AsKd8h')
        self.assertEqual(game._board, Board.from_str('AsKd8h'))
        self.assertEqual(game.street, Street.flop)
        self.assertEqual(game._flop, Board.from_str('AsKd8h'))
        self.assertEqual(game._turn, None)
        self.assertEqual(game._river, None)

        game.board = Board.from_str('AsKd8h2h')
        self.assertEqual(game.street, Street.turn)
        self.assertEqual(game._flop, Board.from_str('AsKd8h'))
        self.assertEqual(game._turn, Board.from_str('AsKd8h2h'))
        self.assertEqual(game._river, None)

        game.board = Board.from_str('AsKd8h2hQc')
        self.assertEqual(game.street, Street.river)
        self.assertEqual(game._flop, Board.from_str('AsKd8h'))
        self.assertEqual(game._turn, Board.from_str('AsKd8h2h'))
        self.assertEqual(game._river, Board.from_str('AsKd8h2hQc'))

    def test_next_street(self):
        game = self.game
        self.assertEqual(game.street, Street.preflop)
        game.next_street()
        self.assertEqual(game.street, Street.flop)
        game.next_street()
        self.assertEqual(game.street, Street.turn)
        game.next_street()
        self.assertEqual(game.street, Street.river)
        game.next_street()
        self.assertEqual(game.street, Street.showdown)

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
        self.assertEqual(game.player_in_action, self.sb)
        game.make_action(Action(ActionType.post_blind, 0.5))
        self.assertEqual(game.possible_actions[0].type_, ActionType.post_blind)
        self.assertEqual(game.possible_actions[0].size, 1)

        game.make_action(Action(ActionType.post_blind, 1))
        game.pot = 1.5
        self.assertEqual(game.possible_actions[0].type_, ActionType.raise_)
        self.assertEqual(game.possible_actions[0].size, 3.5)
        self.assertEqual(game.possible_actions[0].min_size, 2)
        self.assertEqual(game.possible_actions[0].max_size, 3.5)
        self.assertEqual(game.possible_actions[1].type_, ActionType.call)
        self.assertEqual(game.possible_actions[1].size, 1)
        game.make_action(game.possible_actions[0])
        self.assertEqual(game.pot, 5)

    def test_count_pot_bet(self):
        self.assertEqual(Game._count_pot_raise(call_size=1, pot=1.5), 3.5)
        self.assertEqual(Game._count_pot_raise(call_size=1, pot=2.5), 4.5)

    def test_make_action(self):
        game = self.game
        # SB post sb
        self.assertEqual(game.player_in_action, self.sb)
        game.make_action(Action(ActionType.post_blind, 0.5))
        self.assertEqual(self.sb.action.type_, ActionType.post_blind)
        self.assertEqual(self.sb.invested_in_bank, 0.5)
        self.assertEqual(game.player_in_action, self.bb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.bb)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.pot, 0.5)

        # BB post bb
        game.make_action(Action(ActionType.post_blind, 1))
        self.assertEqual(self.bb.action.type_, ActionType.post_blind)
        self.assertEqual(self.bb.invested_in_bank, 1)
        self.assertEqual(game.player_in_action, self.btn)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.btn)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.pot, 1.5)

        # BTN call (limp)
        game.make_action(Action(ActionType.call, 1))
        self.assertEqual(self.btn.action.type_, ActionType.call)
        self.assertEqual(game.player_in_action, self.sb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.btn)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.pot, 2.5)
        self.assertEqual(game.street, Street.preflop)

        # SB call (complete)
        game.make_action(Action(ActionType.call, 0.5))
        self.assertEqual(self.sb.action.type_, ActionType.call)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.bb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.btn)
        self.assertEqual(game.pot, 3)
        self.assertEqual(game.street, Street.preflop)

        # BB check, the prelop round completed
        game.make_action(Action(ActionType.check))
        self.assertEqual(self.bb.action.type_, ActionType.check)
        self.assertEqual(game._is_round_closed, True)
        self.assertEqual(game.player_in_action, self.sb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, None)
        self.assertEqual(game.pot, 3)
        self.assertEqual(game.street, Street.flop)

        # SB check OTF
        game.make_action(Action(ActionType.check))
        self.assertEqual(self.sb.action.type_, ActionType.check)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.bb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, None)
        self.assertEqual(game.pot, 3)
        self.assertEqual(game.street, Street.flop)

        # BB bet OTF
        game.make_action(Action(ActionType.bet, 3))
        self.assertEqual(self.bb.action.type_, ActionType.bet)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.btn)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.bb)
        self.assertEqual(game.pot, 6)
        self.assertEqual(game.street, Street.flop)

        # BTN fold OTF
        game.make_action(Action(ActionType.fold))
        self.assertEqual(self.btn.action.type_, ActionType.fold)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.sb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.bb)
        self.assertEqual(game.pot, 6)
        self.assertEqual(game.street, Street.flop)

        # SB call OTF
        game.make_action(Action(ActionType.call, 3))
        self.assertEqual(self.sb.action.type_, ActionType.call)
        self.assertEqual(game._is_round_closed, True)
        self.assertEqual(game.player_in_action, self.sb)
#        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, None)
        self.assertEqual(game.pot, 9)
        self.assertEqual(game.street, Street.turn)

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
