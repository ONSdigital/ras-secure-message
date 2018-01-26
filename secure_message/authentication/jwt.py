"""
Module to generate jwt token
"""

from flask import current_app
from jose import jwt


def encode(data):
    """
    Function to encode python dict data
    """
    jwt_algorithm = current_app.config['SM_JWT_ALGORITHM']
    jwt_secret = current_app.config['JWT_SECRET']
    return jwt.encode(data, jwt_secret, algorithm=jwt_algorithm, headers={"alg": jwt_algorithm, 'typ': 'jwt'})


def decode(token):
    """
    Function to decode python dict data
    """
    jwt_algorithm = current_app.config['SM_JWT_ALGORITHM']
    jwt_secret = current_app.config['JWT_SECRET']

    return jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
