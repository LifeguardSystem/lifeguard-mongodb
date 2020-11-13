"""
Implementation of repositories using MongoDB
"""
from lifeguard.validations import ValidationResponse
from pymongo import MongoClient

from lifeguard_mongodb.settings import LIFEGUARD_MONGODB_DATABASE, LIFEGUARD_MONGODB_URL

CLIENT = MongoClient(LIFEGUARD_MONGODB_URL)
DATABASE = CLIENT[LIFEGUARD_MONGODB_DATABASE]

from lifeguard.repositories import ValidationRepository


def save_or_update(collection, query, data):
    """
    Check if entry exists and create or update entry
    :param collection:
    :param query:
    :param data:
    """
    if collection.count(query):
        collection.update_many(query, {"$set": data})
    else:
        collection.insert_one(data)


class MongoDBValidationRepository:
    def __init__(self):
        self.collection = DATABASE.validations

    def save_validation_result(self, validation_result):
        save_or_update(
            self.collection,
            {"validation_name": validation_result.validation_name},
            validation_result.__dict__,
        )

    def fetch_last_validation_result(self, validation_name):
        result = self.collection.find_one({"validation_name": validation_name})
        if result:
            return ValidationResponse(
                validation_name, result["status"], result["details"], result["settings"]
            )
        return None
