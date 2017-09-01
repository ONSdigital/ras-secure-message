# Message Definition Constants

MAX_TO_LEN = 100                  # Maximum size of a message TO field
MAX_FROM_LEN = 100                # Maximum size of a From Field in a message
MAX_BODY_LEN = 10000              # Maximum size if the Body field in a message
MAX_SUBJECT_LEN = 100             # Maximum length of the subject field in a message
MAX_THREAD_LEN = 60               # Maximum size of a thread_id UUID in a message
MAX_MSG_ID_LEN = 60               # Maximum size of a message UUID in a message
MAX_COLLECTION_CASE_LEN = 60      # Maximum size of the message collection case identifier
MAX_RU_ID_LEN = 60                # Maximum size of the message ru_id identifier
MAX_BUSINESS_NAME_LEN = 60        # Maximum size of the message business name identifier
MAX_SURVEY_LEN = 60      # Maximum size of the message collection instrument identifier
MAX_COLLECTION_EXERCISE_LEN = 60  # Maximum size of the message collection exercise identifier

# Status Table Column Size Definitions

MAX_STATUS_LABEL_LEN = 50          # Maximum length of a label column
MAX_STATUS_ACTOR_LEN = 100         # Maximum length of the actor column

# Events Table Column Size Definitions

MAX_EVENT_LEN = 20          # Maximum length of a event column

# Endpoint names

MESSAGE_BY_ID_ENDPOINT = "message"
MESSAGE_LIST_ENDPOINT = "messages"
THREAD_BY_ID_ENDPOINT = "thread"
THREAD_LIST_ENDPOINT = "threads"
DRAFT_LIST_ENDPOINT = "drafts"

MESSAGE_QUERY_LIMIT = 20

USER_IDENTIFIER = 'party_id'

BRES_USER = "BRES"
BRES_SURVEY = "BRES"
