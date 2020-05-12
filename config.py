import os
import logging
from distutils.util import strtobool

from structlog import wrap_logger


logger = wrap_logger(logging.getLogger(__name__))


class Config:
    """
    This object is the main configuration for the Secure Messaging Service.
    It contains a full default configuration
    All configuration may be overridden by setting the appropriate environment variable name.
    """
    VERSION = '1.3.0'

    SECURE_MESSAGING_DATABASE_URL = os.getenv(
        'SECURE_MESSAGING_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432')



    # LOGGING SETTINGS
    SMS_LOG_LEVEL = os.getenv('SMS_LOG_LEVEL', 'DEBUG')

    # EMAIL NOTIFICATION SETTINGS
    NOTIFY_VIA_GOV_NOTIFY = os.getenv('NOTIFY_VIA_GOV_NOTIFY')
    NOTIFICATION_TEMPLATE_ID = os.getenv('NOTIFICATION_TEMPLATE_ID')
    NOTIFICATION_DEV_EMAIL = os.getenv('NOTIFICATION_DEV_EMAIL', 'notanemail@email.com')
    NOTIFY_GATEWAY_URL = os.getenv('NOTIFY_GATEWAY_URL')
    REQUESTS_POST_TIMEOUT = os.getenv('REQUESTS_POST_TIMEOUT', 20)

    # JWT authentication config
    JWT_SECRET = os.getenv('JWT_SECRET')

    # Services
    PARTY_SERVICE_HOST = os.getenv('PARTY_SERVICE_HOST', 'localhost')
    PARTY_SERVICE_PORT = os.getenv('PARTY_SERVICE_PORT', 8081)
    PARTY_SERVICE_PROTOCOL = os.getenv('PARTY_SERVICE_PROTOCOL', 'http')
    PARTY_SERVICE = f'{PARTY_SERVICE_PROTOCOL}://{PARTY_SERVICE_HOST}:{PARTY_SERVICE_PORT}/'

    FRONTSTAGE_SERVICE_URL = os.getenv('FRONTSTAGE_SERVICE_HOST', 'localhost:8082')
    FRONTSTAGE_SERVICE_PROTOCOL = os.getenv('FRONTSTAGE_SERVICE_PROTOCOL', 'http')
    RAS_FRONTSTAGE_SERVICE = f'{FRONTSTAGE_SERVICE_PROTOCOL}://{FRONTSTAGE_SERVICE_URL}/'

    # uaa
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    UAA_URL = os.getenv('UAA_URL')

    NON_DEFAULT_VARIABLES = ['JWT_SECRET', 'SECURITY_USER_NAME', 'SECURITY_USER_PASSWORD',
                             'NOTIFICATION_TEMPLATE_ID', 'CLIENT_ID', 'CLIENT_SECRET']

    # These should always be set in the environment on prod
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')

    # Basic auth parameters
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    SQLALCHEMY_DATABASE_URI = SECURE_MESSAGING_DATABASE_URL

    # UAA
    USE_UAA = 1


class DevConfig(Config):

    JWT_SECRET = os.getenv('JWT_SECRET', 'testsecret')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    NOTIFY_VIA_GOV_NOTIFY = os.getenv('NOTIFY_VIA_GOV_NOTIFY', '0')
    NOTIFICATION_TEMPLATE_ID = os.getenv(
        'NOTIFICATION_TEMPLATE_ID', 'test_notification_template_id')
    NOTIFY_GATEWAY_URL = os.getenv('NOTIFY_GATEWAY_URL', 'http://localhost:5181/emails/')
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME', 'admin')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD', 'secret')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    # uaa
    CLIENT_ID = os.getenv('CLIENT_ID', 'secure_message')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'password')
    UAA_URL = os.getenv('UAA_URL', 'http://localhost:9080')
    USE_UAA = int(os.getenv('USE_UAA', 1))


class TestConfig(DevConfig):
    TESTING = True
    USE_UAA = 0

    # LOGGING SETTINGS
    SMS_LOG_LEVEL = 'ERROR'
