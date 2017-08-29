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
        player = Player(Position.BB, 100, "John", is_hero=True)
        self.assertEqual(player.is_hero, True)
        self.assertEqual(player.is_villain, False)
        player.is_villain = True
        self.assertEqual(player.is_hero, False)
        self.assertEqual(player.is_villain, True)


class ActionTest(unittest.TestCase):
    def test__init__(self):
        action = Action(ActionType.BET, 100)
        self.assertEqual(action.type_, ActionType.BET)
        self.assertEqual(action.size, 100)
        self.assertEqual(action.is_sizable, True)
        self.assertEqual(action._is_different_sizes_possible, True)

        action = Action(ActionType.CHECK)
        self.assertEqual(action.type_, ActionType.CHECK)
        self.assertEqual(action.size, None)
        self.assertEqual(action.is_sizable, False)
        self.assertEqual(action._is_different_sizes_possible, False)


class GameTest(unittest.TestCase):
    def setUp(self):
        self.bb = Player(Position.BB, 100, "Hero")
        self.sb = Player(Position.SB, 100, "SB")
        self.btn = Player(Position.BTN, 100, "BTN")
        self.players = [self.bb, self.sb, self.btn]
        self.game = Game(players=self.players)

    def test__init__(self):
        game = self.game
        self.assertEqual(game.players[Position.BB], self.bb)
        self.assertEqual(game.players[Position.SB], self.sb)
        self.assertEqual(game._in_action_position, Position.SB)

    def test__init__with_same_position(self):
        hero = Player(position=Position.BB, name="Hero", stack=100)
        villain = Player(position=Position.BB, name="Villain", stack=100)
        with self.assertRaises(ValueError) as raised:
            game = Game(players=[hero, villain])

    def test_get_player(self):
        self.assertEqual(self.game.get_player(Position.BTN), self.btn)

    def test_positions_and_active_positions(self):
        position = self.game.positions
        self.assertEqual(position, [Position.SB, Position.BB, Position.BTN])

    def test_set_hero(self):
        game = self.game
        game.set_hero(Position.SB)
        self.assertEqual(game.get_player(Position.BB).is_hero, False)
        self.assertEqual(game.get_player(Position.SB).is_hero, True)
        self.assertEqual(game.get_player(Position.BTN).is_hero, False)

    def test_set_player_in_action(self):
        game = self.game
        game.set_player_in_action(self.btn)
        self.assertEqual(game.get_player(Position.BB).in_action, False)
        self.assertEqual(game.get_player(Position.SB).in_action, False)
        self.assertEqual(game.get_player(Position.BTN).in_action, True)
        self.assertEqual(game.player_in_action, self.btn)

    def test_board(self):
        game = self.game
        game.board = Board()
        self.assertEqual(game._board, Board())
        self.assertEqual(game.street, Street.PREFLOP)
        self.assertEqual(game._flop, None)
        self.assertEqual(game._turn, None)
        self.assertEqual(game._river, None)

        game.board = Board.from_str('AsKd8h')
        self.assertEqual(game._board, Board.from_str('AsKd8h'))
        self.assertEqual(game.street, Street.FLOP)
        self.assertEqual(game._flop, Board.from_str('AsKd8h'))
        self.assertEqual(game._turn, None)
        self.assertEqual(game._river, None)

        game.board = Board.from_str('AsKd8h2h')
        self.assertEqual(game.street, Street.TURN)
        self.assertEqual(game._flop, Board.from_str('AsKd8h'))
        self.assertEqual(game._turn, Board.from_str('AsKd8h2h'))
        self.assertEqual(game._river, None)

        game.board = Board.from_str('AsKd8h2hQc')
        self.assertEqual(game.street, Street.RIVER)
        self.assertEqual(game._flop, Board.from_str('AsKd8h'))
        self.assertEqual(game._turn, Board.from_str('AsKd8h2h'))
        self.assertEqual(game._river, Board.from_str('AsKd8h2hQc'))

    def test_next_street(self):
        game = self.game
        self.assertEqual(game.street, Street.PREFLOP)
        game.next_street()
        self.assertEqual(game.street, Street.FLOP)
        game.next_street()
        self.assertEqual(game.street, Street.TURN)
        game.next_street()
        self.assertEqual(game.street, Street.RIVER)
        game.next_street()
        self.assertEqual(game.street, Street.SHOWDOWN)

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
        game.make_action(Action(ActionType.POST_BLIND, 0.5))
        self.assertEqual(game.possible_actions[0].type_, ActionType.POST_BLIND)
        self.assertEqual(game.possible_actions[0].size, 1)

        game.make_action(Action(ActionType.POST_BLIND, 1))
        game.pot = 1.5
        self.assertEqual(game.possible_actions[0].type_, ActionType.RAISE)
        self.assertEqual(game.possible_actions[0].size, 3.5)
        self.assertEqual(game.possible_actions[0].min_size, 2)
        self.assertEqual(game.possible_actions[0].max_size, 3.5)
        self.assertEqual(game.possible_actions[1].type_, ActionType.CALL)
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
        game.make_action(Action(ActionType.POST_BLIND, 0.5))
        self.assertEqual(self.sb.action.type_, ActionType.POST_BLIND)
        self.assertEqual(self.sb.invested_in_bank, 0.5)
        self.assertEqual(game.player_in_action, self.bb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.bb)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.pot, 0.5)

        # BB post bb
        game.make_action(Action(ActionType.POST_BLIND, 1))
        self.assertEqual(self.bb.action.type_, ActionType.POST_BLIND)
        self.assertEqual(self.bb.invested_in_bank, 1)
        self.assertEqual(game.player_in_action, self.btn)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.btn)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.pot, 1.5)

        # BTN call (limp)
        game.make_action(Action(ActionType.CALL, 1))
        self.assertEqual(self.btn.action.type_, ActionType.CALL)
        self.assertEqual(game.player_in_action, self.sb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.btn)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.pot, 2.5)
        self.assertEqual(game.street, Street.PREFLOP)

        # SB call (complete)
        game.make_action(Action(ActionType.CALL, 0.5))
        self.assertEqual(self.sb.action.type_, ActionType.CALL)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.bb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.btn)
        self.assertEqual(game.pot, 3)
        self.assertEqual(game.street, Street.PREFLOP)

        # BB check, the prelop round completed
        game.make_action(Action(ActionType.CHECK))
        self.assertEqual(self.bb.action.type_, ActionType.CHECK)
        self.assertEqual(game._is_round_closed, True)
        self.assertEqual(game.player_in_action, self.sb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, None)
        self.assertEqual(game.pot, 3)
        self.assertEqual(game.street, Street.FLOP)

        # SB check OTF
        game.make_action(Action(ActionType.CHECK))
        self.assertEqual(self.sb.action.type_, ActionType.CHECK)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.bb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, None)
        self.assertEqual(game.pot, 3)
        self.assertEqual(game.street, Street.FLOP)

        # BB bet OTF
        game.make_action(Action(ActionType.BET, 3))
        self.assertEqual(self.bb.action.type_, ActionType.BET)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.btn)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.bb)
        self.assertEqual(game.pot, 6)
        self.assertEqual(game.street, Street.FLOP)

        # BTN fold OTF
        game.make_action(Action(ActionType.FOLD))
        self.assertEqual(self.btn.action.type_, ActionType.FOLD)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.sb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.bb)
        self.assertEqual(game.pot, 6)
        self.assertEqual(game.street, Street.FLOP)

        # SB call OTF
        game.make_action(Action(ActionType.CALL, 3))
        self.assertEqual(self.sb.action.type_, ActionType.CALL)
        self.assertEqual(game._is_round_closed, True)
        self.assertEqual(game.player_in_action, self.sb)
        #        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, None)
        self.assertEqual(game.pot, 9)
        self.assertEqual(game.street, Street.TURN)

    def test_posflop_situation(self):
        hero = Player(Position.BTN, 98, is_hero=True)
        villain = Player(Position.BB, 98, is_hero=True)
        game = Game([hero, villain], pot=4.5, board=Board.from_str('Td4s3s'))
        self.assertEqual(game.player_in_action, villain)
        self.assertEqual(game.street, Street.FLOP)
        game.make_action(Action(ActionType.CHECK))
        self.assertEqual(game.player_in_action, hero)
        self.assertEqual(game.possible_actions, [Action(ActionType.BET, 4.5, 1, 4.5),
                                                 Action(ActionType.CHECK)])

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
