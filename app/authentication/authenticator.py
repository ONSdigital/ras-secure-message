from app.authentication.jwt import decode
from app.authentication.jwe import Decrypter
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


def check_jwt(token):
    try:
        decrypter = Decrypter()
        decrypted_jwt_token = decrypter.decrypt_token(token)
        decoded_jwt_token = decode(decrypted_jwt_token)

        request_authenticated = False
        if 'RU' in decoded_jwt_token and len(decoded_jwt_token['RU']) == 11:
            if 'survey' in decoded_jwt_token and len(decoded_jwt_token['survey']) > 0:
                if 'CC' in decoded_jwt_token and len(decoded_jwt_token['CC']) > 0:
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
                            RU is: {}, survey is: {}, CC is: {}""".format(decoded_jwt_token,
                                                                          decoded_jwt_token['RU'],
                                                                          decoded_jwt_token['survey'],
                                                                          decoded_jwt_token['CC']))
            return {'status': "ok"}

    except JWTError:
        res = Response(response="Invalid token to access this Microservice Resource", status=400, mimetype="text/html")
        logger.debug(
            'The message does not have a JWT that I can decrypted. Is the JWT Algorithm and Secret setup correctly?')
        return res
