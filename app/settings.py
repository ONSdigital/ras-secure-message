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

NOTIFICATION_SERVICE_ID = os.getenv('SERVICE_ID', 'ce3674b1-7b08-4377-a6a7-05b5722d4ea5')
NOTIFICATION_API_KEY = os.getenv('NOTIFICATION_API_KEY', 'c711009f-17d8-44a9-a2be-2cc8c23cdfd4')
NOTIFICATION_COMBINED_KEY = 'key-name-{}-{}'.format(NOTIFICATION_SERVICE_ID, NOTIFICATION_API_KEY)
NOTIFICATION_TEMPLATE_ID = 'f6404844-a994-428c-a5d7-45a4e1cfff4b'
NOTIFICATION_DEV_EMAIL = os.getenv('NOTIFICATION_DEV_EMAIL', 'emilio.ward@ons.gov.uk')


# SQLAlchemy configuration

SQLALCHEMY_POOL_SIZE = os.getenv('SQLALCHEMY_POOL_SIZE', None)


SM_JWT_SECRET = os.getenv('SM_JWT_SECRET', 'vrwgLNWEffe45thh545yuby')
SM_JWT_ENCRYPT = os.getenv('SM_JWT_ENCRYPT', '1')

#  Keys
SM_USER_AUTHENTICATION_PRIVATE_KEY = open("{0}/jwt-test-keys/sm-user-authentication-encryption-private-key.pem".format(os.getenv('RAS_SM_PATH')))\
    .read()
SM_USER_AUTHENTICATION_PUBLIC_KEY = open("{0}/jwt-test-keys/sm-user-authentication-encryption-public-key.pem".format(os.getenv('RAS_SM_PATH'))).read()

#  password
SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD = "digitaleq"
