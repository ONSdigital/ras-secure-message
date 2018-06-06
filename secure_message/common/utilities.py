import collections
import logging
import urllib.parse

from structlog import wrap_logger

from secure_message.constants import MESSAGE_BY_ID_ENDPOINT, MESSAGE_LIST_ENDPOINT, MESSAGE_QUERY_LIMIT
from secure_message.services.service_toggles import party, internal_user_service

logger = wrap_logger(logging.getLogger(__name__))
MessageArgs = collections.namedtuple('MessageArgs', 'page limit ru_id surveys cc label desc ce')


def get_options(args):
    """extract options from request , allow label to be set by caller"""

    fields = {'page': 1, 'limit': MESSAGE_QUERY_LIMIT, 'ru_id': None, 'surveys': None,
              'desc': True, 'cc': None, 'label': None, 'ce': None}

    for field in ['cc', 'ce', 'ru_id', 'label']:
        if args.get(field):
            fields[field] = str(args.get(field))

    fields['surveys'] = args.getlist('survey')

    for field in ['limit', 'page']:
        if args.get(field):
            fields[field] = int(args.get(field))

    if args.get('desc') and args.get('desc') == 'false':
        fields['desc'] = False

    return MessageArgs(page=fields['page'], limit=fields['limit'], ru_id=fields['ru_id'],
                       surveys=fields['surveys'], cc=fields['cc'], label=fields['label'],
                       desc=fields['desc'], ce=fields['ce'])


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


def get_from_details(messages):
    """looks up the details for the from users"""
    update_internal_messages_from(messages)
    from_details = party.get_user_details(get_messages_from_external(messages))
    external_messages = [x for x in messages if x['from_internal'] is False]

    for message in messages:
        if message in external_messages:
            message.update({'@msg_from': from_details[0]})

    return messages


def get_messages_from_external(messages):
    external_msgs = []
    uuid_from = []

    len_list = len(messages)

    update_internal_messages_from(messages)

    for i in range(0, len_list):
        if not messages[i]['from_internal']:
            external_msgs.append(messages[i])
    for uuid in external_msgs:
        if uuid["msg_from"] not in uuid_from:
            uuid_from.append(uuid["msg_from"])


def update_internal_messages_from(messages):

    for message in messages:
        if message["from_internal"]:
            message.update({"@msg_from": internal_user_service.get_user_details(message["msg_from"])})


def get_to_details(messages):
    """looks up the details for the to users"""

    update_external_messages_to(messages)

    to_details = party.get_user_details(get_internal_messages_to_uuid(messages))
    internal_messages = [x for x in messages if x['from_internal'] is True]

    for msg in messages:
        if msg in internal_messages:
            msg.update({'@msg_to': to_details})

    return messages


def update_external_messages_to(messages):

    for message in messages:
        if not message["from_internal"]:
            message.update({"@msg_to": internal_user_service.get_user_details(message["msg_to"][0])})


def get_internal_messages_to_uuid(messages):
    msgs = []
    uuid_to = []
    len_list = len(messages)

    for i in range(0, len_list):
        if messages[i]['from_internal']:
            msgs.append(messages[i])

    for uuid in msgs:
        if uuid["msg_to"][0] not in uuid_to:
            uuid_to.append(uuid["msg_to"][0])
    return uuid_to


def add_business_details(messages):
    """Adds business details"""

    ru_list = []

    for message in messages:
        if message['ru_id'] not in ru_list:
            ru_list.append(message['ru_id'])

    business_details = party.get_business_details(ru_list)

    for message in messages:
        message['@ru_id'] = next((business for business in business_details if business["id"] == message['ru_id']), None)
    return messages


def add_users_and_business_details(messages):
    """Add both user and business details to messages based on data from party service"""
    messages = get_to_details(messages)
    messages = get_from_details(messages)
    logger.info("Successfully added to and from details")
    messages = add_business_details(messages)
    logger.info("Successfully added business details")
    return messages
