import logging
import os

from flask import Flask, request
from flask import json, jsonify
from flask_restful import Api
from flask_cors import CORS
from structlog import wrap_logger
from sqlalchemy import event, DDL

from secure_message.repository import database
from secure_message.resources.health import Health, DatabaseHealth, HealthDetails
from secure_message.resources.info import Info
from secure_message.resources.labels import Labels
from secure_message.resources.messages import MessageList, MessageSend, MessageById, MessageModifyById
from secure_message.authentication.authenticator import authenticate
from secure_message.resources.drafts import DraftSave, DraftById, DraftModifyById, DraftList
from secure_message.resources.threads import ThreadById, ThreadList
from secure_message.logger_config import logger_initial_config


logger_initial_config(service_name='ras-secure-message')
logger = wrap_logger(logging.getLogger(__name__))


def create_app(config=None):
    app = Flask(__name__)
    app_config = f"config.{config or os.getenv('APP_SETTINGS', 'Config')}"
    app.config.from_object(app_config)
    api = Api(app)
    CORS(app)

    database.db.init_app(app)

    logger.info('Starting Secure Message Service...', config=app_config)

    with app.app_context():
        event.listen(database.db.metadata, 'before_create', DDL("CREATE SCHEMA IF NOT EXISTS securemessage"))
        database.db.create_all()
        database.db.session.commit()  # NOQA pylint:disable=no-member

    api.add_resource(Health, '/health')
    api.add_resource(DatabaseHealth, '/health/db')
    api.add_resource(HealthDetails, '/health/details')
    api.add_resource(Info, '/info')
    api.add_resource(MessageList, '/messages')
    api.add_resource(MessageSend, '/message/send')
    api.add_resource(MessageById, '/message/<message_id>')
    api.add_resource(MessageModifyById, '/message/<message_id>/modify')
    api.add_resource(DraftSave, '/draft/save')
    api.add_resource(DraftModifyById, '/draft/<draft_id>/modify')
    api.add_resource(DraftById, '/draft/<draft_id>')
    api.add_resource(ThreadById, '/thread/<thread_id>')
    api.add_resource(DraftList, '/drafts')
    api.add_resource(ThreadList, '/threads')
    api.add_resource(Labels, '/labels')

    @app.before_request
    def before_request():  # NOQA pylint:disable=unused-variable
        if _request_requires_authentication():
            log_request()
            res = authenticate(request.headers)
            if res != {'status': "ok"}:
                logger.error('Failed to authenticate user', result=res)
                return res

    @app.errorhandler(Exception)
    def handle_exception(error):  # NOQA pylint:disable=unused-variable
        logger.exception(error=error)
        response = jsonify({"error": "Unknown internal error"})
        response.status_code = 500
        return response

    return app


def _request_requires_authentication():
    return request.endpoint is not None and 'health' not in request.endpoint and request.endpoint != 'info'and request.method != 'OPTIONS'


def log_request():
    """ Outputs the request header, body and parameters information from request in the form of a debug logger"""
    header = request.headers
    header_list = []
    for x, y in header.items():
        header_list.append(str(x) + ': ' + str(y) + ', ')
    headers = ''.join(header_list)

    req_data = request.data
    if req_data is None or req_data is b'':    # pylint:disable=literal-comparison
        req_data = 'Empty'
    else:
        req_data = json.loads(req_data)

    req_args = request.args
    args_list = []
    count = 0

    for key, val in req_args.items():
        count += 1
        args_list.append('arg ' + str(count) + ' = ' + str(key) + ': ' + str(val))

    params = ''.join(args_list)
    logger.debug('Incoming request', headers=headers, req_data=req_data, arguments=params)
