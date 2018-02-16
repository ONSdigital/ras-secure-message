import logging


from structlog import wrap_logger
from sqlalchemy import and_, or_
from werkzeug.exceptions import InternalServerError

from secure_message.repository.database import SecureMessage, Status
from secure_message.repository.retriever import Retriever
from secure_message import constants

logger = wrap_logger(logging.getLogger(__name__))


class RetrieverV2(Retriever):
    """Created when retrieving messages"""

    @staticmethod
    def unread_message_count_by_survey(user, survey):
        """Count users unread messages for a specific survey"""
        if user.is_internal:
            status_conditions, survey_conditions = RetrieverV2._get_conditions_internal_user(survey, user)
        else:
            status_conditions, survey_conditions = RetrieverV2._get_conditions_respondent(survey, user)

        try:
            result = SecureMessage.query.join(Status). \
                filter(or_(*status_conditions)). \
                filter(and_(*survey_conditions)). \
                filter(Status.label == 'UNREAD').count()
        except Exception as e:
            logger.error('Error retrieving count of unread messages from database', error=e)
            raise InternalServerError(description="Error retrieving count of unread messages from database")
        return result

    @staticmethod
    def _get_conditions_internal_user(survey, user):
        status_conditions = []
        status_conditions.append(Status.actor == str(user.user_uuid))
        status_conditions.append(Status.actor == constants.NON_SPECIFIC_INTERNAL_USER)
        survey_conditions = []
        survey_conditions.append(SecureMessage.survey == survey)
        return status_conditions, survey_conditions

    @staticmethod
    def _get_conditions_respondent(survey, user):
        status_conditions = []
        status_conditions.append(Status.actor == str(user.user_uuid))
        survey_conditions = []
        survey_conditions.append(SecureMessage.survey == survey)
        return status_conditions, survey_conditions
