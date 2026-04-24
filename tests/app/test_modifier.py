import datetime
import unittest
import uuid
from unittest.mock import patch

import pytest
from flask import current_app
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError

from secure_message import constants
from secure_message.application import create_app
from secure_message.repository import database
from secure_message.repository.database import SecureMessage, db
from secure_message.repository.modifier import Modifier
from secure_message.repository.retriever import Retriever
from secure_message.services.service_toggles import internal_user_service
from secure_message.validation.user import User


class ModifyTestCaseHelper:
    """Helper class for Modify Tests"""

    BRES_SURVEY = "33333333-22222-3333-4444-88dc018a1a4c"

    def populate_database(self, record_count=0, mark_as_read=True):
        """Adds a specified number of Messages to the db in a single thread"""
        thread_id = str(uuid.uuid4())
        with self.engine.begin() as con:
            for i in range(record_count):
                msg_id = str(uuid.uuid4())
                # Only the first message in a thread needs a entry in the conversation table
                if i == 0:
                    query = (
                        f"INSERT INTO securemessage.conversation(id, is_closed, closed_by, closed_by_uuid) "
                        f"VALUES('{thread_id}', false, '', '')"
                    )
                    con.execute(text(query))
                sent_at = datetime.datetime.utcnow()
                if mark_as_read:
                    read_at = datetime.datetime.utcnow()
                    query = (
                        f"INSERT INTO securemessage.secure_message(id, msg_id, subject, body, thread_id, "
                        f"case_id, business_id, exercise_id, survey_id, sent_at, read_at) VALUES({i}, '{msg_id}', "
                        f"'test','test','{thread_id}','ACollectionCase', 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', "
                        f"'ACollectionExercise','{constants.NON_SPECIFIC_INTERNAL_USER}', '{sent_at}', '{read_at}')"
                    )
                    con.execute(text(query))
                else:
                    query = (
                        f"INSERT INTO securemessage.secure_message(id, msg_id, subject, body, thread_id, "
                        f"case_id, business_id, exercise_id, survey_id, sent_at) VALUES({i}, '{msg_id}', 'test','test',"
                        f"'{thread_id}','ACollectionCase', 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', "
                        f"'ACollectionExercise','{constants.NON_SPECIFIC_INTERNAL_USER}', '{sent_at}')"
                    )
                    con.execute(text(query))

                query = (
                    f"INSERT INTO securemessage.status(label, msg_id, actor)"
                    f"VALUES('SENT', '{msg_id}','0a7ad740-10d5-4ecb-b7ca-3c0384afb882')"
                )
                con.execute(text(query))
                query = (
                    f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('INBOX', '{msg_id}', "
                    f"'{constants.NON_SPECIFIC_INTERNAL_USER}')"
                )
                con.execute(text(query))
                query = (
                    f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('UNREAD', '{msg_id}',"
                    f"'{constants.NON_SPECIFIC_INTERNAL_USER}')"
                )
                con.execute(text(query))

        return thread_id

    def create_conversation_with_respondent_as_unread(self, user, message_count=0):
        """Adds a specified number of Messages to the db in a single thread"""
        # we should not be inserting records into the db for a unit test but sadly without a greater rework
        # its the only way
        thread_id = str(uuid.uuid4())
        with self.engine.begin() as con:
            for i in range(message_count):
                sent_at = datetime.datetime.utcnow()
                msg_id = str(uuid.uuid4())
                # Only the first message in a thread needs a entry in the conversation table
                if i == 0:
                    query = (
                        f"INSERT INTO securemessage.conversation(id, is_closed, closed_by, closed_by_uuid) "
                        f"VALUES('{thread_id}', false, '', '')"
                    )
                    con.execute(text(query))
                query = (
                    f"INSERT INTO securemessage.secure_message(id, msg_id, subject, body, thread_id,"
                    f"case_id, business_id, exercise_id, survey_id, sent_at) VALUES({i}, '{msg_id}', 'test','test',"
                    f"'{thread_id}','ACollectionCase', 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'ACollectionExercise',"
                    f"'{user.user_uuid}', '{sent_at}')"
                )
                con.execute(text(query))
                query = (
                    f"INSERT INTO securemessage.status(label, msg_id, actor) "
                    f"VALUES('SENT','{msg_id}', '{constants.NON_SPECIFIC_INTERNAL_USER}')"
                )
                con.execute(text(query))
                query = (
                    f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('INBOX', '{msg_id}', "
                    f"'{user.user_uuid}')"
                )
                con.execute(text(query))
                query = (
                    f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('UNREAD', '{msg_id}',"
                    f" '{user.user_uuid}')"
                )
                con.execute(text(query))
        return thread_id

    def add_conversation(
        self, conversation_id=str(uuid.uuid4()), is_closed=False, closed_by="", closed_by_uuid="", closed_at=None
    ):
        """Populate the conversation table"""
        # If conversation created needs to be closed, values are generated for you.  These can be overrriden
        # by passing them into function (i.e., if you need a specific name, but don't care about anything else,
        # then only pass in 'closed_by')
        if is_closed:
            if not closed_by:
                closed_by = "Some person"
            if not closed_by_uuid:
                closed_by_uuid = str(uuid.uuid4())
            if not closed_at:
                closed_at = datetime.datetime.utcnow()
        with self.engine.begin() as con:
            query = (
                f"INSERT INTO securemessage.conversation(id, is_closed, closed_by, closed_by_uuid, closed_at) "
                f"VALUES('{conversation_id}', '{is_closed}', '{closed_by}', '{closed_by_uuid}', '{closed_at}')"
            )
            con.execute(text(query))
        return conversation_id


class ModifyTestCase(unittest.TestCase, ModifyTestCaseHelper):
    """Test case for message retrieval"""

    def setUp(self):
        """setup test environment"""

        self.app = create_app(config="TestConfig")

        self.app.testing = True
        self.engine = create_engine(self.app.config["SQLALCHEMY_DATABASE_URI"])

        with self.app.app_context():
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

        self.user_internal = User("ce12b958-2a5f-44f4-a6da-861e59070a31", "internal")
        self.user_respondent = User("0a7ad740-10d5-4ecb-b7ca-3c0384afb882", "respondent")

    def tearDown(self):
        self.engine.dispose()

    def test_all_messages_in_conversation_marked_unread(self):
        # create a thread with two messages
        conversation_id = self.create_conversation_with_respondent_as_unread(user=self.user_respondent, message_count=2)
        with self.app.app_context():
            conversation = Retriever.retrieve_thread(conversation_id, self.user_respondent)
            for msg in conversation:
                # as there's two ways that a message is unread, first check the `read at` time isn't set
                self.assertIsNone(msg.read_at)
                # now collect all the message labels
                labels = []
                for status in msg.statuses:
                    labels.append(status.label)
                # and check the unread is present
                self.assertTrue("UNREAD" in labels)
            # now mark the first message as read and check the whole conversation is now read
            Modifier.mark_message_as_read(conversation[0].serialize(self.user_respondent), self.user_respondent)
            con = Retriever.retrieve_thread(conversation_id, self.user_respondent)
            for msg in con:
                # message `read at` should now be set
                self.assertIsNotNone(msg.read_at)
                # collect the labels again
                labels = []
                for status in msg.statuses:
                    labels.append(status.label)
                # and there should be no unread
                self.assertFalse("UNREAD" in labels)

    def test_close_conversation(self):
        """Test close conversation works"""
        conversation_id = self.populate_database(1)
        with self.app.app_context():
            internal_user_service.use_mock_service()
            # msg_id is the same as thread id for a conversation of 1
            metadata = Retriever.retrieve_conversation_metadata(conversation_id)
            Modifier.close_conversation(metadata, self.user_internal)
            metadata = Retriever.retrieve_conversation_metadata(conversation_id)

            self.assertTrue(metadata.is_closed)
            self.assertEqual(metadata.closed_by, "Selphie Tilmitt")
            self.assertEqual(metadata.closed_by_uuid, "ce12b958-2a5f-44f4-a6da-861e59070a31")
            self.assertTrue(isinstance(metadata.closed_at, datetime.datetime))
            # Test that timestamp on read message is less than 3 seconds old to prove it
            # was only just created
            delta = datetime.datetime.utcnow() - metadata.closed_at
            self.assertTrue(delta.total_seconds() < 3)

    def test_open_conversation(self):
        """Test re-opening conversation works"""
        conversation_id = self.add_conversation(is_closed=True)
        with self.app.app_context():
            # msg_id is the same as thread id for a conversation of 1
            metadata = Retriever.retrieve_conversation_metadata(conversation_id)
            Modifier.open_conversation(metadata, self.user_internal)
            metadata = Retriever.retrieve_conversation_metadata(conversation_id)
            self.assertFalse(metadata.is_closed)
            self.assertIsNone(metadata.closed_by)
            self.assertIsNone(metadata.closed_by_uuid)
            self.assertIsNone(metadata.closed_at)

    def test_two_unread_labels_are_added_to_message(self):
        """testing duplicate message labels are not added to the database"""
        self.populate_database(1)
        with self.engine.begin() as con:
            query = con.execute(text("SELECT msg_id FROM securemessage.secure_message LIMIT 1"))
            msg_id = query.first()[0]
        with self.app.app_context():
            with current_app.test_request_context():
                message = Retriever.retrieve_message(msg_id, self.user_internal)
                Modifier.add_unread(message, self.user_internal)
                Modifier.add_unread(message, self.user_internal)
        with self.engine.begin() as con:
            query = f"SELECT count(label) FROM securemessage.status WHERE msg_id = '{msg_id}' AND label = 'UNREAD'"
            query_x = con.execute(text(query))
            unread_label_total = []
            for row in query_x:
                unread_label_total.append(row[0])
            self.assertTrue(unread_label_total[0] == 1)

    def test_read_date_is_set(self):
        """testing message read_date is set when unread label is removed"""
        thread_id = self.populate_database(1, mark_as_read=False)
        with self.app.app_context():
            thread = Retriever.retrieve_thread(thread_id, self.user_respondent)
            serialised_message = Retriever.retrieve_message(thread[0].msg_id, self.user_internal)
            Modifier.mark_message_as_read(serialised_message, self.user_internal)
            serialised_message = Retriever.retrieve_message(thread[0].msg_id, self.user_internal)
            db_message = SecureMessage.query.filter(SecureMessage.msg_id == serialised_message["msg_id"]).one()

            self.assertIsNotNone(serialised_message["read_date"])
            self.assertTrue(isinstance(db_message.read_at, datetime.datetime))
            # Test that timestamp on read message is less than 3 seconds old to prove it
            # was only just created
            delta = datetime.datetime.utcnow() - db_message.read_at
            self.assertTrue(delta.total_seconds() < 3)

    def test_read_date_is_reset(self):
        """testing message read_date is changed when unread label is removed for a second time"""
        self.populate_database(1)
        with self.engine.begin() as con:
            query = con.execute(text("SELECT msg_id FROM securemessage.secure_message LIMIT 1"))
            msg_id = query.first()[0]
        with self.app.app_context():
            with current_app.test_request_context():
                message = Retriever.retrieve_message(msg_id, self.user_internal)
                Modifier.mark_message_as_read(message, self.user_internal)
                message = Retriever.retrieve_message(msg_id, self.user_internal)
                read_date_set = message["read_date"]
                Modifier.add_unread(message, self.user_internal)
                message = Retriever.retrieve_message(msg_id, self.user_internal)
                Modifier.mark_message_as_read(message, self.user_internal)
                message = Retriever.retrieve_message(msg_id, self.user_internal)
                self.assertNotEqual(message["read_date"], read_date_set)

    def test_exception_for_add_label_raises(self):
        with self.app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Modifier.add_label("UNREAD", {"survey_id": "survey_id"}, self.user_internal)

    def test_exception_for_remove_label_raises(self):
        with self.app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Modifier.remove_label("UNREAD", {"survey_id": "survey_id"}, self.user_internal)

    def test_get_label_actor_to_respondent(self):
        message_to_respondent = {
            "msg_id": "test1",
            "msg_to": ["0a7ad740-10d5-4ecb-b7ca-3c0384afb882"],
            "msg_from": "ce12b958-2a5f-44f4-a6da-861e59070a31",
            "subject": "MyMessage",
            "body": "hello",
            "thread_id": "",
            "case_id": "ACollectionCase",
            "exercise_id": "ACollectionExercise",
            "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "survey_id": self.BRES_SURVEY,
            "from_internal": True,
        }

        self.assertEqual(
            Modifier._get_label_actor(user=self.user_internal, message=message_to_respondent),
            "ce12b958-2a5f-44f4-a6da-861e59070a31",
        )
        self.assertEqual(
            Modifier._get_label_actor(user=self.user_respondent, message=message_to_respondent),
            "0a7ad740-10d5-4ecb-b7ca-3c0384afb882",
        )

    def test_get_label_actor_to_group(self):
        message_to_internal_group = {
            "msg_id": "test3",
            "msg_to": [constants.NON_SPECIFIC_INTERNAL_USER],
            "msg_from": "0a7ad740-10d5-4ecb-b7ca-3c0384afb882",
            "subject": "MyMessage",
            "body": "hello",
            "thread_id": "",
            "case_id": "ACollectionCase",
            "exercise_id": "ACollectionExercise",
            "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "survey_id": self.BRES_SURVEY,
            "from_internal": False,
        }

        self.assertEqual(
            Modifier._get_label_actor(user=self.user_internal, message=message_to_internal_group),
            constants.NON_SPECIFIC_INTERNAL_USER,
        )
        self.assertEqual(
            Modifier._get_label_actor(user=self.user_respondent, message=message_to_internal_group),
            "0a7ad740-10d5-4ecb-b7ca-3c0384afb882",
        )

    def test_get_label_actor_to_internal_user(self):
        message_to_internal_user = {
            "msg_id": "test4",
            "msg_to": ["ce12b958-2a5f-44f4-a6da-861e59070a31"],
            "msg_from": "0a7ad740-10d5-4ecb-b7ca-3c0384afb882",
            "subject": "MyMessage",
            "body": "hello",
            "thread_id": "",
            "case_id": "ACollectionCase",
            "exercise_id": "ACollectionExercise",
            "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "survey_id": self.BRES_SURVEY,
            "from_internal": False,
        }

        self.assertEqual(
            Modifier._get_label_actor(user=self.user_internal, message=message_to_internal_user),
            "ce12b958-2a5f-44f4-a6da-861e59070a31",
        )
        self.assertEqual(
            Modifier._get_label_actor(user=self.user_respondent, message=message_to_internal_user),
            "0a7ad740-10d5-4ecb-b7ca-3c0384afb882",
        )

    def test_get_label_actor_raises_exception_for_missing_fields(self):
        message_missing_fields = {
            "msg_id": "test5",
            "subject": "MyMessage",
            "body": "hello",
            "thread_id": "",
            "case_id": "ACollectionCase",
            "exercise_id": "ACollectionExercise",
            "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "survey_id": self.BRES_SURVEY,
            "from_internal": False,
        }

        with self.assertRaises(InternalServerError):
            Modifier._get_label_actor(user=self.user_internal, message=message_missing_fields)

    def test_closed_conversations_mark_for_deletion(self):

        # Given 4 conversations are created (1 open, 3 closed or which 2 should be marked for deletion)
        with self.app.app_context():
            offset = current_app.config["MARK_FOR_DELETION_OFFSET_IN_DAYS"]
            now = datetime.datetime.utcnow()

            greater_than_deletion_date = now - datetime.timedelta(days=offset + 1)
            less_than_deletion_date = now - datetime.timedelta(days=offset - 1)

            conv1 = database.Conversation(is_closed=True, closed_at=greater_than_deletion_date)
            conv1.id = "1"
            conv2 = database.Conversation(is_closed=True, closed_at=greater_than_deletion_date)
            conv2.id = "2"
            conv3 = database.Conversation(is_closed=True, closed_at=less_than_deletion_date)
            conv3.id = "3"
            conv4 = database.Conversation(is_closed=False)
            conv4.id = "4"
            db.session.add_all([conv1, conv2, conv3, conv4])
            db.session.commit()

            # When closed_conversations_mark_for_deletion is called
            updated_count = Modifier.closed_conversations_mark_for_deletion()

            # Then 2 conversations are updated, with mark_for_deletion set to True
            self.assertEqual(updated_count, 2)

            refreshed = {
                conv.id: db.session.get(database.Conversation, conv.id) for conv in [conv1, conv2, conv3, conv4]
            }

            self.assertTrue(refreshed["1"].mark_for_deletion)
            self.assertTrue(refreshed["2"].mark_for_deletion)
            self.assertFalse(refreshed["3"].mark_for_deletion)
            self.assertFalse(refreshed["4"].mark_for_deletion)

    def test_closed_conversations_deletion_cascades(self):
        # Given a conversation where mark_for_deletion is True
        with self.app.app_context():
            conversation_id = "conversation_id"
            msg_id = "msg_id"

            conversation = database.Conversation(
                mark_for_deletion=True,
            )
            conversation.id = conversation_id
            message = database.SecureMessage(
                msg_id=msg_id,
                thread_id=conversation_id,
            )
            status = database.Status(msg_id=msg_id)

            db.session.add_all([conversation, message, status])
            db.session.commit()

            self.assertEqual(count(database.Conversation, id=conversation_id), 1)
            self.assertEqual(count(database.SecureMessage, msg_id=msg_id), 1)
            self.assertEqual(count(database.Status, msg_id=msg_id), 1)

            # When closed_conversations_deletion is called
            deleted_count = Modifier.closed_conversations_deletion()

            # Then the conversation, secure message and status associated with it are deleted
            self.assertEqual(deleted_count, 1)
            self.assertEqual(count(database.Conversation, id=conversation_id), 0)
            self.assertEqual(count(database.SecureMessage, msg_id=msg_id), 0)
            self.assertEqual(count(database.Status, msg_id=msg_id), 0)

    def test_closed_conversations_deletion_does_not_remove_unmarked_conversations(self):
        # Given a conversation where mark_for_deletion is False
        with self.app.app_context():
            conversation_id = "conversation_id"
            conversation = database.Conversation(
                mark_for_deletion=False,
            )
            conversation.id = conversation_id
            db.session.add(conversation)
            db.session.commit()

            self.assertEqual(count(database.Conversation, id=conversation_id), 1)

            # When closed_conversations_deletion is called
            deleted_count = Modifier.closed_conversations_deletion()

            # Then the conversation is not deleted
            self.assertEqual(deleted_count, 0)
            self.assertEqual(count(database.Conversation, id=conversation_id), 1)

    def test_closed_conversations_deletion_rolls_back_on_message_delete_error(self):
        # Given a conversation where mark_for_deletion is True
        with self.app.app_context():
            conversation_id = "conversation_id"
            msg_id = "msg_id"

            conversation = database.Conversation(mark_for_deletion=True)
            conversation.id = conversation_id

            message = database.SecureMessage(
                msg_id=msg_id,
                thread_id=conversation_id,
            )
            status = database.Status(msg_id=msg_id)

            db.session.add_all([conversation, message, status])
            db.session.commit()

            self.assertEqual(count(database.Conversation, id=conversation_id), 1)
            self.assertEqual(count(database.SecureMessage, msg_id=msg_id), 1)
            self.assertEqual(count(database.Status, msg_id=msg_id), 1)

            # When closed_conversations_deletion is called, but an SQLAlchemyError is returned on deleting SecureMessages
            with patch(
                "sqlalchemy.orm.query.Query.delete", side_effect=[1, SQLAlchemyError("secure message delete failed")]
            ):
                with pytest.raises(SQLAlchemyError):
                    Modifier.closed_conversations_deletion()

            # Then the conversation, secure message and status associated with it are not deleted
            self.assertEqual(count(database.Conversation, id=conversation_id), 1)
            self.assertEqual(count(database.SecureMessage, msg_id=msg_id), 1)
            self.assertEqual(count(database.Status, msg_id=msg_id), 1)


def count(model, **filters):
    return db.session.query(model).filter_by(**filters).count()


if __name__ == "__main__":
    unittest.main()
