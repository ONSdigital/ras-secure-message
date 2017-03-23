from flask import Flask
from flask_restful import Api
from app.resources.messages import MessageList, MessageSend, MessageById
from app.resources.health import Health
from app.data_model import database
from app import settings
import logging
from logging.config import dictConfig

""" initialise logging defaults for project """
logging_config = dict(
        version = 1,
        disable_existing_loggers = False,
        formatters={
            'f': {'format':
                      '%(asctime)s %(levelname)s %(name)s %(message)s'}
        },
        handlers={
            'h': {'class': 'logging.StreamHandler',
                  'formatter': 'f',
                  'level': settings.SMS_LOG_LEVEL}
        },
        root={
            'handlers': ['h'],
            'level': settings.SMS_LOG_LEVEL,
        },
    )

dictConfig(logging_config)
# set werkzeug logging level
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(level=settings.SMS_WERKZEUG_LOG_LEVEL)

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SECURE_MESSAGING_DATABASE_URL
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(settings.APP_LOG_LEVEL)
database.db.init_app(app)

logger = logging.getLogger(__name__)
logger.info('Starting application')
logger.info('SMS Log level: {}'.format(settings.SMS_LOG_LEVEL))
logger.info('APP Log Level: {}'.format(settings.APP_LOG_LEVEL))
logger.debug('Database URL: {}'.format(settings.SECURE_MESSAGING_DATABASE_URL))


def drop_database():
    database.db.drop_all()

with app.app_context():
    database.db.create_all()
    database.db.session.commit()

api.add_resource(Health, '/health')
api.add_resource(MessageList, '/messages', )
api.add_resource(MessageSend, '/message/send')
api.add_resource(MessageById, '/message/<int:message_id>')
