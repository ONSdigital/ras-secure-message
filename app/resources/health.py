from flask_restful import Resource
from flask import jsonify
from app.repository.retriever import Retriever
from app import settings


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


class Details(Resource):

    """Rest endpoint to provide application details"""

    @staticmethod
    def get():
        from app import application
        func_list = {}
        for rule in application.app.url_map.iter_rules():
            if rule.endpoint != 'static':
                func_list[rule.rule] = application.app.view_functions[rule.endpoint].__doc__

        details = {'SMS Log level': settings.SMS_LOG_LEVEL,
                   'APP Log Level': settings.APP_LOG_LEVEL,
                   'Database URL': settings.SECURE_MESSAGING_DATABASE_URL,
                   'API Functionality': func_list
                   }

        return jsonify(details)
