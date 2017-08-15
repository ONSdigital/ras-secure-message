#!flask/bin/python
import os
import logging
from app.application import app
from app.cloud.cloud_foundry import ONSCloudFoundry
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))

if __name__ == '__main__':
    cf = ONSCloudFoundry()
    # First check if secure messaging is deployed in a Cloud Foundry environment
    if cf.detected:
        port = cf.port
        logger.info('* Cloud Foundry environment detected.')
        logger.info('* Cloud Foundry port "{}"'.format(port))

    else:
        port = os.getenv('SMS_DEV_PORT', 5050)
    logger.info('* starting listening port "{}"'.format(port))
    app.run(debug=True, host='0.0.0.0', port=int(port))
