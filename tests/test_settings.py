import unittest
from ploev.settings import CONFIG


class SettingTest(unittest.TestCase):

    def test_settings(self):
        self.assertEqual(CONFIG['SERVER']['host'], 'localhost')