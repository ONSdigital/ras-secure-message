import os
import logging

from structlog import wrap_logger

from secure_message.cloud.cloud_foundry import ONSCloudFoundry

# use cf env to extract Cloud Foundry environment
cf = ONSCloudFoundry()
logger = wrap_logger(logging.getLogger(__name__))


class Config:
    """
    This object is the main configuration for the Secure Messaging Service.
    It contains a full default configuration
    All configuration may be overridden by setting the appropriate environment variable name.
    """
    NAME = os.getenv('NAME', 'ras-secure-message')
    VERSION = os.getenv('VERSION', '0.3.0')

    SECURE_MESSAGING_DATABASE_URL = os.getenv(
        'SECURE_MESSAGING_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432')

    if cf.detected:
        logger.info('Cloud Foundry environment identified.',
                    protocol=cf.protocol, database=cf.database())
        SQLALCHEMY_DATABASE_URI = cf.credentials()
    else:
        SQLALCHEMY_DATABASE_URI = SECURE_MESSAGING_DATABASE_URL

    # LOGGING SETTINGS
    SMS_LOG_LEVEL = os.getenv('SMS_LOG_LEVEL', 'DEBUG')

    # EMAIL NOTIFICATION SETTINGS
    NOTIFICATION_SERVICE_ID = os.getenv('SERVICE_ID')
    NOTIFICATION_API_KEY = os.getenv('NOTIFICATION_API_KEY')
    NOTIFICATION_COMBINED_KEY = f'key-name-{NOTIFICATION_SERVICE_ID}-{NOTIFICATION_API_KEY}'
    NOTIFICATION_TEMPLATE_ID = os.getenv('NOTIFICATION_TEMPLATE_ID')
    NOTIFICATION_DEV_EMAIL = os.getenv('NOTIFICATION_DEV_EMAIL', 'notanemail@email.com')
    NOTIFY_VIA_GOV_NOTIFY = os.getenv('NOTIFY_VIA_GOV_NOTIFY', '1')
    RM_NOTIFY_GATEWAY_URL = os.getenv(
        'RM_NOTIFY_GATEWAY_URL', "http://notifygatewaysvc-dev.apps.devtest.onsclofo.uk/emails/")
    REQUESTS_POST_TIMEOUT = os.getenv('REQUESTS_POST_TIMEOUT', 20)

    # SQLAlchemy configuration
    SQLALCHEMY_POOL_SIZE = os.getenv('SQLALCHEMY_POOL_SIZE', 5)

    # JWT authentication config
    SM_JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_SECRET = os.getenv('JWT_SECRET')

    # Services
    RAS_PARTY_SERVICE_HOST = os.getenv('RAS_PARTY_SERVICE_HOST', 'localhost')
    RAS_PARTY_SERVICE_PORT = os.getenv('RAS_PARTY_SERVICE_PORT', 8081)
    RAS_PARTY_SERVICE_PROTOCOL = os.getenv('RAS_PARTY_SERVICE_PROTOCOL', 'http')
    RAS_PARTY_SERVICE = f'{RAS_PARTY_SERVICE_PROTOCOL}://{RAS_PARTY_SERVICE_HOST}:{RAS_PARTY_SERVICE_PORT}/'

    RM_CASE_SERVICE_HOST = os.getenv('RM_CASE_SERVICE_HOST', 'localhost')
    RM_CASE_SERVICE_PORT = os.getenv('RM_CASE_SERVICE_PORT', 8171)
    RM_CASE_SERVICE_PROTOCOL = os.getenv('RM_CASE_SERVICE_PROTOCOL', 'http')
    RM_CASE_SERVICE = f'{RM_CASE_SERVICE_PROTOCOL}://{RM_CASE_SERVICE_HOST}:{RM_CASE_SERVICE_PORT}/'

    NOTIFY_CASE_SERVICE = os.getenv('NOTIFY_CASE_SERVICE', '1')

    # uaa
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    UAA_URL = os.getenv('UAA_URL')

    NON_DEFAULT_VARIABLES = ['JWT_SECRET', 'SECURITY_USER_NAME', 'SECURITY_USER_PASSWORD',
                             'NOTIFICATION_API_KEY', 'SERVICE_ID', 'NOTIFICATION_TEMPLATE_ID',
                             'CLIENT_ID', 'CLIENT_SECRET']

    # These should always be set in the environment on prod
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
    NOTIFY_VIA_GOV_NOTIFY = os.getenv('NOTIFY_VIA_GOV_NOTIFY')
    NOTIFICATION_API_KEY = os.getenv('NOTIFICATION_API_KEY')
    NOTIFICATION_TEMPLATE_ID = os.getenv('NOTIFICATION_TEMPLATE_ID')
    SERVICE_ID = os.getenv('SERVICE_ID')

    # Basic auth parameters
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # UAA
    USE_UAA = 1


class DevConfig(Config):

    JWT_SECRET = os.getenv('JWT_SECRET', 'testsecret')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    NOTIFY_VIA_GOV_NOTIFY = os.getenv('NOTIFY_VIA_GOV_NOTIFY', '0')
    NOTIFICATION_API_KEY = os.getenv('NOTIFICATION_API_KEY', 'test_notification_api_key')
    NOTIFICATION_TEMPLATE_ID = os.getenv(
        'NOTIFICATION_TEMPLATE_ID', 'test_notification_template_id')
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME', 'admin')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD', 'secret')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)
    SERVICE_ID = os.getenv('SERVICE_ID', 'test_service_id')

    # uaa
    CLIENT_ID = os.getenv('CLIENT_ID', 'secure_message')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'password')
    UAA_URL = os.getenv('UAA_URL', 'http://uaa-dev.apps.devtest.onsclofo.uk')
    USE_UAA = int(os.getenv('USE_UAA', 1))


class TestConfig(DevConfig):
    TESTING = True
    USE_UAA = 0

    # LOGGING SETTINGS
    SMS_LOG_LEVEL = 'ERROR'
