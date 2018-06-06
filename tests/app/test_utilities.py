import requests_mock
import unittest

from secure_message.application import create_app, get_client_token
from secure_message.common.utilities import MessageArgs, update_external_messages_to, update_internal_messages_from

BRES_SURVEY = "33333333-22222-3333-4444-88dc018a1a4c"


def get_args(page=1, limit=100, surveys=None, cc="", ru="", label="", desc=True, ce=""):
    return MessageArgs(page=page, limit=limit, ru_id=ru, surveys=surveys, cc=cc, label=label,
                       desc=desc, ce=ce)


class UtilitiesTestCase(unittest.TestCase):
    """Test cases for party service"""

    def setUp(self):
        """setup test environment"""
        self.app = create_app()
        self.app.testing = True

        self.app.oauth_client_token = get_client_token(self.app.config['CLIENT_ID'],
                                                       self.app.config['CLIENT_SECRET'],
                                                       self.app.config['UAA_URL'])

    user_info = {'id': 'bca50ef9-ff50-44b1-adf5-b6728e0bd360',
                 'lastLogonTime': 1528278309563,
                 'meta': {'created': '2018-06-06T09:36:31.509Z',
                          'lastModified': '2018-06-06T09:36:31.509Z',
                          'version': 0},
                 'name': {'name': 'John',
                          'givenName': 'Shaw',
                          'familyName': 'Shaw'},
                 'emails': [{'value': 'uaa_user',
                             'primary': False}],
                 'origin': 'uaa',
                 'passwordLastModified': '2018-06-06T09:36:31.000Z',
                 'previousLogonTime': 1528278248442,
                 'schemas': ['urn:scim:schemas:core:1.0'],
                 'userName': 'uaa_user',
                 'verified': True,
                 'zoneId': 'uaa'}

    messages = [{
        'body': 'Reply body from respondent',
        'collection_case': '',
        'collection_exercise': '',
        'from_internal': False,
        'labels': ['INBOX'],
        'msg_from': 'c8059a4d-5de0-4551-bdf2-09c8d1fe896e',
        'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513',
        'msg_to': ['GROUP'],
        'read_date': '2018-06-05 15:23:39.898317',
        'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251',
        'sent_date': '2018-06-05 15:23:38.025084',
        'subject': 'Message to ONS',
        'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54',
        'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6'}, {
        'body': 'Reply body from respondent',
        'collection_case': '',
        'collection_exercise': '',
        'from_internal': True,
        'labels': ['INBOX'],
        'msg_from': 'c8059a4d-5de0-4551-bdf2-09c8d1fe896e',
        'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513',
        'msg_to': ['GROUP'],
        'read_date': '2018-06-05 15:23:39.898317',
        'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251',
        'sent_date': '2018-06-05 15:23:38.025084',
        'subject': 'Message to ONS',
        'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54',
        'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6'}]

    def test_dictionary_update_for_message_to(self):
        self.assertNotIn('@msg_to', self.messages[0])
        update_external_messages_to(self.messages)
        self.assertIn('@msg_to', self.messages[0])

    @requests_mock.mock()
    def test_dictionary_update_for_message_from(self, mock_request):
        uuid = "c8059a4d-5de0-4551-bdf2-09c8d1fe896e"
        url = f"{self.app.config['UAA_URL']}/Users/{uuid}"
        mock_request.get(url, status_code=200, json=self.user_info)
        self.assertNotIn('@msg_to', self.messages[1])
        with self.app.app_context():
            update_internal_messages_from(self.messages)
        self.assertIn('@msg_from', self.messages[1])
