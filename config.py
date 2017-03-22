import os
from app import settings

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Configuration set up"""
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = settings.JWT_SECRET
    DATABASE_URI = settings.SECURE_MESSAGING_DATABASE_URL
