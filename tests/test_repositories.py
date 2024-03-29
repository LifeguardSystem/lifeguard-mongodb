from datetime import datetime

import unittest
from unittest.mock import patch, MagicMock

from lifeguard import NORMAL
from lifeguard.notifications import NotificationStatus
from lifeguard.validations import ValidationResponse
from lifeguard_mongodb.repositories import (
    MongoDBHistoryRepository,
    MongoDBValidationRepository,
    MongoDBNotificationRepository,
)


class TestMongoDBHistoryRepository(unittest.TestCase):
    @patch("lifeguard_mongodb.repositories.DATABASE")
    def setUp(self, mock_database):
        self.collection = MagicMock(name="history")
        mock_database.history = self.collection
        self.repository = MongoDBHistoryRepository()

    def test_append_notification(self):
        notification_occurrence = MagicMock(name="notification_occurrence")
        notification_occurrence.validation_name = "validation_name"
        notification_occurrence.details = "details"
        notification_occurrence.status = "status"
        notification_occurrence.notification_type = "notification_type"
        notification_occurrence.created_at = "created_at"

        self.repository.append_notification(notification_occurrence)

        self.collection.insert_one.assert_called_with(
            {
                "validation_name": "validation_name",
                "details": "details",
                "status": "status",
                "notification_type": "notification_type",
                "created_at": "created_at",
            }
        )

    def test_fetch_notifications(self):
        start_interval = MagicMock(name="start_interval")
        end_interval = MagicMock(name="end_interval")
        filters = {}

        mock_sort = MagicMock(name="sort")

        self.collection.find.return_value = mock_sort
        mock_sort.sort.return_value = [
            {
                "validation_name": "validation_name",
                "details": "details",
                "status": "status",
                "notification_type": "notification_type",
                "created_at": "created_at",
            }
        ]

        result = self.repository.fetch_notifications(
            start_interval, end_interval, filters, None, None
        )

        self.collection.find.assert_called_with(
            {"created_at": {"$gte": start_interval, "$lte": end_interval}}
        )
        mock_sort.sort.assert_called_with("created_at", -1)
        self.assertEqual(
            result[0].__dict__,
            {
                "_created_at": "created_at",
                "_details": "details",
                "_notification_type": "notification_type",
                "_status": "status",
                "_validation_name": "validation_name",
            },
        )

    def test_count_notifications(self):
        start_interval = MagicMock(name="start_interval")
        end_interval = MagicMock(name="end_interval")
        filters = {}

        result = self.repository.count_notifications(
            start_interval, end_interval, filters
        )
        self.collection.count_documents.assert_called_with(
            {"created_at": {"$gte": start_interval, "$lte": end_interval}}
        )

        self.assertIsNotNone(result)

    def test_fetch_notifications_with_pagination(self):
        start_interval = MagicMock(name="start_interval")
        end_interval = MagicMock(name="end_interval")
        filters = {}

        mock_limit = MagicMock(name="limit")
        mock_skip = MagicMock(name="skip")
        mock_sort = MagicMock(name="sort")

        self.collection.find.return_value = mock_limit
        mock_limit.limit.return_value = mock_skip
        mock_skip.skip.return_value = mock_sort
        mock_sort.sort.return_value = [
            {
                "validation_name": "validation_name",
                "details": "details",
                "status": "status",
                "notification_type": "notification_type",
                "created_at": "created_at",
            }
        ]

        result = self.repository.fetch_notifications(
            start_interval, end_interval, filters, 1, 10
        )

        self.collection.find.assert_called_with(
            {"created_at": {"$gte": start_interval, "$lte": end_interval}}
        )

        mock_skip.skip.assert_called_with(0)
        mock_limit.limit.assert_called_with(10)
        mock_sort.sort.assert_called_with("created_at", -1)

        self.assertEqual(
            result[0].__dict__,
            {
                "_created_at": "created_at",
                "_details": "details",
                "_notification_type": "notification_type",
                "_status": "status",
                "_validation_name": "validation_name",
            },
        )


class TestMongoDBValidationRepository(unittest.TestCase):
    @patch("lifeguard_mongodb.repositories.DATABASE")
    def setUp(self, mock_database):
        self.collection = MagicMock(name="validations")
        mock_database.validations = self.collection
        self.repository = MongoDBValidationRepository()

    def test_fetch_last_validation_result_none(self):
        validation_name = "validation"
        self.collection.find_one.return_value = None

        result = self.repository.fetch_last_validation_result(validation_name)

        self.assertIsNone(result)
        self.collection.find_one.assert_called_with(
            {"validation_name": validation_name}
        )

    def test_fetch_last_validation_result_not_none(self):
        validation_name = "validation"
        self.collection.find_one.return_value = {
            "validation_name": "validation",
            "status": NORMAL,
            "details": "details",
            "settings": "settings",
            "last_execution": datetime(2020, 11, 19),
        }

        result = self.repository.fetch_last_validation_result(validation_name)

        self.assertEqual(result.status, NORMAL)
        self.assertEqual(result.details, "details")
        self.assertEqual(result.settings, "settings")
        self.assertEqual(result.last_execution, datetime(2020, 11, 19))
        self.collection.find_one.assert_called_with(
            {"validation_name": validation_name}
        )

    def test_save_validation_result_create(self):
        self.collection.count_documents.return_value = 0
        response = ValidationResponse(NORMAL, {}, validation_name="name")

        self.repository.save_validation_result(response)

        self.collection.insert_one.assert_called_with(
            {
                "validation_name": "name",
                "status": NORMAL,
                "details": {},
                "settings": None,
                "last_execution": None,
            }
        )

    def test_save_validation_result_update(self):
        self.collection.count_documents.return_value = 1
        response = ValidationResponse(NORMAL, {}, validation_name="name")

        self.repository.save_validation_result(response)

        self.collection.update_many.assert_called_with(
            {"validation_name": "name"},
            {
                "$set": {
                    "validation_name": "name",
                    "status": NORMAL,
                    "details": {},
                    "settings": None,
                    "last_execution": None,
                }
            },
        )

    def test_fetch_all_validation_results_not_none(self):
        self.collection.find.return_value = [
            {
                "validation_name": "validation",
                "status": NORMAL,
                "details": "details",
                "settings": "settings",
                "last_execution": datetime(2020, 11, 19),
            }
        ]

        result = self.repository.fetch_all_validation_results()

        self.assertEqual(result[0].validation_name, "validation")
        self.assertEqual(result[0].status, NORMAL)
        self.assertEqual(result[0].details, "details")
        self.assertEqual(result[0].settings, "settings")
        self.assertEqual(result[0].last_execution, datetime(2020, 11, 19))
        self.collection.find.assert_called()

    def test_delete_validation_result(self):
        self.repository.delete_validation_result("validation_name")
        self.collection.delete_one.assert_called_with(
            {"validation_name": "validation_name"}
        )


class TestMongoDBNotificationRepository(unittest.TestCase):
    @patch("lifeguard_mongodb.repositories.DATABASE")
    def setUp(self, mock_database):
        self.collection = MagicMock(name="notifications")
        mock_database.notifications = self.collection
        self.repository = MongoDBNotificationRepository()

    def test_fetch_last_notification_for_a_validation_is_none(self):
        validation_name = "notification"
        self.collection.find_one.return_value = None

        result = self.repository.fetch_last_notification_for_a_validation(
            validation_name
        )

        self.assertIsNone(result)
        self.collection.find_one.assert_called_with(
            {"validation_name": validation_name, "is_opened": True}
        )

    def test_fetch_last_notification_for_a_validation_not_none(self):
        validation_name = "validation"
        self.collection.find_one.return_value = {
            "thread_ids": {},
            "is_opened": True,
            "options": {},
            "last_notification": datetime(2020, 11, 19),
        }

        result = self.repository.fetch_last_notification_for_a_validation(
            validation_name
        )

        self.assertEqual(result.thread_ids, {})
        self.assertEqual(result.is_opened, True)
        self.assertEqual(result.options, {})
        self.assertEqual(result.last_notification, datetime(2020, 11, 19))
        self.collection.find_one.assert_called_with(
            {"validation_name": validation_name, "is_opened": True}
        )

    @patch("lifeguard.notifications.datetime")
    def test_save_last_notification_for_a_validation_create(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2020, 12, 31)

        self.collection.count_documents.return_value = 0
        notification_status = NotificationStatus("name", "status", {})

        self.repository.save_last_notification_for_a_validation(notification_status)

        self.collection.insert_one.assert_called_with(
            {
                "validation_name": "name",
                "thread_ids": "status",
                "is_opened": True,
                "options": {},
                "last_notification": datetime(2020, 12, 31, 0, 0),
            }
        )

    @patch("lifeguard.notifications.datetime")
    def test_save_last_notification_for_a_validation_update(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2020, 12, 31)

        self.collection.count_documents.return_value = 1
        notification_status = NotificationStatus("name", {}, {})

        self.repository.save_last_notification_for_a_validation(notification_status)

        self.collection.update_many.assert_called_with(
            {"validation_name": "name"},
            {
                "$set": {
                    "validation_name": "name",
                    "thread_ids": {},
                    "is_opened": True,
                    "options": {},
                    "last_notification": datetime(2020, 12, 31, 0, 0),
                }
            },
        )
