import unittest
from datetime import timedelta
from unittest import mock

import maya
import responses
from sqlalchemy import create_engine

from secure_message import application
from secure_message.application import cache_client_token, get_client_token


class TestClientTokenFunctions(unittest.TestCase):
    """Test case for functions that interact with UAA to retrieve client tokens"""

    def setUp(self):
        """setup test environment"""
        self.app = application.create_app(config='TestConfig')
        self.client = self.app.test_client()
        self.engine = create_engine(self.app.config['SQLALCHEMY_DATABASE_URI'])

        self.oauth_client_token = {
            "access_token": "705288eea2474641bde364032d465157",
            "token_type": "bearer",
            "expires_in": 43199,
            "scope": "clients.read emails.write scim.userids password.write idps.write notifications.write oauth.login scim.write critical_notifications.write",
            "jti": "705288eea2474641bde364032d465157"
        }

    def test_set_expiry_on_startup(self):
        """Test token_expires_at is set on app startup"""
        with self.app.app_context():
            self.assertAlmostEqual(self.app.oauth_client_token_expires_at,
                                   maya.now(),
                                   delta=timedelta(seconds=1))

    def test_cache_client_token(self):
        with mock.patch('secure_message.application.get_client_token') as m:
            m.return_value = self.oauth_client_token
            with self.app.app_context():
                cache_client_token(self.app)
                self.assertTrue(m.called_with(self.app.config['CLIENT_ID'],
                                              self.app.config['CLIENT_SECRET'],
                                              self.app.config['UAA_URL']))
                self.assertEqual(self.app.oauth_client_token, self.oauth_client_token)
                self.assertAlmostEqual(self.app.oauth_client_token_expires_at,
                                       maya.now().add(seconds=self.oauth_client_token['expires_in'] - 10),
                                       delta=timedelta(1))

    @responses.activate
    def test_get_client_token(self):
        responses.add(responses.POST,
                      'http://test/oauth/token?grant_type=client_credentials&response_type=token&token_format=opaque',
                      json=self.oauth_client_token,
                      status=201)

        with self.app.app_context():
            resp = get_client_token('test_id',
                                    'test_secret',
                                    'http://test')
            self.assertEqual(resp, self.oauth_client_token)

    @responses.activate
    def test_get_client_token_http_error_400_range(self):
        responses.add(responses.POST,
                      'http://test/oauth/token?grant_type=client_credentials&response_type=token&token_format=opaque',
                      json=self.oauth_client_token,
                      status=401)

        with self.assertRaises(SystemExit):
            get_client_token('test_id',
                             'test_secret',
                             'http://test')

    @responses.activate
    def test_get_client_token_http_error_500_range(self):
        responses.add(responses.POST,
                      'http://test/oauth/token?grant_type=client_credentials&response_type=token&token_format=opaque',
                      json=self.oauth_client_token,
                      status=500)
        responses.add(responses.POST,
                      'http://test/oauth/token?grant_type=client_credentials&response_type=token&token_format=opaque',
                      json=self.oauth_client_token,
                      status=201)

        resp = get_client_token('test_id',
                                'test_secret',
                                'http://test')

        self.assertEqual(self.oauth_client_token, resp)
