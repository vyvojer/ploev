import unittest

from ploev.easy_range import BoardExplorer
from ploev.game import *

odds_oracle = OddsOracle()


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


class EasyRangeTest(unittest.TestCase):
    def test_ppt(self):
        board_explorer = BoardExplorer(Board.from_str('AsKdTh'))
        easy_range = EasyRange('TS+')
        easy_range.board_explorer = board_explorer
        self.assertEqual(easy_range.ppt(), '(QJ,AA)')


class PlayerTest(unittest.TestCase):
    def test_villain_and_hero(self):
        player = Player(Position.BB, 100, name="John", is_hero=True)
        self.assertEqual(player.is_hero, True)
        self.assertEqual(player.is_villain, False)
        player.is_villain = True
        self.assertEqual(player.is_hero, False)
        self.assertEqual(player.is_villain, True)

    def test_save_state(self):
        player = Player(Position.BB, 100, name="John", is_hero=True)
        player.action = Action(ActionType.BET, 10)
        state = player.clone()
        player.name = "Pupa"
        player.stack = 200
        player.position = Position.SB
        player.action = None
        player.restore(state)
        self.assertEqual(player.name, "John")
        self.assertEqual(player.position, Position.BB)
        self.assertEqual(player.stack, 100)

    def test_add_range(self):
        player = Player(Position.BB, 100, name="John", is_hero=True)
        self.assertEqual(player.ranges, [])
        player.add_range(PptRange('70%'))
        self.assertEqual(len(player.ranges), 1)
        self.assertEqual(player.ranges[0].range_, '70%')

    def test_ppt(self):
        player = Player(Position.BB, 100, name="John", is_hero=True)
        player.add_range(PptRange('70%'))
        player.add_range(PptRange('A,K2'))
        self.assertEqual(player.ppt(), '(70%):(A,K2)')


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
        self.assertEqual(game.in_action_position, Position.SB)

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

    def test_get_hero(self):
        game = self.game
        game.set_hero(Position.SB)
        self.assertEqual(game.get_player(Position.BB).is_hero, False)
        self.assertEqual(game.get_player(Position.SB).is_hero, True)
        self.assertEqual(game.get_player(Position.BTN).is_hero, False)
        self.assertEqual(game.get_hero(), self.sb)

    def test_set_player_in_action(self):
        game = self.game
        game.set_player_in_action(self.btn)
        self.assertEqual(game.get_player(Position.BB).in_action, False)
        self.assertEqual(game.get_player(Position.SB).in_action, False)
        self.assertEqual(game.get_player(Position.BTN).in_action, True)
        self.assertEqual(game.player_in_action, self.btn)

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

    def test_possible_action_when_raise_not_possible(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s')
        game.make_action(Action(ActionType.BET, size=33))
        self.assertEqual(len(game.possible_actions), 2)
        self.assertEqual(game.possible_actions[0].type_, ActionType.CALL)
        self.assertEqual(game.possible_actions[1].type_, ActionType.FOLD)

        btn = Player(Position.BTN, stack=30, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s')
        game.make_action(Action(ActionType.BET, size=33))
        self.assertEqual(len(game.possible_actions), 2)
        self.assertEqual(game.possible_actions[0].type_, ActionType.CALL)
        self.assertEqual(game.possible_actions[0].min_size, 30)
        self.assertEqual(game.possible_actions[0].max_size, 30)
        self.assertEqual(game.possible_actions[1].type_, ActionType.FOLD)

    def test_possible_action_when_only_allin_possible(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s')
        game.make_action(Action(ActionType.BET, size=10))
        self.assertEqual(len(game.possible_actions), 3)
        self.assertEqual(game.possible_actions[0].type_, ActionType.RAISE)
        self.assertEqual(game.possible_actions[0].min_size, 20)
        self.assertEqual(game.possible_actions[0].max_size, 33)
        self.assertEqual(game.possible_actions[1].type_, ActionType.CALL)
        self.assertEqual(game.possible_actions[2].type_, ActionType.FOLD)

        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s')
        game.make_action(Action(ActionType.BET, size=20))
        self.assertEqual(len(game.possible_actions), 3)
        self.assertEqual(game.possible_actions[0].type_, ActionType.RAISE)
        self.assertEqual(game.possible_actions[0].min_size, 33)
        self.assertEqual(game.possible_actions[0].max_size, 33)
        self.assertEqual(game.possible_actions[1].type_, ActionType.CALL)
        self.assertEqual(game.possible_actions[2].type_, ActionType.FOLD)

    def test_possible_action_when_allin_allowed(self):
        btn = Player(Position.BTN, stack=330, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=400, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s', allin_allowed=True)
        game.make_action(Action(ActionType.BET, size=10))
        self.assertEqual(len(game.possible_actions), 3)
        self.assertEqual(game.possible_actions[0].type_, ActionType.RAISE)
        self.assertEqual(game.possible_actions[0].min_size, 20)
        self.assertEqual(game.possible_actions[0].max_size, 330)
        self.assertEqual(game.possible_actions[1].type_, ActionType.CALL)
        self.assertEqual(game.possible_actions[2].type_, ActionType.FOLD)

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
        active_players = game.get_active_players()
        self.assertEqual(len(active_players), 3)

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
        active_players = game.get_active_players()
        self.assertEqual(len(active_players), 3)

        # BTN fold OTF
        game.make_action(Action(ActionType.FOLD))
        self.assertEqual(self.btn.action.type_, ActionType.FOLD)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.sb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.bb)
        self.assertEqual(game.pot, 6)
        self.assertEqual(game.street, Street.FLOP)
        active_players = game.get_active_players()
        self.assertEqual(len(active_players), 2)

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
        game = Game([hero, villain], pot=4.5, board='Td4s3s')
        self.assertEqual(game.player_in_action, villain)
        self.assertEqual(game.street, Street.FLOP)
        game.make_action(Action(ActionType.CHECK))
        self.assertEqual(game.player_in_action, hero)
        self.assertEqual(game.possible_actions, [Action(ActionType.BET, 4.5, 1, 4.5),
                                                 Action(ActionType.CHECK)])
        game.make_action(Action(ActionType.BET, 4.5, 1, 4.5))
        self.assertEqual(game.player_in_action, villain)
        self.assertEqual(game.possible_actions, [Action(ActionType.RAISE, 18, 9, 18),
                                                 Action(ActionType.CALL, 4.5),
                                                 Action(ActionType.FOLD)])
        self.assertEqual(game._last_aggressor, hero)
        self.assertEqual(game._is_round_closed, False)

    def test_game_state(self):
        hero = Player(Position.BTN, 98, is_hero=True)
        villain = Player(Position.BB, 98)
        game = Game([hero, villain], pot=4.5, board='Td4s3s')
        self.assertEqual(game.player_in_action, villain)
        self.assertEqual(game.street, Street.FLOP)
        self.assertEqual(villain.stack, 98)
        self.assertEqual(game.pot, 4.5)
        state_in_the_begin = game.clone()
        game.make_action(Action(ActionType.BET, size=4.5))
        self.assertEqual(game.player_in_action, hero)
        self.assertEqual(villain.stack, 93.5)
        self.assertEqual(game.street, Street.FLOP)
        self.assertEqual(game.pot, 9)
        state_after_villain_action = game.clone()
        game.restore_state(state_in_the_begin)
        self.assertEqual(game.player_in_action, villain)
        self.assertEqual(game.street, Street.FLOP)
        self.assertEqual(villain.stack, 98)
        self.assertEqual(game.pot, 4.5)
        game.restore_state(state_after_villain_action)
        self.assertEqual(game.player_in_action, hero)
        self.assertEqual(game.street, Street.FLOP)
        self.assertEqual(villain.stack, 93.5)
        self.assertEqual(game.pot, 9)

    def test_leaf_none(self):
        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([bb, btn], pot=3, board='AsKs2d')
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(ActionType.CHECK))
        self.assertEqual(game.leaf, GameLeaf.NONE)

    def test_leaf_round_closed(self):
        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([bb, btn], pot=3, board='AsKs2d')
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(ActionType.CHECK))
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(ActionType.CHECK))
        self.assertEqual(game.leaf, GameLeaf.ROUND_CLOSED)

        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([bb, btn], pot=3, board='AsKs2d')
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(ActionType.BET, 3))
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(ActionType.CALL, 3))
        self.assertEqual(game.leaf, GameLeaf.ROUND_CLOSED)

    def test_leaf_fold(self):
        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([bb, btn], pot=3, board='AsKs2d')
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(ActionType.BET, 3))
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(ActionType.FOLD))
        self.assertEqual(game.leaf, GameLeaf.FOLD)

    def test_leaf_showdown(self):
        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([bb, btn], pot=3, board='AsKs2d2s4h')
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(ActionType.BET, 3))
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(ActionType.CALL, 3))
        self.assertEqual(game.leaf, GameLeaf.SHOWDOWN)


class GameFlowTest(unittest.TestCase):
    def test_next_and_previous(self):
        self.bb = Player(Position.BB, 100, "Hero")
        self.sb = Player(Position.SB, 100, "SB")
        self.btn = Player(Position.BTN, 100, "BTN")
        self.players = [self.bb, self.sb, self.btn]
        self.game = Game(players=self.players)


class GameNodeTest(unittest.TestCase):
    def setUp(self):
        self.btn = Player(Position.BTN, 100)
        self.bb = Player(Position.BB, 100)
        self.game = Game(players=[self.bb, self.btn], pot=6, board='2cKd8s')
        self.game.make_action(Action(ActionType.CHECK))

    def test__init__(self):
        game_node = GameNode(self.game)
        self.assertEqual(game_node.parent, None)
        self.assertEqual(game_node.lines, [])

    def test_add_line(self):
        root = GameNode(self.game)
        self.assertEqual(root.game_state.player_in_action.position, Position.BTN)
        self.assertEqual(root.game_state.player_in_action.stack, 100)

        line_check = root.add_line(Action(ActionType.CHECK))
        self.assertEqual(root.game_state.player_in_action.position, Position.BTN)
        self.assertEqual(line_check.game_state.player_in_action.position, Position.BB)
        self.assertEqual(line_check.game_state.get_player(Position.BTN).stack, 100)
        self.assertEqual(line_check.parent, root)

        line_bet = root.add_line(Action(ActionType.BET, 6))
        self.assertEqual(root.game_state.player_in_action.position, Position.BTN)
        self.assertEqual(line_check.game_state.player_in_action.position, Position.BB)
        self.assertEqual(line_check.game_state.get_player(Position.BTN).stack, 100)
        self.assertEqual(line_bet.game_state.player_in_action.position, Position.BB)
        self.assertEqual(line_bet.game_state.get_player(Position.BTN).stack, 94)
        self.assertEqual(line_bet.game_state.player_in_action.stack, 100)

        self.assertEqual(root.lines, [line_check, line_bet])

    def test_add_standard_lines(self):
        root = GameNode(self.game)
        root.add_standard_lines()
        self.assertEqual(len(root.lines), 2)
        self.assertEqual(root.lines[0].game_state.previous_action.type_, ActionType.BET)
        self.assertEqual(root.lines[1].game_state.previous_action.type_, ActionType.CHECK)

    def test__iter__(self):
        root = GameNode(self.game)
        root.add_standard_lines()
        all_nodes = [game_node for game_node in root]
        self.assertEqual(all_nodes[0], root)
        self.assertEqual(all_nodes[1], root.lines[0])
        self.assertEqual(all_nodes[2], root.lines[1])

    def test_game(self):
        root = GameNode(self.game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_check = root.lines[1]
        self.assertEqual(line_bet.game.get_player(Position.BTN), self.btn)
        self.assertEqual(line_bet.game.get_player(Position.BTN).stack, 94)
        self.assertEqual(self.btn.stack, 94)

    def test_id(self):
        root = GameNode(self.game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_check = root.lines[1]
        self.assertEqual(root.id, (1, 1))
        self.assertEqual(line_bet.id, (2, 1))
        self.assertEqual(line_check.id, (2, 2))

    def test_pot_share(self):
        root = GameNode(self.game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_check = root.lines[1]
        self.assertEqual(line_check.pot_share, None)
        line_check._equity = 0.5
        self.assertEqual(line_check.pot_share, 3)


class GameTreeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.btn = Player(Position.BTN, 100, is_hero=True)
        cls.bb = Player(Position.BB, 100)
        cls.game = Game(players=[cls.bb, cls.btn], pot=6, board='2cKd8s')
        cls.game.make_action(Action(ActionType.CHECK))

    def test_hero(self):
        root = GameNode(self.game)
        game_tree = GameTree(root, odds_oracle)
        self.assertEqual(game_tree.hero, self.btn)

    def test__iter__(self):
        root = GameNode(self.game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        all_nodes = [game_node for game_node in game_tree]
        self.assertEqual(all_nodes[0], game_tree.root)
        self.assertEqual(all_nodes[1], root.lines[0])
        self.assertEqual(all_nodes[2], root.lines[1])

    def test_calculate_equity(self):
        self.game.board = Board.from_str('As2dKs')
        self.bb.add_range(PptRange('20%'))
        self.btn.add_range(PptRange('2hKh7d8d'))
        root = GameNode(self.game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        line_bet = root.lines[0]
        game_tree.calculate_equity(line_bet)
        self.assertAlmostEqual(line_bet.equity, 0.45, delta=0.1)

    def test_calculate_node_when_hero_close_action(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game([bb, btn], 33, board='2c Kd 8s')
        bb.add_range(PptRange('AA'))
        btn.add_range(PptRange('8h 9h Tc Js'))
        game.make_action(Action(ActionType.BET, size=33))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)


class TypicalGameSituationTest(unittest.TestCase):

    def test_calculate_node_when_hero_close_action(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game([bb, btn], 33, board='2c Kd 8s')
        bb.add_range(PptRange('AA'))
        btn.add_range(PptRange('8h 9h Tc Js'))
        game.make_action(Action(ActionType.BET, size=33))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        call_line = root.lines[0]
        fold_line = root.lines[1]
        game_tree.calculate_node(call_line)
        self.assertEqual(call_line.equity, 0.354)

    def test_SPR1_call_pot_bet(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s')
        bb.add_range(PptRange('AA'))
        btn.add_range(PptRange('8h 9h Tc Js'))
        game.make_action(Action(ActionType.BET, size=33))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        call_line = root.lines[0]
        fold_line = root.lines[1]
        game_tree.calculate()
        self.assertAlmostEqual(call_line.equity, 35.4, delta=0.5)
