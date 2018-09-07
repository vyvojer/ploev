import unittest
from ploev.ranges import *


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