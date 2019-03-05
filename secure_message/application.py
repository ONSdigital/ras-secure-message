import logging
import os
import sys
from time import sleep
import requestsdefaulter

from flask import Flask, request
from flask import json, jsonify
from flask_restful import Api
from flask_cors import CORS
import maya
from flask_zipkin import Zipkin
from retrying import retry
import requests
from requests.adapters import HTTPAdapter
from sqlalchemy import DDL, event
from sqlalchemy.exc import DatabaseError, ProgrammingError
from structlog import wrap_logger


from secure_message.authentication.authenticator import authenticate
from secure_message.exception.exceptions import MissingEnvironmentVariable
from secure_message.logger_config import logger_initial_config
from secure_message.repository import database
from secure_message.resources.health import DatabaseHealth, Health, HealthDetails
from secure_message.resources.info import Info
from secure_message.resources.messages import MessageModifyById, MessageSend
from secure_message.resources.threads import ThreadById, ThreadCounter, ThreadList

logger = wrap_logger(logging.getLogger(__name__))


def create_app(config=None):
    app = Flask(__name__)
    app.name = "ras-secure-message"
    app_config = f"config.{config or os.getenv('APP_SETTINGS', 'Config')}"
    app.config.from_object(app_config)

    # Zipkin
    zipkin = Zipkin(app=app, sample_rate=app.config.get("ZIPKIN_SAMPLE_RATE"))
    requestsdefaulter.default_headers(zipkin.create_http_headers_for_new_span)

    logger_initial_config(service_name='ras-secure-message', log_level=app.config.get('SMS_LOG_LEVEL'))

    missing_vars = [var for var in app.config['NON_DEFAULT_VARIABLES']
                    if app.config.get(var) is None]

    if missing_vars:
        raise MissingEnvironmentVariable(missing_vars)

    api = Api(app)
    CORS(app)

    logger.info('Starting Secure Message Service...', config=app_config)

    create_db(app)

    api.add_resource(Health, '/health')
    api.add_resource(DatabaseHealth, '/health/db')
    api.add_resource(HealthDetails, '/health/details')
    api.add_resource(Info, '/info')

    api.add_resource(MessageSend, '/message/send', '/v2/messages')
    api.add_resource(MessageModifyById, '/message/<message_id>/modify',
                     '/v2/messages/modify/<message_id>')

    api.add_resource(ThreadList, '/threads')
    api.add_resource(ThreadById, '/thread/<thread_id>', '/v2/threads/<thread_id>')
    api.add_resource(ThreadCounter, '/v2/messages/count')

    app.oauth_client_token_expires_at = maya.now()

    if app.config['USE_UAA']:
        cache_client_token(app)

    @app.before_request
    def before_request():  # NOQA pylint:disable=unused-variable
        if app.config['USE_UAA']:
            refresh_client_token_if_required(app)
        if _request_requires_authentication():
            log_request()
            res = authenticate(request.headers)
            if res != {'status': "ok"}:
                logger.error('Failed to authenticate user', result=res)
                return res
        return None

    @app.errorhandler(Exception)
    def handle_exception(error):  # NOQA pylint:disable=unused-variable
        logger.exception(error=error)
        response = jsonify({"error": "Unknown internal error"})
        response.status_code = 500
        return response

    return app


def refresh_client_token_if_required(app):
    if app.oauth_client_token_expires_at <= maya.now():
        cache_client_token(app)


def cache_client_token(app):
    app.oauth_client_token = get_client_token(app.config['CLIENT_ID'],
                                              app.config['CLIENT_SECRET'],
                                              app.config['UAA_URL'])

    expires_in = app.oauth_client_token['expires_in'] - 10
    app.oauth_client_token_expires_at = maya.now().add(seconds=expires_in)


def get_client_token(client_id, client_secret, url):
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}

    payload = {'grant_type': 'client_credentials',
               'response_type': 'token',
               'token_format': 'opaque'}

    get_token_url = f'{url}/oauth/token'

    s = requests.Session()
    s.mount(get_token_url, HTTPAdapter(max_retries=15))

    try:
        logger.info("Attempting to GET client token from UAA")
        response = s.post(get_token_url,
                          headers=headers,
                          params=payload,
                          auth=(client_id, client_secret))
        response.raise_for_status()

        try:
            logger.info("Decoding client token response json")
            return response.json()
        except ValueError:
            logger.exception("Failed to decode response JSON. Retrying in 10 seconds.")
            sleep(10)
            return get_client_token(client_id, client_secret, url)

    except requests.HTTPError as e:
        logger.exception(
            f"{e.response.status_code} response received while retrieving client token.")
        if e.response.status_code >= 500:
            logger.info("Retrying client token retrieval in 1 seconds.")
            sleep(1)
            return get_client_token(client_id, client_secret, url)
        if 400 <= e.response.status_code < 500:
            logger.warning("Client error encountered. Shutting down.")
            sys.exit(1)
    except requests.RequestException as e:
        logger.exception(f"{e.__class__.__name__} occured while retrieving client token.")
        logger.info("Retrying client token retrieval in 10 seconds.")
        sleep(10)
        return get_client_token(client_id, client_secret, url)


def retry_if_database_error(exception):
    logger.error('Database error has occurred', error=exception)
    return isinstance(exception, DatabaseError) and not isinstance(exception, ProgrammingError)


@retry(retry_on_exception=retry_if_database_error, wait_fixed=2000, stop_max_delay=30000, wrap_exception=True)
def create_db(app):
    database.db.init_app(app)
    with app.app_context():
        event.listen(database.db.metadata, 'before_create', DDL(
            "CREATE SCHEMA IF NOT EXISTS securemessage"))
        database.db.create_all()
        database.db.session.commit()  # NOQA pylint:disable=no-member


def _request_requires_authentication():
    return request.endpoint is not None and 'health' not in request.endpoint and request.endpoint != 'info' and request.method != 'OPTIONS'


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
