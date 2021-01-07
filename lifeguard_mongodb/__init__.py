"""
Lifeguard integration with MongoDB
"""
from lifeguard.repositories import declare_implementation

from lifeguard_mongodb.repositories import (MongoDBNotificationRepository,
                                            MongoDBValidationRepository)


class LifeguardMongoDBPlugin:
    def __init__(self, lifeguard_context):
        self.lifeguard_context = lifeguard_context
        declare_implementation("notification", MongoDBNotificationRepository)
        declare_implementation("validation", MongoDBValidationRepository)


def init(lifeguard_context):
    LifeguardMongoDBPlugin(lifeguard_context)
