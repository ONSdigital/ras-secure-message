import unittest

from flask import current_app
from flask import json

from app import application
from app.application import app
from app.repository import database
from app.repository.retriever import Retriever
from sqlalchemy.engine import Engine
from sqlalchemy import event

class HealthTestCase(unittest.TestCase):
    """Test case for application health monitor"""
    def setUp(self):
        """setup test environment"""
        self.app = application.app.test_client()
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """enable foreign key constraint for tests"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def test_health_status(self):
        """sends GET request to the application health monitor endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)

    def test_db_health_status_healthy(self):
        """sends GET request to the application db health monitor endpoint"""
        response = self.app.get('/health/db')
        self.assertEqual(response.status_code, 200)

    def test_db_connection_test_fails(self):
        """runs check_db_connection function after dropping database"""
        with app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                response = Retriever().check_db_connection()
                self.assertEqual(response.status_code, 500)

    def test_keys_in_app_details_true(self):
        """sends GET request to the application health details endpoint"""
        response = self.app.get('/health/details')
        details = {'SMS Log level': '',
                   'APP Log Level': '',
                   'Database URL': '',
                   'API Functionality': ''
                   }
        self.assertEqual(json.loads(response.get_data()).keys(), details.keys())
