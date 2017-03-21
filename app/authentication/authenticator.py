from app.authentication.jwt import decode
from flask import Response
from jose import JWTError
import logging

logger = logging.getLogger(__name__)


def authenticate(request):

    if request.headers.get('authorization'):
        jwt_token = request.headers.get('authorization')

        res = check_jwt(jwt_token)

        return res

    else:
        res = Response(response="Invalid token to access this Microservice Resource", status=400, mimetype="text/html")
        logger.debug("""The message does not have any JWT needed for Authorisation.
                    The only headers I have are: {}""").format(request.headers)
        return res


def check_jwt(jwt_token):
    try:
        decrypted_jwt_token = decode(jwt_token)

        request_authenticated = False
        if 'RU' in decrypted_jwt_token and len(decrypted_jwt_token['RU']) == 11:
            if 'survey' in decrypted_jwt_token and len(decrypted_jwt_token['survey']) > 0:
                if 'CC' in decrypted_jwt_token and len(decrypted_jwt_token['CC']) > 0:
                    request_authenticated = True
                else:
                    res = Response(response="Collection Case required to access this Microservice Resource",
                                   status=400, mimetype="text/html")
                    return res
            else:
                res = Response(response="Survey required to access this Microservice Resource",
                               status=400, mimetype="text/html")
                return res
        else:
            res = Response(response="Missing RU or invalid RU supplied to access this Microservice Resource",
                           status=400, mimetype="text/html")
            return res

        if request_authenticated:
            # create user model
            logger.debug("""The message has the correct claims and it can be decrypted properly. JWT value is: {},
                            RU is: {}, survey is: {}, CC is: {}""".format(decrypted_jwt_token,
                                                                          decrypted_jwt_token['RU'],
                                                                          decrypted_jwt_token['survey'],
                                                                          decrypted_jwt_token['CC']))
            return {'status': "ok"}

    except JWTError:
        res = Response(response="Invalid token to access this Microservice Resource", status=400, mimetype="text/html")
        logger.debug(
            'The message does not have a JWT that I can decrypted. Is the JWT Algorithm and Secret setup correctly?')
        return res
