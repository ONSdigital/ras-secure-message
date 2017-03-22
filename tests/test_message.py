import unittest
import json
import sys
sys.path.append('../ras-secure-message')
from app.domain_model.domain import Message, MessageSchema


class MessageTestCase(unittest.TestCase):
    """Test case for message validation"""
    def test_message(self):
        """creating message object"""
        message = Message('me', 'you', 'tomorrow')
        self.assertEquals(repr(message), '<Message(msg_to=me msg_from=you body=tomorrow)>')

    def test_message_not_equal(self):
        """creating message objects that are not equal"""
        message1 = Message('1', '2', '3')
        message2 = Message('1', '2', '4')
        self.assertTrue(message1 != message2)

    def test_message_equal(self):
        """creating message objects that are equal"""
        message1 = Message('1', '2', '3')
        message2 = Message('1', '2', '3')
        self.assertTrue(message1 == message2)

    def test_marshal_json(self):
        """marshaling from message object json"""
        message = Message('richard', 'torrance', 'hello')
        schema = MessageSchema()
        json_result = schema.dumps(message)
        message_load = schema.load(json.loads(json_result.data))
        self.assertTrue(message_load.data == message)

    def test_validation_true(self):
        """message marshalling passes all validation"""
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {})

    def test_msg_to_max_length_validation_false(self):
        """message marshalling fails max length for msg_to field"""
        msg_to = "x" * 101
        message = {'msg_to': msg_to, 'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_to': ['Quantity must not be greater than 100.']})

    def test_msg_to_min_length_validation_false(self):
        """message marshalling fails min length for msg_to field"""
        message = {'msg_to': '', 'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_to': ['Quantity must be greater than 0.']})

    def test_msg_to_required_validation_false(self):
        """message marshalling fails msg_to not given"""
        message = {'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_to': ['Missing data for required field.']})

    def test_msg_from_max_length_validation_false(self):
        """message marshalling fails max length for msg_from field"""
        msg_from = "x" * 101
        message = {'msg_to': 'richard', 'msg_from': msg_from, 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_from': ['Quantity must not be greater than 100.']})

    def test_msg_from_min_length_validation_false(self):
        """message marshalling fails min length for msg_from field"""
        message = {'msg_to': 'richard', 'msg_from': '', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_from': ['Quantity must be greater than 0.']})

    def test_msg_from_required_validation_false(self):
        """message marshalling fails msg_from not given"""
        message = {'msg_to': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_from': ['Missing data for required field.']})

    def test_body_max_length_validation_false(self):
        """message marshalling fails max length for body field"""
        body = "x" * 10001
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': body}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'body': ['Quantity must not be greater than 10000.']})

    def test_body_min_length_validation_false(self):
        """message marshalling fails min length for body field"""
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': ''}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'body': ['Quantity must be greater than 0.']})

    def test_body_required_validation_false(self):
        """message marshalling fails body not given"""
        message = {'msg_to': 'richard', 'msg_from': 'torrance'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'body': ['Missing data for required field.']})


