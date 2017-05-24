import os


''' This file is the main configuration for the Secure Messaging Service.
    It contains a full default configuration
    All configuration may be overridden by setting the appropriate environment variable name. '''

SECURE_MESSAGING_DATABASE_URL = os.getenv('SECURE_MESSAGING_DATABASE_URL', 'sqlite:////tmp/messages.db')

ACCESS_CONTROL_ALLOW_ORIGIN = os.getenv('ACCESS_CONTROL_ALLOW_ORIGIN', '*')

# LOGGING SETTINGS

SMS_LOG_LEVEL = os.getenv('SMS_LOG_LEVEL', 'INFO')
APP_LOG_LEVEL = os.getenv('APP_LOG_LEVEL', 'INFO')
SMS_WERKZEUG_LOG_LEVEL = os.getenv('SMS_WERKZEUG_LOG_LEVEL', 'INFO')


# EMAIL NOTIFICATION SETTINGS

NOTIFICATION_SERVICE_ID = os.getenv('SERVICE_ID', '2ef5c492-8b04-4ba9-a4be-ac39419d2ede')
NOTIFICATION_API_KEY = os.getenv('NOTIFICATION_API_KEY', '61f1c499-edbe-4bf9-8dd7-bdf63923c2fd')
NOTIFICATION_COMBINED_KEY = 'key-name-{}-{}'.format(NOTIFICATION_SERVICE_ID, NOTIFICATION_API_KEY)
NOTIFICATION_TEMPLATE_ID = 'a1995c3d-68ce-42be-bddf-287b0870544b'
NOTIFICATION_DEV_EMAIL = os.getenv('NOTIFICATION_DEV_EMAIL', 'gemma.irving@ons.gov.uk')


MESSAGE_QUERY_LIMIT = os.getenv('MESSAGE_QUERY_LIMIT', 10)

# SQLAlchemy configuration

SQLALCHEMY_POOL_SIZE = os.getenv('SQLALCHEMY_POOL_SIZE', None)


JWT_SECRET = os.getenv('JWT_SECRET', 'vrwgLNWEffe45thh545yuby')

#  Keys
SM_USER_AUTHENTICATION_PRIVATE_KEY = open("{0}/jwt-test-keys/sm-user-authentication-encryption-private-key.pem".format(os.getenv('RAS_SM_PATH'))).read()
SM_USER_AUTHENTICATION_PUBLIC_KEY = open("{0}/jwt-test-keys/sm-user-authentication-encryption-public-key.pem".format(os.getenv('RAS_SM_PATH'))).read()

#  password
SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD = "digitaleq"

