"""
Lifeguard MongoDB Settings
"""
from lifeguard.settings import SettingsManager

SETTINGS_MANAGER = SettingsManager(
    {
        "LIFEGUARD_MONGODB_DATABASE": {
            "default": "lifeguard",
            "description": "MongoDB database name",
        },
        "LIFEGUARD_MONGODB_URL": {
            "default": "mongodb://localhost:27017",
            "description": "MongoDB connection url",
        },
    }
)

LIFEGUARD_MONGODB_URL = SETTINGS_MANAGER.read_value("LIFEGUARD_MONGODB_URL")
LIFEGUARD_MONGODB_DATABASE = SETTINGS_MANAGER.read_value("LIFEGUARD_MONGODB_DATABASE")
