import unittest
import json
from app.domain_model.domain import Message, MessageSchema


class MessageTestCase(unittest.TestCase):

    def testMarshalJson(self):
        message = Message('richard', 'torrance', 'hello')
        schema = MessageSchema()
        json_result = schema.dumps(message)
        message_load = schema.load(json.loads(json_result.data))
        self.assertTrue(message_load.data == message)

    def test_validation_true(self):
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {})

    def test_msg_to_max_length_validation_false(self):
        msg_to = "x" * 101
        message = {'msg_to': msg_to, 'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_to': ['Quantity must not be greater than 100.']})

    def test_msg_to_min_length_validation_false(self):
        message = {'msg_to': '', 'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_to': ['Quantity must be greater than 0.']})

    def test_msg_to_required_validation_false(self):
        message = {'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_to': ['Missing data for required field.']})

    def test_msg_from_max_length_validation_false(self):
        msg_from = "x" * 101
        message = {'msg_to': 'richard', 'msg_from': msg_from, 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_from': ['Quantity must not be greater than 100.']})

    def test_msg_from_min_length_validation_false(self):
        message = {'msg_to': 'richard', 'msg_from': '', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_from': ['Quantity must be greater than 0.']})

    def test_msg_from_required_validation_false(self):
        message = {'msg_to': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_from': ['Missing data for required field.']})

    def test_body_max_length_validation_false(self):
        body = "x" * 10001
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': body}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'body': ['Quantity must not be greater than 10000.']})

    def test_body_min_length_validation_false(self):
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': ''}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'body': ['Quantity must be greater than 0.']})

    def test_body_required_validation_false(self):
        message = {'msg_to': 'richard', 'msg_from': 'torrance'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'body': ['Missing data for required field.']})

