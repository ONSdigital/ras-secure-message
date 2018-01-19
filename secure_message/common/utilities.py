import collections
import hashlib
import logging

from flask import jsonify
from structlog import wrap_logger
from secure_message.services.service_toggles import party
from secure_message.constants import MESSAGE_BY_ID_ENDPOINT, MESSAGE_LIST_ENDPOINT, MESSAGE_QUERY_LIMIT

logger = wrap_logger(logging.getLogger(__name__))


MessageArgs = collections.namedtuple('MessageArgs', 'string_query_args page limit ru_id survey cc label desc ce')


def get_options(args):
    """extract options"""

    string_query_args = '?'
    page = 1
    limit = MESSAGE_QUERY_LIMIT
    ru_id = None
    survey = None
    cc = None
    label = None
    desc = True
    ce = None

    if args.get('limit'):
        limit = int(args.get('limit'))

    if args.get('page'):
        page = int(args.get('page'))

    if args.get('ru_id'):
        string_query_args = add_string_query_args(string_query_args, 'ru_id', args.get('ru_id'))
        ru_id = str(args.get('ru_id'))
    if args.get('survey'):
        survey = str(args.get('survey'))
        string_query_args = add_string_query_args(string_query_args, 'survey', args.get('survey'))
    if args.get('cc'):
        cc = str(args.get('cc'))
        string_query_args = add_string_query_args(string_query_args, 'cc', args.get('cc'))
    if args.get('label'):
        label = str(args.get('label'))
        string_query_args = add_string_query_args(string_query_args, 'label', args.get('label'))
    if args.get('ce'):
        ce = str(args.get('ce'))
        string_query_args = add_string_query_args(string_query_args, 'ce', args.get('ce'))
    if args.get('desc'):
        desc = False if args.get('desc') == 'false' else True
        string_query_args = add_string_query_args(string_query_args, 'desc', args.get('desc'))

    return MessageArgs(string_query_args=string_query_args, page=page, limit=limit, ru_id=ru_id, survey=survey,
                       cc=cc, label=label, desc=desc, ce=ce)


def add_string_query_args(string_query_args, arg, val):
    """Create query string for get messages options"""
    if string_query_args == '?':
        return f'{string_query_args}{arg}={val}'
    return f'{string_query_args}&{arg}={val}'


def paginated_list_to_json(paginated_list, page, limit, host_url, user, string_query_args,
                           endpoint=MESSAGE_LIST_ENDPOINT):
    """used to change a pagination object to json format with links"""
    messages = []
    msg_count = 0
    arg_joiner = ''
    if string_query_args != '?':
        arg_joiner = '&'

    for message in paginated_list.items:
        msg_count += 1
        msg = message.serialize(user, body_summary=True)
        msg['_links'] = {"self": {"href": f"{host_url}{MESSAGE_BY_ID_ENDPOINT}/{msg['msg_id']}"}}
        messages.append(msg)

    links = {'first': {"href": f"{host_url}{endpoint}"},
             'self': {"href": f"{host_url}{endpoint}{arg_joiner}{string_query_args}page={page}&limit={limit}"}}

    if paginated_list.has_next:
        links['next'] = {
            "href": f"{host_url}{endpoint}{arg_joiner}{string_query_args}page={page + 1}&limit={limit}"}

    if paginated_list.has_prev:
        links['prev'] = {
            "href": f"{host_url}{endpoint}{arg_joiner}{string_query_args}page={page - 1}&limit={limit}"}
    messages = add_users_and_business_details(messages)
    return jsonify({"messages": messages, "_links": links})


def generate_etag(msg_to, msg_id, subject, body):
    """Function used to create an ETag"""
    if msg_to is None:
        msg_to = []

    msg_to_str = ' '.join(str(uuid) for uuid in msg_to)

    data_to_hash = {'msg_to': msg_to_str,
                    'msg_id': msg_id,
                    'subject': subject,
                    'body': body}

    hash_object = hashlib.sha1(str(sorted(data_to_hash.items())).encode())

    return hash_object.hexdigest()


def get_business_details_by_ru(rus):
    """Function to retrieve business details from ru using the party service"""

    details = []

    for ru in rus:

        detail, status_code = party.get_business_details(ru)

        if status_code == 200:
            details.append(detail)
        else:
            logger.info('No details found for RU ID', ru=ru)

    return details


def get_details_by_uuids(uuids):
    """Function to retrieve user details from uuids using the party service"""

    respondent_details = []
    for uuid in uuids:

        detail, status_code = party.get_user_details(uuid)

        if status_code == 200:
            respondent_details.append(detail)
        else:
            logger.info('No details found for user', uuid=uuid)

    return respondent_details


def add_to_and_from_details(messages):
    """Adds user details for sender and recipient"""

    uuid_list = []

    for message in messages:
        uuid_list.extend([uuid for uuid in message['msg_to'] if uuid not in uuid_list])
        if message['msg_from'] not in uuid_list:
            uuid_list.append(message['msg_from'])

    user_details = get_details_by_uuids(uuid_list)

    for message in messages:

        message['@msg_to'] = [user for user in user_details if user["id"] in message['msg_to']]
        message['@msg_from'] = next((user for user in user_details if user["id"] == message['msg_from']), None)

    return messages


def add_business_details(messages):
    """Adds business details"""

    ru_list = []

    for message in messages:
        if message['ru_id'] not in ru_list:
            ru_list.append(message['ru_id'])

    business_details = get_business_details_by_ru(ru_list)

    for message in messages:
        message['@ru_id'] = next((business for business in business_details if business["id"] == message['ru_id']), None)
    return messages


def add_users_and_business_details(messages):
    """Add both user and business details to messages based on data from party service"""
    messages = add_to_and_from_details(messages)
    messages = add_business_details(messages)
    return messages
