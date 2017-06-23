from app.constants import MESSAGE_BY_ID_ENDPOINT, MESSAGE_LIST_ENDPOINT, MESSAGE_QUERY_LIMIT
from flask import jsonify
from structlog import wrap_logger
import logging
import hashlib

logger = wrap_logger(logging.getLogger(__name__))


def get_options(args):
    """extract options"""
    string_query_args = '?'
    page = 1
    limit = MESSAGE_QUERY_LIMIT
    ru = None
    survey = None
    cc = None
    label = None
    business = None
    desc = True

    if args.get('limit'):
        limit = int(args.get('limit'))

    if args.get('page'):
        page = int(args.get('page'))

    if args.get('ru'):
        string_query_args = add_string_query_args(string_query_args, 'ru', args.get('ru'))
        ru = str(args.get('ru'))
    if args.get('business'):
        string_query_args = add_string_query_args(string_query_args, 'business', args.get('business'))
        business = str(args.get('business'))
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

    return string_query_args, page, limit, ru, survey, cc, label, business, desc


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

    return jsonify({"messages": messages, "_links": links})


def generate_etag(draft_data):
    hash_object = hashlib.sha1(str(sorted(draft_data.items())).encode())
    etag = hash_object.hexdigest()

    return etag
