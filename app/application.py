import logging
from logging.config import dictConfig
from flask import Flask, request
from flask import jsonify
from flask_restful import Api
from flask_cors import CORS
from app import settings
from app.exception.exceptions import MessageSaveException
from app.repository import database
from app.resources.health import Health, DatabaseHealth, HealthDetails
from app.resources.messages import MessageList, MessageSend, MessageById, MessageModifyById
from app.authentication.authenticator import authenticate
from app.resources.drafts import DraftSave, DraftById, DraftModifyById, DraftList
from app.resources.threads import ThreadById, ThreadList
from app import connector
from app.logger_config import logger_initial_config

logger_initial_config(service_name='ras-secure-message')

logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = connector.getDatabaseUri()
app.config['SQLALCHEMY_POOL_SIZE'] = settings.SQLALCHEMY_POOL_SIZE
database.db.init_app(app)

logger.info('Starting application')


def drop_database():
    database.db.drop_all()

with app.app_context():
    database.db.create_all()
    database.db.session.commit()

api.add_resource(Health, '/health')
api.add_resource(DatabaseHealth, '/health/db')
api.add_resource(HealthDetails, '/health/details')
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
    if request.endpoint is not None and 'health' not in request.endpoint and request.method != 'OPTIONS':
        res = authenticate(request.headers)
        if res != {'status': "ok"}:
            return res


@app.errorhandler(MessageSaveException)
def handle_save_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
