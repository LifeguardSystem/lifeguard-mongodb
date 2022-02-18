"""
Implementation of repositories using MongoDB
"""
from lifeguard.notifications import NotificationStatus, NotificationOccurrence
from lifeguard.validations import ValidationResponse
from pymongo import MongoClient

from lifeguard_mongodb.settings import LIFEGUARD_MONGODB_DATABASE, LIFEGUARD_MONGODB_URL

CLIENT = MongoClient(LIFEGUARD_MONGODB_URL)
DATABASE = CLIENT[LIFEGUARD_MONGODB_DATABASE]


def save_or_update(collection, query, data):
    """
    Check if entry exists and create or update entry
    :param collection:
    :param query:
    :param data:
    """
    if collection.count_documents(query):
        collection.update_many(query, {"$set": data})
    else:
        collection.insert_one(data)


class MongoDBHistoryRepository:
    def __init__(self):
        self.collection = DATABASE.history

    def append_notification(self, notification_occurrence):
        self.collection.insert_one(
            {
                "validation_name": notification_occurrence.validation_name,
                "details": notification_occurrence.details,
                "status": notification_occurrence.status,
                "notification_type": notification_occurrence.notification_type,
                "created_at": notification_occurrence.created_at,
            }
        )

    def fetch_notifications(self, start_interval, end_interval, filters):
        filters.update({"created_at": {"$gte": start_interval, "$lte": end_interval}})
        return [
            self.__convert_to_occurrence(entry)
            for entry in self.collection.find(filters)
        ]

    def __convert_to_occurrence(self, entry):
        return NotificationOccurrence(
            validation_name=entry["validation_name"],
            details=entry["details"],
            status=entry["status"],
            notification_type=entry["notification_type"],
            created_at=entry["created_at"],
        )


class MongoDBValidationRepository:
    def __init__(self):
        self.collection = DATABASE.validations

    def save_validation_result(self, validation_result):
        save_or_update(
            self.collection,
            {"validation_name": validation_result.validation_name},
            {
                "validation_name": validation_result.validation_name,
                "status": validation_result.status,
                "details": validation_result.details,
                "settings": validation_result.settings,
                "last_execution": validation_result.last_execution,
            },
        )

    def fetch_last_validation_result(self, validation_name):
        result = self.collection.find_one({"validation_name": validation_name})
        if result:
            return self.__convert_to_validation(result)
        return None

    def fetch_all_validation_results(self):
        results = []
        for result in self.collection.find():
            results.append(self.__convert_to_validation(result))

        return results

    def __convert_to_validation(self, validation_document):
        return ValidationResponse(
            validation_document["validation_name"],
            validation_document["status"],
            validation_document["details"],
            validation_document["settings"],
            last_execution=validation_document["last_execution"],
        )


class MongoDBNotificationRepository:
    def __init__(self):
        self.collection = DATABASE.notifications

    def save_last_notification_for_a_validation(self, notification):
        save_or_update(
            self.collection,
            {
                "validation_name": notification.validation_name,
            },
            {
                "validation_name": notification.validation_name,
                "thread_ids": notification.thread_ids,
                "is_opened": notification.is_opened,
                "options": notification.options,
                "last_notification": notification.last_notification,
            },
        )

    def fetch_last_notification_for_a_validation(self, validation_name):
        result = self.collection.find_one(
            {"validation_name": validation_name, "is_opened": True}
        )
        if result:
            last_notification_status = NotificationStatus(
                validation_name, result["thread_ids"], result["options"]
            )
            last_notification_status.last_notification = result["last_notification"]
            last_notification_status.is_opened = result["is_opened"]
            return last_notification_status
        return None
