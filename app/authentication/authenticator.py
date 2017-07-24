from app.authentication.jwt import decode
from app.authentication.jwe import Decrypter
from flask import Response, g
from jose import JWTError
from app.validation.user import User
from werkzeug.exceptions import BadRequest
from app import settings

import logging

logger = logging.getLogger(__name__)


def authenticate(headers):

    if headers.get('Authorization'):
        jwt_token = headers.get('Authorization')

        res = check_jwt(jwt_token)

        return res

    else:
        res = Response(response="Invalid token to access this Microservice Resource", status=400, mimetype="text/html")
        return res


def check_jwt(token):
    JWT_ENCRYPT = settings.SM_JWT_ENCRYPT
    logger.debug('JWT Encryption (0=disabled, 1=enabled) : %s', JWT_ENCRYPT)
    try:
        if (JWT_ENCRYPT == '1'):
            decrypter = Decrypter()
            decrypted_jwt_token = decrypter.decrypt_token(token)
            logger.debug("Decrypted JWT.")
            decoded_jwt_token = decode(decrypted_jwt_token)
            logger.debug("Decoded JWT. User ID: %s", decoded_jwt_token.get('user_uuid'))
        else:
            decoded_jwt_token = decode(token)
            logger.debug("Decoded JWT. User ID: %s", decoded_jwt_token.get('user_uuid'))

        if not decoded_jwt_token.get('user_uuid'):
            raise BadRequest(description="Missing user_uuid claim,"
                                         "user_uuid is required to access this Microservice Resource")
        if not decoded_jwt_token.get('role'):
            raise BadRequest(description="Missing role claim, role is required to access this Microservice Resource")

        g.user = User(decoded_jwt_token.get('user_uuid'), decoded_jwt_token.get('role'))

        return {'status': "ok"}

    except JWTError:
        res = Response(response="Invalid token to access this Microservice Resource", status=400, mimetype="text/html")
        logger.debug('Failed to decrypt or decoded the JWT. Is the JWT Algorithm and Secret setup correctly?')
        return res
