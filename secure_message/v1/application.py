import logging

from structlog import wrap_logger

from secure_message.resources.health import Health, DatabaseHealth, HealthDetails
from secure_message.resources.info import Info
from secure_message.resources.labels import Labels
from secure_message.resources.messages import MessageList, MessageSend, MessageById, MessageModifyById
from secure_message.resources.drafts import DraftSave, DraftById, DraftModifyById, DraftList
from secure_message.resources.threads import ThreadById, ThreadList

logger = wrap_logger(logging.getLogger(__name__))


def set_v1_resources(api):
    api.add_resource(Health, '/health')
    api.add_resource(DatabaseHealth, '/health/db')
    api.add_resource(HealthDetails, '/health/details')
    api.add_resource(Info, '/info')
    api.add_resource(MessageList, '/messages')
    api.add_resource(MessageSend, '/message/send')
    api.add_resource(MessageById, '/message/<message_id>')
    api.add_resource(MessageModifyById, '/message/<message_id>/modify')
    api.add_resource(DraftSave, '/draft/save')
    api.add_resource(DraftModifyById, '/draft/<draft_id>/modify')
    api.add_resource(DraftById, '/draft/<draft_id>')
    api.add_resource(ThreadById, '/thread/<thread_id>')
    api.add_resource(DraftList, '/drafts')
    api.add_resource(ThreadList, '/threads')
    api.add_resource(Labels, '/labels')