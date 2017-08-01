import logging
from flask_restful import Resource
from flask import jsonify
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class Info(Resource):

    """Rest endpoint to provide application information"""

    @staticmethod
    def get():
        details = {'name': 'secure_message',
                   'version': '0.0.1',
                   'origin': 'https://github.com/ONSdigital/ras-secure-message.git',
                   'commit': 'not specified',
                   'branch': 'not specified',
                   'built': '01-01-1900 00:00:00.000'}

        return jsonify(details)
