"""
Module to generate jwt token
"""

from flask import current_app
from jose import jwt


def encode(data):
    """
    Function to encode python dict data
    """
    JWT_ALGORITHM = current_app.config['SM_JWT_ALGORITHM']
    JWT_SECRET = current_app.config['SM_JWT_SECRET']

    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM, headers={"alg": JWT_ALGORITHM, 'typ': 'jwt'})


def decode(token):
    """
    Function to decode python dict data
    """
    JWT_ALGORITHM = current_app.config['SM_JWT_ALGORITHM']
    JWT_SECRET = current_app.config['SM_JWT_SECRET']

    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
