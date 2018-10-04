import unittest
from ploev.ranges import *
from ploev.game import *


class TagTest(unittest.TestCase):

    def test_add_tag(self):
        parent = Tag('parent')
        child = Tag('child')
        parent.add_tag(child)
        self.assertEqual(child.parent, parent)
        self.assertEqual(parent.children, [child])

    def test_add_tags(self):
        parent = Tag('parent')
        child1 = Tag('child1')
        child2 = Tag('child2')
        parent.add_tags([child1, child2])
        self.assertEqual(child1.parent, parent)
        self.assertEqual(child2.parent, parent)
        self.assertEqual(parent.children, [child1, child2])

    def test_is_leaf(self):
        parent = Tag('parent')
        child = Tag('child')
        parent.add_tag(child)
        self.assertFalse(parent.is_leaf())
        self.assertTrue(child.is_leaf())


class SubRangesTest(unittest.TestCase):
    def setUp(self):
        self.root = Tag()
        self.parent = Tag('parent')
        self.child1 = Tag('child1')
        self.child2 = Tag('child2')
        self.root.add_tag(self.parent)
        self.parent.add_tag(self.child1)
        self.parent.add_tag(self.child2)

    def test__init(self):
        sub_ranges = SubRanges('c1', [
            SubRange('raise', EasyRange('MS+')),
            SubRange('call', EasyRange('*')),
        ], [self.child1, self.child2])
        self.assertEqual(sub_ranges.sub_ranges[0].name, 'raise')
        self.assertEqual(sub_ranges.tags[0], self.child1)
        self.assertEqual(sub_ranges.tags[1], self.child2)

    def test_add_sub_range(self):
        sub_ranges = SubRanges('tight')
        sub_ranges.add_sub_range(SubRange('raise', EasyRange('MS+')))
        self.assertEqual(sub_ranges.sub_ranges[0].name, 'raise')


class RangesListTest(unittest.TestCase):

    def setUp(self):
        self.root = Tag()
        self.parent = Tag('parent')
        self.child1 = Tag('child1')
        self.child2 = Tag('child2')
        self.root.add_tag(self.parent)
        self.parent.add_tag(self.child1)
        self.parent.add_tag(self.child2)
        self.sub_ranges1 = SubRanges('c1', [
            SubRange('raise', EasyRange('MS+')),
            SubRange('call', EasyRange('*')),
        ],
                                     [self.child1])
        self.sub_ranges2 = SubRanges('c2', [
            SubRange('raise', EasyRange('BS+')),
            SubRange('call', EasyRange('*')),
        ], [self.child2])
