import collections
import logging
import urllib.parse

from structlog import wrap_logger

from secure_message.constants import MESSAGE_BY_ID_ENDPOINT, MESSAGE_LIST_ENDPOINT, MESSAGE_QUERY_LIMIT
from secure_message.services.service_toggles import party, internal_user_service

logger = wrap_logger(logging.getLogger(__name__))
MessageArgs = collections.namedtuple('MessageArgs', 'page limit ru_id surveys cc label desc ce is_closed')


def get_options(args):
    """extract options from request , allow label to be set by caller"""

    fields = {'page': 1, 'limit': MESSAGE_QUERY_LIMIT, 'ru_id': None, 'surveys': None,
              'desc': True, 'cc': None, 'label': None, 'ce': None, 'is_closed': False}

    for field in ['cc', 'ce', 'ru_id', 'label']:
        if args.get(field):
            fields[field] = str(args.get(field))

    fields['surveys'] = args.getlist('survey')

    for field in ['limit', 'page']:
        if args.get(field):
            fields[field] = int(args.get(field))

    if args.get('desc') == 'false':
        fields['desc'] = False

    if args.get('is_closed') == 'true':
        fields['is_closed'] = True

    return MessageArgs(page=fields['page'], limit=fields['limit'], ru_id=fields['ru_id'],
                       surveys=fields['surveys'], cc=fields['cc'], label=fields['label'],
                       desc=fields['desc'], ce=fields['ce'], is_closed=fields['is_closed'])


def generate_string_query_args(args):
    params = {}
    for field in args._fields:
        if field in ['page']:
            continue
        value = getattr(args, field)
        if value:
            params[field] = value
    return urllib.parse.urlencode(params)


def process_paginated_list(paginated_list, host_url, user, message_args, endpoint=MESSAGE_LIST_ENDPOINT, body_summary=True):
    """used to change a pagination object to json format with links"""
    messages = []
    string_query_args = generate_string_query_args(message_args)

    for message in paginated_list.items:
        msg = message.serialize(user, body_summary=body_summary)
        msg['_links'] = {"self": {"href": f"{host_url}{MESSAGE_BY_ID_ENDPOINT}/{msg['msg_id']}"}}
        messages.append(msg)

    links = {'first': {"href": f"{host_url}{endpoint}"},
             'self': {"href": f"{host_url}{endpoint}?{string_query_args}&page={message_args.page}"}}

    if paginated_list.has_next:
        links['next'] = {
            "href": f"{host_url}{endpoint}?{string_query_args}&page={message_args.page + 1}"}

    if paginated_list.has_prev:
        links['prev'] = {
            "href": f"{host_url}{endpoint}?{string_query_args}&page={message_args.page - 1}"}

    return messages, links


def add_to_details(messages):
    """Adds a @msg_to key every message in a list of messages.
    Every msg_to uuid is resolved to include details of the user.

    If the call for the internal user id fails, an exception will be thrown.
    If the external user id cannot be found in the list that we got from the party service.  There
    won't be a @msg_to value returned in the payload.  The API documentation notes that these elements
    aren't guaranteed to be provided so we're not breaking the contract by doing this.
    """
    external_user_details = {}
    for user in party.get_users_details(get_external_user_uuid_list(messages)):
        external_user_details[user['id']] = user

    for message in messages:
        if not message["from_internal"]:
            message.update({"@msg_to": [internal_user_service.get_user_details(message["msg_to"][0])]})
        else:
            if external_user_details.get(message['msg_to'][0]):
                message.update({'@msg_to': [external_user_details.get(message['msg_to'][0])]})

    return messages


def add_from_details(messages):
    """Adds a @msg_from key every message in a list of messages.
    Every msg_to uuid is resolved to include details of the user.

    If the call for the internal user id fails, an exception will be thrown.
    If the external user id cannot be found in the list that we got from the party service.  There
    won't be a @msg_from value returned in the payload.  The API documentation notes that these elements
    aren't guaranteed to be provided so we're not breaking the contract by doing this.
    """
    external_user_details = {}
    for user in party.get_users_details(get_external_user_uuid_list(messages)):
        external_user_details[user['id']] = user
    for message in messages:
        if message["from_internal"]:
            message.update({"@msg_from": internal_user_service.get_user_details(message["msg_from"])})
        else:
            if external_user_details.get(message['msg_from']):
                message.update({'@msg_from': external_user_details.get(message['msg_from'])})
    return messages


def get_external_user_uuid_list(messages):
    """Compiles a list of all unique the external user (respondent) uuids from a list of messages"""
    external_user_uuids = set()

    external_msgs = [message for message in messages if message['from_internal'] is False]
    for message in external_msgs:
        external_user_uuids.add(message["msg_from"])

    internal_messages = [message for message in messages if message['from_internal'] is True]
    for uuid in internal_messages:
        external_user_uuids.add(uuid["msg_to"][0])

    return external_user_uuids


def add_business_details(messages):
    """Adds a @ru_id key every message in a list of messages."""
    ru_ids = set()

    for message in messages:
        ru_ids.add(message['ru_id'])

    business_details = party.get_business_details(ru_ids)

    for message in messages:
        message['@ru_id'] = next((business for business in business_details if business["id"] == message['ru_id']), None)
    return messages


def add_users_and_business_details(messages):
    """Add both user and business details to messages based on data from party service"""
    if not messages:
        return messages

    messages = add_to_details(messages)
    messages = add_from_details(messages)
    logger.info("Successfully added to and from details")
    messages = add_business_details(messages)
    logger.info("Successfully added business details")
    return messages
