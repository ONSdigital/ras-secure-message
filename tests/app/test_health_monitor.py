import unittest

from flask import current_app, json

from secure_message import application
from secure_message.application import create_app
from secure_message.repository import database
from secure_message.repository.retriever import Retriever


class HealthTestCase(unittest.TestCase):
    """Test case for application health monitor"""
    def setUp(self):
        """setup test environment"""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True
        with self.app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    def test_health_status(self):
        """sends GET request to the application health monitor endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

    def test_db_health_status_healthy(self):
        """sends GET request to the application db health monitor endpoint"""
        response = self.client.get('/health/db')
        self.assertEqual(response.status_code, 200)

    def test_db_connection_test_fails(self):
        """runs check_db_connection function after dropping database"""
        with self.app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                response = Retriever().check_db_connection()
                self.assertEqual(response.status_code, 500)

    def test_keys_in_app_details_true(self):
        """sends GET request to the application health details endpoint"""
        response = self.client.get('/health/details')
        details = {'Name': '',
                   'Version': '',
                   'SMS Log level': '',
                   'APP Log Level': '',
                   'Database URL': '',
                   'API Functionality': '',
                   'Using party service mock': '',
                   'SM JWT ENCRYPT': '',
                   'RAS PARTY SERVICE HOST': '',
                   'RAS PARTY SERVICE PORT': '',
                   'RAS PARTY SERVICE PROTOCOL': '',
                   'NOTIFY VIA GOV NOTIFY': '',
                   'NOTIFY CASE SERVICE': ''}

        self.assertEqual(json.loads(response.get_data()).keys(), details.keys())


if __name__ == '__main__':
    unittest.main()