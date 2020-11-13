import unittest

from lifeguard_mongodb.settings import (
    SETTINGS_MANAGER,
    LIFEGUARD_MONGODB_URL,
    LIFEGUARD_MONGODB_DATABASE,
)


class SettingsTest(unittest.TestCase):
    def test_lifeguard_mongodb_database(self):
        self.assertEqual(LIFEGUARD_MONGODB_DATABASE, "lifeguard")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_MONGODB_DATABASE"]["description"],
            "MongoDB database name",
        )

    def test_lifeguard_mongodb_url(self):
        self.assertEqual(LIFEGUARD_MONGODB_URL, "mongodb://localhost:27017")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_MONGODB_URL"]["description"],
            "MongoDB connection url",
        )
