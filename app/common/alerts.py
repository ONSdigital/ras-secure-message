from app import settings
from notifications_python_client import NotificationsAPIClient
from notifications_python_client import errors

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
    alertMethod = AlertViaGovNotify()

    def __init__(self, alerter=None):
        if alerter is not None:
            self.alertMethod = alerter

    def send(self, email, reference):
        try:
            self.alertMethod.send(email, reference)

        except errors.HTTPError as http_error:
            logger.exception(http_error)
            return http_error.status_code, http_error.message[0]
        except BaseException as e:
            logger.exception(e)
            return 400, 'Notification not sent'

        return 201, 'OK'
