from enum import Enum


class Labels(Enum):
    """Includes all labels for the api"""

    INBOX = "INBOX"
    UNREAD = "UNREAD"
    SENT = "SENT"

    label_list = [INBOX, UNREAD, SENT]
