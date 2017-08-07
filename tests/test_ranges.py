import unittest
from ranges import PostflopRange, PostflopRanges, PostflopRanges


class TestPostflopRanges(unittest.TestCase):
    def test_range_group(self):
        name = "Two tone boards"
        range_group = PostflopRanges(name=name)
        self.assertEqual(range_group.name, name)
        self.assertEqual(range_group.parent, None)
        self.assertEqual(range_group.descriptions, None)

    def test_equal(self):
        r1 = PostflopRanges(name="pum")
        r2 = PostflopRanges(name="pum")
        self.assertEqual(r1, r2)
        r2 = PostflopRanges(name="pum", descriptions=['a', 'b'])
        self.assertNotEqual(r1, r2)
        r1 = PostflopRanges(name="pum", descriptions=['a', 'b'])
        self.assertEqual(r1, r2)
        child1 = PostflopRanges("child")
        child2 = PostflopRanges("child")
        r1.add_child(child1)
        self.assertNotEqual(r1, r2)
        r2.add_child(child1)
        self.assertEqual(r1, r2)

    def test_range_group_with_descriptions(self):
        descriptions = [
            'raise',
            'call',
            'fold'
        ]
        range_group = PostflopRanges(name="", descriptions=descriptions)
        self.assertEqual(range_group.descriptions, descriptions)

    def test_range_group_descriptions_inherited_from_parent(self):
        parent_descriptions = [
            'raise',
            'call',
            'fold'
        ]
        parent_group = PostflopRanges(name="parent", descriptions=parent_descriptions)
        range_group = PostflopRanges(name="child", parent=parent_group)
        self.assertEqual(range_group.descriptions, parent_descriptions)

    def test_children(self):
        parent1 = PostflopRanges(name="parent")
        self.assertEqual(parent1.has_children, False)
        child1 = PostflopRanges(name="child1")
        child2 = PostflopRanges(name="child2")
        parent1.add_child(child1)
        parent1.add_child(child2)
        self.assertEqual(child1.parent, parent1)
        self.assertEqual(child2.parent, parent1)
        self.assertEqual(len(parent1.children), 2)
        self.assertEqual(parent1.children[0].name, "child1")
        self.assertEqual(parent1.children[1].name, "child2")
        self.assertEqual(parent1.has_children, True)
        parent2 = PostflopRanges(name='parent2')
        self.assertEqual(parent2.has_children, False)
        child1.parent = parent2
        self.assertEqual(parent1.children[0].name, "child2")
        self.assertEqual(parent1.has_children, True)
        self.assertEqual(len(parent1.children), 1)
        self.assertEqual(parent2.children[0].name, "child1")
        self.assertEqual(parent2.has_children, True)
        self.assertEqual(len(parent2.children), 1)
        parent3 = PostflopRanges(name="parent3")
        child3 = PostflopRanges(name="child3", parent=parent3)
        self.assertEqual(child3.parent, parent3)
        self.assertEqual(child3.parent.children, [child3])

    def test_children_as_attr(self):
        parent1 = PostflopRanges(name="parent")
        child1 = PostflopRanges(name="child1")
        child2 = PostflopRanges(name="child2")
        parent1.add_child(child1)
        parent1.add_child(child2)
        self.assertEqual(parent1.child1, child1)
        self.assertEqual(parent1.child2, child2)

    def test_to_dict(self):
        pr_dict_expected = {'name': 'parent',
                            'ranges': [
                                {'name': 'child1',
                                 'ranges': []},
                                {'name': 'child2',
                                 'ranges': []},
                            ],
                            }

        pr = PostflopRanges(name="parent")
        pr.add_child(PostflopRanges(name="child1"))
        pr.add_child(PostflopRanges(name="child2"))
        pr_dict = PostflopRanges._to_dict(pr)
        self.assertEqual(pr_dict, pr_dict_expected)

    def test_to_dict_with_sub_ranges(self):
        pr_dict_expected = {'name': 'parent',
                            'ranges': [
                                {'name': 'child1',
                                 'ranges': [
                                     {'name': 'Tight',
                                      'sub_ranges': ['TS, TP+']},
                                     {'name': 'Loose',
                                      'sub_ranges': ['TP+, BP+']},
                                 ]},
                                {'name': 'child2',
                                 'ranges': []},
                            ],
                            }
        pr = PostflopRanges(name="parent")
        child1 = PostflopRanges(name="child1")
        child1.add_child(PostflopRange('Tight', ['TS, TP+']))
        child1.add_child(PostflopRange('Loose', ['TP+, BP+']))
        pr.add_child(child1)
        pr.add_child(PostflopRanges(name="child2"))
        pr_dict = PostflopRanges._to_dict(pr)
        self.assertEqual(pr_dict, pr_dict_expected)

    def test_to_dict_with_description(self):
        pr_dict_expected = {'name': 'parent',
                            'descriptions': ['raise', 'call'],
                            'ranges': [
                                {'name': 'child1',
                                 'ranges': [
                                     {'name': 'Tight',
                                      'sub_ranges': ['TS', 'TP+']},
                                     {'name': 'Loose',
                                      'sub_ranges': ['TP+', 'BP+']},
                                 ]},
                                {'name': 'child2',
                                 'ranges': []},
                            ],
                            }
        pr = PostflopRanges(name="parent", descriptions=['raise', 'call'])
        child1 = PostflopRanges(name="child1")
        child1.add_child(PostflopRange('Tight', ['TS', 'TP+']))
        child1.add_child(PostflopRange('Loose', ['TP+', 'BP+']))
        pr.add_child(child1)
        pr.add_child(PostflopRanges(name="child2"))
        pr_dict = PostflopRanges._to_dict(pr)
        self.assertEqual(pr_dict, pr_dict_expected)

    def test_dict_to_ranges(self):
        pr_dict = {'name': 'parent',
                   'descriptions': ['raise', 'call'],
                   'ranges': [
                       {'name': 'child1',
                        'ranges': [
                            {'name': 'Tight',
                             'sub_ranges': ['TS', 'TP+']},
                            {'name': 'Loose',
                             'sub_ranges': ['TP+', 'BP+']},
                        ]},
                       {'name': 'child2',
                        'ranges': []},
                   ],
                   }

        pr = PostflopRanges._from_dict(pr_dict)
        self.assertEqual(pr.name, 'parent')
        self.assertEqual(pr.descriptions, ['raise', 'call'])
        self.assertEqual(len(pr.children), 2)
        self.assertEqual(pr.children[0].name, "child1")
        self.assertEqual(pr.children[0].descriptions, ['raise', 'call'])
        self.assertEqual(len(pr.children[0].children), 2)
        self.assertEqual(pr.children[0].children[0].sub_ranges, ['TS', 'TP+'])
        self.assertEqual(pr.children[0].children[0].descriptions, ['raise', 'call'])
        self.assertEqual(pr.child1.Tight.descriptions, ['raise', 'call'])

    def test_dict_to_ranges_and_back(self):
        pr_dict = {'name': 'parent',
                   'descriptions': ['raise', 'call'],
                   'ranges': [
                       {'name': 'child1',
                        'ranges': [
                            {'name': 'Tight',
                             'sub_ranges': ['TS', 'TP+']},
                            {'name': 'Loose',
                             'sub_ranges': ['TP+', 'BP+']},
                        ]},
                       {'name': 'child2',
                        'ranges': []},
                   ],
                   }
        pr = PostflopRanges._from_dict(pr_dict)
        new_dict = PostflopRanges._to_dict(pr)
        self.assertEqual(pr_dict, new_dict)
        pr2 = PostflopRanges._from_dict(new_dict)
        self.assertEqual(pr, pr2)

    def test_save_and_load_range(self):
        descriptions = [
            'raise',
            'call',
            'fold'
        ]
        pr = PostflopRanges(name="Dry board", descriptions=descriptions)
        pr.save('pr.json')
        pr2 = PostflopRanges.load('pr.json')
        self.assertEqual(pr, pr2)


class TestPostflopRange(unittest.TestCase):
    def test_postflop_range(self):
        sub_ranges = [
            'MS+',
            '2P+'
        ]
        pf_range = PostflopRange("Tight", sub_ranges=sub_ranges)
        self.assertEqual(pf_range.name, "Tight")
        self.assertEqual(pf_range.sub_ranges[1], '2P+')
        self.assertEqual(pf_range.descriptions, ['r_0', 'r_1'])
        self.assertEqual(pf_range.r_1, '2P+')

    def test_postflop_range_with_parent_descriptions(self):
        range_group = PostflopRanges("vs pfr", descriptions=['raise', 'call'])
        sub_ranges = [
            'MS+',
            '2P+'
        ]
        pf_range = PostflopRange("Tight", sub_ranges=sub_ranges, parent=range_group)
        self.assertEqual(pf_range.sub_ranges[1], '2P+')
        self.assertEqual(pf_range.descriptions, ['raise', 'call'])
        self.assertEqual(pf_range.call, '2P+')

    def test_postflop_range_with_descriptions(self):
        range_group = PostflopRanges("vs pfr", descriptions=['raise', 'call'])
        sub_ranges = [
            'MS+',
            '2P+'
        ]
        pf_range = PostflopRange(name="Range",
                                 sub_ranges=sub_ranges,
                                 parent=range_group,
                                 descriptions=['pum', 'bum'])
        self.assertEqual(pf_range.sub_ranges[1], '2P+')
        self.assertEqual(pf_range.descriptions, ['pum', 'bum'])
        self.assertEqual(pf_range.bum, '2P+')


