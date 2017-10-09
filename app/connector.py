import os
import json
import logging

from structlog import wrap_logger

conn = None
uri = os.environ.get('SECURE_MESSAGING_DATABASE_URL', 'postgresql://rhi:password@localhost:5432/sms')


# Extract the database URI value from VCAP_SERVICES
def get_database_uri():

    logger = wrap_logger(logging.getLogger(__name__))
    global uri

    if uri is not None:
        return uri

    if 'VCAP_SERVICES' in os.environ:
        logger.info('VCAP_SERVICES found in environment')
        decoded_config = json.loads(os.environ['VCAP_SERVICES'])
    else:
        logger.info('VCAP_SERVICES NOT found in environment')
        return uri

    for key, value in decoded_config.items():
        logger.info('VCAP SERVICES environment variable', key=key, value=value)
        if decoded_config[key][0]['name'] == 'secure-message-db':
            creds = decoded_config[key][0]['credentials']
            uri = creds['uri']
            return uri
        else:
            logger.info('VCAP_SERVICES defined but no URI credential found')
            return uri
