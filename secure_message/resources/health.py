import logging

from flask import current_app, jsonify
from flask_restful import Resource
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
            if rule.endpoint != "static":
                func_list[rule.rule] = current_app.view_functions[rule.endpoint].__doc__

        details = {
            "Name": "ras-secure-message",
            "Version": current_app.config["VERSION"],
            "Logging level": current_app.config["LOGGING_LEVEL"],
            "API Functionality": func_list,
            "Using party service mock": party.using_mock,
            "RAS-PARTY URL": current_app.config["PARTY_URL"],
            "NOTIFY VIA GOV NOTIFY": current_app.config["NOTIFY_VIA_GOV_NOTIFY"],
        }

        return jsonify(details)
