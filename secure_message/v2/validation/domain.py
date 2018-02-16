from flask import g
from marshmallow import validates, ValidationError

from secure_message import constants
from secure_message.validation.domain import MessageSchema, logger


class MessageSchemaV2(MessageSchema):

    @validates("msg_from")
    def validate_from(self, msg_from):
        self.validate_non_zero_field_length("msg_from", len(msg_from), constants.MAX_FROM_LEN)

        if msg_from != g.user.user_uuid:
            logger.error('Users can only send messages from themselves',
                         message_from=msg_from, user_uuid=g.user.user_uuid)
            raise ValidationError('You are not authorised to send a message on behalf of user or work group {0}'.format(msg_from))
