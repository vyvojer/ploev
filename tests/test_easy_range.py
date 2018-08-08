import unittest
from ploev.cards import *
from ploev.easy_range import *
from ploev.easy_range import  _StraightDrawExplorer, _StraightExplorer
from ploev.easy_range import _MadeHandExplorer, _FlushDrawExplorer


class MadeHandTest(unittest.TestCase):
    hand = CardSet.from_str('AA')

    def test__init__(self):
        hole = CardSet.from_str('AK')
        hand = CardSet.from_str('AK')
        absolute_rank = (14, 13)
        relative_rank = (1, 2)
        tp = MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE, absolute_rank, relative_rank, hole, hand)
        self.assertEqual(tp.hole, CardSet.from_ranks([14, 13]))
        self.assertEqual(tp.relative_rank, (1, 2))

    def test_comparison(self):
        hole = CardSet.from_str('AK')
        hand = CardSet.from_str('AK')
        ts = MadeHand(MadeHand.SET, MadeHand.NONE, (14,), (1,), hole, hand)
        ms = MadeHand(MadeHand.SET, MadeHand.NONE, (13,), (1,), hole, hand)
        nut_str = MadeHand(MadeHand.STRAIGHT, MadeHand.NONE, (13,), (1,), hole, hand)
        second_str = MadeHand(MadeHand.STRAIGHT, MadeHand.NONE, (12,), (1,), hole, hand)
        tt2p = MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE, (13, 12), (1,), hole, hand)
        tb2p = MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE, (13, 3), (1,), hole, hand)
        self.assertLess(tt2p, ts)
        self.assertLess(tb2p, tt2p)
        self.assertLess(tt2p, ms)
        self.assertLess(ms, ts)
        self.assertLess(ts, second_str)
        self.assertLess(second_str, nut_str)

    def test__repr__(self):
        hand = MadeHand(MadeHand.SET, MadeHand.NONE, (14,), (1,), CardSet.from_str('AA'), CardSet.from_str('AAA'))
        self.assertEqual(eval(repr(hand)), hand)


class StraightDrawTest(unittest.TestCase):
    def test_create_straight_draw(self):
        ranks = (8, 9)
        outs = (11, 7)
        nut_outs = (7,)
        sd = StraightDraw(StraightDraw.NORMAL, ranks, outs, nut_outs)
        self.assertEqual((9, 8), sd.hole_ranks)
        self.assertEqual((11, 7), sd.outs)
        self.assertEqual((7,), sd.nut_outs)

    def test__repr__(self):
        sd = StraightDraw(StraightDraw.NORMAL, (8, 9), (11, 7), (7,))
        self.assertEqual(eval(repr(sd)), sd)

    def test_hole(self):
        sd = StraightDraw(StraightDraw.NORMAL, (4, 5), (4,), ())
        self.assertEqual(sd.hole, CardSet.from_ranks((4, 5)))

    def test_get_card_set(self):
        sd = StraightDraw(StraightDraw.NORMAL, (8, 9), (11, 7), (7,))
        cs = sd.get_card_set()
        self.assertEqual(CardSet.from_str('98'), cs)

    def test__eq__(self):
        sd1 = StraightDraw(StraightDraw.NORMAL, (8, 9), (11, 7), (7,))
        sd2 = StraightDraw(StraightDraw.NORMAL, (9, 8), (11, 7), (7,))
        self.assertEqual(sd1, sd2)

    def test__lt__(self):
        sd1 = StraightDraw(StraightDraw.NORMAL, (8, 9), (11, 7), (11, 7))
        sd2 = StraightDraw(StraightDraw.NORMAL, (9, 8), (11, 7, 6), (7,))
        sd3 = StraightDraw(StraightDraw.NORMAL, (9, 8), (11, 7,), (11,))
        self.assertLess(sd3, sd1)
        self.assertLess(sd3, sd2)
        sd1 = StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(11, 10), outs=(12,), nut_outs=(12,))
        sd2 = StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(12, 11), outs=(10,), nut_outs=(10,))
        sd3 = StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(12, 10), outs=(11,), nut_outs=(11,))
        self.assertLess(sd3, sd2)
        self.assertLess(sd1, sd3)

    def test_create_from_string(self):
        sd = StraightDraw.from_str('98', 'J7', '7')
        self.assertEqual(sd.hole_ranks, (9, 8))
        self.assertEqual(sd.outs, (11, 7))
        self.assertEqual(sd.nut_outs, (7,))
        sd = StraightDraw.from_str('98', 'J7', '')
        self.assertEqual(sd.hole_ranks, (9, 8))
        self.assertEqual(sd.outs, (11, 7))
        self.assertEqual(sd.nut_outs, ())

    def test_add_outs(self):
        sd = StraightDraw(StraightDraw.NORMAL, (8, 7), (6,), (6,))
        sd.add_outs(11)
        self.assertEqual(sd.outs, (11, 6))

    def test_add_nut_outs(self):
        sd = StraightDraw(StraightDraw.NORMAL, (8, 7), (11,), ())
        sd.add_nut_outs(6)
        self.assertEqual(sd.outs, (11, 6))
        self.assertEqual(sd.nut_outs, (6,))

    def test_ranks_card_set(self):
        sd = StraightDraw(StraightDraw.NORMAL, (8, 7), (11,), ())
        cs = CardSet.from_ranks([8, 7])
        self.assertEqual(sd.ranks_card_set, cs)


class FlushDrawTest(unittest.TestCase):
    def test__init__(self):
        fd = FlushDraw(0, FlushDraw.NORMAL, (13,), (1,), CardSet.from_str('Kdd'))
        self.assertEqual(fd.type_, 0)
        self.assertEqual(fd.absolute_rank, (13,))
        self.assertEqual(fd.relative_rank, (1,))
        self.assertEqual(fd.hole, CardSet.from_str('Kdd'))

    def test__eq__(self):
        fd_kdd_1 = FlushDraw(0, FlushDraw.NORMAL, (13,), (1,), CardSet.from_str('Kdd'))
        fd_kdd_2 = FlushDraw(0, FlushDraw.NORMAL, (13,), (1,), CardSet.from_str('Kdd'))
        fd_kdd_turned = FlushDraw(1, FlushDraw.NORMAL, (13,), (1,), CardSet.from_str('Kdd'))
        fd_kcc = FlushDraw(1, FlushDraw.NORMAL, (13,), (1,), CardSet.from_str('Kcc'))
        fd_add = FlushDraw(0, FlushDraw.NORMAL, (14,), (1,), CardSet.from_str('Add'))
        self.assertTrue(fd_kdd_1 == fd_kdd_2)
        self.assertFalse(fd_kdd_1 == fd_kdd_turned)
        self.assertFalse(fd_kdd_1 == fd_kcc)
        self.assertFalse(fd_kdd_1 == fd_add)

    def test__lt__(self):
        fd_kdd_1 = FlushDraw(0, FlushDraw.NORMAL, (13,), (2,), CardSet.from_str('Kdd'))
        fd_kdd_2 = FlushDraw(0, FlushDraw.NORMAL, (13,), (2,), CardSet.from_str('Kdd'))
        fd_kdd_turned = FlushDraw(1, FlushDraw.NORMAL, (13,), (2,), CardSet.from_str('Kdd'))
        fd_kcc = FlushDraw(1, FlushDraw.NORMAL, (13,), (2,), CardSet.from_str('Kcc'))
        fd_kdd = FlushDraw(0, FlushDraw.NORMAL, (14,), (1,), CardSet.from_str('Add'))
        self.assertFalse(fd_kdd_1 < fd_kdd_2)
        self.assertFalse(fd_kdd_1 < fd_kdd_turned)
        self.assertFalse(fd_kdd_1 < fd_kcc)
        self.assertTrue(fd_kdd_1 < fd_kdd)

        bfd_add = FlushDraw(FlushDraw.BACKDOOR, FlushDraw.NORMAL, (14,), (1,), CardSet.from_str('Add'))
        bfd_kdd = FlushDraw(FlushDraw.BACKDOOR, FlushDraw.NORMAL, (13,), (2,), CardSet.from_str('Kdd'))
        bfd_ass = FlushDraw(FlushDraw.BACKDOOR, FlushDraw.NORMAL, (14,), (1,), CardSet.from_str('Ass'))
        bfd_kss = FlushDraw(FlushDraw.BACKDOOR, FlushDraw.NORMAL, (13,), (2,), CardSet.from_str('Kss'))
        bfd_khh = FlushDraw(FlushDraw.BACKDOOR, FlushDraw.NORMAL, (13,), (1,), CardSet.from_str('Add'))
        bfd_dhh = FlushDraw(FlushDraw.BACKDOOR, FlushDraw.NORMAL, (12,), (2,), CardSet.from_str('Kdd'))
        bfd_acc = FlushDraw(FlushDraw.BACKDOOR, FlushDraw.NORMAL, (14,), (1,), CardSet.from_str('Acc'))

        self.assertTrue(bfd_kdd < bfd_add)
        self.assertTrue(bfd_kss < bfd_ass)
        self.assertTrue(bfd_dhh < bfd_khh)
        self.assertTrue(bfd_khh < bfd_ass)
        self.assertFalse(bfd_khh < bfd_acc)

    def test_repr(self):
        fd = FlushDraw(0, FlushDraw.NORMAL, (13,), (1,), CardSet.from_str('Kdd'))
        self.assertEqual(eval(repr(fd)), fd)


class BlockerTest(unittest.TestCase):
    def test__eq__(self):
        blocker = Blocker(Blocker.FLUSH_BLOCKER, Blocker.ONE_CARD, (14,), (1,), CardSet.from_str('Ad'))
        blocker_eq = Blocker(Blocker.FLUSH_BLOCKER, Blocker.ONE_CARD, (14,), (1,), CardSet.from_str('Ad'))
        blocker_not_eq = Blocker(Blocker.FLUSH_BLOCKER, Blocker.ONE_CARD, (14,), (1,), CardSet.from_str('As'))
        self.assertEqual(blocker, blocker_eq)
        self.assertNotEqual(blocker, blocker_not_eq)

    def test__repr__(self):
        blocker = Blocker(Blocker.FLUSH_BLOCKER, Blocker.ONE_CARD, (14,), (1,), CardSet.from_str('Ad'))
        self.assertEqual(eval(repr(blocker)), blocker)

    def test__lt__(self):
        first_blocker = Blocker(Blocker.FLUSH_BLOCKER, Blocker.FLOPPED, (14,), (1,), CardSet.from_str('Ad'))
        second_blocker = Blocker(Blocker.FLUSH_BLOCKER, Blocker.FLOPPED, (13,), (2,), CardSet.from_str('Kd'))
        self.assertTrue(second_blocker < first_blocker)

        flopped_blocker = Blocker(Blocker.FLUSH_BLOCKER, Blocker.FLOPPED, (14,), (1,), CardSet.from_str('Ad'))
        turned_blocker = Blocker(Blocker.FLUSH_BLOCKER, Blocker.TURNED, (14,), (1,), CardSet.from_str('As'))
        self.assertTrue(turned_blocker < flopped_blocker)

        first_blocker = Blocker(Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (13,), (1,), CardSet.from_str('KK'))
        second_blocker = Blocker(Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (12,), (1,), CardSet.from_str('QQ'))
        self.assertTrue(second_blocker < first_blocker)


class StraightExplorerTest(unittest.TestCase):
    def test_get_unranked_straights(self):
        board = CardSet.from_str('AsKd2c')
        unr_straights = _StraightExplorer.get_unranked_straights(board)
        self.assertEqual(len(unr_straights), 0)

        board = CardSet.from_str('AsKdTc')
        unr_straights = _StraightExplorer.get_unranked_straights(board)
        self.assertEqual(len(unr_straights), 1)

        board = CardSet.from_str('AsKd2Thc3d')
        unr_straights = _StraightExplorer.get_unranked_straights(board)
        self.assertEqual(len(unr_straights), 2)

    def test_straighted(self):
        board = CardSet.from_str('AsKd2c')
        se = _StraightExplorer(board)
        self.assertFalse(se.is_straighted)

        board = CardSet.from_str('AsKd2cJh')
        se = _StraightExplorer(board)
        self.assertTrue(se.is_straighted)

    def test_straights(self):
        board = CardSet.from_str('AsKd2c')
        se = _StraightExplorer(board)
        self.assertEqual(se.straights, [])

        board = CardSet.from_str('AsKd2cJh')
        se = _StraightExplorer(board)
        hand = MadeHand(MadeHand.STRAIGHT, MadeHand.NONE, (14,), (1,), CardSet.from_str('QT'),
                        CardSet.from_str('AKQJT'))
        self.assertEqual(se.straights, [hand])

        board = CardSet.from_str('KdJcTh')
        se = _StraightExplorer(board)
        hand1 = MadeHand(MadeHand.STRAIGHT, MadeHand.NONE, (14,), (1,), CardSet.from_str('AQ'),
                         CardSet.from_str('AKQJT'))
        hand2 = MadeHand(MadeHand.STRAIGHT, MadeHand.NONE, (13,), (2,), CardSet.from_str('Q9'),
                         CardSet.from_str('KQJT9'))
        self.assertEqual(se.straights, [hand1, hand2])

    def test_straight_blockers(self):
        se = _StraightExplorer(Board.from_str('Ad Jd Td'))
        straight_blockers = se.straight_blockers
        self.assertEqual(straight_blockers[0],
                         Blocker(Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (13,), (1,), CardSet.from_str('KK')))

        se = _StraightExplorer(Board.from_str('KdJdTs'))
        straight_blockers = se.straight_blockers
        self.assertEqual(len(straight_blockers), 6)


class StraightDrawExplorerTest(unittest.TestCase):
    def test_straights(self):
        board = CardSet.from_str('AsKd2cJh')
        sde = _StraightDrawExplorer(board)
        hand = MadeHand(MadeHand.STRAIGHT, MadeHand.NONE, (14,), (1,), CardSet.from_str('QT'),
                        CardSet.from_str('AKQJT'))
        sde._get_straights()
        self.assertEqual(sde._straights, [hand])

    def test_straights_holes(self):
        board = CardSet.from_str('AsKd2cJh')
        sde = _StraightDrawExplorer(board)
        sde._get_straights()
        self.assertEqual(sde._straights_holes, [{12, 10}])

    def test_find_two_card_draws(self):
        board = CardSet.from_str('AT2').ranks
        remaining_ranks = CardSet.from_str('AT2').remaining_ranks
        draws, all_draw_ranks, draws_ranks = _StraightDrawExplorer._find_two_card_draws(board,
                                                                                        remaining_ranks,
                                                                                        set())
        draws.sort(reverse=True)
        self.assertEqual(len(draws), 6, msg='draws was {}'.format(draws))
        self.assertEqual(draws[0], StraightDraw(StraightDraw.NORMAL, (13, 12), (11,), (11,)))
        self.assertEqual(all_draw_ranks, {13, 12, 11, 5, 4, 3})
        self.assertEqual(len(draws_ranks), 6)
        self.assertIn((13, 12), draws_ranks)
        self.assertIn((13, 11), draws_ranks)
        self.assertIn((12, 11), draws_ranks)

    def test_fill_by_outs_and_by_ranks(self):
        draws = [
            StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(13, 12), outs=(11,), nut_outs=(11,)),
            StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(12, 11), outs=(13,), nut_outs=(13,)),
            StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(13, 11), outs=(12,), nut_outs=(12,))
        ]
        by_ranks, by_outs = _StraightDrawExplorer._fill_by_outs_and_by_ranks(draws, 2)
        self.assertEqual(by_ranks[2][(13, 12)],
                         StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(13, 12), outs=(11,), nut_outs=(11,)))
        self.assertEqual(by_ranks[2][(13, 11)],
                         StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(13, 11), outs=(12,), nut_outs=(12,)))
        self.assertEqual(by_outs[2][(12,), (12,)],
                         StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(13, 11), outs=(12,), nut_outs=(12,)))

    def test_find_x_size_card_draws(self):
        draws = [
            StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(13, 12), outs=(11,), nut_outs=(11,)),
            StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(12, 11), outs=(13,), nut_outs=(13,)),
            StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(13, 11), outs=(12,), nut_outs=(12,))
        ]
        all_draw_ranks = {13, 12, 11}
        by_ranks, by_outs = _StraightDrawExplorer._fill_by_outs_and_by_ranks(draws, 2)
        draws_3_cards, by_ranks, by_outs = _StraightDrawExplorer._find_x_size_card_draws(by_ranks, by_outs,
                                                                                         all_draw_ranks)
        self.assertEqual(draws_3_cards,
                         [StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(13, 12, 11), outs=(13, 12, 11),
                                       nut_outs=(13, 12, 11))])
        self.assertEqual(by_ranks[3][13, 12, 11],
                         StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(13, 12, 11), outs=(13, 12, 11),
                                      nut_outs=(13, 12, 11)))
        self.assertEqual(by_outs[3][(13, 12, 11), (13, 12, 11)],
                         StraightDraw(type_=StraightDraw.NORMAL, hole_ranks=(13, 12, 11), outs=(13, 12, 11),
                                      nut_outs=(13, 12, 11)))

    def test_explore(self):
        board = CardSet.from_str('AdKs2d')
        be = _StraightDrawExplorer(board)
        be._explore()
        sd = be.straight_draws
        self.assertEqual(len(sd), 17)

    def test_straight_draws(self):
        board = CardSet.from_str('AdKs7d')
        sd = _StraightDrawExplorer(board).straight_draws
        self.assertEqual(len(sd), 4)
        self.assertEqual(sd[0], StraightDraw(StraightDraw.NORMAL, (12, 11, 10), (12, 11, 10), (12, 11, 10)))

    def test_straight_draws_on_straighted_board(self):
        board = Board.from_str('5s8d9c')
        sd = _StraightDrawExplorer(board).straight_draws
        self.assertEqual(len(sd), 22)

    def test_straight_draw_blockers(self):
        sde = _StraightDrawExplorer(Board.from_str('KdQd6c'))
        straight_draw_blockers = sde.straight_draw_blockers
        self.assertEqual(straight_draw_blockers[0],
                         Blocker(Blocker.STRAIGHT_DRAW_BLOCKER, Blocker.TWO_CARD, (14,), (1,),
                                 CardSet.from_str('AA')))
        self.assertEqual(straight_draw_blockers[-1],
                         Blocker(Blocker.STRAIGHT_DRAW_BLOCKER, Blocker.ONE_CARD, (9,), (4,),
                                 CardSet.from_str('9')))

    def test_backdoor_straight_draws(self):
        sde = _StraightDrawExplorer(Board.from_str('KdQd6c'))
        backdoors = sde.backdoor_straight_draws
        self.assertEqual(backdoors[0], StraightDraw(StraightDraw.BACKDOOR, (9, 8), (11, 10, 7, 5), ()))
        self.assertEqual(backdoors[-1], StraightDraw(StraightDraw.BACKDOOR, (3, 2), (5, 4), ()))


class FlushDrawExplorerTest(unittest.TestCase):
    def test_is_rainbow(self):
        two_tone = Board.from_str('AdKd7s')
        fde = _FlushDrawExplorer(two_tone)
        self.assertFalse(fde.is_rainbow)

        rainbow = Board.from_str('AdKh7s')
        fde = _FlushDrawExplorer(rainbow)
        self.assertTrue(fde.is_rainbow)

        monotone = Board.from_str('AdKd7d')
        fde = _FlushDrawExplorer(monotone)
        self.assertTrue(fde.is_rainbow)

    def test_is_flushed(self):
        two_tone = Board.from_str('AdKd7s')
        fde = _FlushDrawExplorer(two_tone)
        self.assertFalse(fde.is_flushed)

        rainbow = Board.from_str('AdKh7s')
        fde = _FlushDrawExplorer(rainbow)
        self.assertFalse(fde.is_flushed)

        monotone = Board.from_str('AdKd7d')
        fde = _FlushDrawExplorer(monotone)
        self.assertTrue(fde.is_flushed)

    def test_has_flopped_flush_draw(self):
        board = Board.from_str('AdKd7s')
        fde = _FlushDrawExplorer(board)
        self.assertTrue(fde.has_flopped_flush_draw)

        board = Board.from_str('AdKd7s9s')
        fde = _FlushDrawExplorer(board)
        self.assertTrue(fde.has_flopped_flush_draw)

        board = Board.from_str('AdKd7s9s3d')
        fde = _FlushDrawExplorer(board)
        self.assertTrue(fde.has_flopped_flush_draw)

        board = Board.from_str('AdKh7s')
        fde = _FlushDrawExplorer(board)
        self.assertFalse(fde.has_flopped_flush_draw)

        board = Board.from_str('AdKh7s2s')
        fde = _FlushDrawExplorer(board)
        self.assertFalse(fde.has_flopped_flush_draw)

        board = Board.from_str('AdKh7s2s4s')
        fde = _FlushDrawExplorer(board)
        self.assertFalse(fde.has_flopped_flush_draw)

    def test_has_turned_flush_draw(self):
        board_with_turned = Board.from_str('AdKd7s9s')
        fde = _FlushDrawExplorer(board_with_turned)
        self.assertTrue(fde.has_turned_flush_draw)

        board_with_turned = Board.from_str('AdKd7s9s2s')
        fde = _FlushDrawExplorer(board_with_turned)
        self.assertTrue(fde.has_turned_flush_draw)

        board_with_turned = Board.from_str('AdKd7s9h')
        fde = _FlushDrawExplorer(board_with_turned)
        self.assertFalse(fde.has_turned_flush_draw)

        board_with_turned = Board.from_str('AdKd7s9d')
        fde = _FlushDrawExplorer(board_with_turned)
        self.assertFalse(fde.has_turned_flush_draw)

    def test_flush_draws(self):
        fde = _FlushDrawExplorer(Board.from_str('AdKd7s'))
        flush_draws = fde.flush_draws
        self.assertEqual(flush_draws[0],
                         FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (12,), (1,), CardSet.from_str('Qdd')))
        self.assertEqual(flush_draws[-1],
                         FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (3,), (10,), CardSet.from_str('3dd')))

        fde = _FlushDrawExplorer(Board.from_str('AdKd7s8s'))
        flush_draws = fde.flush_draws
        self.assertEqual(flush_draws[0],
                         FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (12,), (1,), CardSet.from_str('Qdd')))
        self.assertEqual(flush_draws[1],
                         FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (14,), (1,), CardSet.from_str('Ass')))
        self.assertEqual(flush_draws[18],
                         FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (3,), (10,), CardSet.from_str('3dd')))
        self.assertEqual(flush_draws[19],
                         FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (3,), (10,), CardSet.from_str('3ss')))

        fde = _FlushDrawExplorer(Board.from_str('AsKd3h2h'))
        flush_draws = fde.flush_draws
        self.assertEqual(flush_draws[0],
                         FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (14,), (1,), CardSet.from_str('Ahh')))

    def test_backdoor_flush_draws(self):
        fde = _FlushDrawExplorer(Board.from_str('AdKd7s'))
        backdoors = fde.backdoor_flush_draws
        self.assertEqual(backdoors[0],
                         FlushDraw(FlushDraw.BACKDOOR, FlushDraw.FLOPPED, (14,), (1,), CardSet.from_str('Ass')))
        self.assertEqual(backdoors[-1],
                         FlushDraw(FlushDraw.BACKDOOR, FlushDraw.FLOPPED, (3,), (11,), CardSet.from_str('3ss')))

        board = Board.from_str('As Kd 7h')
        fde = _FlushDrawExplorer(board)
        backdoors = fde.backdoor_flush_draws
        self.assertEqual(len(backdoors), 33)
        self.assertEqual(backdoors[0],
                         FlushDraw(FlushDraw.BACKDOOR, FlushDraw.FLOPPED, (13,), (1,), CardSet.from_str('Kss')))
        self.assertEqual(backdoors[1],
                         FlushDraw(FlushDraw.BACKDOOR, FlushDraw.FLOPPED, (14,), (1,), CardSet.from_str('Ahh')))
        self.assertEqual(backdoors[2],
                         FlushDraw(FlushDraw.BACKDOOR, FlushDraw.FLOPPED, (14,), (1,), CardSet.from_str('Add')))

    def test_flush_draw_blockers(self):
        fde = _FlushDrawExplorer(Board.from_str('AdKd7s'))
        blockers = fde.flush_draw_blockers
        self.assertEqual(len(blockers), 11)
        self.assertEqual(blockers[0], Blocker(Blocker.FLUSH_DRAW_BLOCKER, Blocker.FLOPPED,
                                              (12,), (1,), CardSet.from_str('Qd')))
        self.assertEqual(blockers[-1], Blocker(Blocker.FLUSH_DRAW_BLOCKER, Blocker.FLOPPED,
                                               (2,), (11,), CardSet.from_str('2d')))

        fde = _FlushDrawExplorer(Board.from_str('AdKd7s2s'))
        blockers = fde.flush_draw_blockers
        self.assertEqual(len(blockers), 22)
        self.assertEqual(blockers[0], Blocker(Blocker.FLUSH_DRAW_BLOCKER, Blocker.FLOPPED,
                                              (12,), (1,), CardSet.from_str('Qd')))
        self.assertEqual(blockers[1], Blocker(Blocker.FLUSH_DRAW_BLOCKER, Blocker.TURNED,
                                              (14,), (1,), CardSet.from_str('As')))
        self.assertEqual(blockers[-2], Blocker(Blocker.FLUSH_DRAW_BLOCKER, Blocker.FLOPPED,
                                               (2,), (11,), CardSet.from_str('2d')))
        self.assertEqual(blockers[-1], Blocker(Blocker.FLUSH_DRAW_BLOCKER, Blocker.TURNED,
                                               (3,), (11,), CardSet.from_str('3s')))


class MadeHandsExplorerTest(unittest.TestCase):
    def test_paired(self):
        unpaired_board = Board.from_str('Ad2s7d')
        mhe = _MadeHandExplorer(unpaired_board)
        self.assertFalse(mhe.is_paired)
        paired_board = Board.from_str('Ad2s2d')
        mhe = _MadeHandExplorer(paired_board)
        self.assertTrue(mhe.is_paired)

    def test_get_sets(self):
        board = Board.from_str('Ad2s7d')
        mhe = _MadeHandExplorer(board)
        sets = mhe.sets
        self.assertEqual(sets[0], MadeHand(MadeHand.SET, MadeHand.NONE, (14,), (1,), CardSet.from_str('AA'),
                                           CardSet.from_str('AAA')))
        self.assertEqual(sets[2], MadeHand(MadeHand.SET, MadeHand.NONE, (2,), (3,), CardSet.from_str('22'),
                                           CardSet.from_str('222')))

    def test_two_pairs(self):
        board = Board.from_str('Ad2s7d')
        mhe = _MadeHandExplorer(board)
        tps = mhe.two_pairs
        self.assertEqual(tps[0], MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE, (14, 7), (1, 2), CardSet.from_str('A7'),
                                          CardSet.from_str('AA77')))
        self.assertEqual(tps[1], MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE, (14, 2), (1, 3), CardSet.from_str('A2'),
                                          CardSet.from_str('AA22')))
        self.assertEqual(tps[2], MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE, (7, 2), (2, 3), CardSet.from_str('72'),
                                          CardSet.from_str('7722')))

    def test_two_pairs_on_paired_board(self):
        board = Board.from_str('KsKdQs3s')
        mhe = _MadeHandExplorer(board)
        tps = mhe.two_pairs
        self.assertEqual(len(tps), 0)

        board = Board.from_str('KsKdQsAs')
        mhe = _MadeHandExplorer(board)
        tps = mhe.two_pairs
        self.assertEqual(len(tps), 0)

        board = Board.from_str('JsJdQsAs')
        mhe = _MadeHandExplorer(board)
        tps = mhe.two_pairs
        self.assertEqual(len(tps), 1)

        board = Board.from_str('3s3dQsAsJh')
        mhe = _MadeHandExplorer(board)
        tps = mhe.two_pairs
        self.assertEqual(len(tps), 3)

    def test_board_pairs(self):
        board = Board.from_str('Ad2s7d')
        mhe = _MadeHandExplorer(board)
        bps = mhe.board_pairs
        self.assertEqual(bps[0],
                         MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (14, 13), (1, 1, 1), CardSet.from_str('AK'),
                                  CardSet.from_str('AAK')))
        self.assertEqual(bps[1],
                         MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (14, 12), (1, 1, 2), CardSet.from_str('AQ'),
                                  CardSet.from_str('AAQ')))
        self.assertEqual(bps[13],
                         MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (7, 10), (8, 2, 4), CardSet.from_str('7T'),
                                  CardSet.from_str('77T')))
        self.assertEqual(bps[-1],
                         MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (2, 3), (13, 3, 10), CardSet.from_str('23'),
                                  CardSet.from_str('223')))

    def test_board_pairs_on_paired_board(self):
        board = Board.from_str('Ad2s7d7h')
        mhe = _MadeHandExplorer(board)
        bps = mhe.board_pairs
        self.assertEqual(len(bps), 20)

    def test_pocket_pairs_on_paired_board(self):
        board = Board.from_str('Ad2s7d7h')
        mhe = _MadeHandExplorer(board)
        pps = mhe.pocket_pairs
        self.assertEqual(len(pps), 10)

    def test_pocket_pairs(self):
        board = Board.from_str('Qd5s7d3h')
        mhe = _MadeHandExplorer(board)
        pocket_pairs = mhe.pocket_pairs
        self.assertEqual(pocket_pairs[0], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (14,), (1, 1, 1), CardSet.from_str('AA'), CardSet.from_str('AA')))
        self.assertEqual(pocket_pairs[1], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (13,), (2, 1, 2), CardSet.from_str('KK'), CardSet.from_str('KK')))
        self.assertEqual(pocket_pairs[2], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (11,), (4, 2, 1), CardSet.from_str('JJ'), CardSet.from_str('JJ')))
        self.assertEqual(pocket_pairs[3], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (10,), (5, 2, 2), CardSet.from_str('TT'), CardSet.from_str('TT')))
        self.assertEqual(pocket_pairs[4], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (9,), (6, 2, 3), CardSet.from_str('99'), CardSet.from_str('99')))
        self.assertEqual(pocket_pairs[5], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (8,), (7, 2, 4), CardSet.from_str('88'), CardSet.from_str('88')))
        self.assertEqual(pocket_pairs[6], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (6,), (9, 3, 1), CardSet.from_str('66'), CardSet.from_str('66')))
        self.assertEqual(pocket_pairs[7], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (4,), (11, 4, 1), CardSet.from_str('44'), CardSet.from_str('44')))
        self.assertEqual(pocket_pairs[8], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (2,), (13, 5, 1), CardSet.from_str('22'), CardSet.from_str('22')))

    def test_flush_blockers(self):
        mhe = _MadeHandExplorer(Board.from_str('AdKd4d'))
        flush_blockers = mhe.flush_blockers
        self.assertEqual(flush_blockers[0],
                         Blocker(Blocker.FLUSH_BLOCKER, Blocker.NONE, (12,), (1,), CardSet.from_str('Qd')))
        self.assertEqual(flush_blockers[-1],
                         Blocker(Blocker.FLUSH_BLOCKER, Blocker.NONE, (2,), (10,), CardSet.from_str('2d')))

    def test_pocket_pairs_AK783(self):
        board = Board.from_str('AdKc7h8s3s')
        mhe = _MadeHandExplorer(board)
        pocket_pairs = mhe.pocket_pairs
        self.assertEqual(pocket_pairs[0], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (12,), (3, 2, 1), CardSet.from_str('QQ'), CardSet.from_str('QQ')))
        self.assertEqual(pocket_pairs[1], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (11,), (4, 2, 2), CardSet.from_str('JJ'), CardSet.from_str('JJ')))
        self.assertEqual(pocket_pairs[2], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (10,), (5, 2, 3), CardSet.from_str('TT'), CardSet.from_str('TT')))
        self.assertEqual(pocket_pairs[3], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (9,), (6, 2, 4), CardSet.from_str('99'), CardSet.from_str('99')))
        self.assertEqual(pocket_pairs[4], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (6,), (9, 3, 1), CardSet.from_str('66'), CardSet.from_str('66')))
        self.assertEqual(pocket_pairs[5], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (5,), (10, 3, 2), CardSet.from_str('55'), CardSet.from_str('55')))
        self.assertEqual(pocket_pairs[6], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (4,), (11, 3, 3), CardSet.from_str('44'), CardSet.from_str('44')))
        self.assertEqual(pocket_pairs[7], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                   (2,), (13, 4, 1), CardSet.from_str('22'), CardSet.from_str('22')))

    def test_is_flushed(self):
        board = Board.from_str('AdKd9s2h')
        mhe = _MadeHandExplorer(board)
        self.assertFalse(mhe.is_flushed)

        board = Board.from_str('AdKd9s2d')
        mhe = _MadeHandExplorer(board)
        self.assertTrue(mhe.is_flushed)

    def test_flushes(self):
        board = Board.from_str('KdQd9s2d')
        mhe = _MadeHandExplorer(board)
        flushes = mhe.flushes
        self.assertEqual(flushes[0], MadeHand(MadeHand.FLUSH, MadeHand.NONE, (14,), (1,),
                                              CardSet.from_str('Add'), CardSet.from_str('AdKdQd2dd')))
        self.assertEqual(flushes[1], MadeHand(MadeHand.FLUSH, MadeHand.NONE, (11,), (2,),
                                              CardSet.from_str('Jdd'), CardSet.from_str('KdQdJd2dd')))

        board = Board.from_str('AdKs2d7d8d')
        mhe = _MadeHandExplorer(board)
        flushes = mhe.flushes
        self.assertEqual(flushes[0], MadeHand(MadeHand.FLUSH, MadeHand.NONE, (13,), (1,),
                                              CardSet.from_str('Kdd'), CardSet.from_str('AdKd8d7dd')))

    def test_get_paired_ranks(self):
        board = Board.from_str('AdKd2s2d3h')
        mhe = _MadeHandExplorer(board)
        self.assertEqual(mhe.paired_ranks, [2])
        self.assertEqual(mhe.unpaired_ranks, [14, 13, 3])

    def test_trips(self):
        board = Board.from_str('AdAs2d4s8d')
        mhe = _MadeHandExplorer(board)
        trips = mhe.trips
        self.assertEqual(len(trips), 9)
        self.assertEqual(trips[0],
                         MadeHand(MadeHand.TRIPS, MadeHand.NONE, (14, 13), (1, 1), CardSet.from_str('AK'),
                                  CardSet.from_str('AAAK')))
        self.assertEqual(trips[8],
                         MadeHand(MadeHand.TRIPS, MadeHand.NONE, (14, 3), (1, 9), CardSet.from_str('A3'),
                                  CardSet.from_str('AAA3')))

        board = Board.from_str('AdAs2d2s8d')
        mhe = _MadeHandExplorer(board)
        trips = mhe.trips
        self.assertEqual(len(trips), 20)
        self.assertEqual(trips[0],
                         MadeHand(MadeHand.TRIPS, MadeHand.NONE, (14, 13), (1, 1), CardSet.from_str('AK'),
                                  CardSet.from_str('AAAK')))
        self.assertEqual(trips[9],
                         MadeHand(MadeHand.TRIPS, MadeHand.NONE, (14, 3), (1, 10), CardSet.from_str('A3'),
                                  CardSet.from_str('AAA3')))
        self.assertEqual(trips[10],
                         MadeHand(MadeHand.TRIPS, MadeHand.NONE, (2, 13), (2, 1), CardSet.from_str('2K'),
                                  CardSet.from_str('222K')))
        self.assertEqual(trips[19],
                         MadeHand(MadeHand.TRIPS, MadeHand.NONE, (2, 3), (2, 10), CardSet.from_str('23'),
                                  CardSet.from_str('2223')))

    def test_check_pairness(self):
        board = Board.from_str('AK23')
        mhe = _MadeHandExplorer(board)
        mhe._check_pairness()
        self.assertFalse(mhe.is_paired)
        self.assertFalse(mhe.is_exactly_paired)
        self.assertFalse(mhe.is_exactly_tripsed)
        self.assertFalse(mhe.is_exactly_quaded)

        board = Board.from_str('AK22')
        mhe = _MadeHandExplorer(board)
        mhe._check_pairness()
        self.assertTrue(mhe.is_paired)
        self.assertTrue(mhe.is_exactly_paired)
        self.assertFalse(mhe.is_exactly_tripsed)
        self.assertFalse(mhe.is_exactly_quaded)

        board = Board.from_str('AK222')
        mhe = _MadeHandExplorer(board)
        mhe._check_pairness()
        self.assertTrue(mhe.is_paired)
        self.assertFalse(mhe.is_exactly_paired)
        self.assertTrue(mhe.is_exactly_tripsed)
        self.assertFalse(mhe.is_exactly_quaded)

    def test_full_houses(self):
        board = Board.from_str('AKK34')
        mhe = _MadeHandExplorer(board)
        full_houses = mhe.full_houses
        self.assertEqual(len(full_houses), 6)
        self.assertEqual(full_houses[0],
                         MadeHand(MadeHand.FULL_HOUSE, MadeHand.NONE, (14, 13), (1,), CardSet.from_str('AA'),
                                  CardSet.from_str('AAAKK')))
        self.assertEqual(full_houses[1],
                         MadeHand(MadeHand.FULL_HOUSE, MadeHand.NONE, (13, 14), (2,), CardSet.from_str('AK'),
                                  CardSet.from_str('KKKAA')))
        self.assertEqual(full_houses[2],
                         MadeHand(MadeHand.FULL_HOUSE, MadeHand.NONE, (13, 4), (3,), CardSet.from_str('K4'),
                                  CardSet.from_str('KKK44')))
        self.assertEqual(full_houses[3],
                         MadeHand(MadeHand.FULL_HOUSE, MadeHand.NONE, (13, 3), (4,), CardSet.from_str('K3'),
                                  CardSet.from_str('KKK33')))
        self.assertEqual(full_houses[4],
                         MadeHand(MadeHand.FULL_HOUSE, MadeHand.NONE, (4, 13), (5,), CardSet.from_str('44'),
                                  CardSet.from_str('444KK')))
        self.assertEqual(full_houses[5],
                         MadeHand(MadeHand.FULL_HOUSE, MadeHand.NONE, (3, 13), (6,), CardSet.from_str('33'),
                                  CardSet.from_str('333KK')))

    def test_quads(self):
        board = Board.from_str('AKK34')
        mhe = _MadeHandExplorer(board)
        quads = mhe.quads
        self.assertEqual(len(quads), 1)
        self.assertEqual(quads[0],
                         MadeHand(MadeHand.QUADS, MadeHand.NONE, (13,), (1,), CardSet.from_str('KK'),
                                  CardSet.from_str('KKKK')))


class BoardExplorerTest(unittest.TestCase):

    def test_from_str(self):
        be = BoardExplorer.from_str('Ad2s3h')
        self.assertEqual(be._board, Board.from_str('Ad2s3h'))
        self.assertTrue(be.is_straighted)

    def test_is_paired(self):
        be = BoardExplorer(Board.from_str('AKJ23'))
        self.assertFalse(be.is_paired)
        be = BoardExplorer(Board.from_str('AKJ22'))
        self.assertTrue(be.is_paired)

    def test_is_straighted(self):
        be = BoardExplorer(Board.from_str('AsKs7s8s3s'))
        self.assertFalse(be.is_straighted)
        be = BoardExplorer(Board.from_str('AsKsJs2s2s'))
        self.assertTrue(be.is_straighted)

    def test_made_hands_on_non_paired_non_straighted_rainbow_board(self):
        be = BoardExplorer(Board.from_str('AdKc7h8s3s'))
        made_hands = be.made_hands
        self.assertEqual(made_hands[0], MadeHand(MadeHand.SET, MadeHand.NONE,
                                                 (14,), (1,), CardSet.from_str('AA'), CardSet.from_str('AAA')))
        self.assertEqual(made_hands[4], MadeHand(MadeHand.SET, MadeHand.NONE,
                                                 (3,), (5,), CardSet.from_str('33'), CardSet.from_str('333')))
        self.assertEqual(made_hands[5], MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE,
                                                 (14, 13), (1, 2), CardSet.from_str('AK'), CardSet.from_str('AAKK')))
        self.assertEqual(made_hands[-2], MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR,
                                                  (3, 2), (12, 5, 8), CardSet.from_str('32'), CardSet.from_str('332')))
        self.assertEqual(made_hands[-1], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                  (2,), (13, 4, 1), CardSet.from_str('22'), CardSet.from_str('22')))

    def test_made_hands_on_non_paired_straighted_rainbow_board(self):
        be = BoardExplorer(Board.from_str('KsQdTh7d'))
        made_hands = be.made_hands
        self.assertEqual(made_hands[0], MadeHand(MadeHand.STRAIGHT, MadeHand.NONE,
                                                 (14,), (1,), CardSet.from_str('AJ'), CardSet.from_str('AKQJT')))
        self.assertEqual(made_hands[1], MadeHand(MadeHand.STRAIGHT, MadeHand.NONE,
                                                 (13,), (2,), CardSet.from_str('J9'), CardSet.from_str('KQJT9')))
        self.assertEqual(made_hands[2], MadeHand(MadeHand.SET, MadeHand.NONE,
                                                 (13,), (1,), CardSet.from_str('KK'), CardSet.from_str('KKK')))
        self.assertEqual(made_hands[-1], MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR,
                                                  (2,), (13, 4, 5), CardSet.from_str('22'), CardSet.from_str('22')))

    def test_generalize_hands(self):
        made_hands = [
            MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE, (14, 13), (1, 2), CardSet.from_str('AK'),
                     CardSet.from_str('AAKK')),
            MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (14, 12), (1, 1, 1), CardSet.from_str('AQ'),
                     CardSet.from_str('AAQ')),
            MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (14, 11), (1, 1, 2), CardSet.from_str('AJ'),
                     CardSet.from_str('AAJ')),
            MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (13, 12), (2, 2, 1), CardSet.from_str('KQ'),
                     CardSet.from_str('KKQ')),
            MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (13, 11), (2, 2, 2), CardSet.from_str('KJ'),
                     CardSet.from_str('KKJ')),
            MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR, (12,), (3, 2, 1), CardSet.from_str('QQ'),
                     CardSet.from_str('QQ')),
            MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR, (11,), (4, 2, 2), CardSet.from_str('JJ'),
                     CardSet.from_str('JJ')),
            MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (2, 12), (13, 3, 1), CardSet.from_str('2Q'),
                     CardSet.from_str('22Q')),
            MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (2, 11), (13, 3, 2), CardSet.from_str('2J'),
                     CardSet.from_str('22J')),

        ]
        generic_hands = BoardExplorer._generalize_hands(made_hands, [MadeHand.PAIR])
        self.assertEqual(len(generic_hands), 6)

    def test_find_made_hands(self):
        be = BoardExplorer(Board.from_str('AdKc7h8s3s'))
        hand = be.find_made_hands(MadeHand.SET, MadeHand.NONE, (2,))
        hand_and_better = be.find_made_hands(MadeHand.SET, MadeHand.NONE, (2,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(hand[0], MadeHand(MadeHand.SET, MadeHand.NONE, (13,), (2,), CardSet.from_str('KK'),
                                           CardSet.from_str('KKK')))
        self.assertEqual(len(hand_and_better), 2)

        hand = be.find_made_hands(MadeHand.SET, MadeHand.NONE, (6,))
        hand_and_better = be.find_made_hands(MadeHand.SET, MadeHand.NONE, (6,),
                                             strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(hand[0], MadeHand(MadeHand.SET, MadeHand.NONE, (3,), (5,), CardSet.from_str('33'),
                                           CardSet.from_str('333')))
        self.assertEqual(len(hand_and_better), 5)

        hand = be.find_made_hands(MadeHand.TWO_PAIR, MadeHand.NONE, (3, 4))
        hand_and_better = be.find_made_hands(MadeHand.TWO_PAIR, MadeHand.NONE, (3, 4),
                                             strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(hand[0], MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE, (8, 7), (3, 4), CardSet.from_str('87'),
                                           CardSet.from_str('8877')))
        self.assertEqual(len(hand_and_better), 13)

        hand = be.find_made_hands(MadeHand.PAIR, MadeHand.NONE, (2,))
        self.assertEqual(hand[0], MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (13,), (2, 2), CardSet.from_str('K'),
                                           CardSet.from_str('KK')))

        hand = be.find_made_hands(MadeHand.PAIR, MadeHand.NONE, (3,))
        self.assertEqual(hand[0],
                         MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (12,), (3, 2, 1), CardSet.from_str('QQ'),
                                  CardSet.from_str('QQ')))

        hand = be.find_made_hands(MadeHand.PAIR, MadeHand.BOARD_PAIR, (3, 1))
        self.assertEqual(hand[0],
                         MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (8, 12), (7, 3, 1), CardSet.from_str('8Q'),
                                  CardSet.from_str('88Q')))

        hand = be.find_made_hands(MadeHand.PAIR, MadeHand.BOARD_PAIR, (3,))
        self.assertEqual(hand[0], MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (8,), (7, 3,), CardSet.from_str('8'),
                                           CardSet.from_str('88')))

        hand = be.find_made_hands(MadeHand.PAIR, MadeHand.POCKET_PAIR, (2, 2))
        self.assertEqual(hand[0],
                         MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR, (11,), (4, 2, 2), CardSet.from_str('JJ'),
                                  CardSet.from_str('JJ')))

        hand = be.find_made_hands(MadeHand.PAIR, MadeHand.POCKET_PAIR, (3, 3))
        self.assertEqual(hand[0],
                         MadeHand(MadeHand.PAIR, MadeHand.POCKET_PAIR, (4,), (11, 3, 3), CardSet.from_str('44'),
                                  CardSet.from_str('44')))

        hand = be.find_made_hands(MadeHand.STRAIGHT, MadeHand.NONE, (1,))
        hand_and_better = be.find_made_hands(MadeHand.STRAIGHT, MadeHand.NONE, (1,),
                                             strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(hand), 0)
        self.assertEqual(len(hand_and_better), 0)

        be = BoardExplorer(Board.from_str('AdQdKh8h2d'))
        hand = be.find_made_hands(MadeHand.SET, MadeHand.NONE, (1,))
        hand_and_better = be.find_made_hands(MadeHand.SET, MadeHand.NONE, (1,),
                                             strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(hand[0], MadeHand(MadeHand.SET, MadeHand.NONE, (14,), (1,),
                                           CardSet.from_str('AA'), CardSet.from_str('AAA')))
        self.assertEqual(hand_and_better[-2], MadeHand(MadeHand.STRAIGHT, MadeHand.NONE, (14,), (1,),
                                                       CardSet.from_str('JT'), CardSet.from_str('AKQJT')))
        self.assertEqual(hand_and_better[0], MadeHand(MadeHand.FLUSH, MadeHand.NONE, (13,), (1,),
                                                      CardSet.from_str('Kdd'), CardSet.from_str('AdKdQd2dd')))
        self.assertEqual(hand_and_better[-3], MadeHand(MadeHand.FLUSH, MadeHand.NONE, (4,), (9,),
                                                       CardSet.from_str('4dd'), CardSet.from_str('AdQd4d2dd')))
        hand = be.find_made_hands(MadeHand.FLUSH, MadeHand.NONE, (0,))
        self.assertEqual(hand[0], MadeHand(MadeHand.FLUSH, MadeHand.NONE, (0,), (0,),
                                           CardSet.from_str('dd'), CardSet.from_str('AdQd2ddd')))

        be = BoardExplorer(Board.from_str('AdQd2d2s'))
        hand = be.find_made_hands(MadeHand.TRIPS, MadeHand.NONE, (1, 2))
        self.assertEqual(hand[0], MadeHand(MadeHand.TRIPS, MadeHand.NONE, (2, 11), (1, 2),
                                           CardSet.from_str('2J'), CardSet.from_str('222J')))

        hand = be.find_made_hands(MadeHand.FLUSH, MadeHand.NONE, (2,))
        self.assertEqual(hand[0], MadeHand(MadeHand.FLUSH, MadeHand.NONE, (11,), (2,),
                                           CardSet.from_str('Jdd'), CardSet.from_str('AdQdJd2dd')))

        be = BoardExplorer(Board.from_str('AdQdQsKh'))
        hands = be.find_made_hands(MadeHand.FULL_HOUSE, MadeHand.NONE, (2, 1))
        self.assertEqual(hands[0],
                         MadeHand(MadeHand.FULL_HOUSE, MadeHand.NONE, (13, 12), (2,), CardSet.from_str('KK'),
                                  CardSet.from_str('KKKQQ')))

        hands = be.find_made_hands(MadeHand.TRIPS, MadeHand.NONE, (1, 2))
        self.assertEqual(hands[0], MadeHand(MadeHand.TRIPS, MadeHand.NONE, (12, 10), (1, 2),
                                            CardSet.from_str('QT'), CardSet.from_str('QQQT')))

        be = BoardExplorer(Board.from_str('AdKc7h8s3s'))
        hands = be.find_made_hands(MadeHand.PAIR, MadeHand.BOARD_PAIR, (2,))
        self.assertEqual(hands[0], MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (13,), (2, 2),
                                            CardSet.from_str('K'), CardSet.from_str('KK')))

        be = BoardExplorer(Board.from_str('AdKsKh2s'))
        hands = be.find_made_hands(MadeHand.FULL_HOUSE)
        self.assertEqual(len(hands), 4)
        hands = be.find_made_hands(MadeHand.TRIPS)
        self.assertEqual(len(hands), 10)

    def test_find_made_hands_pocket_pairs(self):
        be = BoardExplorer(Board.from_str('Js2d3h'))
        hands = be.find_made_hands(MadeHand.PAIR, MadeHand.POCKET_PAIR, relative_rank=(1,))
        self.assertEqual(len(hands), 3)

    def test_find_made_hands_two_pairs(self):
        be = BoardExplorer(Board.from_str('Js2d3h'))
        hands = be.find_made_hands(MadeHand.TWO_PAIR, MadeHand.NONE)
        self.assertEqual(len(hands), 3)
        self.assertEqual(hands[0], MadeHand(MadeHand.TWO_PAIR, MadeHand.NONE, (11, 3), (1, 2),
                                            CardSet.from_str('J3'), CardSet.from_str('JJ33')))

    def test_flush_draws(self):
        be = BoardExplorer(Board.from_str('AdKd8s'))
        draws = be.flush_draws
        self.assertEqual(len(draws), 10)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (12,), (1,), CardSet.from_str('Qdd')))
        self.assertEqual(draws[-1],
                         FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (3,), (10,), CardSet.from_str('3dd')))

    def test_is_rainbow(self):
        be = BoardExplorer(Board.from_str('AdKd8s'))
        self.assertFalse(be.is_rainbow)

    def test_has_turned_flush_draw(self):
        be = BoardExplorer(Board.from_str('AdKd8ss'))
        self.assertTrue(be.has_turned_flush_draw)

    def test_find_flush_draws(self):
        be = BoardExplorer(Board.from_str('AdKd8s'))
        draws = be.find_flush_draws(relative_rank=(3,))
        self.assertEqual(len(draws), 1)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (10,), (3,), CardSet.from_str('Tdd')))

        draws = be.find_flush_draws(sub_type=FlushDraw.FLOPPED, relative_rank=(3,))
        self.assertEqual(len(draws), 1)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (10,), (3,), CardSet.from_str('Tdd')))

        draws = be.find_flush_draws(sub_type=FlushDraw.TURNED, relative_rank=(3,))
        self.assertEqual(len(draws), 0)

        draws = be.find_flush_draws(relative_rank=(3,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(draws), 3)

        be = BoardExplorer(Board.from_str('AdKd8s2s'))
        draws = be.find_flush_draws(relative_rank=(1,))
        self.assertEqual(len(draws), 2)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (12,), (1,), CardSet.from_str('Qdd')))
        self.assertEqual(draws[1], FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (14,), (1,), CardSet.from_str('Ass')))

        draws = be.find_flush_draws(sub_type=FlushDraw.TURNED, relative_rank=(1,))
        self.assertEqual(len(draws), 1)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (14,), (1,), CardSet.from_str('Ass')))

        be = BoardExplorer(Board.from_str('AdQd8s2s'))
        draws = be.find_flush_draws(relative_rank=(3,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(draws), 6)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (13,), (1,), CardSet.from_str('Kdd')))
        self.assertEqual(draws[1], FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (14,), (1,), CardSet.from_str('Ass')))
        self.assertEqual(draws[4], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (10,), (3,), CardSet.from_str('Tdd')))
        self.assertEqual(draws[5], FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (12,), (3,), CardSet.from_str('Qss')))

        be = BoardExplorer(Board.from_str('7d2d3s'))
        draws = be.find_flush_draws()
        self.assertEqual(len(draws), 1)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (0,), (0,), CardSet.from_str('dd')))

        be = BoardExplorer(Board.from_str('7d2d3ss'))
        draws = be.find_flush_draws()
        self.assertEqual(len(draws), 2)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (0,), (0,), CardSet.from_str('dd')))

        be = BoardExplorer(Board.from_str('7d2d3ss'))
        draws = be.find_flush_draws(sub_type=FlushDraw.FLOPPED)
        self.assertEqual(len(draws), 1)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (0,), (0,), CardSet.from_str('dd')))

        be = BoardExplorer(Board.from_str('7d2d3ss'))
        draws = be.find_flush_draws(sub_type=FlushDraw.TURNED)
        self.assertEqual(len(draws), 1)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (0,), (0,), CardSet.from_str('ss')))

    def test_straight_draws(self):
        be = BoardExplorer(Board.from_str('AdKc8s'))
        draws = be.straight_draws
        self.assertEqual(len(draws), 4)
        self.assertEqual(draws[0], StraightDraw(StraightDraw.NORMAL, (12, 11, 10), (12, 11, 10), (12, 11, 10)))
        self.assertEqual(draws[1], StraightDraw(StraightDraw.NORMAL, (12, 11), (10,), (10,)))

    def test_find_straight_draws(self):
        be = BoardExplorer(None)
        be._straight_draw_explorer._straight_draws = [
            StraightDraw.from_str('KQJ', 'KQJ', 'KQJ'),
            StraightDraw.from_str('QJ', 'K', 'K'),
            StraightDraw.from_str('KJ', 'Q', 'Q'),
            StraightDraw.from_str('KQ', 'J', 'J'),
        ]

        draws = be.find_straight_draws(StraightDraw.NORMAL, (12,))
        self.assertEqual(len(draws), 0)

        draws = be.find_straight_draws(StraightDraw.NORMAL, (4,))
        self.assertEqual(len(draws), 3)

        draws = be.find_straight_draws(StraightDraw.NORMAL, (2,))
        self.assertEqual(len(draws), 3)

        draws = be.find_straight_draws(StraightDraw.NORMAL, (9,))
        self.assertEqual(len(draws), 1)

        draws = be.find_straight_draws(StraightDraw.NORMAL, (4, 4))
        self.assertEqual(len(draws), 3)

        draws = be.find_straight_draws(StraightDraw.NORMAL, (2,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(draws), 3)  # KQJ is excess
        self.assertEqual(draws[0], StraightDraw(StraightDraw.NORMAL, (13, 12), (11,), (11,)))
        self.assertEqual(draws[1], StraightDraw(StraightDraw.NORMAL, (13, 11), (12,), (12,)))
        self.assertEqual(draws[2], StraightDraw(StraightDraw.NORMAL, (12, 11), (13,), (13,)))

        draws = be.find_straight_draws(StraightDraw.NORMAL, (6,))
        self.assertEqual(len(draws), 1)

        draws = be.find_straight_draws(StraightDraw.NORMAL, (9,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(draws), 1)

        board = Board.from_str('9s8d2h')
        be = BoardExplorer(board)
        draws = be.find_straight_draws(StraightDraw.NORMAL, (12, 12), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(draws), 2)

    def test_get_first_suitable_straight_draw(self):
        be = BoardExplorer(None)
        be._straight_draw_explorer._straight_draws = [
            StraightDraw.from_str('KQJ', 'KQJ', 'KQJ'),
            StraightDraw.from_str('QJ', 'K', 'K'),
            StraightDraw.from_str('KJ', 'Q', 'Q'),
            StraightDraw.from_str('KQ', 'J', 'J'),
        ]

        index = be._get_first_suitable_straight_draw_index(outs=12)
        self.assertEqual(index, -1)
        index = be._get_first_suitable_straight_draw_index(outs=4)
        self.assertEqual(index, 3)
        index = be._get_first_suitable_straight_draw_index(outs=3)
        self.assertEqual(index, 3)
        index = be._get_first_suitable_straight_draw_index(outs=5)
        self.assertEqual(index, 0)
        index = be._get_first_suitable_straight_draw_index(outs=9)
        self.assertEqual(index, 0)

    def test_remove_excess_straight_draws(self):
        draws = {
            (14, 13, 12, 11): StraightDraw.from_str('KQJ', 'KQJ', 'KQJ'),  # excess draw
            (13, 12, 11): StraightDraw.from_str('KQJ', 'KQJ', 'KQJ'),  # excess draw
            (12, 11): StraightDraw.from_str('QJ', 'K', 'K'),
            (13, 11): StraightDraw.from_str('KJ', 'Q', 'Q'),
            (13, 12): StraightDraw.from_str('KQ', 'J', 'J'),
        }
        BoardExplorer._remove_excess_straight_draws(draws)
        self.assertEqual(len(draws), 3)

    def test_flush_blockers(self):
        board = Board.from_str('Ad Kd 5d')
        be = BoardExplorer(board)
        blockers = be.flush_blockers
        self.assertEqual(len(blockers), 10)

        board = Board.from_str('Ad Kd 5s')
        be = BoardExplorer(board)
        blockers = be.flush_blockers
        self.assertEqual(len(blockers), 0)

    def test_find_flush_blockers(self):
        board = Board.from_str('Ad Kd 5d')
        be = BoardExplorer(board)
        blockers = be.find_blockers(type_=Blocker.FLUSH_BLOCKER, relative_rank=(2,))
        self.assertEqual(len(blockers), 1)
        blockers = be.find_blockers(type_=Blocker.FLUSH_BLOCKER, relative_rank=(2,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(blockers), 2)
        blockers = be.find_blockers(type_=Blocker.FLUSH_BLOCKER)
        self.assertEqual(len(blockers), 10)

    def test_flush_draw_blockers(self):
        board = Board.from_str('Ad Kd 5s')
        be = BoardExplorer(board)
        blockers = be.flush_draw_blockers
        self.assertEqual(len(blockers), 11)

        board = Board.from_str('Ad Kd 5d')
        be = BoardExplorer(board)
        blockers = be.flush_draw_blockers
        self.assertEqual(len(blockers), 0)

    def test_find_draw_blockers(self):
        board = Board.from_str('Ad Kd 5s')
        be = BoardExplorer(board)
        blockers = be.find_blockers(Blocker.FLUSH_DRAW_BLOCKER, )
        self.assertEqual(len(blockers), 11)

    def test_backdoor_flush_draws(self):
        board = Board.from_str('As Kd 7h')
        be = BoardExplorer(board)
        backdoors = be.find_flush_draws(type_=FlushDraw.BACKDOOR, relative_rank=(2,))
        self.assertEqual(len(backdoors), 3)
        backdoors = be.find_flush_draws(type_=FlushDraw.BACKDOOR, relative_rank=(2,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(backdoors), 6)

        board = Board.from_str('As Ks 7h')
        be = BoardExplorer(board)
        backdoors = be.find_flush_draws(type_=FlushDraw.BACKDOOR, relative_rank=(2,))
        self.assertEqual(len(backdoors), 1)
        backdoors = be.find_flush_draws(type_=FlushDraw.BACKDOOR, relative_rank=(2,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(backdoors), 2)

    def test_straight_blockers(self):
        board = Board.from_str('Ad Kd Td')
        be = BoardExplorer(board)
        blockers = be.straight_blockers
        self.assertEqual(len(blockers), 4)

        board = Board.from_str('Ad Kd 5s')
        be = BoardExplorer(board)
        blockers = be.straight_blockers
        self.assertEqual(len(blockers), 0)

    def test_find_straight_blockers(self):
        board = Board.from_str('Ah Kd Td 2d 3c')
        be = BoardExplorer(board)
        blockers = be.find_blockers(Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (2,))
        self.assertEqual(len(blockers), 2)
        self.assertEqual(blockers[0],
                         Blocker(Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (5,), (2,), CardSet.from_str('55')))
        blockers = be.find_blockers(Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (2,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(blockers), 4)
        self.assertEqual(blockers[0],
                         Blocker(Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (12,), (1,), CardSet.from_str('QQ')))
        blockers = be.find_blockers(Blocker.STRAIGHT_BLOCKER, Blocker.ONE_CARD, (2,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(blockers), 4)
        self.assertEqual(blockers[0],
                         Blocker(Blocker.STRAIGHT_BLOCKER, Blocker.ONE_CARD, (12,), (1,), CardSet.from_str('Q')))

    def test_straight_draw_blockers(self):
        board = Board.from_str('Ad 7s 3s')
        be = BoardExplorer(board)
        blockers = be.straight_draw_blockers
        self.assertEqual(len(blockers), 8)

    def test_backdoor_straight_draws(self):
        board = Board.from_str('Ad 7s 3s')
        be = BoardExplorer(board)
        backdoors = be.backdoor_straight_draws
        self.assertEqual(len(backdoors), 18)

    def test_find_backdoor_straight_draws(self):
        board = Board.from_str('Ad 7s 3s')
        be = BoardExplorer(board)
        backdoors = be.backdoor_straight_draws
        self.assertEqual(len(backdoors), 18)
        finding = be.find_straight_draws(StraightDraw.BACKDOOR, (16, 0))
        self.assertEqual(len(finding), 3)
        finding = be.find_straight_draws(StraightDraw.BACKDOOR, (12, 0))
        self.assertEqual(len(finding), 4)
        finding = be.find_straight_draws(StraightDraw.BACKDOOR, (12, 0), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(finding), 7)

    def test_find(self):
        be = BoardExplorer(Board.from_str('Ad 7s 3s'))
        hands = be.find(BoardExplorer.MADE_HAND, MadeHand.SET, relative_rank=(2,))
        self.assertEqual(hands[0], MadeHand(MadeHand.SET, MadeHand.NONE, (7,), (2,),
                                            CardSet.from_str('77'), CardSet.from_str('777')))
        hands = be.find(BoardExplorer.FLUSH_DRAW, FlushDraw.NORMAL, FlushDraw.NONE, relative_rank=(2,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(hands[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (14,), (1,), CardSet.from_str('Ass')))
        self.assertEqual(hands[1], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (13,), (2,), CardSet.from_str('Kss')))
        hands = be.find(BoardExplorer.STRAIGHT_DRAW, StraightDraw.NORMAL, relative_rank=(9, 9))
        self.assertEqual(hands[0], StraightDraw(StraightDraw.NORMAL, (6, 5, 4), (6, 5, 4, 2), (6, 5, 4, 2)))
        hands = be.find(BoardExplorer.BLOCKER, Blocker.STRAIGHT_DRAW_BLOCKER, Blocker.ONE_CARD,
                        relative_rank=(3,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(hands), 3)
        self.assertEqual(hands[0], Blocker(Blocker.STRAIGHT_DRAW_BLOCKER, Blocker.ONE_CARD,
                                           (6,), (1,), CardSet.from_str('6')))

    def test_easy_range2hands(self):
        be = BoardExplorer(Board.from_str('AdKc7h8s3s'))
        hand = be._easy_range2hands(BoardExplorer.MADE_HAND, 'TS')
        self.assertEqual(hand[0], MadeHand(MadeHand.SET, MadeHand.NONE, (14,), (1,), CardSet.from_str('AA'),
                                           CardSet.from_str('AAA')))

        hands = be._easy_range2hands(BoardExplorer.MADE_HAND, 'S', (4,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(hands[0], MadeHand(MadeHand.SET, MadeHand.NONE, (14,), (1,), CardSet.from_str('AA'),
                                            CardSet.from_str('AAA')))
        self.assertEqual(hands[-1], MadeHand(MadeHand.SET, MadeHand.NONE, (7,), (4,), CardSet.from_str('77'),
                                             CardSet.from_str('777')))

        be = BoardExplorer(Board.from_str('AdKc2d'))
        hands = be._easy_range2hands(BoardExplorer.STRAIGHT_DRAW, 'SD', (9,))
        self.assertEqual(hands[0], StraightDraw(StraightDraw.NORMAL, (12, 11, 10), (12, 11, 10), (12, 11, 10)))
        self.assertEqual(hands[1], StraightDraw(StraightDraw.NORMAL, (5, 4, 3), (5, 4, 3), (5, 4, 3)))

        be = BoardExplorer(Board.from_str('AdQd8s2s'))
        draws = be._easy_range2hands(BoardExplorer.FLUSH_DRAW, 'FD', (3,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(draws), 6)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (13,), (1,), CardSet.from_str('Kdd')))
        self.assertEqual(draws[1], FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (14,), (1,), CardSet.from_str('Ass')))
        self.assertEqual(draws[4], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (10,), (3,), CardSet.from_str('Tdd')))
        self.assertEqual(draws[5], FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (12,), (3,), CardSet.from_str('Qss')))

        draws = be._easy_range2hands(BoardExplorer.FLUSH_DRAW, 'FDF', (3,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(draws), 3)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (13,), (1,), CardSet.from_str('Kdd')))

        draws = be._easy_range2hands(BoardExplorer.FLUSH_DRAW, 'FDT', (3,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(draws), 3)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (14,), (1,), CardSet.from_str('Ass')))

        draws = be._easy_range2hands(BoardExplorer.FLUSH_DRAW, 'NFD', strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(draws), 2)
        self.assertEqual(draws[1], FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (14,), (1,), CardSet.from_str('Ass')))

        draws = be._easy_range2hands(BoardExplorer.FLUSH_DRAW, 'FD')
        self.assertEqual(len(draws), 2)
        self.assertEqual(draws[0], FlushDraw(FlushDraw.NORMAL, FlushDraw.FLOPPED, (0,), (0,), CardSet.from_str('dd')))
        self.assertEqual(draws[1], FlushDraw(FlushDraw.NORMAL, FlushDraw.TURNED, (0,), (0,), CardSet.from_str('ss')))

        board = Board.from_str('AdQdQsKh')
        be = BoardExplorer(board)
        hands = be._easy_range2hands(BoardExplorer.MADE_HAND, 'Q', (1,))
        self.assertEqual(hands[0], MadeHand(MadeHand.QUADS, MadeHand.NONE, (12,), (1,), CardSet.from_str('QQ'),
                                            CardSet.from_str('QQQQ')))
        hands = be._easy_range2hands(BoardExplorer.MADE_HAND, 'FH', (1,))
        self.assertEqual(hands[0],
                         MadeHand(MadeHand.FULL_HOUSE, MadeHand.NONE, (14, 12), (1,), CardSet.from_str('AA'),
                                  CardSet.from_str('AAAQQ')))
        hands = be._easy_range2hands(BoardExplorer.MADE_HAND, 'FH', (2,))
        self.assertEqual(hands[0],
                         MadeHand(MadeHand.FULL_HOUSE, MadeHand.NONE, (13, 12), (2,), CardSet.from_str('KK'),
                                  CardSet.from_str('KKKQQ')))
        hands = be._easy_range2hands(BoardExplorer.MADE_HAND, 'Tr', (1, 3))
        self.assertEqual(hands[0], MadeHand(MadeHand.TRIPS, MadeHand.NONE, (12, 9), (1, 3), CardSet.from_str('Q9'),
                                            CardSet.from_str('QQQ9')))

        be = BoardExplorer(Board.from_str('AdKc7h8s3s'))
        hands = be._easy_range2hands(BoardExplorer.MADE_HAND, 'PB', (2,))
        self.assertEqual(hands[0], MadeHand(MadeHand.PAIR, MadeHand.BOARD_PAIR, (13,), (2, 2),
                                            CardSet.from_str('K'), CardSet.from_str('KK')))

        # Backdoors
        be = BoardExplorer(Board.from_str('Ad9h5s'))
        hands = be._easy_range2hands(BoardExplorer.FLUSH_DRAW, 'BFD', (2,))
        self.assertEqual(len(hands), 3)
        self.assertEqual(hands[0],
                         FlushDraw(FlushDraw.BACKDOOR, FlushDraw.FLOPPED, (13,), (2,), CardSet.from_str('Kss')))
        hands = be._easy_range2hands(BoardExplorer.FLUSH_DRAW, 'NBFD')
        self.assertEqual(len(hands), 3)
        self.assertEqual(hands[0],
                         FlushDraw(FlushDraw.BACKDOOR, FlushDraw.FLOPPED, (14,), (1,), CardSet.from_str('Ass')))
        hands = be._easy_range2hands(BoardExplorer.STRAIGHT_DRAW, 'BSD', (12,), strictness=BoardExplorer.THAT_AND_BETTER)
        self.assertEqual(len(hands), 9)
        self.assertEqual(hands[0], StraightDraw(StraightDraw.BACKDOOR, (11, 10), (13, 12, 8, 7), ()))

        # Blockers
        be = BoardExplorer(Board.from_str('QdKdTd'))
        hands = be._easy_range2hands(BoardExplorer.BLOCKER, 'FB', (2,))
        self.assertEqual(len(hands), 1)
        self.assertEqual(hands[0], Blocker(Blocker.FLUSH_BLOCKER, Blocker.NONE, (11,), (2,), CardSet.from_str('Jd')))
        hands = be._easy_range2hands(BoardExplorer.BLOCKER, 'NFB')
        self.assertEqual(len(hands), 1)
        self.assertEqual(hands[0], Blocker(Blocker.FLUSH_BLOCKER, Blocker.NONE, (14,), (1,), CardSet.from_str('Ad')))
        hands = be._easy_range2hands(BoardExplorer.BLOCKER, 'SB', (2,))
        self.assertEqual(len(hands), 1)
        self.assertEqual(hands[0],
                         Blocker(Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (9,), (2,), CardSet.from_str('99')))
        hands = be._easy_range2hands(BoardExplorer.BLOCKER, 'NSB')
        self.assertEqual(len(hands), 2)
        self.assertEqual(hands[0],
                         Blocker(Blocker.STRAIGHT_BLOCKER, Blocker.TWO_CARD, (14,), (1,), CardSet.from_str('AA')))

        be = BoardExplorer(Board.from_str('Qd5sTd'))
        hands = be._easy_range2hands(BoardExplorer.BLOCKER, 'FDB', (2,))
        self.assertEqual(len(hands), 1)
        self.assertEqual(hands[0],
                         Blocker(Blocker.FLUSH_DRAW_BLOCKER, Blocker.FLOPPED, (13,), (2,), CardSet.from_str('Kd')))

        be = BoardExplorer(Board.from_str('Qd5sTd7s'))
        hands = be._easy_range2hands(BoardExplorer.BLOCKER, 'FDB', (2,))
        self.assertEqual(len(hands), 2)
        self.assertEqual(hands[0],
                         Blocker(Blocker.FLUSH_DRAW_BLOCKER, Blocker.FLOPPED, (13,), (2,), CardSet.from_str('Kd')))
        self.assertEqual(hands[1],
                         Blocker(Blocker.FLUSH_DRAW_BLOCKER, Blocker.TURNED, (13,), (2,), CardSet.from_str('Ks')))

        be = BoardExplorer(Board.from_str('AdKsKh2s'))
        hands = be._easy_range2hands(BoardExplorer.MADE_HAND, 'Tr')
        self.assertEqual(len(hands), 1)
        self.assertEqual(hands[0], MadeHand(MadeHand.TRIPS, MadeHand.NONE, (13,), (1,),
                                            CardSet.from_str('K'), CardSet.from_str('KKK')))

    def test_hands2ppt(self):
        hand = MadeHand(MadeHand.SET, MadeHand.NONE, (13,), (2,), CardSet.from_str('KK'), CardSet.from_str('KKK'))
        self.assertEqual(BoardExplorer._hands2ppt([hand]), 'KK')

        hands = [
            MadeHand(MadeHand.SET, MadeHand.NONE, (14,), (1,), CardSet.from_str('AA'), CardSet.from_str('AAA')),
            MadeHand(MadeHand.SET, MadeHand.NONE, (13,), (2,), CardSet.from_str('KK'), CardSet.from_str('KKK')),
        ]
        self.assertEqual(BoardExplorer._hands2ppt(hands), 'AA,KK')

    def test_ppt(self):
        be = BoardExplorer(Board.from_str('AdKc7h8s3s'))
        self.assertEqual(be.ppt('S3+'), '(AA,KK,88)')
        self.assertEqual(be.ppt('S3'), '88')
        self.assertEqual(be.ppt('TS'), 'AA')
        self.assertEqual(be.ppt('MS'), 'KK')
        self.assertEqual(be.ppt('BS'), '33')
        self.assertEqual(be.ppt('T2P'), 'AK')
        self.assertEqual(be.ppt('2P3_4'), '87')
        self.assertEqual(be.ppt('2P3_5'), '83')
        self.assertEqual(be.ppt('2P3_6'), '83')
        self.assertEqual(be.ppt('2P'), '(AK,A8,A7,A3,K8,K7,K3,87,83,73)')
        self.assertEqual(be.ppt('P2'), 'K')
        self.assertEqual(be.ppt('P3'), 'QQ')
        self.assertEqual(be.ppt('PB1'), 'A')
        self.assertEqual(be.ppt('PB2'), 'K')
        self.assertEqual(be.ppt('MP'), 'K')
        self.assertEqual(be.ppt('MP1'), 'KQ')
        self.assertEqual(be.ppt('MP1K'), 'KQ')
        self.assertEqual(be.ppt('PB3'), '8')
        self.assertEqual(be.ppt('PP2_2'), 'JJ')
        self.assertEqual(be.ppt('PP2'), '(QQ,JJ,TT,99)')
        self.assertEqual(be.ppt('PP1_2'), '73')

        be = BoardExplorer(Board.from_str('Js4d2s'))
        self.assertEqual(be.ppt('OP'), '(AA,KK,QQ)')

        be = BoardExplorer(Board.from_str('AdKs2d4h'))
        self.assertEqual(be.ppt('S3+'), '(53,AA,KK,44)')
        self.assertEqual(be.ppt('Str1'), '53')

        be = BoardExplorer(Board.from_str('AdKs2d4hTs'))
        self.assertEqual(be.ppt('S3+'), '(QJ,53,AA,KK,TT)')
        self.assertEqual(be.ppt('Str2'), '53')

        be = BoardExplorer(Board.from_str('AdKs2d'))
        self.assertEqual(be.ppt('SD9'), '(QJT,543)')
        self.assertEqual(be.ppt('SD9+'), '(QJT,543)')

        be = BoardExplorer(Board.from_str('AdKs2d7d8d'))
        self.assertEqual(be.ppt('TS+'), '(Kdd,Qdd,Jdd,Tdd,9dd,6dd,5dd,4dd,AA)')

        be = BoardExplorer(Board.from_str('AdKd2d'))
        self.assertEqual(be.ppt('F2'), 'Jdd')
        self.assertEqual(be.ppt('F2+'), '(Qdd,Jdd)')
        self.assertEqual(be.ppt('F'), 'dd')

        be = BoardExplorer(Board.from_str('Ad2d4s'))
        self.assertEqual(be.ppt('FD1'), 'Kdd')
        self.assertEqual(be.ppt('FD2'), 'Qdd')
        self.assertEqual(be.ppt('FD3+'), '(Kdd,Qdd,Jdd)')
        self.assertEqual(be.ppt('FD'), 'dd')
        self.assertEqual(be.ppt('TB2P+'), '(53,AA,44,22,A4,A2)')
        self.assertEqual(be.ppt('TB2P+:(FD)'), '(53,AA,44,22,A4,A2):(dd)')

        be = BoardExplorer(Board.from_str('AsJcJh2s'))
        self.assertEqual(be.ppt('Q1'), 'JJ')
        self.assertEqual(be.ppt('FH3+'), '(JJ,AA,JA,J2)')
        self.assertEqual(be.ppt('FH'), '(AA,JA,J2,22)')
        self.assertEqual(be.ppt('Tr1_2+'), '(JJ,AA,JA,J2,22,JK,JQ)')
        self.assertEqual(be.ppt('Tr'), 'J')
        self.assertEqual(be.ppt('Tr+'), '(JJ,AA,JA,J2,22,J)')

        # Backdoors
        be = BoardExplorer(Board.from_str('As2h3s'))
        self.assertEqual(be.ppt('NBFD'), 'Ahh')

        # Blockers
        be = BoardExplorer(Board.from_str('As2s3s'))
        self.assertEqual(be.ppt('NFB'), 'Ks')

        be = BoardExplorer.from_str('Js 9h 4h')
        self.assertEqual(be.ppt('SDB1'), 'KK')
        self.assertEqual(be.ppt('SDBO1'), 'K')

        # '*'
        self.assertEqual(be.ppt('*'), '*')

    def test_ppt_parenthesis(self):
        be = BoardExplorer(Board.from_str('As 2d Ks'))
        ppt = be.ppt('(T2P+,NFD,SD9+)')
        self.assertEqual(ppt, '((AA,KK,22,AK),Qss,(QJT,543))')


class EasyRangeTest(unittest.TestCase):

    def test_check_range(self):
        right_range = 'MS+,TP+'
        wrong_range = 'MS+,YB'
        self.assertTrue(check_range(right_range))
        with self.assertRaises(EasyRangeValueError) as raised:
           check_range(wrong_range)
        self.assertEqual(raised.exception.column, 5)
        self.assertEqual(raised.exception.easy_range, 'MS+,YB')


class CombinationsTest(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
