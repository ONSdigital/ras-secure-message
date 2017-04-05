import unittest
from unittest.mock import Mock
from unittest.mock import patch
from app import settings
from app.common.alerts import AlertUser, AlertViaGovNotify
from notifications_python_client import errors


class AlertsTestCase(unittest.TestCase):
    """Test case for Alerts"""

    @staticmethod
    def test_alert_user_send_if_forwarded_to_alert_method():
        """sending email notification"""
        sut = AlertUser(Mock(AlertViaGovNotify))
        sut.send(settings.NOTIFICATION_DEV_EMAIL, None)
        sut.alertMethod.send.assert_called_with(settings.NOTIFICATION_DEV_EMAIL, None)

    def test_init_with_alerter_params_sets_alert_method(self):
        """test uses alertMethod from constructor if provided"""
        sut = AlertUser(Mock(AlertViaGovNotify))
        self.assertTrue(isinstance(sut.alertMethod, Mock))

    def test_init_with_alerter_no_params_sets_alert_method_to_alert_via_gov_notify(self):
        """test uses AlertViaGovNotify if no alert_method specified"""
        sut = AlertUser()
        self.assertTrue(isinstance(sut.alertMethod, AlertViaGovNotify))

    @patch.object(AlertViaGovNotify, 'send')
    def test_when_alert_method_throws_an_exception_the_http_status_is_201(self, mock_alerter):
        """test an exception other than http exception returns a 201"""
        mock_alerter.send.side_effect = Exception('Oh Dear')
        sut = AlertUser(mock_alerter)

        resp = sut.send("MyEmail", "MyRef")
        self.assertTrue(resp[0] == 201)

    @patch.object(AlertViaGovNotify, 'send')
    def test_when_alert_method_throws_a_http_exception_the_http_status_is_201(self, mock_alerter):
        """test given a http exception the http error code is returned"""
        mock_alerter.send.side_effect = errors.HTTPError()
        sut = AlertUser(mock_alerter)
        resp = sut.send("MyEmail", "MyRef")
        self.assertTrue(resp[0] == 201)


if __name__ == '__main__':
    unittest.main()
