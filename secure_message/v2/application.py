import logging

from structlog import wrap_logger

from secure_message.resources.health import Health, DatabaseHealth, HealthDetails
from secure_message.resources.info import Info
from secure_message.resources.labels import Labels
from secure_message.resources.messages import MessageList, MessageById, MessageModifyById, MessageSend
from secure_message.resources.drafts import DraftSave, DraftById, DraftModifyById, DraftList
from secure_message.resources.threads import ThreadById, ThreadList

logger = wrap_logger(logging.getLogger(__name__))


def set_v2_resources(api):
    """v2 endpoints """

    #api.add_resource(MessageByIdV2, '/v2/message/<message_id>')