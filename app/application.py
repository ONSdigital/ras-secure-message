from flask import Flask
import os
from flask_restful import Api
from app.resources.messages import MessageList, MessageSend, MessageById
from app.resources.health import Health
from structlog import get_logger
from app.data_model import database
from app import settings
import logging

logger = get_logger(__name__)

SMS_LOG_LEVEL = os.getenv('SMS_LOG_LEVEL', 'INFO')
SMS_WERKZEUG_LOG_LEVEL = os.getenv('SMS_WERKZEUG_LOG_LEVEL', 'INFO')
SMS_DEVELOPER_LOGGING = os.getenv('SMS_DEVELOPER_LOGGING', 'FALSE').upper() == 'TRUE'


def configure_logging():
    log_format = "%(message)s"
    levels = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }
    handler = logging.StreamHandler()
    logging.basicConfig(level=levels[SMS_LOG_LEVEL], format=log_format, handlers=[handler])

    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(level=levels[SMS_WERKZEUG_LOG_LEVEL])

configure_logging()

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SECURE_MESSAGING_DATABASE_URL
database.db.init_app(app)


def drop_database():
    database.db.drop_all()

with app.app_context():
    database.db.create_all()
    database.db.session.commit()

api.add_resource(Health, '/health')
api.add_resource(MessageList, '/messages', )
api.add_resource(MessageSend, '/message/send')
api.add_resource(MessageById, '/message/<int:message_id>')


app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.INFO)

