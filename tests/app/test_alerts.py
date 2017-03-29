import unittest
from unittest.mock import Mock
from app import settings
from app.common.alerts import AlertUser, AlertViaGovNotify


class AlertsTestCase(unittest.TestCase):
    """Test case for Alerts"""
    @staticmethod
    def test_email_notification_send():
        """sending email notification"""
        alert_service = AlertViaGovNotify()
        sut = AlertUser(alert_service)
        alert_service.send = Mock()
        sut.send('gemma.irving@ons.gov.uk', settings.NOTIFICATION_TEMPLATE_ID, None)
        alert_service.send.assert_called_with('gemma.irving@ons.gov.uk', settings.NOTIFICATION_TEMPLATE_ID, None)

if __name__ == '__main__':
    unittest.main()
