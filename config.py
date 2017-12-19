import os


class Config(object):
    DEBUG = False
    TESTING = False
    NAME = 'ras-secure-message'
    VERSION = '1.0.0'

    SECURE_MESSAGING_DATABASE_URL = os.getenv('SECURE_MESSAGING_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432')

    # LOGGING STANDARDS
    SMS_LOG_LEVEL = os.getenv('SMS_LOG_LEVEL', 'INFO')
    APP_LOG_LEVEL = os.getenv('APP_LOG_LEVEL', 'INFO')
    SMS_WERKZEUG_LOG_LEVEL = os.getenv('SMS_WERKZEUG_LOG_LEVEL', 'INFO')

    # EMAIL NOTIFICATION SETTINGS
    NOTIFICATION_SERVICE_ID = os.getenv('SERVICE_ID')
    NOTIFICATION_API_KEY = os.getenv('NOTIFICATION_API_KEY')
    NOTIFICATION_COMBINED_KEY = 'key-name-{}-{}'.format(NOTIFICATION_SERVICE_ID, NOTIFICATION_API_KEY)
    NOTIFICATION_TEMPLATE_ID = os.getenv('NOTIFICATION_TEMPLATE_ID')
    NOTIFICATION_DEV_EMAIL = os.getenv('NOTIFICATION_DEV_EMAIL', 'notanemail@email.com')
    NOTIFY_VIA_GOV_NOTIFY = os.getenv('NOTIFY_VIA_GOV_NOTIFY', '1')
    RM_NOTIFY_GATEWAY_URL = os.getenv('RM_NOTIFY_GATEWAY_URL', "http://notifygatewaysvc-dev.apps.devtest.onsclofo.uk/emails/")
    REQUESTS_POST_TIMEOUT = os.getenv('REQUESTS_POST_TIMEOUT', 20)

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
    SM_USER_AUTHENTICATION_PRIVATE_KEY = open("{0}/jwt-test-keys/sm-user-authentication-encryption-private-key.pem".format(os.getenv('RAS_SM_PATH'))) \
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

    NOTIFY_CASE_SERVICE = os.getenv('NOTIFY_CASE_SERVICE', '1')

    NON_DEFAULT_VARIABLES = ['JWT_SECRET', 'SECURITY_USER_NAME', 'SECURITY_USER_PASSWORD',
                             'NOTIFICATION_API_KEY', 'SERVICE_ID', 'NOTIFICATION_TEMPLATE_ID']


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SM_JWT_SECRET = os.getenv('JWT_SECRET', 'vrwgLNWEffe45thh545yuby')
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME', 'test_user')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD', 'test_password')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)
    SMS_LOG_LEVEL = os.getenv('SMS_LOG_LEVEL', 'DEBUG')
    APP_LOG_LEVEL = os.getenv('APP_LOG_LEVEL', 'DEBUG')
    SMS_WERKZEUG_LOG_LEVEL = os.getenv('SMS_WERKZEUG_LOG_LEVEL', 'DEBUG')
    JWT_SECRET = os.getenv('JWT_SECRET', 'vrwgLNWEffe45thh545yuby')
    NOTIFY_VIA_GOV_NOTIFY = os.getenv('NOTIFY_VIA_GOV_NOTIFY', '0')
    NOTIFICATION_API_KEY = os.getenv('NOTIFICATION_API_KEY', 'test_notification_api_key')
    SERVICE_ID = os.getenv('SERVICE_ID', 'test_service_id')
    NOTIFICATION_TEMPLATE_ID = os.getenv('NOTIFICATION_TEMPLATE_ID', 'test_notification_template_id')
    RAS_SM_PATH = os.getenv('RAS_SM_PATH', './')


class TestingConfig(DevelopmentConfig):
    TESTING = True
    DEVELOPMENT = False
