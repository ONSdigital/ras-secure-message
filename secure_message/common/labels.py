from enum import Enum


class Labels(Enum):
    """Includes all labels for the api"""

    INBOX = "INBOX"
    UNREAD = "UNREAD"
    SENT = "SENT"
    DRAFT = "DRAFT"
    DRAFT_INBOX = "DRAFT_INBOX"

    label_list = [INBOX, UNREAD, SENT, DRAFT, DRAFT_INBOX]
