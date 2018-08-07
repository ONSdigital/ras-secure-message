import logging

from flask_restful import Resource
from flask import jsonify, current_app
from structlog import wrap_logger

from secure_message.repository.retriever import Retriever
from secure_message.services.service_toggles import party

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
        return Retriever.check_db_connection()


class HealthDetails(Resource):

    """Rest endpoint to provide application details"""

    @staticmethod
    def get():
        """returns environment and api endpoint details"""
        func_list = {}
        for rule in current_app.url_map.iter_rules():
            if rule.endpoint != 'static':
                func_list[rule.rule] = current_app.view_functions[rule.endpoint].__doc__

        details = {'Name': current_app.config['NAME'],
                   'Version': current_app.config['VERSION'],
                   'SMS Log level': current_app.config['SMS_LOG_LEVEL'],
                   'API Functionality': func_list,
                   'Using party service mock': party.using_mock,
                   'RAS PARTY SERVICE HOST': current_app.config['RAS_PARTY_SERVICE_HOST'],
                   'RAS PARTY SERVICE PORT': current_app.config['RAS_PARTY_SERVICE_PORT'],
                   'RAS PARTY SERVICE PROTOCOL': current_app.config['RAS_PARTY_SERVICE_PROTOCOL'],
                   'NOTIFY VIA GOV NOTIFY': current_app.config['NOTIFY_VIA_GOV_NOTIFY']}

        return jsonify(details)
