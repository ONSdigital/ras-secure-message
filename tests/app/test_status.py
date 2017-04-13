import unittest



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


