import unittest
from flask import json
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from app import application, constants, settings
from app.application import app
from app.common.utilities import get_business_details_by_ru, get_details_by_uuids
from app.authentication.jwe import Encrypter
from app.authentication.jwt import encode


def _generate_encrypted_token():
    token_data = {constants.USER_IDENTIFIER: "0a7ad740-10d5-4ecb-b7ca-3c0384afb882",
                  "role": "respondent"}

    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    encrypted_jwt = encrypter.encrypt_token(signed_jwt)
    return encrypted_jwt


class PartyTestCase(unittest.TestCase):
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """enable foreign key constraint for tests"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def test_get_user_details_by_uuid(self):
        """Test that user details are returned using uuids"""

        list_uuids = ['f62dfda8-73b0-4e0e-97cf-1b06327a6712']
        expected = {"id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                    "firstName": "Bhavana",
                    "lastName": "Lincoln",
                    "emailAddress": "lincoln.bhavana@gmail.com",
                    "telephone": "+443069990888",
                    "status": "ACTIVE",
                    "sampleUnitType": "BI"}
        user_details = get_details_by_uuids(list_uuids)
        result = user_details[0]
        self.assertTrue(result == expected)

    def test_get_user_details_by_uuids(self):
        """Test that user details are returned using uuids"""

        list_uuids = ['f62dfda8-73b0-4e0e-97cf-1b06327a6712',
                      '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                      'dd5a38ff-1ecb-4634-94c8-2358df33e614',
                      'ab123456-ce17-40c2-a8fc-abcdef123456',
                      '654321ab-ce17-40c2-a8fc-abcdef123456'
                     ]

        user_details = get_details_by_uuids(list_uuids)

        self.assertEqual(user_details[0], {"id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                                           "firstName": "Bhavana",
                                           "lastName": "Lincoln",
                                           "emailAddress": "lincoln.bhavana@gmail.com",
                                           "telephone": "+443069990888",
                                           "status": "ACTIVE",
                                           "sampleUnitType": "BI"})
        self.assertEqual(user_details[1], {"id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
                                           "firstName": "Chandana",
                                           "lastName": "Blanchet",
                                           "emailAddress": "cblanc@hotmail.co.uk",
                                           "telephone": "+443069990854",
                                           "status": "ACTIVE",
                                           "sampleUnitType": "BI"})
        self.assertEqual(user_details[2], {"id": "dd5a38ff-1ecb-4634-94c8-2358df33e614",
                                           "firstName": "Ida",
                                           "lastName": "Larue",
                                           "emailAddress": "ilarue47@yopmail.com",
                                           "telephone": "+443069990250",
                                           "status": "ACTIVE",
                                           "sampleUnitType": "BI"})
        expected = {"associations": [
                                           {"enrolments": [
                                               {
                                                   "enrolmentStatus": "ENABLED",
                                                   "name": "Business Register and Employment Survey",
                                                   "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
                                               }

                                           ],
                                            "partyId": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
                                            "sampleUnitRef": "50012345678"
                                            }
                                        ],
                                        "id": "ab123456-ce17-40c2-a8fc-abcdef123456",
                                        "firstName": "Ivor",
                                        "lastName": "Bres",
                                        "emailAddress": "ivor.bres@hostmail.com",
                                        "telephone": "+447894056785",
                                        "status": "ACTIVE",
                                        "sampleUnitType": "BI"}
        self.assertEqual(user_details[3], expected)
        expected = {"associations": [
                                                                   {"enrolments": [],
                                                                    "partyId": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
                                                                    "sampleUnitRef": "50012345678"
                                                                    }
                                                               ],
                                                                   "id": "654321ab-ce17-40c2-a8fc-abcdef123456",
                                                                   "firstName": "IvorNot",
                                                                   "lastName": "Bres",
                                                                   "emailAddress": "ivorNot.bres@hostmail.com",
                                                                   "telephone": "+447894056786",
                                                                   "status": "ACTIVE",
                                                                   "sampleUnitType": "BI"}

        self.assertEqual(user_details[4], expected)

    # def test_get_user_details_by_invalid_uuid(self):
    #     """Test that function returns error when invalid uuid present"""
    #
    #     list_uuids = ['f62dfda8-73b0-4e0e-97cf-1b06327a6778']
    #
    #     with self.assertRaises(ExpectationFailed):
    #         get_details_by_uuids(list_uuids)
    #
    # def test_get_business_details_by_invalid_ru(self):
    #     """Test that function returns error when invalid ru present"""
    #
    #     list_ru = ['f62dfda8-73b0-4e0e-97cf-1b06327a6778']
    #
    #     with self.assertRaises(ExpectationFailed):
    #         get_business_details_by_ru(list_ru)

    def test_message_by_id_replaces_uuids(self):
        """Test get message by id endpoint replaces to and from with user details"""
        data = {'msg_to': [constants.BRES_USER],
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                'survey': constants.BRES_SURVEY}

        encrypted_token = _generate_encrypted_token()

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_token}

        self.app = application.app.test_client()

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        resp = self.app.post("http://localhost:5050/message/send", data=json.dumps(data), headers=self.headers)
        resp_data = json.loads(resp.data)
        msg_id = resp_data['msg_id']

        message_resp = self.app.get("http://localhost:5050/message/{}".format(msg_id), headers=self.headers)
        message = json.loads(message_resp.data)

        self.assertEqual(message['@msg_from'], {'telephone': '+443069990289',
                                                'firstName': 'Vana',
                                                'emailAddress': 'vana123@aol.com',
                                                'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                                'status': 'ACTIVE',
                                                'lastName': 'Oorschot',
                                                'sampleUnitType': 'BI'
                                                })
        self.assertEqual(message['@msg_to'], [{"id": "BRES",
                                               "firstName": "BRES",
                                               "lastName": "",
                                               "emailAddress": "",
                                               "telephone": "",
                                               "status": "",
                                               "sampleUnitType": "BI"
                                               }])

    def test_messages_get_replaces_uuids_with_user_details(self):
        """Test get all messages endpoint replaces every messages to and from with user details"""
        data = {'msg_to': [constants.BRES_USER],
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                'survey': constants.BRES_SURVEY}

        self.app = application.app.test_client()

        encrypted_token = _generate_encrypted_token()

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_token}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        self.app.post("http://localhost:5050/message/send", data=json.dumps(data), headers=self.headers)
        self.app.post("http://localhost:5050/message/send", data=json.dumps(data), headers=self.headers)

        messages_get = self.app.get("http://localhost:5050/messages", headers=self.headers)
        get_return = json.loads(messages_get.data)
        messages = get_return['messages']

        for message in messages:
            self.assertEqual(message['@msg_from'], {'firstName': 'Vana',
                                                    'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                                    'status': 'ACTIVE',
                                                    'telephone': '+443069990289',
                                                    'lastName': 'Oorschot',
                                                    'emailAddress': 'vana123@aol.com',
                                                    'sampleUnitType': 'BI'
                                                    })

    def test_draft_get_return_user_details_for_to_and_from(self):
        """Test get draft replaces sender and recipient with user details"""
        data = {'msg_to': [constants.BRES_USER],
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                'survey': constants.BRES_SURVEY}

        self.app = application.app.test_client()

        encrypted_token = _generate_encrypted_token()

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_token}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        draft_resp = self.app.post("http://localhost:5050/draft/save", data=json.dumps(data), headers=self.headers)
        draft_details = json.loads(draft_resp.data)
        draft_id = draft_details['msg_id']

        draft_get = self.app.get("http://localhost:5050/draft/{}".format(draft_id), headers=self.headers)
        draft = json.loads(draft_get.data)

        self.assertEqual(draft['@msg_from'], {'telephone': '+443069990289', 'firstName': 'Vana',
                                              'emailAddress': 'vana123@aol.com',
                                              'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                              'status': 'ACTIVE', 'lastName': 'Oorschot',
                                              'sampleUnitType': 'BI'})

    def test_drafts_get_return_user_details_in_to_and_from(self):
        """Test get all drafts returns to and from as user details"""
        data = {'msg_to': [constants.BRES_USER],
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                'survey': constants.BRES_SURVEY}

        self.app = application.app.test_client()

        encrypted_token = _generate_encrypted_token()

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_token}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        self.app.post("http://localhost:5050/draft/save", data=json.dumps(data), headers=self.headers)
        self.app.post("http://localhost:5050/draft/save", data=json.dumps(data), headers=self.headers)

        drafts_get = self.app.get("http://localhost:5050/drafts", headers=self.headers)
        drafts_data = json.loads(drafts_get.data)
        drafts = drafts_data['messages']

        for draft in drafts:
            self.assertEqual(draft['@msg_from'], {'telephone': '+443069990289',
                                                  'firstName': 'Vana',
                                                  'emailAddress': 'vana123@aol.com',
                                                  'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                                  'status': 'ACTIVE',
                                                  'lastName': 'Oorschot',
                                                  'sampleUnitType': 'BI'})
            self.assertEqual(draft['@msg_to'][0], {"id": constants.BRES_SURVEY,
                                                   "firstName": "BRES",
                                                   "lastName": "",
                                                   "emailAddress": "",
                                                   "telephone": "", "status": "",
                                                   "sampleUnitType": "BI"})

    def test_get_business_details_by_ru(self):
        """Test get details for one business using ru_id"""

        list_ru = ['f1a5e99c-8edf-489a-9c72-6cabe6c387fc']

        business_details = get_business_details_by_ru(list_ru)

        self.assertEqual(business_details[0]['id'], list_ru[0])
        self.assertEqual(business_details[0]['name'], "Apple")

    def test_get_business_details_multiple_ru(self):
        """Test business details are returned for multiple ru's"""

        list_ru = ['0a6018a0-3e67-4407-b120-780932434b36',
                   'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                   'c614e64e-d981-4eba-b016-d9822f09a4fb',
                   'b3ba864b-7cbc-4f44-84fe-88dc018a1a4c'
                   ]

        business_details = get_business_details_by_ru(list_ru)

        self.assertEqual(business_details[0]['id'], list_ru[0])
        self.assertEqual(business_details[1]['id'], list_ru[1])
        self.assertEqual(business_details[2]['id'], list_ru[2])
        self.assertEqual(business_details[3]['id'], list_ru[3])

    def test_get_message_returns_business_details(self):
        """Test get message by id returns business details"""

        data = {'msg_to': [constants.BRES_USER],
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                'survey': constants.BRES_SURVEY}

        self.app = application.app.test_client()

        encrypted_token = _generate_encrypted_token()

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_token}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        message_post = self.app.post("http://localhost:5050/message/send", data=json.dumps(data), headers=self.headers)
        message_data = json.loads(message_post.data)
        msg_id = message_data['msg_id']

        message_get = self.app.get("http://localhost:5050/message/{}".format(msg_id), headers=self.headers)
        message = json.loads(message_get.data)

        self.assertEqual(message['@ru_id']['name'], "Apple")

    def test_get_messages_returns_business_details(self):
        """Test get all messages returns business details"""

        data = {'msg_to': [constants.BRES_USER],
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                'survey': constants.BRES_SURVEY}

        self.app = application.app.test_client()

        encrypted_token = _generate_encrypted_token()

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_token}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        self.app.post("http://localhost:5050/message/send", data=json.dumps(data), headers=self.headers)
        self.app.post("http://localhost:5050/message/send", data=json.dumps(data), headers=self.headers)

        messages_get = self.app.get("http://localhost:5050/messages", headers=self.headers)
        get_return = json.loads(messages_get.data)
        messages = get_return['messages']

        for message in messages:
            self.assertEqual(message['@ru_id']['name'], "Apple")

    def test_get_draft_returns_business_details(self):
        """Test get draft returns business details"""

        data = {'msg_to': [constants.BRES_USER],
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                'survey': constants.BRES_SURVEY}

        self.app = application.app.test_client()

        encrypted_token = _generate_encrypted_token()

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_token}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        draft_save = self.app.post("http://localhost:5050/draft/save", data=json.dumps(data), headers=self.headers)
        draft_data = json.loads(draft_save.data)
        draft_id = draft_data['msg_id']

        message_get = self.app.get("http://localhost:5050/draft/{}".format(draft_id), headers=self.headers)
        message = json.loads(message_get.data)

        self.assertEqual(message['@ru_id']['name'], "Apple")

    def test_get_drafts_returns_business_details(self):
        """Test get all drafts includes business details"""

        data = {'msg_to': [constants.BRES_USER],
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                'survey': constants.BRES_SURVEY}

        self.app = application.app.test_client()

        encrypted_token = _generate_encrypted_token()

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_token}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        self.app.post("http://localhost:5050/draft/save", data=json.dumps(data), headers=self.headers)
        self.app.post("http://localhost:5050/draft/save", data=json.dumps(data), headers=self.headers)

        drafts_get = self.app.get("http://localhost:5050/drafts", headers=self.headers)
        drafts_data = json.loads(drafts_get.data)
        drafts = drafts_data['messages']

        for draft in drafts:
            self.assertEqual(draft['@ru_id']['name'], "Apple")


if __name__ == '__main__':
    unittest.main()
