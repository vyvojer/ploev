import unittest
from ploev.cards import CardSet, Board, Deck, Card, card_from_str, card_to_str


class CardTest(unittest.TestCase):

    def test_card_from_str(self):
        self.assertEqual(card_from_str('As'), Card(14, 1))
        self.assertEqual(card_from_str('A'), Card(14, 0))
        self.assertEqual(card_from_str('s'), Card(0, 1))
        self.assertEqual(card_from_str('*'), Card(0, 0))

    def test_card_to_str(self):
        self.assertEqual(card_to_str(Card(14, 1)), 'As')
        self.assertEqual(card_to_str(Card(14, 0)), 'A')
        self.assertEqual(card_to_str(Card(0, 1)), 's')
        self.assertEqual(card_to_str(Card(0, 0)), '*')


class DeckTest(unittest.TestCase):

    def test_cards(self):
        deck = Deck()
        self.assertEqual(len(deck), 52)
        self.assertEqual(max(deck.cards), Card(14, 4))

    def test_create_deck_with_dead_cards(self):
        dead_cards = [Card(14, 4), Card(2, 1)]
        deck = Deck(dead_cards)
        self.assertEqual(len(deck), 50)
        self.assertEqual(max(deck.cards), Card(14, 3))
        self.assertEqual(min(deck.cards), Card(2, 2))

    def test_remove_cards(self):
        deck = Deck()
        deck.remove_cards([Card(14, 1), Card(14, 2), Card(14, 3)])
        self.assertEqual(len(deck), 49)


class CardSetTest(unittest.TestCase):

    def test_create_new_card_set(self):
        card_set = CardSet([Card(2, 2), Card(2, 1)])
        self.assertEqual(Card(2, 2), card_set[0])
        self.assertEqual(Card(2, 1), card_set[1])

    def test_create_new_card_set_from_string(self):
        card_set = CardSet.from_str('Ah2d3s')
        self.assertEqual(Card(14, 2), card_set[0])
        self.assertEqual(Card(2, 3), card_set[1])
        self.assertEqual(Card(3, 1), card_set[2])

        card_set = CardSet.from_str('Ah 2d 3s')
        self.assertEqual(Card(14, 2), card_set[0])
        self.assertEqual(Card(2, 3), card_set[1])
        self.assertEqual(Card(3, 1), card_set[2])

        card_set = CardSet.from_str('Ah33s')
        self.assertEqual(Card(14, 2), card_set[0])
        self.assertEqual(card_from_str('3'), card_set[1])
        self.assertEqual(card_from_str('3s'), card_set[2])

        card_set = CardSet.from_str('Ah*c33s*AAsssddd2hh')
        self.assertEqual(card_from_str('Ah'), card_set[0])
        self.assertEqual(card_from_str('*'), card_set[1])
        self.assertEqual(card_from_str('c'), card_set[2])
        self.assertEqual(card_from_str('3'), card_set[3])
        self.assertEqual(card_from_str('3s'), card_set[4])
        self.assertEqual(card_from_str('*'), card_set[5])
        self.assertEqual(card_from_str('A'), card_set[6])
        self.assertEqual(card_from_str('As'), card_set[7])
        self.assertEqual(card_from_str('s'), card_set[8])

    def test_slicing(self):
        card_set = CardSet.from_str('AdKd7s2s')
        self.assertEqual(card_set[0], Card(14, 3))
        self.assertEqual(card_set[1:], CardSet.from_str('Kd7s2s'))
        self.assertRaises(TypeError, card_set.__getitem__, 'a')

    def test_index(self):
        card_set = CardSet.from_str('AdKs2h')
        self.assertEqual(card_set.index(Card(14, 3)), 0)
        self.assertEqual(card_set.index(Card(2, 2)), 2)

    def test_set_item(self):
        card_set = CardSet.from_str('Add')
        card_set[0] = Card(0, 3)
        self.assertEqual(card_set, CardSet.from_str('dd'))

    def test_pop(self):
        card_set = CardSet.from_str('AAK')
        card_set.pop()
        self.assertEqual(card_set,CardSet.from_str('AA'))

        card_set = CardSet.from_str('AAK')
        card_set.pop(1)
        self.assertEqual(card_set,CardSet.from_str('AK'))

    def test_ranks(self):
        card_set = CardSet.from_str('As2d3sQdTd')
        ranks = card_set.ranks
        self.assertEqual(14, ranks[0])
        self.assertEqual(2, ranks[1])
        self.assertEqual(3, ranks[2])
        self.assertEqual(12, ranks[3])
        self.assertEqual(10, ranks[4])

    def test_unique_ranks(self):
        card_set = CardSet.from_str('AsAd2d')
        unique_ranks = card_set.unique_ranks
        self.assertEqual(14, unique_ranks[0])
        self.assertEqual(2, unique_ranks[1])
        self.assertEqual(2, len(unique_ranks))

    def test_remaining_ranks(self):
        card_set = CardSet.from_str('AKQJT98')
        remaining_ranks = card_set.remaining_ranks
        self.assertEqual(remaining_ranks, [2, 3, 4, 5, 6, 7])

    def test_get_suits(self):
        card_set = CardSet.from_str('As2d3sQdTd')
        suits = card_set.suits
        self.assertEqual(1, suits[0])
        self.assertEqual(3, suits[1])
        self.assertEqual(1, suits[2])
        self.assertEqual(3, suits[3])
        self.assertEqual(3, suits[4])

    def test_get_unique_suits(self):
        card_set = CardSet.from_str('AsAd2d')
        unique_suits = card_set.unique_suits
        self.assertEqual(3, unique_suits[0])
        self.assertEqual(1, unique_suits[1])
        self.assertEqual(2, len(unique_suits))

    def test_get_combinations(self):
        card_set = CardSet.from_str('AsAdAhAc')
        combinations = card_set.get_combinations(2)
        self.assertEqual(6, len(combinations))

    def test_get_rank_combinations(self):
        card_set = CardSet.from_str('AsAdAhAcKhTd')
        rank_combinations = card_set.get_rank_combinations(2)
        self.assertEqual(3, len(rank_combinations))
        self.assertIn([14, 10], rank_combinations)

    def test_add(self):
        cs1 = CardSet.from_str('Ad 2d 3d')
        cs2 = CardSet.from_str('4d 5d')
        cs_sum = cs1 + cs2
        self.assertEqual(5, len(cs_sum))

    def test_from_ranks(self):
        ranks = [14, 3, 2]
        card_set = CardSet.from_ranks(ranks)
        self.assertEqual(card_from_str('A'), card_set[0])

    def test_from_card_sets(self):
        kings = CardSet([card_from_str('Ks'), card_from_str('Kd')])
        jacks = CardSet([card_from_str('Js'), card_from_str('Jd')])
        kings_and_jacks = CardSet.from_card_sets(kings, jacks)
        self.assertEqual(len(kings_and_jacks.cards), 4)

    def test_equals(self):
        cs1 = CardSet.from_str('As 2s 3s')
        cs2 = CardSet.from_str('As 2s 3s')
        cs3 = CardSet.from_str('As 3s 2s')
        self.assertEqual(cs1, cs2)
        self.assertEqual(cs1, cs3)

    def test_get_rank_jokers(self):
        card_set_without_rank_jokers = CardSet.from_str('As 2s 3s')
        card_set_with_1_rank_joker = CardSet.from_str('As 2s 3')
        card_set_with_2_rank_jokers = CardSet.from_str('As 2 3')
        card_set_with_3_rank_jokers = CardSet.from_str('A 2 3')
        self.assertEqual(card_set_without_rank_jokers.get_rank_jokers(), [])
        self.assertEqual(card_set_with_1_rank_joker.get_rank_jokers(), [3])
        self.assertEqual(card_set_with_2_rank_jokers.get_rank_jokers(), [2, 3])
        self.assertEqual(card_set_with_3_rank_jokers.get_rank_jokers(), [14, 2, 3])

    def test_get_particular_cards(self):
        card_set = CardSet.from_str('As 2s d d')
        self.assertEqual(card_set.get_particular_cards(), [Card(14, 1), Card(2, 1)])
        card_set = CardSet.from_str('As 2s d 3 *')
        self.assertEqual(card_set.get_particular_cards(), [Card(14, 1), Card(2, 1)])

    def test_get_suit_jokers(self):
        card_set = CardSet.from_str('As 2s d d s c c')
        self.assertEqual(card_set.get_suit_jokers(), [3, 3, 1, 4, 4])

    def test_count_full_jokers(self):
        card_set = CardSet.from_str('As2s**')
        self.assertEqual(card_set.count_full_jokers(), 2)

    def test_get_ranks_for_suit(self):
        card_set = CardSet.from_str('AdKd3s7s2d')
        self.assertEqual(card_set.get_ranks_for_suit(3), [14, 13, 2])
        self.assertEqual(card_set.get_ranks_for_suit(1), [3, 7])

    def test_str(self):
        cs = CardSet([Card(14, 1), Card(13, 3)])
        self.assertEqual(str(cs), 'AsKd')


class BoardTest(unittest.TestCase):

    def test_create_board(self):
        flop = Board([Card(14, 3), Card(13, 3), Card(10, 3)])
        self.assertEqual(Board.from_str('Ad Kd Td'), flop)
        self.assertEqual([CardSet.from_str('Ad Kd Td')], flop.get_combinations(3))
        turn = Board.from_str('Ad Kd Td 9d')
        self.assertEqual(4, len(turn.get_combinations(3)))
