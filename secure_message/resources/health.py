import logging

from flask_restful import Resource
from flask import jsonify, current_app
from secure_message.repository.retriever import Retriever
from secure_message.services.service_toggles import party
from secure_message import settings
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class Health(Resource):

    """Rest endpoint to provide application general health"""

    @staticmethod
    def get():
        return "{status : healthy}"


class DatabaseHealth(Resource):

    """Rest endpoint to provide application database health"""

    @staticmethod
    def get():
        return Retriever().check_db_connection()


class HealthDetails(Resource):

    """Rest endpoint to provide application details"""

    @staticmethod
    def get():
        """returns environment and api endpoint details"""
        from secure_message import application
        func_list = {}
        for rule in application.app.url_map.iter_rules():
            if rule.endpoint != 'static':
                func_list[rule.rule] = application.app.view_functions[rule.endpoint].__doc__

        details = {'Name': settings.NAME,
                   'Version': settings.VERSION,
                   'SMS Log level': settings.SMS_LOG_LEVEL,
                   'APP Log Level': settings.APP_LOG_LEVEL,
                   'Database URL': current_app.config['SQLALCHEMY_DATABASE_URI'],
                   'API Functionality': func_list,
                   'Using party service mock': party._use_mock,
                   'SM JWT ENCRYPT': settings.SM_JWT_ENCRYPT,
                   'RAS PARTY SERVICE HOST': settings.RAS_PARTY_SERVICE_HOST,
                   'RAS PARTY SERVICE PORT': settings.RAS_PARTY_SERVICE_PORT,
                   'RAS PARTY SERVICE PROTOCOL': settings.RAS_PARTY_SERVICE_PROTOCOL,
                   'NOTIFY VIA GOV NOTIFY': settings.NOTIFY_VIA_GOV_NOTIFY,
                   'NOTIFY CASE SERVICE': settings.NOTIFY_CASE_SERVICE}

        return jsonify(details)
