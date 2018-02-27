import json
import unittest
from unittest import mock

import redis
from requests import HTTPError
import responses
from mockredis import MockRedis
from mockredis import mock_strict_redis_client

from secure_message.application import cache_client_token, put_token, get_client_token

class MockApp:
    config = {"CLIENT_ID": "test_id",
              "CLIENT_SECRET": "test_secret",
              "UAA_URL": "http://test",
              "REDIS_HOST": 'test',
              "REDIS_PORT": 0,
              "REDIS_DB": 0,
              }

class TestClientTokenFunctions(unittest.TestCase):
    """Test case for functions that interact with UAA to retrieve client tokens"""
    token = {
        "access_token" : "705288eea2474641bde364032d465157",
        "token_type" : "bearer",
        "expires_in" : 43199,
        "scope" : "clients.read emails.write scim.userids password.write idps.write notifications.write oauth.login scim.write critical_notifications.write",
        "jti" : "705288eea2474641bde364032d465157"
    }

    @mock.patch('redis.StrictRedis', mock_strict_redis_client)
    def test_cache_client_token(self):

        with mock.patch('secure_message.application.get_client_token', return_value=self.token):
            self.assertIsNone(cache_client_token(MockApp))

    @mock.patch('redis.StrictRedis', mock_strict_redis_client)
    def test_put_token(self):
        r = redis.StrictRedis()
        put_token(r, self.token)
        stored_token = r.get('secure-message-client-token').decode().replace("'", '"')
        self.assertEqual(self.token, json.loads(stored_token))


    @responses.activate
    @mock.patch('redis.StrictRedis', mock_strict_redis_client)
    def test_get_client_token(self):
        r = redis.StrictRedis()
        responses.add(responses.POST,
                      'http://test/oauth/token?grant_type=client_credentials&response_type=token&token_format=opaque',
                      json=self.token,
                      status=201)

        resp = get_client_token('test_id',
                                'test_secret',
                                'http://test')

        self.assertEqual(resp, self.token)

    @responses.activate
    @mock.patch('redis.StrictRedis', mock_strict_redis_client)
    def test_get_client_token_http_error_400_range(self):
        r = redis.StrictRedis()
        responses.add(responses.POST,
                      'http://test/oauth/token?grant_type=client_credentials&response_type=token&token_format=opaque',
                      json=self.token,
                      status=401)

        with self.assertRaises(SystemExit):
            resp = get_client_token('test_id',
                                    'test_secret',
                                    'http://test')

    @responses.activate
    @mock.patch('redis.StrictRedis', mock_strict_redis_client)
    def test_get_client_token_http_error_500_range(self):
        r = redis.StrictRedis()
        responses.add(responses.POST,
                      'http://test/oauth/token?grant_type=client_credentials&response_type=token&token_format=opaque',
                      json=self.token,
                      status=500)
        responses.add(responses.POST,
                      'http://test/oauth/token?grant_type=client_credentials&response_type=token&token_format=opaque',
                      json=self.token,
                      status=201)

        resp = get_client_token('test_id',
                                'test_secret',
                                'http://test')

        self.assertEqual(self.token, resp)


