import unittest
import uuid
from datetime import datetime

from flask import current_app
from sqlalchemy import create_engine
from werkzeug.exceptions import Forbidden, NotFound

from secure_message.application import create_app
from secure_message.common.utilities import MessageArgs
from secure_message.constants import MESSAGE_QUERY_LIMIT
from secure_message.repository import database
from secure_message.repository.retriever import Retriever
from secure_message.services.service_toggles import party
from secure_message.validation.user import User
from tests.app.test_utilities import get_args


class RetrieverTestCaseHelper:
    default_internal_actor = "internal_actor"
    second_internal_actor = "second_internal_actor"
    default_external_actor = "external_actor"
    second_external_actor = "second_external_actor"
    BRES_SURVEY = "33333333-22222-3333-4444-88dc018a1a4c"

    """Helper class for Retriever Tests"""

    def add_secure_message(
        self,
        msg_id,
        subject="test",
        body="test",
        thread_id="ThreadId",
        case_id="ACollectionCase",
        business_id="f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
        survey_id=BRES_SURVEY,
        exercise_id="CollectionExercise",
        from_internal=False,
        sent_at=datetime.utcnow(),
        include_read_at=False,
    ):
        """Populate the secure_message table"""

        with self.engine.connect() as con:
            if include_read_at:
                read_at = datetime.utcnow()
                query = (
                    f"INSERT INTO securemessage.secure_message(msg_id, subject, body, thread_id,"
                    f"case_id, business_id, survey_id, exercise_id, from_internal, sent_at, read_at)"
                    f"VALUES ('{msg_id}', '{subject}','{body}',"
                    f"'{thread_id}', '{case_id}', '{business_id}', '{survey_id}',"
                    f" '{exercise_id}', '{from_internal}',  '{sent_at}', '{read_at}')"
                )
            else:
                query = (
                    f"INSERT INTO securemessage.secure_message(msg_id, subject, body, thread_id,"
                    f"case_id, business_id, survey_id, exercise_id, from_internal, sent_at)"
                    f"VALUES ('{msg_id}', '{subject}','{body}',"
                    f"'{thread_id}', '{case_id}', '{business_id}', '{survey_id}',"
                    f" '{exercise_id}', '{from_internal}',  '{sent_at}')"
                )
            con.execute(query)

    def add_conversation(self, conversation_id, is_closed=False, category="SURVEY"):
        """Populate the conversation table"""

        with self.engine.connect() as con:
            query = (
                f"INSERT INTO securemessage.conversation(id, is_closed, category) "
                f"VALUES('{conversation_id}', '{is_closed}', '{category}')"
            )
            con.execute(query)

    def add_status(self, label, msg_id, actor):
        """Populate the status table"""

        with self.engine.connect() as con:
            query = f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('{label}', '{msg_id}', '{actor}')"
            con.execute(query)

    def create_thread(
        self,
        no_of_messages=1,
        external_actor=default_external_actor,
        internal_actor=default_internal_actor,
        category="SURVEY",
        include_read_at=False,
    ):
        """Populate the db with a thread with a specified number of messages"""

        msg_id = str(uuid.uuid4())
        thread_id = msg_id
        self.add_conversation(conversation_id=thread_id, category=category)
        self.add_secure_message(
            msg_id=msg_id,
            thread_id=thread_id,
            survey_id=self.BRES_SURVEY,
            from_internal=False,
            include_read_at=include_read_at,
        )
        self.add_status(label="SENT", msg_id=msg_id, actor=external_actor)
        self.add_status(label="INBOX", msg_id=msg_id, actor=internal_actor)

        if no_of_messages > 1:
            for _ in range(no_of_messages - 1):
                msg_id = str(uuid.uuid4())
                self.add_secure_message(
                    msg_id=msg_id,
                    thread_id=thread_id,
                    survey_id=self.BRES_SURVEY,
                    from_internal=True,
                    include_read_at=include_read_at,
                )
                self.add_status(label="SENT", msg_id=msg_id, actor=internal_actor)
                self.add_status(label="UNREAD", msg_id=msg_id, actor=external_actor)
                self.add_status(label="INBOX", msg_id=msg_id, actor=external_actor)

        return thread_id


class RetrieverTestCase(unittest.TestCase, RetrieverTestCaseHelper):
    """Test case for message retrieval"""

    def setUp(self):
        """setup test environment"""
        self.app = create_app(config="TestConfig")
        self.app.testing = True
        self.engine = create_engine(self.app.config["SQLALCHEMY_DATABASE_URI"])
        self.MESSAGE_LIST_ENDPOINT = "http://localhost:5050/messages"
        self.MESSAGE_BY_ID_ENDPOINT = "http://localhost:5050/message/"
        with self.app.app_context():
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

        self.user_internal = User(RetrieverTestCaseHelper.default_internal_actor, "internal")
        self.second_user_internal = User(RetrieverTestCaseHelper.second_internal_actor, "internal")
        self.user_respondent = User(RetrieverTestCaseHelper.default_external_actor, "respondent")
        self.second_user_respondent = User(RetrieverTestCaseHelper.second_external_actor, "respondent")
        party.use_mock_service()

    def test_msg_returned_with_msg_id_true(self):
        """retrieves message using id"""
        self.create_thread(no_of_messages=2)
        with self.engine.connect() as con:
            query = con.execute("SELECT msg_id FROM securemessage.secure_message LIMIT 1")
            msg_id = query.first()[0]
            with self.app.app_context():
                with current_app.test_request_context():
                    response = Retriever.retrieve_message(msg_id, self.user_internal)
                    self.assertEqual(response["msg_id"], msg_id)

    def test_msg_returned_with_msg_id_returns_404(self):
        """retrieves message using id that doesn't exist"""
        message_id = "1"
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever.retrieve_message(message_id, self.user_internal)

    def test_get_nonexistant_conversation_returns_none(self):
        """retrieves message using id that doesn't exist"""
        random_uuid = str(uuid.uuid4())
        with self.app.app_context():
            with current_app.test_request_context():
                result = Retriever.retrieve_conversation_metadata(random_uuid)
                self.assertIsNone(result)

    def test_correct_labels_returned_internal(self):
        """retrieves message using id and checks the labels are correct"""
        self.create_thread()
        with self.engine.connect() as con:
            query = con.execute("SELECT msg_id FROM securemessage.secure_message LIMIT 1")
            msg_id = query.first()[0]
            with self.app.app_context():
                with current_app.test_request_context():
                    response = Retriever.retrieve_message(msg_id, self.user_internal)
                    labels = ["INBOX"]
                    self.assertCountEqual(response["labels"], labels)

    def test_correct_labels_returned_external(self):
        """retrieves message using id and checks the labels are correct"""
        self.create_thread()
        with self.engine.connect() as con:
            query = con.execute("SELECT msg_id FROM securemessage.secure_message LIMIT 1")
            msg_id = query.first()[0]
            with self.app.app_context():
                with current_app.test_request_context():
                    response = Retriever.retrieve_message(msg_id, self.user_respondent)
                    labels = ["SENT"]
                    self.assertCountEqual(response["labels"], labels)

    def test_correct_to_and_from_returned_internal_user(self):
        """retrieves message using id and checks the to and from urns are correct"""
        self.create_thread(internal_actor=self.user_internal.user_uuid)
        with self.engine.connect() as con:
            query = con.execute("SELECT msg_id FROM securemessage.secure_message LIMIT 1")
            msg_id = query.first()[0]
            with self.app.app_context():
                with current_app.test_request_context():
                    response = Retriever.retrieve_message(msg_id, self.user_respondent)
                    self.assertEqual(response["msg_to"][0], self.user_internal.user_uuid)
                    self.assertEqual(response["msg_from"], self.user_respondent.user_uuid)

    def test_sent_date_returned_for_message(self):
        """retrieves message using id and checks the sent date returned"""
        self.create_thread()
        with self.engine.connect() as con:
            query = con.execute("SELECT msg_id FROM securemessage.secure_message LIMIT 1")
            msg_id = query.first()[0]
            with self.app.app_context():
                with current_app.test_request_context():
                    response = Retriever.retrieve_message(msg_id, self.user_internal)
                    self.assertTrue("modified_date" not in response)
                    self.assertTrue(response["sent_date"] != "N/A")
            con.close()

    def test_read_date_returned_for_message(self):
        """retrieves message using id and checks the read date returned"""
        self.create_thread(no_of_messages=2, include_read_at=True)
        with self.engine.connect() as con:
            query = con.execute("SELECT msg_id FROM securemessage.secure_message LIMIT 1")
            msg_id = query.first()[0]
            with self.app.app_context():
                with current_app.test_request_context():
                    response = Retriever.retrieve_message(msg_id, self.user_internal)
                    self.assertTrue("modified_date" not in response)
                    self.assertTrue(response["read_date"] != "N/A")
            con.close()

    def test_all_msg_returned_for_thread_id(self):
        """retrieves messages for thread_id from database"""
        thread_id = self.create_thread(no_of_messages=6)

        with self.app.app_context():
            with current_app.test_request_context():
                response = Retriever.retrieve_thread(thread_id, self.user_respondent)
                self.assertEqual(len(response.all()), 6)

    def test_thread_returned_in_desc_order(self):
        """check thread returned in correct order"""
        thread_id = self.create_thread(no_of_messages=6)

        with self.app.app_context():
            with current_app.test_request_context():
                response = Retriever.retrieve_thread(thread_id, self.user_respondent)
                self.assertEqual(len(response.all()), 6)

                sent = [str(message.sent_at) for message in response.all()]

                desc_date = sorted(sent, reverse=True)
                self.assertEqual(len(sent), 6)
                self.assertListEqual(desc_date, sent)

    def test_thread_returned_with_thread_id_returns_404(self):
        """retrieves thread using id that doesn't exist"""
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever.retrieve_thread("anotherThreadId", self.user_respondent)

    def test_thread_list_gets_messages_of_specific_category(self):
        """retrieves threads from database for a specific category"""
        self.create_thread(category="SURVEY")
        self.create_thread(category="ACCOUNT")

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(category="ACCOUNT")
                response = Retriever.retrieve_thread_list(self.user_internal, args)

                self.assertEqual(len(response.items), 1)

    def test_thread_list_all_messages_when_no_category_provided(self):
        """retrieves all threads for the user if a category isn't specified"""
        self.create_thread(category="SURVEY")
        self.create_thread(category="ACCOUNT")

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args()
                response = Retriever.retrieve_thread_list(self.user_internal, args)

                self.assertEqual(len(response.items), 2)

    def test_thread_list_returned_in_descending_order_respondent(self):
        """retrieves threads from database in desc sent_date order for respondent"""
        for _ in range(5):
            self.create_thread(no_of_messages=2)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever.retrieve_thread_list(self.user_respondent, args)

                date = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    if "sent_date" in serialized_msg:
                        date.append(serialized_msg["sent_date"])
                    elif "modified_date" in serialized_msg:
                        date.append(serialized_msg["modified_date"])

                desc_date = sorted(date, reverse=True)
                self.assertEqual(len(date), 5)
                self.assertListEqual(desc_date, date)

    def test_thread_list_returned_in_descending_order_internal(self):
        """retrieves threads from database in desc sent_date order for internal user"""
        for _ in range(5):
            self.create_thread(no_of_messages=3)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever.retrieve_thread_list(self.user_internal, args)

                date = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    if "sent_date" in serialized_msg:
                        date.append(serialized_msg["sent_date"])
                    elif "modified_date" in serialized_msg:
                        date.append(serialized_msg["modified_date"])

                desc_date = sorted(date, reverse=True)
                print(len(date))
                self.assertEqual(len(date), 5)
                self.assertListEqual(desc_date, date)

    def test_latest_message_from_each_thread_chosen_desc(self):
        """checks the message chosen for each thread is the latest message within that thread"""
        for _ in range(5):
            self.create_thread(no_of_messages=3)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever.retrieve_thread_list(self.user_internal, args)

                date = []
                thread_ids = []
                msg_ids = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    if "sent_date" in serialized_msg:
                        date.append(serialized_msg["sent_date"])
                    elif "modified_date" in serialized_msg:
                        date.append(serialized_msg["modified_date"])
                    thread_ids.append(serialized_msg["thread_id"])
                    msg_ids.append(serialized_msg["msg_id"])

                self.assertEqual(len(msg_ids), 5)

                for x in range(0, len(thread_ids)):
                    thread = Retriever.retrieve_thread(thread_ids[x], self.user_internal)
                    first_msg_in_thread = thread.all()[0]
                    self.assertEqual(date[x], str(first_msg_in_thread.sent_at))
                    self.assertEqual(msg_ids[x], first_msg_in_thread.msg_id)

    def test_thread_count_by_survey_my_conversations_off(self):
        """checks that the returned thread count is the same for every internal user
        even if they are not part of the conversations"""
        request_args = MessageArgs(
            page=0,
            limit=100,
            business_id=None,
            cc=None,
            label=None,
            desc=None,
            ce=None,
            surveys=[self.BRES_SURVEY],
            is_closed=False,
            my_conversations=False,
            new_respondent_conversations=False,
            all_conversation_types=False,
            unread_conversations=False,
            category=None,
        )

        for _ in range(5):
            self.create_thread(no_of_messages=2)

        with self.app.app_context():
            with current_app.test_request_context():
                thread_count_internal = Retriever.thread_count_by_survey(
                    request_args, User(self.default_internal_actor, role="internal")
                )
                thread_count_second_internal = Retriever.thread_count_by_survey(
                    request_args, User(self.second_internal_actor, role="internal")
                )
                self.assertEqual(thread_count_internal, thread_count_second_internal)

    def test_thread_count_by_survey_my_conversations_on(self):
        """checks that the returned thread count is the same for every internal user
        even if they are not part of the conversations"""
        request_args = MessageArgs(
            page=0,
            limit=100,
            business_id=None,
            cc=None,
            label=None,
            desc=None,
            ce=None,
            surveys=[self.BRES_SURVEY],
            is_closed=False,
            my_conversations=True,
            new_respondent_conversations=False,
            all_conversation_types=False,
            unread_conversations=False,
            category=None,
        )

        for _ in range(5):
            self.create_thread(no_of_messages=2)

        with self.app.app_context():
            with current_app.test_request_context():
                thread_count_internal = Retriever.thread_count_by_survey(
                    request_args, User(self.default_internal_actor, role="internal")
                )
                thread_count_second_internal = Retriever.thread_count_by_survey(
                    request_args, User(self.second_internal_actor, role="internal")
                )
                self.assertEqual(thread_count_internal, 5)
                self.assertEqual(thread_count_second_internal, 0)

    def test_respondent_can_only_see_their_messages(self):
        """tests that a respondent can only see their messages i.e. they should not
        see any messages sent to another respondent"""
        first_respondent_thread_id = self.create_thread(
            no_of_messages=1, external_actor=self.default_external_actor, internal_actor=self.default_internal_actor
        )
        second_respondent_thread_id = self.create_thread(
            no_of_messages=1, external_actor=self.second_external_actor, internal_actor=self.default_internal_actor
        )

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args()
                first_respondent_thread_list = Retriever.retrieve_thread_list(self.user_respondent, args)
                self.assertEqual(first_respondent_thread_list.total, 1)
                second_respondent_thread_list = Retriever.retrieve_thread_list(self.second_user_respondent, args)
                self.assertEqual(second_respondent_thread_list.total, 1)
                internal_thread_list = Retriever.retrieve_thread_list(self.user_internal, args)
                self.assertEqual(internal_thread_list.total, 2)

                # first respondent can retrieve the message they sent
                first_respondent_thread = Retriever.retrieve_thread(first_respondent_thread_id, self.user_respondent)
                self.assertIsNotNone(first_respondent_thread)

                # second respondent can retrieve the message they sent
                second_respondent_thread = Retriever.retrieve_thread(
                    second_respondent_thread_id, self.second_user_respondent
                )
                self.assertIsNotNone(second_respondent_thread)

                # first respondent shouldn't be able to retrieve second respondent's message
                with self.assertRaises(Forbidden):
                    Retriever.retrieve_thread(first_respondent_thread_id, self.second_user_respondent)

                # second respondent shouldn't be able to retrieve first respondent's message
                with self.assertRaises(Forbidden):
                    Retriever.retrieve_thread(second_respondent_thread_id, self.user_respondent)


if __name__ == "__main__":
    unittest.main()
