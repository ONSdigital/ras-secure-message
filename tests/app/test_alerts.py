import unittest
from unittest import mock
from unittest.mock import Mock

from secure_message.application import create_app
from secure_message.exception.exceptions import RasNotifyException
from secure_message.common.alerts import AlertViaGovNotify
import json


class AlertsTestCase(unittest.TestCase):
    """Test case for Alerts"""

    def setUp(self):
        """setup test environment"""
        self.app = create_app()
        self.app.testing = True

    personalisation = {"RANDOM_URL": "randomemail"}

    def test_post_to_notify_gateway_with_correct_params(self):
        future = mock.MagicMock()
        publisher = mock.MagicMock()
        publisher.publish.return_value = future
        alert = AlertViaGovNotify({
            'NOTIFICATION_TEMPLATE_ID': "123",
            "GOOGLE_CLOUD_PROJECT": "test",
            "PUBSUB_TOPIC": "testTopic"
        })
        expectedPayload = json.dumps({
            "emailAddress": "test@email.com",
            "personalisation": self.personalisation,
            "reference": "myReference"
        }).encode()
        alert.publisher = publisher
        with self.app.app_context():
            alert.send('test@email.com', 'myReference', self.personalisation, "survey123", "party123")

        publisher.assert_called_once_with('topic_path', data=expectedPayload)

    def test_request_to_notify_with_pubsub_timeout_error(self):
        """Tests if the future.result() raises a TimeoutError then the function raises a RasNotifyException"""
        future = mock.MagicMock()
        future.result.side_effect = TimeoutError("bad")
        publisher = mock.MagicMock()
        publisher.publish.return_value = future

        # Given a mocked notify gateway
        alert = AlertViaGovNotify({
            'NOTIFICATION_TEMPLATE_ID': "123",
            "GOOGLE_CLOUD_PROJECT": "test",
            "PUBSUB_TOPIC": "testTopic"
        })
        alert.publisher = publisher
        with self.assertRaises(RasNotifyException):
            alert.send('test@email.com', data={})


if __name__ == '__main__':
    unittest.main()
