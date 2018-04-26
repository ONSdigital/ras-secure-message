from enum import Enum


class Labels(Enum):
    """Includes all labels for the api"""

    INBOX = "INBOX"
    UNREAD = "UNREAD"
    SENT = "SENT"
    ARCHIVE = "ARCHIVE"

    label_list = [INBOX, UNREAD, SENT, ARCHIVE]
