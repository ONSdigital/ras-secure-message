import unittest

from flask import current_app, json
from sqlalchemy import create_engine

from secure_message import constants
from secure_message.application import create_app
from secure_message.authentication.jwe import Encrypter
from secure_message.authentication.jwt import encode
from secure_message.repository import database


class LabelTestCase(unittest.TestCase):
    """ Test cases for label endpoint"""

    def setUp(self):
        """setup test environment"""
        self.app = create_app()
        self.client = self.app.test_client()
        self.engine = create_engine(self.app.config['SQLALCHEMY_DATABASE_URI'])
        token_data = {
            constants.USER_IDENTIFIER: constants.BRES_USER,
            "role": "internal"
            }
        encrypter = Encrypter(_private_key=self.app.config['SM_USER_AUTHENTICATION_PRIVATE_KEY'],
                              _private_key_password=self.app.config['SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD'],
                              _public_key=self.app.config['SM_USER_AUTHENTICATION_PUBLIC_KEY'])

        with self.app.app_context():
            signed_jwt = encode(token_data)
            encrypted_jwt = encrypter.encrypt_token(signed_jwt)

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_jwt}

        self.app.config['NOTIFY_CASE_SERVICE'] = '1'

        with self.app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    def test_invalid_label(self):
        """testing response from an invalid label"""
        self.url = "http://localhost:5050/labels?name=test"
        response = self.client.get(self.url, headers=self.headers)

        self.assertEqual(response.status_code, 400)

    def test_unread_label_response(self):
        """testing unread label"""
        self.url = "http://localhost:5050/labels?name=unread"
        response = self.client.get(self.url, headers=self.headers)

        self.assertEqual(response.status_code, 200)

    def test_unread_label_json(self):
        """ validating json response data"""
        self.url = "http://localhost:5050/labels?name=unread"
        response = self.client.get(self.url, headers=self.headers)
        data = {'name': 'unread', 'total': ''}

        self.assertEqual(json.loads(response.get_data()).keys(), data.keys())


if __name__ == '__main__':
    unittest.main()