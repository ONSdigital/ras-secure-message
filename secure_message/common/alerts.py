import json
import logging

from google.cloud import pubsub_v1
from structlog import wrap_logger

from secure_message.exception.exceptions import RasNotifyException

logger = wrap_logger(logging.getLogger(__name__))


class AlertViaGovNotify:
    """Notify Api handler"""

    def __init__(self, config):
        self.config = config
        self.template_id = self.config['NOTIFICATION_TEMPLATE_ID']
        self.project_id = self.config['GOOGLE_CLOUD_PROJECT']
        self.topic_id = self.config['PUBSUB_TOPIC']
        self.publisher = None

    def send(self, email, msg_id, personalisation, survey_id, party_id):
        """Sends an email via pubsub topic

        :param email: Email address to send the email too
        :type email: str
        :param msg_id: the notification reference
        :type msg_id: str
        :param personalisation: A dictionary containing variables that will be used in the email e.g., names, ru refs
        :type personalisation: dict
        :param survey_id: the survey Id
        :type survey_id: str
        :param party_id: the party UUID
        :type party_id: UUID
        :raises RasNotifyError: Raised on any Exception that occurs.  Most likely will happen if there is an issue when
                                publishing to pubsub.
        :return: None
        """
        bound_logger = logger.bind(template_id=self.template_id, project_id=self.project_id, topic_id=self.topic_id)
        bound_logger.info("Sending email via pubsub")
        payload = {
            'notify': {
                'email_address': email,
                "personalisation": personalisation,
                "reference": msg_id,
                'template_id': self.template_id,
            }
        }

        payload_str = json.dumps(payload)
        if self.publisher is None:
            self.publisher = pubsub_v1.PublisherClient()
        topic_path = self.publisher.topic_path(self.project_id, self.topic_id) # NOQA pylint:disable=no-member

        bound_logger.info("About to publish to pubsub")
        future = self.publisher.publish(topic_path, data=payload_str.encode())

        try:
            message = future.result()
            bound_logger.info("Publish succeeded", msg_id=message)
        except TimeoutError:
            bound_logger.error("Publish to pubsub timed out", exc_info=True)
            raise RasNotifyException(survey_id=survey_id, party_id=party_id)
        except Exception: # noqa
            bound_logger.error("A non-timeout error was raised when publishing to pubsub", exc_info=True)
            raise RasNotifyException(survey_id=survey_id, party_id=party_id)


class AlertViaLogging:
    """Alert goes via gov notify (0) or via logs (1)"""

    def send(self, email, msg_id, personalisation, survey_id, party_id):  # NOQA pylint:disable=no-self-use
        logger.info('Email sent', email=email, msg_id=msg_id, personalisation=personalisation, survey=survey_id,
                    party_id=party_id)
