import logging

from flask import Response, g
from jwt.exceptions import InvalidTokenError
from structlog import wrap_logger
from werkzeug.exceptions import BadRequest

from secure_message import constants
from secure_message.validation.user import User
from secure_message.authentication.jwt import decode

logger = wrap_logger(logging.getLogger(__name__))


def authenticate(headers):

    if headers.get('Authorization'):
        jwt_token = headers.get('Authorization')
        res = check_jwt(jwt_token)
        return res

    res = Response(response="Authorization header required.", status=400, mimetype="text/html")
    logger.error('Authorization header not supplied.')
    return res


def check_jwt(token):
    try:
        decoded_jwt_token = decode(token)
        logger.info("Decoded JWT", user_uuid=decoded_jwt_token.get(constants.USER_IDENTIFIER))

        if not decoded_jwt_token.get(constants.USER_IDENTIFIER):
            raise BadRequest(description="Missing user_uuid claim,"
                                         "user_uuid is required to access this Microservice Resource")
        if not decoded_jwt_token.get('role'):
            raise BadRequest(description="Missing role claim, role is required to access this Microservice Resource")

        g.user = User(decoded_jwt_token.get(constants.USER_IDENTIFIER), decoded_jwt_token.get('role'))

        return {'status': "ok"}

    except InvalidTokenError:
        logger.error('Failed decode the JWT. Is the JWT Algorithm and Secret setup correctly?')
        return Response(response="Invalid token to access this Microservice Resource", status=400, mimetype="text/html")
    except BadRequest as e:
        logger.error(str(e))
        raise
