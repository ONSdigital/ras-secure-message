from flask import json

from app.authentication.jwe import Encrypter
from app.authentication.jwt import encode
from app import settings
from app import constants
from app.common import utilities
import copy


class BddTestHelper:
    """The Bdd test helper is used to pass information between steps . In use it is attached to the context
    The message data holds data that will be sent to an endpoint
    single_message_responses_data holds responses regarding a specific message
    messages_responses_data holds responses regarding lists of messages . Both are lists so can hold multiple responses
    if needed

    """
    __DEFAULT_RU = 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc'
    __ALTERNATE_RU = 'b3ba864b-7cbc-4f44-84fe-88dc018a1a4c'

    __DEFAULT_SURVEY = constants.BRES_SURVEY
    __ALTERNATE_SURVEY = '11111111-22222-3333-4444-88dc018a1a4c'

    __DEFAULT_COLLECTION_CASE = 'collection case1'
    __ALTERNATE_COLLECTION_CASE = 'AnotherCollectionCase'

    __DEFAULT_COLLECTION_EXERCISE = 'collection exercise1'
    __ALTERNATE_COLLECTION_EXERCISE = 'AnotherCollectionExercise'

    __INTERNAL_USER_TOKEN = {constants.USER_IDENTIFIER: "BRES", "role": "internal"}

    __RESPONDENT_USER_ID = "01b51fcc-ed43-4cdb-ad1c-450f9986859b"
    __RESPONDENT_USER_TOKEN = {constants.USER_IDENTIFIER: __RESPONDENT_USER_ID, "role": "respondent"}

    __ALTERNATIVE_RESPONDENT_USER_ID = "0a7ad740-10d5-4ecb-b7ca-3c0384afb882"
    __ALTERNATIVE_RESPONDENT_USER_TOKEN = {constants.USER_IDENTIFIER: __ALTERNATIVE_RESPONDENT_USER_ID,
                                           "role": "respondent"}

    __default_message_data = data = {'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                                     'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                                     'subject': 'Hello World',
                                     'body': 'Test',
                                     'thread_id': '',
                                     'collection_case': __DEFAULT_COLLECTION_CASE,
                                     'collection_exercise': __DEFAULT_COLLECTION_EXERCISE,
                                     'ru_id': __DEFAULT_RU,
                                     'survey': __DEFAULT_SURVEY}



    def __init__(self):
        self._token_data = {}
        self._headers = {'Content-Type': 'application/json', 'Authorization': ''}
        self.token_data = BddTestHelper.__INTERNAL_USER_TOKEN  # use attribute to set headers
        self._message_data = copy.deepcopy(BddTestHelper.__default_message_data)
        self._sent_messages = []
        self._single_message_responses_data = []
        self._messages_responses_data = []
        self._last_saved_message_data = None
        self._message_post_url = 'http://localhost:5050/message/send'   # todo get these from settings
        self._message_get_url = 'http://localhost:5050/message/{0}'
        self._draft_post_url = "http://localhost:5050/draft/save"
        self._draft_put_url = "http://localhost:5050/draft/{0}/modify"
        self._draft_get_url = "http://localhost:5050/draft/{0}"
        self._message_put_url = "http://localhost:5050/message/{}/modify"
        self._messages_get_url = "http://localhost:5050/messages"
        self._drafts_get_url = "http://localhost:5050/drafts"

    @staticmethod
    def _encrypt_token_data(token_data):
        encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                              _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                              _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
        signed_jwt = encode(token_data)
        return encrypter.encrypt_token(signed_jwt)

    @property
    def token_data(self):
        return self._token_data

    @token_data.setter         # headers property automatically updated each time token_data changed
    def token_data(self, value):
        self._token_data = value
        self._headers['Authorization'] = self._encrypt_token_data(self._token_data)

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value

    @property
    def message_data(self):
        return self._message_data

    @message_data.setter
    def message_data(self, value):
        self._message_data = value

    @property       # return an internal user that the client is free to change
    def internal_user_token(self):
        return copy.deepcopy(BddTestHelper.__INTERNAL_USER_TOKEN)

    @property       # return an external user that the client is free to change
    def respondent_user_token(self):
        return copy.deepcopy(BddTestHelper.__RESPONDENT_USER_TOKEN)

    @property
    def alternative_respondent_user_token(self):
        return copy.deepcopy(BddTestHelper.__ALTERNATIVE_RESPONDENT_USER_TOKEN)

    @property
    def message_post_url(self):
        return self._message_post_url

    @property
    def message_get_url(self):
        return self._message_get_url

    @property
    def messages_get_url(self):
        return self._messages_get_url

    @property
    def message_put_url(self):
        return self._message_put_url

    @property
    def draft_post_url(self):
        return self._draft_post_url

    @property
    def draft_put_url(self):
        return self._draft_put_url

    @property
    def draft_get_url(self):
        return self._draft_get_url

    @property
    def drafts_get_url(self):
        return self._drafts_get_url

    @property
    def respondent_id(self):
        return copy.copy(BddTestHelper.__RESPONDENT_USER_ID)

    @property
    def alternative_respondent_id(self):
        return copy.copy(BddTestHelper.__ALTERNATIVE_RESPONDENT_USER_ID)

    @property
    def internal_id(self):
        return copy.copy(constants.BRES_USER)

    @property
    def last_saved_message_data(self):
        return copy.deepcopy(self.sent_messages[len(self.sent_messages)-1])

    @last_saved_message_data.setter
    def last_saved_message_data(self, value):
        self._last_saved_message_data = copy.deepcopy(value)

    @property
    def sent_messages(self):
        return self._sent_messages   # allows direct access

    @property
    def single_message_responses_data(self):
        return self._single_message_responses_data

    def store_last_single_message_response_data(self, response):
        response_data = json.loads(response.data)
        self._single_message_responses_data.append(response_data)

    @property
    def messages_responses_data(self):
        return self._messages_responses_data

    def store_messages_response_data(self, response):
        response_data = json.loads(response)  # Handle the fact that get mesages returns data differently
        self._messages_responses_data.append(response_data)

    def set_message_data_to_a_prior_version(self, message_index):
        self._message_data = copy.deepcopy(self.sent_messages[message_index])

    def get_etag(self, message_data):
        if 'msg_to' in self._message_data:
            return utilities.generate_etag(message_data['msg_to'],
                                           message_data['msg_id'],
                                           message_data['subject'],
                                           message_data['body'])

    def use_alternate_ru(self):
        self._message_data['ru_id'] = BddTestHelper.__ALTERNATE_RU

    def use_default_ru(self):
        self._message_data['ru_id'] = BddTestHelper.__DEFAULT_RU

    def use_alternate_survey(self):
        self._message_data['survey'] = BddTestHelper.__ALTERNATE_SURVEY

    def use_default_survey(self):
        self._message_data['survey'] = BddTestHelper.__DEFAULT_SURVEY

    def use_alternate_collection_case(self):
        self._message_data['collection_case'] = BddTestHelper.__ALTERNATE_COLLECTION_CASE

    def use_default_collection_case(self):
        self._message_data['collection_case'] = BddTestHelper.__DEFAULT_COLLECTION_CASE

    def use_alternate_collection_exercise(self):
        self._message_data['collection_exercise'] = BddTestHelper.__ALTERNATE_COLLECTION_EXERCISE

    def use_default_collection_exercise(self):
        self._message_data['collection_exercise'] = BddTestHelper.__DEFAULT_COLLECTION_EXERCISE

