import logging

from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class Authorizer:

    @staticmethod
    def can_user_view_message(user, message):
        """ 
            A user can view message if
            a) The user is internal ( currently no restrictions )
            or b) The user uuid is either the from or the to
            This implies that if the user for a ru changes or there are more than one enrolled users per ru
            then they cannot see the messages to the other users/ predecessors.
            If this is a problem we can add a third or whereby the user uuid appears in the business associations as
            a party_id, and the enrolment is valid for the survey
         """
        if user.is_internal:
            return True

        if user.user_uuid == message['msg_from']:
            return True

        if user.user_uuid in message['msg_to'] and 'DRAFT_INBOX' not in message['labels']:
            return True

        logger.info('User was refused viewing of message', user_uuid=user.user_uuid, role=user.role, message_id=message['msg_id'])
        return False

        # A user can save a message for a specific ru if their uuid exists in the associations and they are
        # currently enrolled on the survey