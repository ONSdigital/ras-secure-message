from app import settings
from notifications_python_client import NotificationsAPIClient

import logging


logger = logging.getLogger(__name__)


class AlertViaGovNotify:
    """Notify Api handler"""

    @staticmethod
    def send(email,  reference):
        notifications_client = NotificationsAPIClient(settings.NOTIFICATION_COMBINED_KEY)
        notifications_client.send_email_notification(
            email_address=email,
            template_id=settings.NOTIFICATION_TEMPLATE_ID,
            personalisation=None,
            reference=reference
        )


class AlertUser:
    """Alert User"""
    alert_method = AlertViaGovNotify()

    def __init__(self, alerter=None):
        if alerter is not None:
            self.alert_method = alerter

    def send(self, email, reference):
        try:
            self.alert_method.send(email, reference)
        except BaseException as e:
            logger.exception(e)
        finally:
            return 201, 'OK'
