import unittest

from flask import current_app, json
from sqlalchemy import create_engine

from secure_message import application, settings, constants
from secure_message.application import app
from secure_message.authentication.jwe import Encrypter
from secure_message.authentication.jwt import encode
from secure_message.repository import database


class LabelTestCase(unittest.TestCase):
    """ Test cases for label endpoint"""

    def setUp(self):
        """setup test environment"""
        self.app = application.app.test_client()
        self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        token_data = {
            constants.USER_IDENTIFIER: constants.BRES_USER,
            "role": "internal"
            }
        encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                              _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                              _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
        signed_jwt = encode(token_data)
        encrypted_jwt = encrypter.encrypt_token(signed_jwt)

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_jwt}

        settings.NOTIFY_CASE_SERVICE = '1'

        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    def test_invalid_label(self):
        """testing response from an invalid label"""
        self.url = "http://localhost:5050/labels?name=test"
        response = self.app.get(self.url, headers=self.headers)

        self.assertEqual(response.status_code, 400)

    def test_unread_label_response(self):
        """testing unread label"""
        self.url = "http://localhost:5050/labels?name=unread"
        response = self.app.get(self.url, headers=self.headers)

        self.assertEqual(response.status_code, 200)

    def test_unread_label_json(self):
        """ validating json response data"""
        self.url = "http://localhost:5050/labels?name=unread"
        response = self.app.get(self.url, headers=self.headers)
        data = {'name': 'unread', 'total': ''}

        self.assertEqual(json.loads(response.get_data()).keys(), data.keys())
