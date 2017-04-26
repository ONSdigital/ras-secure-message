from enum import Enum


class Labels(Enum):
    """Includes all labels for the api"""

    INBOX = "INBOX"
    UNREAD = "UNREAD"
    SENT = "SENT"
    ARCHIVE = "ARCHIVE"
    DRAFT = "DRAFT"
    DRAFT_INBOX = "DRAFT_INBOX"

    label_list = [INBOX, UNREAD, SENT, ARCHIVE, DRAFT, DRAFT_INBOX]
