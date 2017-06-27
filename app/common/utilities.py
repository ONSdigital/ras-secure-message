import logging
from flask import jsonify
from structlog import wrap_logger
from app.common import user_by_uuid, business_by_ru
from app.constants import MESSAGE_BY_ID_ENDPOINT, MESSAGE_LIST_ENDPOINT, MESSAGE_QUERY_LIMIT

logger = wrap_logger(logging.getLogger(__name__))


def get_options(args):
    """extract options"""
    string_query_args = '?'
    page = 1
    limit = MESSAGE_QUERY_LIMIT
    ru_ref = None
    survey = None
    cc = None
    label = None
    desc = True

    if args.get('limit'):
        limit = int(args.get('limit'))

    if args.get('page'):
        page = int(args.get('page'))

    if args.get('ru_ref'):
        string_query_args = add_string_query_args(string_query_args, 'ru_ref', args.get('ru_ref'))
        ru_ref = str(args.get('ru_ref'))
    if args.get('survey'):
        survey = str(args.get('survey'))
        string_query_args = add_string_query_args(string_query_args, 'survey', args.get('survey'))
    if args.get('cc'):
        cc = str(args.get('cc'))
        string_query_args = add_string_query_args(string_query_args, 'cc', args.get('cc'))
    if args.get('label'):
        label = str(args.get('label'))
        string_query_args = add_string_query_args(string_query_args, 'label', args.get('label'))
    if args.get('desc'):
        desc = False if args.get('desc') == 'false' else True
        string_query_args = add_string_query_args(string_query_args, 'desc', args.get('desc'))

    return string_query_args, page, limit, ru_ref, survey, cc, label, desc


def add_string_query_args(string_query_args, arg, val):
    """Create query string for get messages options"""
    if string_query_args == '?':
        return '{0}{1}={2}'.format(string_query_args, arg, val)
    else:
        return '{0}&{1}={2}'.format(string_query_args, arg, val)


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
        msg = message.serialize(user)
        msg['_links'] = {"self": {"href": "{0}{1}/{2}".format(host_url, MESSAGE_BY_ID_ENDPOINT, msg['msg_id'])}}
        messages.append(msg)

    links = {
        'first': {"href": "{0}{1}".format(host_url, endpoint)},
        'self': {"href": "{0}{1}{2}{3}page={4}&limit={5}".format(host_url, endpoint, arg_joiner,
                                                                 string_query_args, page, limit)}
    }

    if paginated_list.has_next:
        links['next'] = {
            "href": "{0}{1}{2}{3}page={4}&limit={5}".format(host_url, endpoint, arg_joiner,
                                                            string_query_args, (page + 1), limit)}

    if paginated_list.has_prev:
        links['prev'] = {
            "href": "{0}{1}{2}{3}page={4}&limit={5}".format(host_url, endpoint, arg_joiner,
                                                            string_query_args, (page - 1), limit)}
    messages = add_to_and_from_details(messages)

    return jsonify({"messages": messages, "_links": links})


def add_to_and_from_details(messages):
    """Adds user details for sender and reciepient"""

    uuid_list = []

    for message in messages:
        if message['msg_to'] not in uuid_list:
            uuid_list.append(message['msg_to'][0])
        if message['msg_from'] not in uuid_list:
            uuid_list.append(message['msg_from'])

    user_details = user_by_uuid.get_details_by_uuids(uuid_list)

    for message in messages:
        message['msg_to'][0] = next((user for user in user_details if user["id"] == message['msg_to'][0]), None)
        message['msg_from'] = next((user for user in user_details if user["id"] == message['msg_from']), None)

    messages = add_business_details(messages)
    return messages


def add_business_details(messages):
    """Adds business details"""

    ru_list = []

    for message in messages:
        if message['ru_ref'] not in ru_list:
            ru_list.append(message['ru_ref'])

    business_details = business_by_ru.get_business_details_by_ru(ru_list)

    for message in messages:
        message['ru_ref'] = next((user for user in business_details if user["ru_ref"] == message['ru_ref']), None)
    return messages