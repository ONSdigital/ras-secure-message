from enum import Enum


class EventsApi(Enum):
    """Includes all event for the api"""

    SENT = "Sent"
    READ = "Read"
    event_list = [SENT, READ]
