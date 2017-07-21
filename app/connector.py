import os
import json
import logging
from structlog import wrap_logger

conn = None
# uri = 'postgres://postgres:password@host.pcfdev.io:5431/postgres'
uri = None


# Extract the database URI value from VCAP_SERVICES
def getDatabaseUri():

    logger = wrap_logger(logging.getLogger(__name__))
    global uri

    if uri is not None:
        return uri

    if 'VCAP_SERVICES' in os.environ:
        logger.info('VCAP_SERVICES found in environment')
        decoded_config = json.loads(os.environ['VCAP_SERVICES'])
    else:
        logger.info('VCAP_SERVICES NOT found in environment')
        return os.environ.get('SECURE_MESSAGING_DATABASE_URL', 'sqlite:////tmp/messages.db')

    for key, value in decoded_config.items():
        logger.info('Inspecting key: "' + str(key) + '" with value: ' + str(value))
        if decoded_config[key][0]['name'] == 'secure-message-db':
            creds = decoded_config[key][0]['credentials']
            uri = creds['uri']
            logger.info('Postgres DATABASE URI: ' + uri)
            return uri
        else:
            logger.info('VCAP_SERVICES defined but no URI credential found')
            return os.environ.get('SECURE_MESSAGING_DATABASE_URL', 'sqlite:////tmp/messages.db')
