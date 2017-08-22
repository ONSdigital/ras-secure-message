import json
import logging

from pathlib import Path
from flask import jsonify, make_response
from flask_restful import Resource
from structlog import wrap_logger
from app import settings

logger = wrap_logger(logging.getLogger(__name__))


class Info(Resource):

    """Rest endpoint to provide application information"""

    @staticmethod
    def get():
        _health_check = {}
        if Path('git_info').exists():
            with open('git_info') as io:
                _health_check = json.loads(io.read())

        info = {"name": settings.NAME,
                "version": settings.VERSION, }

        info = dict(_health_check, **info)

        return make_response(jsonify(info), 200)
