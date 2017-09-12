import os
import logging
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))

''' This file is the main configuration for the Secure Messaging Service.
    It contains a full default configuration
    All configuration may be overridden by setting the appropriate environment variable name. '''

NAME = os.getenv('NAME', 'ras-secure-message')
VERSION = os.getenv('VERSION', '0.1.0')

SECURE_MESSAGING_DATABASE_URL = os.getenv('SECURE_MESSAGING_DATABASE_URL', 'sqlite:////tmp/messages.db')

ACCESS_CONTROL_ALLOW_ORIGIN = os.getenv('ACCESS_CONTROL_ALLOW_ORIGIN', '*')

# LOGGING SETTINGS
SMS_LOG_LEVEL = os.getenv('SMS_LOG_LEVEL', 'INFO')
APP_LOG_LEVEL = os.getenv('APP_LOG_LEVEL', 'INFO')
SMS_WERKZEUG_LOG_LEVEL = os.getenv('SMS_WERKZEUG_LOG_LEVEL', 'INFO')


# EMAIL NOTIFICATION SETTINGS
NOTIFICATION_SERVICE_ID = os.getenv('SERVICE_ID')
NOTIFICATION_API_KEY = os.getenv('NOTIFICATION_API_KEY')
NOTIFICATION_COMBINED_KEY = 'key-name-{}-{}'.format(NOTIFICATION_SERVICE_ID, NOTIFICATION_API_KEY)
NOTIFICATION_API_KEY = os.getenv('NOTIFICATION_TEMPLATE_ID')
NOTIFICATION_DEV_EMAIL = os.getenv('NOTIFICATION_DEV_EMAIL', 'notanemail@email.com')

# LOGGING NOTIFICATION SETTINGS
NOTIFY_VIA_LOGGING = os.getenv('NOTIFY_VIA_LOGGING', '0')

# SQLAlchemy configuration
SQLALCHEMY_POOL_SIZE = os.getenv('SQLALCHEMY_POOL_SIZE', None)

# JWT authentication config
SM_JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
SM_JWT_SECRET = os.getenv('JWT_SECRET')
SM_JWT_ENCRYPT = os.getenv('SM_JWT_ENCRYPT', '1')

# Basic auth parameters
SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME')
SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD')
BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

#  Keys
SM_USER_AUTHENTICATION_PRIVATE_KEY = open("{0}/jwt-test-keys/sm-user-authentication-encryption-private-key.pem".format(os.getenv('RAS_SM_PATH')))\
    .read()
SM_USER_AUTHENTICATION_PUBLIC_KEY = open("{0}/jwt-test-keys/sm-user-authentication-encryption-public-key.pem".format(os.getenv('RAS_SM_PATH'))).read()

#  password
SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD = "digitaleq"

# Services
RAS_PARTY_SERVICE_HOST = os.getenv('RAS_PARTY_SERVICE_HOST', 'localhost')
RAS_PARTY_SERVICE_PORT = os.getenv('RAS_PARTY_SERVICE_PORT', 8001)
RAS_PARTY_SERVICE_PROTOCOL = os.getenv('RAS_PARTY_SERVICE_PROTOCOL', 'http')
RAS_PARTY_SERVICE = '{}://{}:{}/'.format(RAS_PARTY_SERVICE_PROTOCOL, RAS_PARTY_SERVICE_HOST, RAS_PARTY_SERVICE_PORT)
RAS_PARTY_GET_BY_BUSINESS = '{}party-api/v1/businesses/id/{}'
RAS_PARTY_GET_BY_RESPONDENT = '{}party-api/v1/respondents/id/{}'

RM_CASE_SERVICE_HOST = os.getenv('RM_CASE_SERVICE_HOST', 'localhost')
RM_CASE_SERVICE_PORT = os.getenv('RM_CASE_SERVICE_PORT', 8171)
RM_CASE_SERVICE_PROTOCOL = os.getenv('RM_CASE_SERVICE_PROTOCOL', 'http')
RM_CASE_SERVICE = '{}://{}:{}/'.format(RM_CASE_SERVICE_PROTOCOL, RM_CASE_SERVICE_HOST, RM_CASE_SERVICE_PORT)
RM_CASE_POST = '{}cases/{}/events'

NOTIFY_CASE_SERVICE = os.getenv('NOTIFY_CASE_SERVICE', 1)

NON_DEFAULT_VARIABLES = ['JWT_SECRET', 'SECURITY_USER_NAME', 'SECURITY_USER_PASSWORD',
                         'NOTIFICATION_API_KEY', 'SERVICE_ID', 'NOTIFICATION_TEMPLATE_ID']
