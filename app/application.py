from flask import Flask
from flask_restful import Api
from app.resources.messages import MessageList, MessageSend, MessageById
from app.resources.health import Health
from app.data_model import database
from app import settings
import logging.config

logger = logging.getLogger(__name__)


def configure_logging():
    """ initialise logging defaults for project """
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # add the handlers to the logger
    # logging.root.addHandler(console_handler)
    logging.root.setLevel(logging.DEBUG)
    # set werkzeug logging level
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(level=settings.SMS_WERKZEUG_LOG_LEVEL)

configure_logging()

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SECURE_MESSAGING_DATABASE_URL
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(settings.APP_LOG_LEVEL)
database.db.init_app(app)
logging.debug("Starting application")

def drop_database():
    database.db.drop_all()

with app.app_context():
    database.db.create_all()
    database.db.session.commit()

api.add_resource(Health, '/health')
api.add_resource(MessageList, '/messages', )
api.add_resource(MessageSend, '/message/send')
api.add_resource(MessageById, '/message/<int:message_id>')
