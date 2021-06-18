import logging

from marshmallow import Schema, fields, validates, ValidationError
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class ThreadPatch(Schema):

    """ Class to marshal JSON to Message"""
    category = fields.Str()
    is_closed = fields.Boolean()

    @staticmethod
    @validates("category")
    def validate_category(value):
        if not value:
            raise ValidationError("category cannot be empty")

        valid_survey_categories = ['SURVEY', 'TECHNICAL', 'MISC']
        if value and value not in valid_survey_categories:
            raise ValidationError(f"category can only be one of {valid_survey_categories}")
