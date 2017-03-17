import os

''' This file is the main configuration for the Secure Messaging Service.
    It contains a full default configuration
    All configuration may be overridden by setting the appropriate environment variable name. '''

SECURE_MESSAGING_DATABASE_URL = os.getenv('SECURE_MESSAGING_DATABASE_URL', 'sqlite:////tmp/messages.db')
SMS_LOG_LEVEL = os.getenv('SMS_LOG_LEVEL', 'INFO')
APP_LOG_LEVEL = os.getenv('APP_LOG_LEVEL', 'INFO')
SMS_WERKZEUG_LOG_LEVEL = os.getenv('SMS_WERKZEUG_LOG_LEVEL', 'INFO')