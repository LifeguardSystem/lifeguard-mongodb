from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock

from lifeguard.validations import ValidationResponse
from lifeguard_mongodb.repositories import MongoDBValidationRepository


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
            "status": "status",
            "details": "details",
            "settings": "settings",
            "last_execution": datetime(2020, 11, 19),
        }

        result = self.repository.fetch_last_validation_result(validation_name)

        self.assertEqual(result.status, "status")
        self.assertEqual(result.details, "details")
        self.assertEqual(result.settings, "settings")
        self.assertEqual(result.last_execution, datetime(2020, 11, 19))
        self.collection.find_one.assert_called_with(
            {"validation_name": validation_name}
        )

    def test_save_validation_result_create(self):
        self.collection.count.return_value = 0
        response = ValidationResponse("name", "status", {})

        self.repository.save_validation_result(response)

        self.collection.insert_one.assert_called_with(
            {
                "validation_name": "name",
                "status": "status",
                "details": {},
                "settings": None,
                "last_execution": None,
            }
        )

    def test_save_validation_result_update(self):
        self.collection.count.return_value = 1
        response = ValidationResponse("name", "status", {})

        self.repository.save_validation_result(response)

        self.collection.update_many.assert_called_with(
            {"validation_name": "name"},
            {
                "$set": {
                    "validation_name": "name",
                    "status": "status",
                    "details": {},
                    "settings": None,
                    "last_execution": None,
                }
            },
        )
