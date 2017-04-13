import unittest
from app.authentication.jwt import decode
from flask_restful import Resource
from flask import request, jsonify, Response
from sqlalchemy import engine

from app.validation.domain import MessageSchema
from app.repository.saver import Saver
from app.repository.retriever import Retriever
import logging
import uuid
from app.common.alerts import AlertUser
from app import settings
from app.settings import MESSAGE_QUERY_LIMIT


class MessageStatusTestCase(unittest.TestCase):
    # Test Case for Status of Messages

    def passing_urn(self):
        """testing that the passed urn is the user_urn from the header"""
        urn = header.urn
        self.assertEquals()


    def label_created_is_added_in_status_table(self):
        """testing to check if label is added to the status table"""
        self.assertTrue(query='SELECT label FROM status WHERE label IS NULL')

    def label_check(self):
        """testing that the label name is only from the valid list of labels"""
        # schema = MessageSchema()
        # data, errors = schema.load(message)
        expected_labels = 'INBOX','SENT','READ','UNREAD','ARCHIVED','TRASH'
        self.assertTrue(expected_labels in sut.errors['body'])


    def status_table_entry(self):
        """check to see if the actor column in the status label has been set to the user_urn"""
        status1 = query = 'INSERT into secure_mess

        self.assertTrue(status1==status2)


