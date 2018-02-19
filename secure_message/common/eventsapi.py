from enum import Enum


class EventsApi(Enum):
    """Includes all event for the api"""

    SENT = "Sent"
    READ = "Read"
    DRAFT_SAVED = "Draft_Saved"
    event_list = [SENT, READ, DRAFT_SAVED]