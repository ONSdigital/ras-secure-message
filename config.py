import logging
import os

from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class Config:
    """
    This object is the main configuration for the Secure Messaging Service.
    It contains a full default configuration
    All configuration may be overridden by setting the appropriate environment variable name.
    """

    VERSION = "1.3.0"
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432")
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")

    # EMAIL NOTIFICATION SETTINGS
    NOTIFY_VIA_GOV_NOTIFY = os.getenv("NOTIFY_VIA_GOV_NOTIFY")
    NOTIFICATION_TEMPLATE_ID = os.getenv("NOTIFICATION_TEMPLATE_ID")
    REQUESTS_POST_TIMEOUT = os.getenv("REQUESTS_POST_TIMEOUT", 20)

    # JWT authentication config
    JWT_SECRET = os.getenv("JWT_SECRET")

    # Services
    PARTY_URL = os.getenv("PARTY_URL")
    FRONTSTAGE_URL = os.getenv("FRONTSTAGE_URL")

    # UAA
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    UAA_URL = os.getenv("UAA_URL")
    USE_UAA = 1

    NON_DEFAULT_VARIABLES = [
        "JWT_SECRET",
        "SECURITY_USER_NAME",
        "SECURITY_USER_PASSWORD",
        "NOTIFICATION_TEMPLATE_ID",
        "CLIENT_ID",
        "CLIENT_SECRET",
    ]

    # Basic auth parameters
    SECURITY_USER_NAME = os.getenv("SECURITY_USER_NAME")
    SECURITY_USER_PASSWORD = os.getenv("SECURITY_USER_PASSWORD")
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_ECHO = True

    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "ras-rm-sandbox")
    PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "ras-rm-notify-test")


class DevConfig(Config):

    JWT_SECRET = os.getenv("JWT_SECRET", "testsecret")
    NOTIFY_VIA_GOV_NOTIFY = os.getenv("NOTIFY_VIA_GOV_NOTIFY", "0")
    NOTIFICATION_TEMPLATE_ID = os.getenv("NOTIFICATION_TEMPLATE_ID", "test_notification_template_id")
    FRONTSTAGE_URL = os.getenv("PARTY_URL", "http://localhost:8082")
    PARTY_URL = os.getenv("PARTY_URL", "http://localhost:8081")
    SECURITY_USER_NAME = os.getenv("SECURITY_USER_NAME", "admin")
    SECURITY_USER_PASSWORD = os.getenv("SECURITY_USER_PASSWORD", "secret")
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)
    SQLALCHEMY_ECHO = True

    # UAA
    CLIENT_ID = os.getenv("CLIENT_ID", "secure_message")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "password")
    UAA_URL = os.getenv("UAA_URL", "http://localhost:9080")
    USE_UAA = int(os.getenv("USE_UAA", 1))


class TestConfig(DevConfig):
    TESTING = True
    USE_UAA = 0
    SQLALCHEMY_ECHO = True

    # LOGGING SETTINGS
    LOGGING_LEVEL = "ERROR"
    GOOGLE_CLOUD_PROJECT = "test-project-id"
    PUBSUB_TOPIC = "ras-rm-notify-test"
