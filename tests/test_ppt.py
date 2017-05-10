import unittest
import os

from ploev.ppt import OddsOracle, Pql, PqlResult


class OddsOracleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        oo = OddsOracle()
        oo.trials = 100000
        oo.seconds = 1
        cls.oo = oo

    def test_equity(self):
        board = 'Ad Ks 3s'
        villain = 'AA'
        hero = 'Qs Ts Jd 2d'
        equities = self.oo.equity(board=board, hands=[hero, villain])
        self.assertAlmostEqual(equities[0], 0.41, delta=0.02)
        self.assertAlmostEqual(equities[1], 0.59, delta=0.02)

    def test_pql(self):
        # noinspection SqlNoDataSourceInspection,SqlDialectInspection
        pql = """
            select count(inRange(PLAYER_1,'AA')),
              count(inRange(PLAYER_1,'AK,KK'))
            from game='omahahi', syntax='Generic',
                 board='Ad Ks 3s',
                 PLAYER_1='10%',
                 PLAYER_2='Qs Ts Jd 2d'
        """
        result = self.oo.pql(pql)
        self.assertAlmostEqual(result.results_list[0][PqlResult.PERCENTAGE], 0.24, delta=0.02)

    def test_pql_error(self):
        pql = "la-la"
        self.assertRaises(ValueError, self.oo.pql, pql)


class PqlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        oo = OddsOracle()
        cls.pql = Pql(oo)

    def test_equity(self):
        board = 'Ad Ks 3s'
        villain = 'AA'
        hero = 'Qs Ts Jd 2d'
        equities = self.pql.equity(board=board, players=[hero, villain])
        self.assertAlmostEqual(equities[0], 0.41, delta=0.02)
        self.assertAlmostEqual(equities[1], 0.59, delta=0.02)

    def test_pql_hero_equity(self):
        board = 'Ad Ks 3s'
        villains = ['AA']
        hero = 'Qs Ts Jd 2d'
        equity = self.pql.hero_equity(hero, villains, board)
        self.assertAlmostEqual(equity, 0.41, delta=0.02)

    def test_count_in_range(self):
        board = 'Ad Ks 3s'
        dead = 'As Ah 2s 2h'
        main_range = '10%'
        sub_ranges = ['KK,33', 'QJT:ss']
        rd = self.pql.count_in_range(main_range, sub_ranges, board, dead)
        self.assertAlmostEqual(rd[0], 0.27, delta=0.02)
        self.assertAlmostEqual(rd[1], 0.02, delta=0.02)


class PqlResultTest(unittest.TestCase):
    def test_count_result(self):
        result = """
        IN_RANGE = 8.8167% (2645)
        COUNT 4 = 61.0800% (18324)
        30000 trials
        """
        pql_result = PqlResult(result)
        self.assertEqual(pql_result.trials, 30000)
        self.assertEqual(pql_result.results_dict['IN_RANGE'],
                         {'name': 'IN_RANGE', 'percentage': 0.088, 'counts': 2645})
        self.assertEqual(pql_result.results_dict['COUNT 4'],
                         {'name': 'COUNT 4', 'percentage': 0.611, 'counts': 18324})
        self.assertEqual(pql_result.results_list[0],
                         {'name': 'IN_RANGE', 'percentage': 0.088, 'counts': 2645})
        self.assertEqual(pql_result.results_list[1],
                         {'name': 'COUNT 4', 'percentage': 0.611, 'counts': 18324})
        self.assertEqual(pql_result.results_dict['IN_RANGE'],
                         {'name': 'IN_RANGE', 'percentage': 0.088, 'counts': 2645})

    def test_avg_result(self):
        result = """
        ACES_EQUITY = 0.8471333333333333
        30000 trials
        """
        pql_result = PqlResult(result)
        self.assertEqual(pql_result.trials, 30000)
        self.assertEqual(pql_result.results_dict['ACES_EQUITY'],
                         {'name': 'ACES_EQUITY', 'percentage': 0.847, })

    def test_histogram_fraction_result(self):
        result = """
        EQUITY_FRACTION = [0:32.2367% (9671)],[1/4:0.0133% (4)],[1/2:38.0700% (11421)],[3/4:0.0033% (1)],[1:29.6767% (8903)]
        30000 trials
        """
        pql_result = PqlResult(result)
        self.assertEqual(pql_result.trials, 30000)
        self.assertEqual(pql_result.results_dict['EQUITY_FRACTION']['name'], 'EQUITY_FRACTION')
        self.assertEqual(len(pql_result.results_dict['EQUITY_FRACTION'][PqlResult.HISTOGRAM]), 5)
        self.assertEqual(pql_result.results_dict['EQUITY_FRACTION'][PqlResult.HISTOGRAM]['1/2'][PqlResult.COUNTS],
                         11421)
        self.assertEqual(pql_result.results_dict['EQUITY_FRACTION'][PqlResult.HISTOGRAM]['1/2'][PqlResult.PERCENTAGE],
                         0.381)

    def test_histogram_percent_result(self):
        result = """
        FLOP = [0:1.1200% (336)],[1:0.5233% (157)],[2:0.5333% (160)],[3:0.3933% (118)],[4:0.4000% (120)],[5:0.4133% (124)],[6:0.4467% (134)],[7:0.5700% (171)],[8:0.4967% (149)],[9:0.6333% (190)],[10:0.6233% (187)],[11:0.6233% (187)],[12:0.7333% (220)],[13:0.8133% (244)],[14:1.0133% (304)],[15:0.7333% (220)],[16:0.7633% (229)],[17:0.8900% (267)],[18:0.8400% (252)],[19:0.9667% (290)],[20:0.7733% (232)],[21:0.7800% (234)],[22:0.7833% (235)],[23:0.7800% (234)],[24:1.0033% (301)],[25:0.8200% (246)],[26:1.0200% (306)],[27:1.0633% (319)],[28:1.0367% (311)],[29:1.3300% (399)],[30:1.3200% (396)],[31:1.3000% (390)],[32:1.2400% (372)],[33:1.1933% (358)],[34:1.3400% (402)],[35:1.2633% (379)],[36:1.3367% (401)],[37:1.2067% (362)],[38:1.1867% (356)],[39:1.1633% (349)],[40:1.1667% (350)],[41:1.2300% (369)],[42:1.2167% (365)],[43:1.2267% (368)],[44:1.3167% (395)],[45:1.1600% (348)],[46:1.2733% (382)],[47:1.2333% (370)],[48:1.3633% (409)],[49:1.3100% (393)],[50:1.1267% (338)],[51:1.2300% (369)],[52:1.1800% (354)],[53:1.1700% (351)],[54:1.1400% (342)],[55:1.2967% (389)],[56:1.1267% (338)],[57:1.0600% (318)],[58:1.1200% (336)],[59:1.2567% (377)],[60:0.9933% (298)],[61:1.0233% (307)],[62:0.9267% (278)],[63:0.9467% (284)],[64:0.9733% (292)],[65:0.8000% (240)],[66:0.8667% (260)],[67:0.8667% (260)],[68:0.9800% (294)],[69:1.1567% (347)],[70:0.9700% (291)],[71:1.0300% (309)],[72:1.0800% (324)],[73:1.2167% (365)],[74:1.2433% (373)],[75:1.2000% (360)],[76:1.1367% (341)],[77:1.1100% (333)],[78:1.1167% (335)],[79:1.2567% (377)],[80:1.2467% (374)],[81:1.1333% (340)],[82:1.1167% (335)],[83:1.0500% (315)],[84:1.1933% (358)],[85:0.9533% (286)],[86:1.0433% (313)],[87:1.0333% (310)],[88:1.0133% (304)],[89:0.9600% (288)],[90:0.9267% (278)],[91:0.8433% (253)],[92:1.0100% (303)],[93:0.7300% (219)],[94:0.7467% (224)],[95:0.7800% (234)],[96:0.8400% (252)],[97:0.9300% (279)],[98:0.5367% (161)],[99:1.3467% (404)]
        TURN = [0:9.5067% (2852)],[1:0.0100% (3)],[2:0.2967% (89)],[3:0.2300% (69)],[4:1.3967% (419)],[5:0.0000% (0)],[6:0.0033% (1)],[7:2.0633% (619)],[8:0.0367% (11)],[9:3.4367% (1031)],[10:0.0000% (0)],[11:0.0733% (22)],[12:0.6533% (196)],[13:0.2133% (64)],[14:2.0733% (622)],[15:0.0000% (0)],[16:0.0833% (25)],[17:1.6900% (507)],[18:0.2433% (73)],[19:2.1167% (635)],[20:0.0000% (0)],[21:0.0767% (23)],[22:3.7767% (1133)],[23:0.2033% (61)],[24:2.5100% (753)],[25:0.0000% (0)],[26:0.1367% (41)],[27:2.4033% (721)],[28:0.1733% (52)],[29:3.4467% (1034)],[30:0.0000% (0)],[31:0.1633% (49)],[32:2.6600% (798)],[33:0.0933% (28)],[34:1.7667% (530)],[35:0.0000% (0)],[36:0.0733% (22)],[37:2.1033% (631)],[38:0.0867% (26)],[39:1.5633% (469)],[40:0.0000% (0)],[41:0.0967% (29)],[42:1.3367% (401)],[43:0.0400% (12)],[44:1.4500% (435)],[45:0.0000% (0)],[46:0.1067% (32)],[47:0.9267% (278)],[48:0.0400% (12)],[49:0.9067% (272)],[50:0.0000% (0)],[51:0.0433% (13)],[52:0.6800% (204)],[53:0.0833% (25)],[54:0.0000% (0)],[55:0.7633% (229)],[56:0.0600% (18)],[57:0.6300% (189)],[58:0.0600% (18)],[59:0.8500% (255)],[60:0.0000% (0)],[61:0.1100% (33)],[62:1.1467% (344)],[63:0.0900% (27)],[64:0.9500% (285)],[65:0.0000% (0)],[66:0.0767% (23)],[67:1.3133% (394)],[68:0.1033% (31)],[69:1.9333% (580)],[70:0.0000% (0)],[71:0.1367% (41)],[72:1.7867% (536)],[73:0.1433% (43)],[74:1.8233% (547)],[75:0.0000% (0)],[76:0.1033% (31)],[77:2.7433% (823)],[78:0.2400% (72)],[79:3.0500% (915)],[80:0.0000% (0)],[81:0.1700% (51)],[82:2.9800% (894)],[83:0.2967% (89)],[84:2.3200% (696)],[85:0.0000% (0)],[86:0.3400% (102)],[87:2.4133% (724)],[88:0.2367% (71)],[89:3.7833% (1135)],[90:0.0000% (0)],[91:0.3367% (101)],[92:2.6833% (805)],[93:0.0600% (18)],[94:2.4867% (746)],[95:0.0000% (0)],[96:0.8533% (256)],[97:0.6567% (197)],[98:0.0100% (3)],[99:11.1867% (3356)]
        30000 trials
        """
        pql_result = PqlResult(result)
        self.assertEqual(pql_result.trials, 30000)
        self.assertEqual(pql_result.results_dict['FLOP'][PqlResult.NAME], 'FLOP')
        self.assertEqual(len(pql_result.results_dict['FLOP'][PqlResult.HISTOGRAM]), 100)
        self.assertEqual(pql_result.results_dict['FLOP'][PqlResult.HISTOGRAM]['0'][PqlResult.COUNTS],
                         336)
        self.assertEqual(pql_result.results_dict['FLOP'][PqlResult.HISTOGRAM]['99'][PqlResult.COUNTS],
                         404)
        self.assertEqual(pql_result.results_dict['FLOP'][PqlResult.HISTOGRAM]['0'][PqlResult.PERCENTAGE],
                         0.011)
        self.assertEqual(pql_result.results_dict['FLOP'][PqlResult.HISTOGRAM]['99'][PqlResult.PERCENTAGE],
                         0.013)
