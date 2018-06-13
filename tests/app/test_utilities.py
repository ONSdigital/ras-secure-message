import copy
import unittest

from secure_message.application import create_app
from secure_message.common.utilities import MessageArgs, get_to_details, get_from_details, add_business_details
from secure_message.services.service_toggles import party, internal_user_service

BRES_SURVEY = "33333333-22222-3333-4444-88dc018a1a4c"


def get_args(page=1, limit=100, surveys=None, cc="", ru="", label="", desc=True, ce=""):
    return MessageArgs(page=page, limit=limit, ru_id=ru, surveys=surveys, cc=cc, label=label,
                       desc=desc, ce=ce)


class UtilitiesTestCase(unittest.TestCase):
    """Test cases for Utilities"""

    def setUp(self):
        """setup test environment"""
        self.app = create_app()
        self.app.testing = True
        party.use_mock_service()
        internal_user_service.use_mock_service()

    messages_external_first = [{'body': 'Reply body from respondent',
                                'collection_case': '',
                                'collection_exercise': '',
                                'from_internal': False,
                                'labels': ['INBOX'],
                                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513',
                                'msg_to': ['01b51fcc-ed43-4cdb-ad1c-450f9986859b'],
                                'read_date': '2018-06-05 15:23:39.898317',
                                'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251',
                                'sent_date': '2018-06-05 15:23:38.025084',
                                'subject': 'Message to ONS',
                                'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54',
                                'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6'},
                               {'body': 'Reply body from internal user',
                                'collection_case': '',
                                'collection_exercise': '',
                                'from_internal': True,
                                'labels': ['INBOX'],
                                'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                                'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513',
                                'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                                'read_date': '2018-06-05 15:23:39.898317',
                                'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251',
                                'sent_date': '2018-06-05 15:23:38.025084',
                                'subject': 'Message to ONS',
                                'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54',
                                'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6'}]

    messages_internal_first = [{'body': 'Reply body from internal user',
                                'collection_case': '',
                                'collection_exercise': '',
                                'from_internal': True,
                                'labels': ['INBOX'],
                                'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                                'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513',
                                'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                                'read_date': '2018-06-05 15:23:39.898317',
                                'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251',
                                'sent_date': '2018-06-05 15:23:38.025084',
                                'subject': 'Message to ONS',
                                'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54',
                                'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6'},
                               {'body': 'Reply body from respondent',
                                'collection_case': '',
                                'collection_exercise': '',
                                'from_internal': False,
                                'labels': ['INBOX'],
                                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513',
                                'msg_to': ['01b51fcc-ed43-4cdb-ad1c-450f9986859b'],
                                'read_date': '2018-06-05 15:23:39.898317',
                                'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251',
                                'sent_date': '2018-06-05 15:23:38.025084',
                                'subject': 'Message to ONS',
                                'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54',
                                'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6'}]

    internal_user_record = {'id': '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'firstName': 'fred', 'lastName': 'flinstone', 'emailAddress': 'mock@email.com'}

    external_user_record = {"id": "0a7ad740-10d5-4ecb-b7ca-3c0384afb882", "firstName": "Vana", "lastName": "Oorschot",
                            "emailAddress": "vana123@aol.com", "telephone": "+443069990289", "status": "ACTIVE", "sampleUnitType": "BI"}

    @unittest.skip("rework")
    def test_get_business_details(self):
        messages_business_internal_first_copy = copy.deepcopy(self.messages_internal_first)

        with self.app.app_context():
            result = add_business_details(messages_business_internal_first_copy)
            print(result)
            self.assertEqual(result, [])

    def test_get_from_details_with_external_message_first(self):

        populated_message = [{'body': 'Reply body from respondent', 'collection_case': '', 'collection_exercise': '', 'from_internal': False,
                              'labels': ['INBOX'], 'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513', 'msg_to': ['01b51fcc-ed43-4cdb-ad1c-450f9986859b'], 'read_date': '2018-06-05 15:23:39.898317', 'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251', 'sent_date': '2018-06-05 15:23:38.025084', 'subject': 'Message to ONS', 'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54', 'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6', '@msg_from': {'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'firstName': 'Vana', 'lastName': 'Oorschot', 'emailAddress': 'vana123@aol.com', 'telephone': '+443069990289', 'status': 'ACTIVE', 'sampleUnitType': 'BI'}},
                             {'body': 'Reply body from internal user', 'collection_case': '', 'collection_exercise': '', 'from_internal': True,
                              'labels': ['INBOX'], 'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513', 'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'], 'read_date': '2018-06-05 15:23:39.898317', 'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251', 'sent_date': '2018-06-05 15:23:38.025084', 'subject': 'Message to ONS', 'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54', 'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6', '@msg_from': {'id': '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'firstName': 'fred', 'lastName': 'flinstone', 'emailAddress': 'mock@email.com'}}]

        messages_from_external_first_copy = copy.deepcopy(self.messages_external_first)
        for message in messages_from_external_first_copy:
            self.assertNotIn('@msg_from', message)

        with self.app.app_context():
            result = get_from_details(messages_from_external_first_copy)
            for message in result:
                self.assertIn('@msg_from', message)

            self.assertEqual(result[0]['@msg_from'], self.external_user_record)
            self.assertEqual(result[1]['@msg_from'], self.internal_user_record)

            print(result)
            self.assertEqual(result[0], populated_message[0])
            self.assertEqual(result[1], populated_message[1])

    def test_get_from_details_with_internal_message_first(self):

        populated_message = [{'body': 'Reply body from internal user', 'collection_case': '', 'collection_exercise': '', 'from_internal': True, 'labels': ['INBOX'], 'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513', 'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'], 'read_date': '2018-06-05 15:23:39.898317', 'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251', 'sent_date': '2018-06-05 15:23:38.025084', 'subject': 'Message to ONS', 'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54', 'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6', '@msg_from': {'id': '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'firstName': 'fred', 'lastName': 'flinstone', 'emailAddress': 'mock@email.com'}},
                             {'body': 'Reply body from respondent', 'collection_case': '', 'collection_exercise': '', 'from_internal': False, 'labels': ['INBOX'], 'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513', 'msg_to': ['01b51fcc-ed43-4cdb-ad1c-450f9986859b'], 'read_date': '2018-06-05 15:23:39.898317', 'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251', 'sent_date': '2018-06-05 15:23:38.025084', 'subject': 'Message to ONS', 'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54', 'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6', '@msg_from': {'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'firstName': 'Vana', 'lastName': 'Oorschot', 'emailAddress': 'vana123@aol.com', 'telephone': '+443069990289', 'status': 'ACTIVE', 'sampleUnitType': 'BI'}}]

        messages_from_internal_first_copy = copy.deepcopy(self.messages_internal_first)
        for message in messages_from_internal_first_copy:
            self.assertNotIn('@msg_from', message)
        with self.app.app_context():
            result = get_from_details(messages_from_internal_first_copy)
            for message in result:
                self.assertIn('@msg_from', message)
            self.assertEqual(result[0]['@msg_from'], self.internal_user_record)
            self.assertEqual(result[1]['@msg_from'], self.external_user_record)

            print(result)
            self.assertEqual(result[0], populated_message[0])
            self.assertEqual(result[1], populated_message[1])

    def test_get_to_details_with_external_message_first(self):

        populated_message = [{'body': 'Reply body from respondent', 'collection_case': '', 'collection_exercise': '', 'from_internal': False,
                              'labels': ['INBOX'], 'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513',
                              'msg_to': ['01b51fcc-ed43-4cdb-ad1c-450f9986859b'], 'read_date': '2018-06-05 15:23:39.898317',
                              'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251', 'sent_date': '2018-06-05 15:23:38.025084', 'subject': 'Message to ONS',
                              'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54', 'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6',
                              '@msg_to': {'id': '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'firstName': 'fred',
                                          'lastName': 'flinstone', 'emailAddress': 'mock@email.com'}},
                             {'body': 'Reply body from internal user', 'collection_case': '', 'collection_exercise': '', 'from_internal': True,
                              'labels': ['INBOX'], 'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513',
                              'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'], 'read_date': '2018-06-05 15:23:39.898317',
                              'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251', 'sent_date': '2018-06-05 15:23:38.025084', 'subject': 'Message to ONS',
                              'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54', 'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6',
                              '@msg_to': [{'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'firstName': 'Vana', 'lastName': 'Oorschot',
                                           'emailAddress': 'vana123@aol.com', 'telephone': '+443069990289', 'status': 'ACTIVE', 'sampleUnitType': 'BI'}]}]

        messages_to_external_first_copy = copy.deepcopy(self.messages_external_first)
        for message in messages_to_external_first_copy:
            self.assertNotIn('@msg_to', message)

        with self.app.app_context():
            result = get_to_details(messages_to_external_first_copy)
            for message in result:
                self.assertIn('@msg_to', message)

            self.assertEqual(result[0]['@msg_to'], self.internal_user_record)
            self.assertEqual(result[1]['@msg_to'], [self.external_user_record])

            self.assertEqual(result[0], populated_message[0])
            self.assertEqual(result[1], populated_message[1])

    def test_get_to_details_with_internal_message_first(self):

        populated_message = [{'body': 'Reply body from internal user', 'collection_case': '', 'collection_exercise': '', 'from_internal': True,
                              'labels': ['INBOX'], 'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513',
                              'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'], 'read_date': '2018-06-05 15:23:39.898317',
                              'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251', 'sent_date': '2018-06-05 15:23:38.025084', 'subject': 'Message to ONS',
                              'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54', 'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6',
                              '@msg_to': [{'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'firstName': 'Vana', 'lastName': 'Oorschot',
                                           'emailAddress': 'vana123@aol.com', 'telephone': '+443069990289', 'status': 'ACTIVE', 'sampleUnitType': 'BI'}]},
                             {'body': 'Reply body from respondent', 'collection_case': '', 'collection_exercise': '', 'from_internal': False,
                              'labels': ['INBOX'], 'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'msg_id': '048ffdb5-18f0-46f0-bfa0-ea298521c513',
                              'msg_to': ['01b51fcc-ed43-4cdb-ad1c-450f9986859b'], 'read_date': '2018-06-05 15:23:39.898317',
                              'ru_id': '6c141ebb-10d1-4065-ac3e-ef5b5c95d251', 'sent_date': '2018-06-05 15:23:38.025084', 'subject': 'Message to ONS',
                              'survey': 'cb8accda-6118-4d3b-85a3-149e28960c54', 'thread_id': '53a430f1-de21-4279-b17e-1bfb4c4813a6',
                              '@msg_to': {'id': '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'firstName': 'fred', 'lastName': 'flinstone',
                                          'emailAddress': 'mock@email.com'}}]

        messages_to_internal_first_copy = copy.deepcopy(self.messages_internal_first)
        for message in messages_to_internal_first_copy:
            self.assertNotIn('@msg_to', message)

        with self.app.app_context():
            result = get_to_details(messages_to_internal_first_copy)
            for message in result:
                self.assertIn('@msg_to', message)

            self.assertEqual(result[0]['@msg_to'], [self.external_user_record])
            self.assertEqual(result[1]['@msg_to'], self.internal_user_record)

            self.assertEqual(result[0], populated_message[0])
            self.assertEqual(result[1], populated_message[1])
