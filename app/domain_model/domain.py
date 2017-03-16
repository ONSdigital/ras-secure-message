from marshmallow import Schema, fields, post_load, validates, ValidationError


class Message:

    def __init__(self, msg_to, msg_from, body):
        self.msg_to = msg_to
        self.msg_from = msg_from
        self.body = body
        # self.submitted_at = datetime.now()

    def __repr__(self):
        return '<Message(msg_to={self.msg_to} msg_from={self.msg_from} body={self.body})>'.format(self=self)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class MessageSchema(Schema):

    """ Class to marshal JSON to Message"""

    msg_to = fields.Str(required=True)
    msg_from = fields.Str(required=True)
    body = fields.Str(required=True)

    @validates('msg_to')
    def validate_msg_to_length(self, x):
        if len(x) <= 0:
            raise ValidationError('Quantity must be greater than 0.')
        if len(x) > 100:
            raise ValidationError('Quantity must not be greater than 100.')

    @validates('msg_from')
    def validate_msg_from_length(self, x):
        if len(x) <= 0:
            raise ValidationError('Quantity must be greater than 0.')
        if len(x) > 100:
            raise ValidationError('Quantity must not be greater than 100.')

    @validates('body')
    def validate_body_length(self, x):
        if len(x) <= 0:
            raise ValidationError('Quantity must be greater than 0.')
        if len(x) > 1000:
            raise ValidationError('Quantity must not be greater than 1000.')

    @post_load
    def make_message(self, data):
        return Message(**data)
