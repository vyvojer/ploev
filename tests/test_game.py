import unittest

from ploev.game import *

odds_oracle = OddsOracle(trials=10000, seconds=1)


class RangeDistributionTest(unittest.TestCase):
    def test_get_not_cumulative_ranges(self):
        sub_ranges = [
            SubRange('bet', PptRange('KK')),
            SubRange('check', PptRange('*!KK'))
        ]
        rd = RangeDistribution(sub_ranges, is_cumulative=False)
        self.assertEqual(rd.ppts(), ['KK', '*!KK'])

    def test_set_cumulative_ranges(self):
        sub_ranges = [
            SubRange('bet', PptRange('KK')),
            SubRange('check', PptRange('*'))
        ]
        rd = RangeDistribution(sub_ranges)
        rd._set_cumulative_ranges()
        self.assertEqual(rd._sub_ranges_dict['check'].cumulative_range, '(*)!(KK)')

    def test_get_cumulative_ranges(self):
        sub_ranges = [
            SubRange('bet', PptRange('KK')),
            SubRange('check', PptRange('*'))
        ]
        rd = RangeDistribution(sub_ranges)
        self.assertEqual(rd.ppts(), ['(KK)', '(*)!(KK)'])

    def test_ppt_ranges(self):
        btn = Player(Position.BTN, stack=97)
        bb = Player(Position.BB, stack=97)
        game = Game([bb, btn], 6.5, board='As 2d Ks')
        sub_ranges = [
            SubRange('bet', EasyRange('T2P+,NFD,SD9+')),
            SubRange('check', EasyRange('*')),
        ]
        rd = RangeDistribution.from_game(sub_ranges, game=game, player=bb)
        bet = rd.sub_range('bet')
        self.assertEqual(bet.ppt(), '((AA,KK,22,AK),Qss,(QJT,543))')
        check = rd.sub_range('check')
        self.assertEqual(check.ppt(), '(*)!((AA,KK,22,AK),Qss,(QJT,543))')

    def test_calculate_from_game(self):
        btn = Player(Position.BTN, stack=97, is_hero=True)
        bb = Player(Position.BB, stack=97)
        bb.add_range(PptRange('30%'))
        game = Game([bb, btn], 6.5, board='As 2d Ks')
        player = bb
        sub_ranges = [
            SubRange('bet', EasyRange('T2P+,NFD,SD9+')),
            SubRange('check', EasyRange('*')),
        ]
        rd = RangeDistribution.from_game(sub_ranges, player=player, game=game, odds_oracle=odds_oracle)
        self.assertEqual(len(rd._another_players), 1)
        bet = rd.sub_range('bet')
        check = rd.sub_range('check')
        rd.calculate()
        self.assertAlmostEqual(bet.fraction, 0.303, delta=0.03)
        self.assertAlmostEqual(check.fraction, 0.697, delta=0.03)
        btn.add_range(PptRange('AdKd3s2s'))
        rd.calculate()
        self.assertAlmostEqual(bet.fraction, 0.217, delta=0.03)
        self.assertAlmostEqual(check.fraction, 0.783, delta=0.03)

    def test_calculate_from_game_with_street(self):
        btn = Player(Position.BTN, stack=97, is_hero=True)
        bb = Player(Position.BB, stack=97)
        bb.add_range(PptRange('30%'))
        game = Game([bb, btn], 6.5, board='As 2d Ks 6d')
        player = bb
        sub_ranges = [
            SubRange('bet', EasyRange('T2P+,NFD,SD9+', street=Street.FLOP)),
            SubRange('check', EasyRange('*', street=Street.FLOP)),
        ]
        rd = RangeDistribution.from_game(sub_ranges,
                                         player=player,
                                         game=game,
                                         street=Street.FLOP,
                                         odds_oracle=odds_oracle)
        self.assertEqual(len(rd._another_players), 1)
        bet = rd.sub_range('bet')
        check = rd.sub_range('check')
        rd.calculate()
        self.assertAlmostEqual(bet.fraction, 0.303, delta=0.03)
        self.assertAlmostEqual(check.fraction, 0.697, delta=0.03)


    def test_calculate(self):
        board = 'As 2d Ks'
        main_range = PptRange('30%')
        players_ranges = [PptRange('*')]
        sub_ranges = [
            SubRange('bet', EasyRange('T2P+,NFD,SD9+')),
            SubRange('check', EasyRange('*')),
        ]
        rd = RangeDistribution(sub_ranges,
                               main_range=main_range,
                               players_ranges=players_ranges,
                               board=board,
                               odds_oracle=odds_oracle)
        bet = rd.sub_ranges[0].range_
        check = rd.sub_ranges[1].range_
        rd.calculate()
        self.assertAlmostEqual(bet.fraction, 0.303, delta=0.03)
        self.assertAlmostEqual(check.fraction, 0.697, delta=0.03)
        rd._another_players = [PptRange('AdKd3s2s')]
        rd.calculate()
        self.assertAlmostEqual(bet.fraction, 0.217, delta=0.03)
        self.assertAlmostEqual(check.fraction, 0.783, delta=0.03)

    def test_get_fraction_bar(self):
        fr = 0.9
        self.assertEqual(RangeDistribution._get_fraction_bar(fr),
                         '█████████')
        fr = 0.92
        self.assertEqual(RangeDistribution._get_fraction_bar(fr),
                         '█████████')
        fr = 0.88
        self.assertEqual(RangeDistribution._get_fraction_bar(fr),
                         '█████████')
        fr = 0.95
        self.assertEqual(RangeDistribution._get_fraction_bar(fr),
                         '█████████▌')

        fr = 0.87
        self.assertEqual(RangeDistribution._get_fraction_bar(fr),
                         '████████▌')

        fr = 0.83
        self.assertEqual(RangeDistribution._get_fraction_bar(fr),
                         '████████▌')

        fr = 0.01
        self.assertEqual(RangeDistribution._get_fraction_bar(fr),
                         '▌')


class ColorCardsTest(unittest.TestCase):

    def test_color_range(self):
        self.assertEqual(color_cards('2s3d'), '<font color=black>2s </font><font color=blue>3d </font>')
        self.assertEqual(color_cards('Ah2s3d'),
                         '<font color=red>Ah </font><font color=black>2s </font><font color=blue>3d </font>')
        self.assertEqual(color_cards('*cAh2s3d'),
                         '<font color=green>*c </font><font color=red>Ah </font><font color=black>2s </font><font color=blue>3d </font>')
        self.assertEqual(color_cards('*cAhd2s3d'),
                         '<font color=green>*c </font><font color=red>Ah </font><font color=blue>d </font><font color=black>2s </font><font color=blue>3d </font>')


class CombinedRangeTest(unittest.TestCase):

    def test_or(self):
        r1 = PptRange('AA')
        r2 = PptRange('30%')
        cr = CombinedRange(r1, r2, CombinedRange.OR)
        self.assertEqual(cr.ppt(), 'AA,30%')

        cr2 = r1 | r2
        self.assertEqual(cr2.ppt(), 'AA,30%')

        cr3 = r1 + r2
        self.assertEqual(cr3.ppt(), 'AA,30%')

    def test_and(self):
        r1 = PptRange('AA')
        r2 = PptRange('30%')
        cr = CombinedRange(r1, r2, CombinedRange.AND)
        self.assertEqual(cr.ppt(), 'AA:30%')

        cr2 = r1 & r2
        self.assertEqual(cr2.ppt(), 'AA:30%')

    def test_not(self):
        r1 = PptRange('AA')
        r2 = PptRange('30%')
        cr = CombinedRange(r1, r2, CombinedRange.NOT)
        self.assertEqual(cr.ppt(), 'AA!30%')

        cr2 = r1 - r2
        self.assertEqual(cr2.ppt(), 'AA!30%')


class PptRangeTest(unittest.TestCase):

    def test_repr_html_(self):
        ppt_range = PptRange('2s3d')
        self.assertEqual(ppt_range._repr_html_(), '<font color=black>2s </font><font color=blue>3d </font>')


class EasyRangeTest(unittest.TestCase):
    def test_ppt(self):
        board_explorer = BoardExplorer(Board.from_str('AsKdTh'))
        easy_range = EasyRange('TS+', is_cumulative=False)
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
        player.action = Action(Action.BET, 10)
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

    def test_update_range(self):
        player = Player(Position.BB, 100, name="John", is_hero=True)
        self.assertEqual(player.ranges, [])
        player.add_range(PptRange('70%'))
        self.assertEqual(len(player.ranges), 1)
        self.assertEqual(player.ranges[0].range_, '70%')
        player.add_range(PptRange('60%'))
        self.assertEqual(len(player.ranges), 2)
        self.assertEqual(player.ranges[0].range_, '70%')
        self.assertEqual(player.ranges[1].range_, '60%')
        player.update_range(PptRange('50%'))
        self.assertEqual(len(player.ranges), 2)
        self.assertEqual(player.ranges[0].range_, '70%')
        self.assertEqual(player.ranges[1].range_, '50%')

    def test_add_easy_range(self):
        hero = Player(Position.BB, 90, is_hero=True)
        villain = Player(Position.BTN, 90)
        game = Game([hero, villain], 20, board='As Kd 2s 3h')
        villain.add_range(EasyRange('TS+', is_cumulative=False))
        self.assertEqual(villain.ranges[-1].ppt(), '(54,AA)')
        villain.add_range(EasyRange('SD9+', street=Street.FLOP, is_cumulative=False))
        self.assertEqual(villain.ranges[-1].ppt(), '(QJT,543)')

    def test_ppt(self):
        player = Player(Position.BB, 100, name="John", is_hero=True)
        player.add_range(PptRange('70%', is_cumulative=False))
        player.add_range(PptRange('A,K2', is_cumulative=False))
        self.assertEqual(player.ppt(), '(70%):(A,K2)')

    def test_main_range_ppt(self):
        player = Player(Position.BB, 100, name="John", is_hero=True)
        player.add_range(PptRange('70%', is_cumulative=False))
        player.add_range(PptRange('A,K2', is_cumulative=False))
        self.assertEqual(player.main_range_ppt(), '(70%)')

    def test_first_range_ppt(self):
        player = Player(Position.BB, 100, name="John", is_hero=True)
        player.add_range(PptRange('70%', is_cumulative=False))
        player.add_range(PptRange('A,K2', is_cumulative=False))
        self.assertEqual(player.first_range_ppt(), '70%')

    def test_previous_stack(self):
        player = Player(Position.BB, 100, name="John", is_hero=True)
        self.assertEqual(player.stack, 100)
        self.assertEqual(player.previous_stack, 100)
        player.stack = 50
        self.assertEqual(player.stack, 50)
        self.assertEqual(player.previous_stack, 100)


class ActionTest(unittest.TestCase):
    def test__init__(self):
        action = Action(Action.BET, 100)
        self.assertEqual(action.type_, Action.BET)
        self.assertEqual(action.size, 100)
        self.assertEqual(action.is_sizable, True)
        self.assertEqual(action._is_different_sizes_possible, True)

        action = Action(Action.CHECK)
        self.assertEqual(action.type_, Action.CHECK)
        self.assertEqual(action.size, None)
        self.assertEqual(action.is_sizable, False)
        self.assertEqual(action._is_different_sizes_possible, False)

    def test_sizeble(self):
        Action(Action.BET, size=10)
        Action(Action.BET, fraction=0.1)
        Action(Action.RAISE, size=10)
        Action(Action.RAISE, fraction=0.1)
        Action(Action.CALL)
        with self.assertRaises(ValueError) as raised:
            Action(Action.BET)
        with self.assertRaises(ValueError) as raised:
            Action(Action.RAISE)


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
        game.make_action(Action(Action.POST_BLIND, 0.5))
        self.assertEqual(game.possible_actions[0].type_, Action.POST_BLIND)
        self.assertEqual(game.possible_actions[0].size, 1)

        game.make_action(Action(Action.POST_BLIND, 1))
        game.pot = 1.5
        self.assertEqual(game.possible_actions[0].type_, Action.RAISE)
        self.assertEqual(game.possible_actions[0].size, 3.5)
        self.assertEqual(game.possible_actions[0].min_size, 2)
        self.assertEqual(game.possible_actions[0].max_size, 3.5)
        self.assertEqual(game.possible_actions[1].type_, Action.CALL)
        self.assertEqual(game.possible_actions[1].size, 1)
        game.make_action(game.possible_actions[0])
        self.assertEqual(game.pot, 5)

        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game([bb, btn], 33, board='2c Kd 8s 3c Jh')
        bb.add_range(PptRange('AA'))
        btn.add_range(PptRange('8h 9h Tc Js'))
        game.make_action(Action(Action.BET, size=6))
        raise_action = game.possible_actions[0]
        self.assertEqual(raise_action.type_, Action.RAISE)
        self.assertEqual(raise_action.min_size, 12)
        self.assertEqual(raise_action.max_size, 33)
        self.assertEqual(raise_action.size, 33)

    def test_possible_action_when_raise_not_possible(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s')
        game.make_action(Action(Action.BET, size=33))
        self.assertEqual(len(game.possible_actions), 2)
        self.assertEqual(game.possible_actions[0].type_, Action.CALL)
        self.assertEqual(game.possible_actions[1].type_, Action.FOLD)

        btn = Player(Position.BTN, stack=30, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s')
        game.make_action(Action(Action.BET, size=33))
        self.assertEqual(len(game.possible_actions), 2)
        self.assertEqual(game.possible_actions[0].type_, Action.CALL)
        self.assertEqual(game.possible_actions[0].min_size, 30)
        self.assertEqual(game.possible_actions[0].max_size, 30)
        self.assertEqual(game.possible_actions[1].type_, Action.FOLD)

    def test_possible_action_when_only_allin_possible(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s')
        game.make_action(Action(Action.BET, size=10))
        self.assertEqual(len(game.possible_actions), 3)
        self.assertEqual(game.possible_actions[0].type_, Action.RAISE)
        self.assertEqual(game.possible_actions[0].min_size, 20)
        self.assertEqual(game.possible_actions[0].max_size, 33)
        self.assertEqual(game.possible_actions[1].type_, Action.CALL)
        self.assertEqual(game.possible_actions[2].type_, Action.FOLD)

        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s')
        game.make_action(Action(Action.BET, size=20))
        self.assertEqual(len(game.possible_actions), 3)
        self.assertEqual(game.possible_actions[0].type_, Action.RAISE)
        self.assertEqual(game.possible_actions[0].min_size, 33)
        self.assertEqual(game.possible_actions[0].max_size, 33)
        self.assertEqual(game.possible_actions[1].type_, Action.CALL)
        self.assertEqual(game.possible_actions[2].type_, Action.FOLD)

    def test_possible_action_when_allin_allowed(self):
        btn = Player(Position.BTN, stack=330, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=400, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s', allin_allowed=True)
        game.make_action(Action(Action.BET, size=10))
        self.assertEqual(len(game.possible_actions), 3)
        self.assertEqual(game.possible_actions[0].type_, Action.RAISE)
        self.assertEqual(game.possible_actions[0].min_size, 20)
        self.assertEqual(game.possible_actions[0].max_size, 330)
        self.assertEqual(game.possible_actions[1].type_, Action.CALL)
        self.assertEqual(game.possible_actions[2].type_, Action.FOLD)

    def test_count_pot_bet(self):
        self.assertEqual(Game._count_pot_raise(call_size=1, pot=1.5), 3.5)
        self.assertEqual(Game._count_pot_raise(call_size=1, pot=2.5), 4.5)

    def test_count_action_size_for_bet(self):
        btn = Player(Position.BTN, stack=330, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=330)
        game = Game(players=[bb, btn], pot=100, board='2c Kd 8s', allin_allowed=True)
        action = Action(Action.BET, fraction=0.85)
        game._count_action_size(action)
        self.assertEqual(action.size, 85)

    def test_count_action_fraction_for_bet(self):
        btn = Player(Position.BTN, stack=330, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=330)
        game = Game(players=[bb, btn], pot=100, board='2c Kd 8s', allin_allowed=True)
        action = Action(Action.BET, size=85)
        game._count_action_size(action)
        self.assertEqual(action.fraction, 0.85)

    def test_count_action_size_for_raise(self):
        btn = Player(Position.BTN, stack=330, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=330)
        game = Game(players=[bb, btn], pot=100, board='2c Kd 8s', allin_allowed=True)
        game.make_action(Action(Action.BET, 50))
        action = Action(Action.RAISE, fraction=0.85)
        game._count_action_size(action)
        self.assertEqual(action.size, 212.5)

    def test_count_action_fraction_for_raise(self):
        btn = Player(Position.BTN, stack=330, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=330)
        game = Game(players=[bb, btn], pot=100, board='2c Kd 8s', allin_allowed=True)
        game.make_action(Action(Action.BET, 50))
        action = Action(Action.RAISE, size=212.5)
        game._count_action_size(action)
        self.assertEqual(action.fraction, 0.85)

    def test_posflop_situation(self):
        hero = Player(Position.BTN, 98, is_hero=True)
        villain = Player(Position.BB, 98, is_hero=True)
        game = Game([hero, villain], pot=4.5, board='Td4s3s')
        self.assertEqual(game.player_in_action, villain)
        self.assertEqual(game.street, Street.FLOP)
        game.make_action(Action(Action.CHECK))
        self.assertEqual(game.player_in_action, hero)
        self.assertEqual(game.possible_actions, [Action(Action.BET, size=4.5, min_size=1, max_size=4.5),
                                                 Action(Action.CHECK)])
        game.make_action(Action(Action.BET, size=4.5, min_size=1, max_size=4.5))
        self.assertEqual(game.player_in_action, villain)
        self.assertEqual(game.possible_actions, [Action(Action.RAISE, size=18, min_size=9, max_size=18),
                                                 Action(Action.CALL, size=4.5),
                                                 Action(Action.FOLD)])
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
        game.make_action(Action(Action.BET, size=4.5))
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

    def test_make_action(self):
        game = self.game
        # SB post sb
        self.assertEqual(game.player_in_action, self.sb)
        game.make_action(Action(Action.POST_BLIND, 0.5))
        self.assertEqual(self.sb.action.type_, Action.POST_BLIND)
        self.assertEqual(self.sb.invested_in_bank, 0.5)
        self.assertEqual(game.player_in_action, self.bb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.bb)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.pot, 0.5)
        active_players = game.get_active_players()
        self.assertEqual(len(active_players), 3)

        # BB post bb
        game.make_action(Action(Action.POST_BLIND, 1))
        self.assertEqual(self.bb.action.type_, Action.POST_BLIND)
        self.assertEqual(self.bb.invested_in_bank, 1)
        self.assertEqual(game.player_in_action, self.btn)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.btn)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.pot, 1.5)

        # BTN call (limp)
        game.make_action(Action(Action.CALL, 1))
        self.assertEqual(self.btn.action.type_, Action.CALL)
        self.assertEqual(game.player_in_action, self.sb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.btn)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.pot, 2.5)
        self.assertEqual(game.street, Street.PREFLOP)

        # SB call (complete)
        game.make_action(Action(Action.CALL, 0.5))
        self.assertEqual(self.sb.action.type_, Action.CALL)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.bb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.btn)
        self.assertEqual(game.pot, 3)
        self.assertEqual(game.street, Street.PREFLOP)

        # BB check, the prelop round completed
        game.make_action(Action(Action.CHECK))
        self.assertEqual(self.bb.action.type_, Action.CHECK)
        self.assertEqual(game._is_round_closed, True)
        self.assertEqual(game.player_in_action, self.sb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, None)
        self.assertEqual(game.pot, 3)
        self.assertEqual(game.street, Street.FLOP)

        # SB check OTF
        game.make_action(Action(Action.CHECK))
        self.assertEqual(self.sb.action.type_, Action.CHECK)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.bb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, None)
        self.assertEqual(game.pot, 3)
        self.assertEqual(game.street, Street.FLOP)

        # BB bet OTF
        game.make_action(Action(Action.BET, 3))
        self.assertEqual(self.bb.action.type_, Action.BET)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.btn)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.bb)
        self.assertEqual(game.pot, 6)
        self.assertEqual(game.street, Street.FLOP)
        active_players = game.get_active_players()
        self.assertEqual(len(active_players), 3)

        # BTN fold OTF
        game.make_action(Action(Action.FOLD))
        self.assertEqual(self.btn.action.type_, Action.FOLD)
        self.assertEqual(game._is_round_closed, False)
        self.assertEqual(game.player_in_action, self.sb)
        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, self.bb)
        self.assertEqual(game.pot, 6)
        self.assertEqual(game.street, Street.FLOP)
        active_players = game.get_active_players()
        self.assertEqual(len(active_players), 2)

        # SB call OTF
        game.make_action(Action(Action.CALL, 3))
        self.assertEqual(self.sb.action.type_, Action.CALL)
        self.assertEqual(game._is_round_closed, True)
        self.assertEqual(game.player_in_action, self.sb)
        #        self.assertEqual(game.player_in_action.action, None)
        self.assertEqual(game._last_aggressor, None)
        self.assertEqual(game.pot, 9)
        self.assertEqual(game.street, Street.TURN)

    def test_make_action_with_fraction(self):
        hero = Player(Position.BTN, 98, is_hero=True)
        villain = Player(Position.BB, 98)
        game = Game([hero, villain], pot=5, board='As2d3h')
        game.make_action(Action(Action.BET, fraction=0.5))
        self.assertEqual(game.pot, 7.5)
        self.assertEqual(hero.stack, 98)
        self.assertEqual(villain.stack, 95.5)
        game.make_action(Action(Action.RAISE, fraction=0.6))
        self.assertEqual(game.pot, 15)
        self.assertEqual(hero.stack, 90.5)
        self.assertEqual(villain.stack, 95.5)

    def test_make_action_when_shortstack_diff(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game([bb, btn], 33, board='2c Kd 8s', allin_allowed=True)
        bb.add_range(PptRange('AA', is_cumulative=False))
        btn.add_range(PptRange('8h 9h Tc Js', is_cumulative=False))
        game.make_action(Action(Action.BET, size=33))
        self.assertEqual(game._shortstack_diff, None)

        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=300, name='Villain')
        game = Game([bb, btn], 33, board='2c Kd 8s', allin_allowed=True)
        bb.add_range(PptRange('AA', is_cumulative=False))
        btn.add_range(PptRange('8h 9h Tc Js', is_cumulative=False))
        game.make_action(Action(Action.BET, size=300))
        self.assertEqual(game._shortstack_diff, 267)

    def test_make_action_when_shortstack_call_all_in(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=300, name='Villain')
        game = Game([bb, btn], 33, board='2c Kd 8s', allin_allowed=True)
        bb.add_range(PptRange('AA', is_cumulative=False))
        btn.add_range(PptRange('8h 9h Tc Js', is_cumulative=False))
        game.make_action(Action(Action.BET, size=300))
        self.assertEqual(game.pot, 333)
        self.assertEqual(bb.side_pot, None)
        self.assertEqual(game._shortstack_diff, 267)
        game.make_action(Action(Action.CALL))
        self.assertEqual(game.pot, 366)
        self.assertEqual(btn.side_pot, 99)

    def test_make_action_with_many_raises(self):
        hero = Player(Position.UTG, 200, is_hero=True, name='hero')
        villain = Player(Position.BB, 200, name='villain')
        game = Game(players=[hero, villain], pot=10, board='6d 4c 8h', allin_allowed=True)
        game.make_action(Action(Action.CHECK))
        game.make_action(Action(Action.BET, 7))  # Hero bet
        self.assertEqual(hero.stack, 193)
        game.make_action(Action(Action.RAISE, 30))  # Villain 2bet
        self.assertEqual(villain.stack, 170)
        game.make_action(Action(Action.RAISE, 193))
        self.assertEqual(hero.stack, 0)
        game.make_action(Action(Action.CALL))
        self.assertEqual(villain.stack, 0)

    def test_make_action_with_size_more_than_stack(self):
        hero = Player(Position.UTG, 200, is_hero=True, name='hero')
        villain = Player(Position.BB, 200, name='villain')
        game = Game(players=[hero, villain], pot=10, board='6d 4c 8h', allin_allowed=True)
        game.make_action(Action(Action.CHECK))
        game.make_action(Action(Action.BET, 7))  # Hero bet
        self.assertEqual(hero.stack, 193)
        game.make_action(Action(Action.RAISE, 30))  # Villain 2bet
        self.assertEqual(villain.stack, 170)
        game.make_action(Action(Action.RAISE, all_in=True))
        self.assertEqual(hero.stack, 0)

    def test_leaf_none(self):
        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([bb, btn], pot=3, board='AsKs2d')
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(Action.CHECK))
        self.assertEqual(game.leaf, GameLeaf.NONE)

    def test_leaf_round_closed(self):
        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([bb, btn], pot=3, board='AsKs2d')
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(Action.CHECK))
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(Action.CHECK))
        self.assertEqual(game.leaf, GameLeaf.ROUND_CLOSED)

        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([bb, btn], pot=3, board='AsKs2d')
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(Action.BET, 3))
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(Action.CALL, 3))
        self.assertEqual(game.leaf, GameLeaf.ROUND_CLOSED)

    def test_leaf_fold(self):
        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([bb, btn], pot=3, board='AsKs2d')
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(Action.BET, 3))
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(Action.FOLD))
        self.assertEqual(game.leaf, GameLeaf.FOLD)

    def test_leaf_showdown(self):
        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([bb, btn], pot=3, board='AsKs2d2s4h')
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(Action.BET, 3))
        self.assertEqual(game.leaf, GameLeaf.NONE)
        game.make_action(Action(Action.CALL, 3))
        self.assertEqual(game.game_over, True)

    def test_board_explorer(self):
        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game([btn, bb], 2, board='AsKs2d2s')
        be_flop1 = BoardExplorer(game.flop)
        be_flop2 = BoardExplorer(game.flop)
        self.assertNotEqual(be_flop1, be_flop2)
        be_flop3 = game.board_explorer(Street.FLOP)
        be_flop4 = game.board_explorer(Street.FLOP)
        self.assertEqual(be_flop3, be_flop4)
        game.board = 'AsKs2d'
        be_flop5 = game.board_explorer(Street.FLOP)
        be_flop6 = game.board_explorer(Street.FLOP)
        self.assertEqual(be_flop3, be_flop4)
        self.assertEqual(be_flop4, be_flop5)
        self.assertEqual(be_flop5, be_flop6)
        game.board = 'AsKs2h'
        be_flop5 = game.board_explorer(Street.FLOP)
        be_flop6 = game.board_explorer(Street.FLOP)
        self.assertEqual(be_flop3, be_flop4)
        self.assertNotEqual(be_flop4, be_flop5)
        self.assertEqual(be_flop5, be_flop6)


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
        self.game.make_action(Action(Action.CHECK))

    def test__init__(self):
        game_node = GameNode(self.game)
        self.assertEqual(game_node.parent, None)
        self.assertEqual(game_node.lines, [])

    def test_add_line(self):
        root = GameNode(self.game)
        self.assertEqual(root.game_state.player_in_action.position, Position.BTN)
        self.assertEqual(root.game_state.player_in_action.stack, 100)

        line_check = root.add_line(Action(Action.CHECK))
        self.assertEqual(root.game_state.player_in_action.position, Position.BTN)
        self.assertEqual(line_check.game_state.player_in_action.position, Position.BB)
        self.assertEqual(line_check.game_state.get_player(Position.BTN).stack, 100)
        self.assertEqual(line_check.parent, root)

        line_bet = root.add_line(Action(Action.BET, 6))
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
        self.assertEqual(root.lines[0].game_state.action.type_, Action.BET)
        self.assertEqual(root.lines[1].game_state.action.type_, Action.CHECK)

    def test_siblings(self):
        root = GameNode(self.game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_check = root.lines[1]
        self.assertEqual(line_bet.siblings, root.lines)
        self.assertEqual(line_check.siblings, root.lines)
        self.assertEqual(root.siblings, None)

    def test_count_cumulative_ranges(self):
        btn = Player(Position.BTN, 100)
        bb = Player(Position.BB, 100)
        game = Game(players=[bb, btn], pot=10, board='AsKs2d')
        game.make_action(Action(Action.CHECK))
        root = GameNode(game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_check = root.lines[1]
        line_check.add_range(EasyRange('MS+'))

    def test__iter__(self):
        root = GameNode(self.game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_bet.add_standard_lines()
        all_nodes = [game_node for game_node in root]
        self.assertEqual(all_nodes[0], root)
        self.assertEqual(all_nodes[1], root.lines[0])
        self.assertEqual(all_nodes[2], line_bet.lines[0])
        self.assertEqual(all_nodes[3], line_bet.lines[1])
        self.assertEqual(all_nodes[4], line_bet.lines[2])
        self.assertEqual(all_nodes[5], root.lines[1])

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

    def test_update_children_for_hero_range(self):
        self.btn.add_range(PptRange('As9d8sTs'))
        self.bb.add_range(PptRange('50%'))
        root = GameNode(self.game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_check = root.lines[0]
        self.assertEqual(root.game.players[Position.BTN].ranges, [PptRange('As9d8sTs')])
        self.assertEqual(line_bet.game.players[Position.BTN].ranges, [PptRange('As9d8sTs')])
        self.assertEqual(line_check.game.players[Position.BTN].ranges, [PptRange('As9d8sTs')])
        root.game_state.players[Position.BTN].ranges = [PptRange('AdKd8s7s')]
        self.assertEqual(root.game.players[Position.BTN].ranges, [PptRange('AdKd8s7s')])
        root.update_children()
        self.assertEqual(line_bet.game.players[Position.BTN].ranges, [PptRange('AdKd8s7s')])
        self.assertEqual(line_check.game.players[Position.BTN].ranges, [PptRange('AdKd8s7s')])

    def test_update_children_for_villain_range(self):
        self.btn.add_range(PptRange('As9d8sTs'))
        self.bb.add_range(PptRange('50%'))
        root = GameNode(self.game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_check = root.lines[0]
        line_villain_raise = line_bet.add_line(Action(Action.RAISE, fraction=1), PptRange("KK+"))
        self.assertEqual(root.game.players[Position.BB].ranges, [PptRange('50%')])
        self.assertEqual(line_bet.game.players[Position.BB].ranges, [PptRange('50%')])
        self.assertEqual(line_villain_raise.game.players[Position.BB].ranges, [PptRange('50%'), PptRange("KK+")])
        root.game_state.players[Position.BB].ranges = [PptRange('20%')]
        self.assertEqual(root.game.players[Position.BB].ranges, [PptRange('20%')])
        root.update_children()
        self.assertEqual(line_bet.game.players[Position.BB].ranges, [PptRange('20%')])
        self.assertEqual(line_check.game.players[Position.BB].ranges, [PptRange('20%')])
        self.assertEqual(line_villain_raise.game.players[Position.BB].ranges, [PptRange('20%'), PptRange("KK+")])

    def test_update_range_for_hero(self):
        self.btn.add_range(PptRange('As9d8sTs'))
        self.bb.add_range(PptRange('50%'))
        root = GameNode(self.game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_check = root.lines[0]
        self.assertEqual(root.game.players[Position.BTN].ranges, [PptRange('As9d8sTs')])
        self.assertEqual(line_bet.game.players[Position.BTN].ranges, [PptRange('As9d8sTs')])
        self.assertEqual(line_check.game.players[Position.BTN].ranges, [PptRange('As9d8sTs')])
        root.game_state.players[Position.BTN].ranges = [PptRange('AdKd8s7s')]
        root.update_range(PptRange('AdKd8s7s'))
        self.assertEqual(root.game.players[Position.BTN].ranges, [PptRange('AdKd8s7s')])
        self.assertEqual(line_bet.game.players[Position.BTN].ranges, [PptRange('AdKd8s7s')])
        self.assertEqual(line_check.game.players[Position.BTN].ranges, [PptRange('AdKd8s7s')])

    def test_update_range_for_villain(self):
        self.btn.add_range(PptRange('As9d8sTs'))
        self.bb.add_range(PptRange('50%'))
        root = GameNode(self.game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_check = root.lines[0]
        line_villain_raise = line_bet.add_line(Action(Action.RAISE, fraction=1), PptRange("KK+"))
        self.assertEqual(root.game.players[Position.BB].ranges, [PptRange('50%')])
        self.assertEqual(line_bet.game.players[Position.BB].ranges, [PptRange('50%')])
        self.assertEqual(line_villain_raise.game.players[Position.BB].ranges, [PptRange('50%'), PptRange("KK+")])
        line_villain_raise.update_range(PptRange('AA+'))
        self.assertEqual(line_villain_raise.game.players[Position.BB].ranges, [PptRange('50%'), PptRange("AA+")])

    def test__extract_action_range(self):
        self.bb.add_range(PptRange('50%'))
        root = GameNode(self.game)
        root.add_standard_lines()
        line_bet = root.lines[0]
        line_check = root.lines[0]
        line_villain_raise = line_bet.add_line(Action(Action.RAISE, fraction=1), PptRange("KK+"))
        extracted = GameNode._extract_action_range(line_bet, line_villain_raise)
        self.assertEqual(extracted, PptRange("KK+"))


class GameTreeTest(unittest.TestCase):
    def setUp(self):
        self.btn = Player(Position.BTN, 100, is_hero=True)
        self.bb = Player(Position.BB, 100)
        self.game = Game(players=[self.bb, self.btn], pot=6, board='2cKd8s')
        self.game.make_action(Action(Action.CHECK))

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

    def test_calculate_node_when_hero_close_game_with_all_in_call(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game([bb, btn], 33, board='2c Kd 8s')
        bb.add_range(PptRange('AA', is_cumulative=False))
        btn.add_range(PptRange('8h 9h Tc Js', is_cumulative=False))
        game.make_action(Action(Action.BET, size=33))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        call_line = root.lines[0]
        game_tree.calculate_node(call_line)
        self.assertAlmostEqual(call_line.hero_equity, 0.354, delta=0.03)
        self.assertAlmostEqual(call_line.hero_pot_share.stack, 35.4, delta=2)
        self.assertAlmostEqual(call_line.hero_ev.stack, 35.4, delta=2)
        self.assertAlmostEqual(call_line.hero_pot_share.relative, 2.4, delta=2)
        self.assertAlmostEqual(call_line.hero_ev.relative, 2.4, delta=2)

    def test_calculate_node_when_shortstack_call_all_in(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=300, name='Villain')
        game = Game([bb, btn], 33, board='2c Kd 8s', allin_allowed=True)
        bb.add_range(PptRange('AA', is_cumulative=False))
        btn.add_range(PptRange('8h 9h Tc Js', is_cumulative=False))
        game.make_action(Action(Action.BET, size=300))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        call_line = root.lines[0]
        game_tree.calculate_node(call_line)
        self.assertAlmostEqual(call_line.hero_equity, 0.354, delta=0.03)
        self.assertAlmostEqual(call_line.hero_pot_share.stack, 35.4, delta=2)
        self.assertAlmostEqual(call_line.hero_ev.stack, 35.4, delta=2)
        self.assertAlmostEqual(call_line.hero_pot_share.relative, 2.4, delta=2)
        self.assertAlmostEqual(call_line.hero_ev.relative, 2.4, delta=2)

    def test_calculate_node_when_hero_close_game_with_river_call(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game([bb, btn], 33, board='2c Kd 8s 3c Jh')
        bb.add_range(PptRange('AA', is_cumulative=False))
        btn.add_range(PptRange('8h 9h Tc Js', is_cumulative=False))
        game.make_action(Action(Action.BET, size=6))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        raise_line = root.lines[0]
        raise_line.add_line(Action(Action.CALL), PptRange('*', is_cumulative=False))
        call_line = root.lines[1]
        #        game_tree.calculate_node(call_line)
        game_tree.calculate()
        self.assertAlmostEqual(call_line.hero_equity, 0.944, delta=0.03)
        self.assertAlmostEqual(call_line.hero_pot_share.stack, 69.5, delta=1)
        self.assertAlmostEqual(call_line.hero_pot_share.relative, 36.5, delta=1)
        self.assertAlmostEqual(call_line.hero_ev.stack, 69.5, delta=1)
        self.assertAlmostEqual(call_line.hero_ev.relative, 36.5, delta=1)

    def test_calculate_node_when_hero_close_round_with_call(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game([bb, btn], 33, board='2c Kd 8s 3c')
        bb.add_range(PptRange('AA', is_cumulative=False))
        btn.add_range(PptRange('8h 9h Tc Js', is_cumulative=False))
        game.make_action(Action(Action.BET, size=6))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        call_line = root.add_line(Action(Action.CALL))
        game_tree.calculate()
        self.assertAlmostEqual(call_line.hero_equity, 0.233, delta=0.03)
        self.assertAlmostEqual(call_line.hero_pot_share.stack, 37.5, delta=1)
        self.assertEqual(call_line.hero_ev, None)

    def test_calculate_node_when_villain_close_game_with_all_in_call(self):
        btn = Player(Position.BTN, stack=33, name='Villain')
        bb = Player(Position.BB, stack=33, is_hero=True, name='Hero')
        game = Game([bb, btn], 33, board='2c Kd 8s')
        bb.add_range(PptRange('As Ad 3s 3h'))
        btn.add_range(PptRange('8h 9h Tc Js'))
        game.make_action(Action(Action.BET, size=33))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        call_line = root.lines[0]
        game_tree.calculate_node(call_line)
        self.assertAlmostEqual(call_line.hero_equity, 0.635, delta=0.03)
        self.assertAlmostEqual(call_line.hero_pot_share.stack, 63.5, delta=1)
        self.assertAlmostEqual(call_line.hero_ev.stack, 63.5, delta=1)
        self.assertAlmostEqual(call_line.hero_pot_share.relative, 30.5, delta=1)
        self.assertAlmostEqual(call_line.hero_ev.relative, 30.5, delta=1)

    def test_calculate_node_with_range_distribution(self):
        bb = Player(Position.BB, stack=33, is_hero=True)
        btn = Player(Position.BTN, stack=33)
        game = Game([bb, btn], 33, board='2c4cKd')
        bb.add_range(PptRange('AsAd8s8h'))
        btn.add_range(PptRange('30%!AA'))
        game.make_action(Action(Action.BET, 33))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        villain_rd = RangeDistribution.from_game(sub_ranges=[
            SubRange('bet', EasyRange('2P+,FD,SD8+')),
            SubRange('fold', EasyRange('*')),
        ], player=btn, game=game)
        line_call = root.lines[0]
        line_fold = root.lines[1]
        line_call.add_range(villain_rd.sub_range('bet'))
        line_fold.add_range(villain_rd.sub_range('fold'))
        game_tree.calculate_node(line_call)
        self.assertAlmostEqual(line_call.hero_equity, 0.396, delta=0.03)
        self.assertAlmostEqual(line_call.line_fraction, 0.486, delta=0.03)
        game_tree.calculate_node(line_fold)
        self.assertAlmostEqual(line_fold.had_equity, 0.24, delta=0.03)
        self.assertAlmostEqual(line_fold.hero_equity, 1, delta=0.03)
        self.assertAlmostEqual(line_fold.hero_pot_share.stack, 66, delta=0.03)

    def test__get_leaf_nodes(self):
        bb = Player(Position.BB, stack=33, is_hero=True)
        btn = Player(Position.BTN, stack=33)
        game = Game([bb, btn], 33, board='2c4cKd')
        game.make_action(Action(Action.BET, 33))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        leaf_nodes = game_tree._get_leaf_nodes()
        self.assertEqual(list(leaf_nodes), root.lines)

    def test_calculate_tree_with_range_distribution(self):
        bb = Player(Position.BB, stack=33, is_hero=True)
        btn = Player(Position.BTN, stack=33)
        game = Game([bb, btn], 33, board='2c4cKd')
        bb.add_range(PptRange('AsAd8s8h'))
        btn.add_range(PptRange('30%!AA'))
        game.make_action(Action(Action.BET, 33))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        villain_rd = RangeDistribution.from_game(sub_ranges=[
            SubRange('bet', EasyRange('2P+,FD,SD8+')),
            SubRange('fold', EasyRange('*')),
        ], player=btn, game=game)
        line_call = root.lines[0]
        line_fold = root.lines[1]
        line_call.add_range(villain_rd.sub_range('bet'))
        line_fold.add_range(villain_rd.sub_range('fold'))
        game_tree.calculate()
        self.assertAlmostEqual(line_call.hero_equity, 0.396, delta=0.03)
        self.assertAlmostEqual(line_call.line_fraction, 0.486, delta=0.03)
        self.assertAlmostEqual(line_call.hero_ev.stack, 39.2, delta=2)

        self.assertAlmostEqual(line_fold.had_equity, 0.24, delta=0.03)
        self.assertAlmostEqual(line_fold.hero_equity, 1, delta=0.03)
        self.assertAlmostEqual(line_fold.hero_pot_share.stack, 66, delta=0.03)
        self.assertAlmostEqual(line_fold.hero_ev.stack, 66, delta=0.03)
        self.assertAlmostEqual(line_fold.line_fraction, 0.514, delta=0.03)

        self.assertAlmostEqual(root.hero_pot_share.stack, 52.8, delta=2)
        self.assertAlmostEqual(root.hero_ev.stack, 52.8, delta=2)

    def test_calculate_multilevel_tree(self):
        """ 3bet pot in position as PFR """
        hero = Player(Position.BTN, 407.81, is_hero=True, name='Hero')
        hero.add_range(PptRange('9s8c6s5d'))
        villain = Player(Position.BB, 90.4)
        villain.add_range(PptRange('$FI50!AA'))
        game = Game([hero, villain], 25.5, board='Td9h2d', allin_allowed=True)
        game.make_action(Action(Action.CHECK))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        hero_bet = root.add_line(Action(Action.BET, size=17.6))
        hero_check = root.add_line(Action(Action.CHECK))
        villain_rd = RangeDistribution.from_game(sub_ranges=[SubRange('raise', EasyRange('TB2P+, FD2+, FD:(TP,MP,BP)')),
                                                             SubRange('fold', EasyRange('*')),
                                                             ],
                                                 player=villain,
                                                 game=game)
        villain_raise = hero_bet.add_line(Action(Action.RAISE, size=90.4), villain_rd.sub_range('raise'))
        villain_fold = hero_bet.add_line(Action(Action.FOLD), villain_rd.sub_range('fold'))
        hero_bet_call = villain_raise.add_line(Action(Action.CALL))
        hero_bet_fold = villain_raise.add_line(Action(Action.FOLD))
        game_tree.calculate()
        self.assertAlmostEqual(hero_check.hero_equity, 0.43, delta=0.03)

    def test_shove_vs_SOR(self):
        hero = Player(Position.BTN, 407.81, is_hero=True, name='Hero')
        hero.add_range(PptRange('9s8c6s5d'))
        villain = Player(Position.BB, 90.4)
        villain.add_range(PptRange('$FI50!AA'))
        game = Game([hero, villain], 25.5, board='Td9h2d', allin_allowed=True)
        game.make_action(Action(Action.CHECK))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        hero_bet = root.add_line(Action(Action.BET, size=17.6))
        hero_check = root.add_line(Action(Action.CHECK))
        villain_rd = RangeDistribution.from_game(sub_ranges=[SubRange('raise', EasyRange('TB2P+, FD2+, FD:(TP,MP,BP)')),
                                                             SubRange('fold', EasyRange('*')),
                                                             ],
                                                 player=villain,
                                                 game=game)
        villain_raise = hero_bet.add_line(Action(Action.RAISE, size=90.4), villain_rd.sub_range('raise'))
        villain_fold = hero_bet.add_line(Action(Action.FOLD), villain_rd.sub_range('fold'))
        hero_bet_call = villain_raise.add_line(Action(Action.CALL))
        game_tree.calculate()
        self.assertAlmostEqual(hero_check.hero_equity, 0.43, delta=0.03)
        self.assertAlmostEqual(villain_raise.line_fraction, 0.275, delta=0.03)
        self.assertAlmostEqual(villain_fold.line_fraction, 0.725, delta=0.03)
        self.assertAlmostEqual(villain_fold.had_equity, 0.5, delta=0.03)
        self.assertAlmostEqual(hero_bet_call.hero_equity, 0.27, delta=0.03)


class TypicalGameSituationTest(unittest.TestCase):
    def test_SPR1_call_pot_bet(self):
        btn = Player(Position.BTN, stack=33, is_hero=True, name='Hero')
        bb = Player(Position.BB, stack=33, name='Villain')
        game = Game(players=[bb, btn], pot=33, board='2c Kd 8s')
        bb.add_range(PptRange('AA'))
        btn.add_range(PptRange('8h 9h Tc Js'))
        game.make_action(Action(Action.BET, size=33))
        root = GameNode(game)
        game_tree = GameTree(root, odds_oracle)
        root.add_standard_lines()
        call_line = root.lines[0]
        fold_line = root.lines[1]
        game_tree.calculate()
        self.assertAlmostEqual(call_line.hero_equity, 0.35, delta=0.03)

