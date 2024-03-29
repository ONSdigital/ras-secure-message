import collections
import logging
import urllib.parse

from structlog import wrap_logger

from secure_message.constants import (
    MESSAGE_BY_ID_ENDPOINT,
    MESSAGE_LIST_ENDPOINT,
    MESSAGE_QUERY_LIMIT,
)
from secure_message.services.service_toggles import internal_user_service, party

logger = wrap_logger(logging.getLogger(__name__))
MessageArgs = collections.namedtuple(
    "MessageArgs",
    "page limit business_id surveys cc label desc ce is_closed my_conversations new_respondent_conversations "
    "all_conversation_types unread_conversations category",
)


def get_options(args) -> MessageArgs:
    """extract options from request , allow label to be set by caller

    :param args: contains search arguments. Not all end points support all args
    :returns: MessageArgs named tuple containing the args for the search

    business_id If set , restricts search to conversations regarding this specific party id
    surveys  If set allows the count to be restricted by a list of survey_ids
    cc  If set , allows the count to be restricted by a particular  case
    ce  If set, alows the count to be restricted by a particular collection exercise
    is_closed If set to 'true' only counts closed conversations, else only open conversations
    my_conversations If set to 'true only counts my conversations.
        I.e conversations where the current user id is the to actor id
    new_respondent_conversations If set to 'true'only counts conversations where the to actor is set to 'GROUP'
    all_conversation_types If set 'true', overrides is_closed, my_conversations and new_respondent_conversations
        and returns 4 counts 1 for each of , open , closed, my_conversations and new_respondent_conversations
    page If set requests the specific page of information to return
    limit If set it sets the maximum number of results to return
    desc If present, requests the information in descending order
    category If set, get threads of a particular category

    """

    fields = {
        "page": 1,
        "limit": MESSAGE_QUERY_LIMIT,
        "business_id": None,
        "surveys": None,
        "desc": True,
        "cc": None,
        "label": None,
        "ce": None,
        "is_closed": False,
        "my_conversations": False,
        "new_respondent_conversations": False,
        "all_conversation_types": False,
        "unread_conversations": False,
        "category": None,
    }

    for field in ["cc", "ce", "business_id", "label", "category"]:
        if args.get(field):
            fields[field] = str(args.get(field))

    fields["surveys"] = args.getlist("survey")

    for field in ["limit", "page"]:
        if args.get(field):
            fields[field] = int(args.get(field))

    if args.get("desc") == "false":
        fields["desc"] = False

    if args.get("is_closed") == "true":
        fields["is_closed"] = True

    if args.get("my_conversations") == "true":
        fields["my_conversations"] = True

    if args.get("new_respondent_conversations") == "true":
        fields["new_respondent_conversations"] = True

    if args.get("all_conversation_types") == "true":
        fields["all_conversation_types"] = True

    if args.get("unread_conversations") == "true":
        fields["unread_conversations"] = True

    return MessageArgs(
        page=fields["page"],
        limit=fields["limit"],
        business_id=fields["business_id"],
        surveys=fields["surveys"],
        cc=fields["cc"],
        label=fields["label"],
        desc=fields["desc"],
        ce=fields["ce"],
        is_closed=fields["is_closed"],
        my_conversations=fields["my_conversations"],
        new_respondent_conversations=fields["new_respondent_conversations"],
        all_conversation_types=fields["all_conversation_types"],
        unread_conversations=fields["unread_conversations"],
        category=fields["category"],
    )


def set_conversation_type_args(
    existing_args,
    is_closed=False,
    my_conversations=False,
    new_conversations=False,
    all_types=False,
    unread_conversations=False,
) -> MessageArgs:
    """Returns a new set of args based on the existing args which are a named tuple,
    but allow the conversation type only to be changed"""

    return MessageArgs(
        page=existing_args.page,
        limit=existing_args.limit,
        business_id=existing_args.business_id,
        surveys=existing_args.surveys,
        cc=existing_args.cc,
        label=existing_args.label,
        desc=existing_args.desc,
        ce=existing_args.ce,
        is_closed=is_closed,
        my_conversations=my_conversations,
        new_respondent_conversations=new_conversations,
        all_conversation_types=all_types,
        unread_conversations=unread_conversations,
        category=existing_args.category,
    )


def generate_string_query_args(args):
    params = {}
    for field in args._fields:
        if field in ["page"]:
            continue
        value = getattr(args, field)
        if value:
            params[field] = value
    return urllib.parse.urlencode(params)


def process_paginated_list(
    paginated_list, host_url: str, user, message_args, endpoint=MESSAGE_LIST_ENDPOINT, body_summary=True
) -> tuple[list, dict]:
    """used to change a pagination object to json format with links"""
    messages = []
    string_query_args = generate_string_query_args(message_args)

    for message in paginated_list.items:
        msg = message.serialize(user, body_summary=body_summary)
        msg["_links"] = {"self": {"href": f"{host_url}{MESSAGE_BY_ID_ENDPOINT}/{msg['msg_id']}"}}
        messages.append(msg)

    links = {
        "first": {"href": f"{host_url}{endpoint}"},
        "self": {"href": f"{host_url}{endpoint}?{string_query_args}&page={message_args.page}"},
    }

    if paginated_list.has_next:
        links["next"] = {"href": f"{host_url}{endpoint}?{string_query_args}&page={message_args.page + 1}"}

    if paginated_list.has_prev:
        links["prev"] = {"href": f"{host_url}{endpoint}?{string_query_args}&page={message_args.page - 1}"}

    return messages, links


def add_to_details(messages):
    """Adds a @msg_to key to every message in a list of messages.
    Every msg_to uuid is resolved to include details of the user.

    If the call for the internal user id fails, an exception will be thrown.
    If the external user id cannot be found in the list that we got from the party service.  There
    won't be a @msg_to value returned in the payload.  The API documentation notes that these elements
    aren't guaranteed to be provided so we're not breaking the contract by doing this.

    Note: Several of these lines of code could be combined into a more succinct view, spreading them out
    is deliberate so that log stack traces are better able to identify the cause of log errors
    """

    external_user_details = {}

    for user in party.get_users_details(get_external_user_uuid_list(messages)):
        external_user_details[user["id"]] = user

    for message in messages:
        try:
            msg_to = message["msg_to"][0]
            from_internal = message["from_internal"]

            if not from_internal:
                msg_to_details = internal_user_service.get_user_details(msg_to)
                message.update({"@msg_to": [msg_to_details]})
            else:
                msg_to_details = external_user_details.get(msg_to)
                if msg_to_details:
                    message.update({"@msg_to": [msg_to_details]})
                else:
                    logger.info("No details found for the message recipient", msg_to=msg_to)

        except IndexError:
            logger.exception("Exception adding to details", msg_to=msg_to, from_internal=from_internal)
            raise

    return messages


def add_from_details(messages: list) -> list:
    """Adds a @msg_from key to every message in a list of messages.
    Every msg_to uuid is resolved to include details of the user.

    If the call for the internal user id fails, an exception will be thrown.
    If the external user id cannot be found in the list that we got from the party service.  There
    won't be a @msg_from value returned in the payload.  The API documentation notes that these elements
    aren't guaranteed to be provided so we're not breaking the contract by doing this.
    """
    external_user_details = {}
    for user in party.get_users_details(get_external_user_uuid_list(messages)):
        external_user_details[user["id"]] = user

    for message in messages:
        try:
            msg_from = message["msg_from"]
            from_internal = message["from_internal"]
            if from_internal:
                message.update({"@msg_from": internal_user_service.get_user_details(msg_from)})
            else:
                if external_user_details.get(message["msg_from"]):
                    message.update({"@msg_from": external_user_details.get(msg_from)})
        except IndexError:
            logger.exception("Exception adding from details message", msg_from=msg_from, from_internal=from_internal)
            raise
    return messages


def get_external_user_uuid_list(messages: list) -> set:
    """Compiles a list of all unique the external user (respondent) uuids from a list of messages"""
    external_user_uuids = set()

    external_msgs = [message for message in messages if message["from_internal"] is False]
    for message in external_msgs:
        external_user_uuids.add(message["msg_from"])

    internal_messages = [message for message in messages if message["from_internal"] is True]
    for uuid in internal_messages:
        external_user_uuids.add(uuid["msg_to"][0])

    return external_user_uuids


def add_business_details(messages):
    """Adds a @business_details key to every message in a list of messages."""
    business_ids = set()

    for message in messages:
        business_ids.add(message["business_id"])

    business_details = party.get_business_details(business_ids)

    for message in messages:
        message["@business_details"] = next(
            (business for business in business_details if business["id"] == message["business_id"]), None
        )
    return messages


def add_users_and_business_details(messages):
    """Add both user and business details to messages based on data from party service"""
    if not messages:
        raise ValueError("messages is a required parameter and must not be empty")
    messages = add_to_details(messages)
    messages = add_from_details(messages)
    logger.info("Successfully added to and from details")
    messages = add_business_details(messages)
    logger.info("Successfully added business details")
    return messages
