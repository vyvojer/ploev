import unittest
import json
from ranges import PostflopRange, RangeGroup, RangeGroup
from ranges import _json_default, _json_object_hook, _name_to_attr


class TestRanges(unittest.TestCase):

    def test_name_to_attr(self):
        self.assertEqual(_name_to_attr('tight range'), 'tight_range')
        self.assertEqual(_name_to_attr('tight range'), 'tight_range')
        self.assertEqual(_name_to_attr('parent'), 'parent_')
        self.assertEqual(_name_to_attr('name'), 'name_')
        self.assertEqual(_name_to_attr('descriptions'), 'descriptions_')


class TestRangeGroup(unittest.TestCase):
    def test_range_group(self):
        name = "Two tone boards"
        range_group = RangeGroup(name=name)
        self.assertEqual(range_group.name, name)
        self.assertEqual(range_group.parent, None)
        self.assertEqual(range_group.descriptions, None)

    def test_equal(self):
        r1 = RangeGroup(name="pum")
        r2 = RangeGroup(name="pum")
        self.assertEqual(r1, r2)
        r2 = RangeGroup(name="pum", descriptions=['a', 'b'])
        self.assertNotEqual(r1, r2)
        r1 = RangeGroup(name="pum", descriptions=['a', 'b'])
        self.assertEqual(r1, r2)
        child1 = RangeGroup("child")
        child2 = RangeGroup("child")
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
        range_group = RangeGroup(name="", descriptions=descriptions)
        self.assertEqual(range_group.descriptions, descriptions)

    def test_range_group_descriptions_inherited_from_parent(self):
        parent_descriptions = [
            'raise',
            'call',
            'fold'
        ]
        parent_group = RangeGroup(name="parent", descriptions=parent_descriptions)
        range_group = RangeGroup(name="child", parent=parent_group)
        self.assertEqual(range_group.descriptions, parent_descriptions)

    def test_children(self):
        parent1 = RangeGroup(name="parent")
        self.assertEqual(parent1.has_children, False)
        child1 = RangeGroup(name="child1")
        child2 = RangeGroup(name="child2")
        parent1.add_child(child1)
        parent1.add_child(child2)
        self.assertEqual(child1.parent, parent1)
        self.assertEqual(child2.parent, parent1)
        self.assertEqual(len(parent1.children), 2)
        self.assertEqual(parent1.children[0].name, "child1")
        self.assertEqual(parent1.children[1].name, "child2")
        self.assertEqual(parent1.has_children, True)
        parent2 = RangeGroup(name='parent2')
        self.assertEqual(parent2.has_children, False)
        child1.parent = parent2
        self.assertEqual(parent1.children[0].name, "child2")
        self.assertEqual(parent1.has_children, True)
        self.assertEqual(len(parent1.children), 1)
        self.assertEqual(parent2.children[0].name, "child1")
        self.assertEqual(parent2.has_children, True)
        self.assertEqual(len(parent2.children), 1)
        parent3 = RangeGroup(name="parent3")
        child3 = RangeGroup(name="child3", parent=parent3)
        self.assertEqual(child3.parent, parent3)
        self.assertEqual(child3.parent.children, [child3])

    def test_str_ancestors(self):
        grand_pa = RangeGroup(name="grand_pa")
        parent1 = RangeGroup(name="parent1")
        child = RangeGroup(name="child")
        self.assertEqual(grand_pa.str_ancestors(), 'grand_pa')
        self.assertEqual(parent1.str_ancestors(), 'parent1')
        self.assertEqual(child.str_ancestors(), 'child')
        child.parent = parent1
        parent1.parent = grand_pa
        self.assertEqual(grand_pa.str_ancestors(), 'grand_pa')
        self.assertEqual(parent1.str_ancestors(), 'grand_pa > parent1')
        self.assertEqual(child.str_ancestors(), 'grand_pa > parent1 > child')

    def test_children_as_attr(self):
        parent1 = RangeGroup(name="parent")
        child1 = RangeGroup(name="child1")
        child2 = RangeGroup(name="child2")
        parent1.add_child(child1)
        parent1.add_child(child2)
        self.assertEqual(parent1.child1, child1)
        self.assertEqual(parent1.child2, child2)

    def test_to_json(self):
        pr_dict_expected = {'name': 'parent',
                            'ranges': [
                                {'name': 'child1',
                                 'ranges': []},
                                {'name': 'child2',
                                 'ranges': []},
                            ],
                            }

        pr = RangeGroup(name="parent")
        pr.add_child(RangeGroup(name="child1"))
        pr.add_child(RangeGroup(name="child2"))
        pr_dict = json.loads(json.dumps(pr, default=_json_default))
        self.assertEqual(pr_dict, pr_dict_expected)

    def test_to_json_with_sub_ranges(self):
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
        pr = RangeGroup(name="parent")
        child1 = RangeGroup(name="child1")
        child1.add_child(PostflopRange('Tight', ['TS, TP+']))
        child1.add_child(PostflopRange('Loose', ['TP+, BP+']))
        pr.add_child(child1)
        pr.add_child(RangeGroup(name="child2"))
        pr_dict = json.loads(json.dumps(pr, default=_json_default))
        self.assertEqual(pr_dict, pr_dict_expected)

    def test_to_json_with_description(self):
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
        pr = RangeGroup(name="parent", descriptions=['raise', 'call'])
        child1 = RangeGroup(name="child1")
        child1.add_child(PostflopRange('Tight', ['TS', 'TP+']))
        child1.add_child(PostflopRange('Loose', ['TP+', 'BP+']))
        pr.add_child(child1)
        pr.add_child(RangeGroup(name="child2"))
        pr_dict = json.loads(json.dumps(pr, default=_json_default))
        self.assertEqual(pr_dict, pr_dict_expected)

    def test_json_to_ranges(self):
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

        pr = json.loads(json.dumps(pr_dict), object_hook=_json_object_hook)
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
        pr = json.loads(json.dumps(pr_dict), object_hook=_json_object_hook)
        new_dict = json.loads(json.dumps(pr, default=_json_default))
        self.assertEqual(pr_dict, new_dict)
        pr2 = json.loads(json.dumps(pr_dict), object_hook=_json_object_hook)
        self.assertEqual(pr, pr2)

    def test_save_and_load_range(self):
        descriptions = [
            'raise',
            'call',
            'fold'
        ]
        pr = RangeGroup(name="Dry board", descriptions=descriptions)
        pr.save('pr.json')
        pr2 = RangeGroup.load('pr.json')
        self.assertEqual(pr, pr2)

    def test_check_sub_ranges(self):
        descriptions = [
            'raise',
            'call',
            'bluff raise',
            'fold',
        ]
        sub_ranges = [
            'MS+',
            'PUPA-',
            'GS+',
            'PINYA',
        ]
        parent1 = RangeGroup('Dry board', descriptions=descriptions)
        child = RangeGroup('Low board', parent=parent1)
        tight = PostflopRange('Tight', sub_ranges=sub_ranges, parent=child)
        self.assertEqual(tight.has_error, False)
        self.assertEqual(child.has_error, False)
        self.assertEqual(parent1.has_error, False)
        parent1.check_sub_ranges(print_error=False)
        self.assertEqual(tight.has_error, True)
        self.assertEqual(child.has_error, True)
        self.assertEqual(parent1.has_error, True)

    def test_check_load_and_check(self):
        descriptions = [
            'raise',
            'call',
            'bluff raise',
            'fold',
        ]
        sub_ranges = [
            'MS+',
            'PUPA-',
            'GS+',
            'PINYA',
        ]
        parent1 = RangeGroup('Dry board', descriptions=descriptions)
        child = RangeGroup('Low board', parent=parent1)
        tight = PostflopRange('Tight', sub_ranges=sub_ranges, parent=child)
        self.assertEqual(tight.has_error, False)
        self.assertEqual(child.has_error, False)
        self.assertEqual(parent1.has_error, False)
        parent1.save('ranges_with_error.json')
        new_parent = RangeGroup.load_and_check('ranges_with_error.json', print_error=False)
        self.assertEqual(new_parent.has_error, True)
        self.assertEqual(new_parent.children[0].has_error, True)
        self.assertEqual(new_parent.children[0].children[0].has_error, True)


class TestPostflopRange(unittest.TestCase):
    def test_postflop_range(self):
        sub_ranges = [
            'MS+',
            '2P+'
        ]
        pf_range = PostflopRange("Tight", sub_ranges=sub_ranges)
        self.assertEqual(pf_range.name, "Tight")
        self.assertEqual(pf_range.sub_ranges[1], '2P+')
        self.assertEqual(pf_range.descriptions, ['r_1', 'r_2'])
        self.assertEqual(pf_range.r_2, '2P+')

    def test_postflop_range_with_parent_descriptions(self):
        range_group = RangeGroup("vs pfr", descriptions=['raise', 'call'])
        sub_ranges = [
            'MS+',
            '2P+'
        ]
        pf_range = PostflopRange("Tight", sub_ranges=sub_ranges, parent=range_group)
        self.assertEqual(pf_range.sub_ranges[1], '2P+')
        self.assertEqual(pf_range.descriptions, ['raise', 'call'])
        self.assertEqual(pf_range.call, '2P+')

    def test_postflop_range_with_descriptions(self):
        range_group = RangeGroup("vs pfr", descriptions=['raise', 'call'])
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

    def test_check_sub_ranges(self):
        sub_ranges = [
            'MS+',
            '2PH+'
        ]
        pf_range = PostflopRange("Wrong", sub_ranges)
        self.assertEqual(pf_range.has_error, False)
        pf_range.check_sub_ranges(print_error=False)
        self.assertEqual(pf_range.has_error, True)
        self.assertEqual(pf_range._errors[0], None)
        self.assertEqual(pf_range._errors[1].easy_range, "2PH+")
        self.assertEqual(pf_range._errors[1].column, 3)

    def test_empty_sub_ranges(self):
        sub_ranges = [
            'MS+',
            None,
            'BS+'
        ]
        pf_range = PostflopRange("With None", sub_ranges)
        self.assertEqual(pf_range.r_3, 'BS+')
        self.assertEqual(pf_range.r_2, None)



