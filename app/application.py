import logging
from flask import Flask, request
from flask import jsonify, json
from flask_restful import Api
from flask_cors import CORS
from app import settings
from app.exception.exceptions import MessageSaveException
from app.repository import database
from app.resources.health import Health, DatabaseHealth, HealthDetails
from app.resources.info import Info
from app.resources.messages import MessageList, MessageSend, MessageById, MessageModifyById
from app.authentication.authenticator import authenticate
from app.resources.drafts import DraftSave, DraftById, DraftModifyById, DraftList
from app.resources.threads import ThreadById, ThreadList
from app.cloud.cloud_foundry import ONSCloudFoundry
from app import connector
from app.logger_config import logger_initial_config
from structlog import wrap_logger

logger_initial_config(service_name='ras-secure-message')

logger = wrap_logger(logging.getLogger(__name__))


# use cf env to extract Cloud Foundry environment
cf = ONSCloudFoundry()


app = Flask(__name__)
api = Api(app)
CORS(app)

if cf.detected:
    protocol = cf.protocol
    cf_database_service = cf.database()
    logger.info('* Cloud Foundry protocol "{}"'.format(protocol))
    logger.info('* Cloud Foundry database service "{}"'.format(cf_database_service))
    app.config['SQLALCHEMY_DATABASE_URI'] = cf.credentials()
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = connector.get_database_uri()

app.config['SQLALCHEMY_POOL_SIZE'] = settings.SQLALCHEMY_POOL_SIZE
database.db.init_app(app)

logger.info('Starting Secure Message Service ...')

def drop_database():
    database.db.drop_all()


with app.app_context():
    database.db.create_all()
    database.db.session.commit()

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


@app.before_request
def before_request():
    if _request_requires_authentication():
        log_request()
        res = authenticate(request.headers)
        if res != {'status': "ok"}:
            logger.debug("Failed to authenticate user")
            return res


def _request_requires_authentication():
    return request.endpoint is not None and \
           'health' not in request.endpoint \
           and request.endpoint != 'info' \
           and request.method != 'OPTIONS'


@app.errorhandler(MessageSaveException)
def handle_save_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def log_request():
    """ Outputs the request header, body and parameters information from request in the form of a debug logger"""
    header = request.headers
    header_list = []
    for x, y in header.items():
        header_list.append(str(x) + ': ' + str(y) + ', ')
    headers = ''.join(header_list)

    req_data = request.data
    if req_data is None or req_data is b'':
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
    logger.debug('Headers: ' + str(headers) + ' Body: ' + str(req_data) + ' Arguments: ' + str(params))
