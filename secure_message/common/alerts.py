import logging

from secure_message import settings
from structlog import wrap_logger
from urllib import parse as urlparse
from secure_message.exception.exceptions import RasNotifyException
import requests

logger = wrap_logger(logging.getLogger(__name__))


class AlertViaGovNotify:
    """Notify Api handler"""

    @staticmethod
    def send(email, reference):

        notification = {
            "emailAddress": email,
            "reference": reference
        }

        url = urlparse.urljoin(settings.RM_NOTIFY_GATEWAY_URL, settings.NOTIFICATION_TEMPLATE_ID)

        response = requests.post(url, auth=settings.BASIC_AUTH, timeout=settings.REQUESTS_POST_TIMEOUT,
                                 json=notification)

        if response.status_code != 201:
            raise RasNotifyException(code=500)
        else:
            logger.info('Sent secure message email notification, via RM Notify-Gateway to GOV.UK Notify.',
                        message_id=response.json()["id"])


class AlertViaLogging:
    """Alert goes via gov notify (0) or via logs (1)"""

    @staticmethod
    def send(email, reference):
        logger.info('email details {}, {}'.format(email, reference))


class AlertUser:
    alert_method = AlertViaGovNotify()

    def __init__(self, alerter=None):
        if alerter is not None:
            self.alert_method = alerter

    def send(self, email, reference):
        self.alert_method.send(email, reference)

