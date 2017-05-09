from app.authentication.jwt import decode
from app.authentication.jwe import Decrypter
from flask import Response, g
from jose import JWTError

import logging

logger = logging.getLogger(__name__)


def authenticate(request):

    if request.headers.get('authentication'):
        jwt_token = request.headers.get('authentication')

        res = check_jwt(jwt_token)

        return res

    else:
        res = Response(response="Invalid token to access this Microservice Resource", status=400, mimetype="text/html")
        logger.debug("""The message does not have any JWT needed for authentication.""")
        return res


def check_jwt(token):
    try:
        decrypter = Decrypter()
        decrypted_jwt_token = decrypter.decrypt_token(token)
        decoded_jwt_token = decode(decrypted_jwt_token)

        if 'user_urn' in decoded_jwt_token:
            g.user_urn = decoded_jwt_token['user_urn']
            return {'status': "ok"}
        else:
            res = Response(response="Missing user_urn or invalid user_urn supplied to access this Microservice Resource"
                           , status=400, mimetype="text/html")
            return res

    except JWTError:
        res = Response(response="Invalid token to access this Microservice Resource", status=400, mimetype="text/html")
        logger.debug(
            'The message does not have a JWT that I can decrypted. Is the JWT Algorithm and Secret setup correctly?')
        return res
