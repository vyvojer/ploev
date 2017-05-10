import unittest
import os
from ploev.settings import CONFIG
import ploev


class SettingTest(unittest.TestCase):

    def test_settings(self):
        self.assertEqual(CONFIG['SERVER']['host'], 'localhost')