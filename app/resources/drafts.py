import hashlib
import logging

from flask import g, Response
from flask import request, jsonify
from flask_restful import Resource
from structlog import wrap_logger
from werkzeug.exceptions import BadRequest

from app.common import user_by_uuid
from app.common.labels import Labels
from app.common.utilities import get_options, paginated_list_to_json
from app.constants import DRAFT_LIST_ENDPOINT
from app.repository.modifier import Modifier
from app.repository.retriever import Retriever
from app.repository.saver import Saver
from app.validation.domain import DraftSchema

logger = wrap_logger(logging.getLogger(__name__))


class DraftSave(Resource):
    def post(self):
        """Handles saving of new draft"""
        post_data = request.get_json()
        draft = DraftSchema().load(post_data)

        if 'msg_id' in post_data:
            raise (BadRequest(description="Message can not include msg_id"))

        if draft.errors == {}:
            self._save_draft(draft)
            message_service = Retriever()
            saved_draft = message_service.retrieve_draft(draft.data.msg_id, g.user)

            hash_object = hashlib.sha1(str(sorted(saved_draft.items())).encode())
            etag = hash_object.hexdigest()
            resp = jsonify({'status': 'OK', 'msg_id': draft.data.msg_id, 'thread_id': draft.data.thread_id})
            resp.headers['ETag'] = etag
            resp.status_code = 201

            return resp
        else:
            res = jsonify(draft.errors)
            res.status_code = 400
            return res

    @staticmethod
    def _save_draft(draft, saver=Saver()):
        saver.save_message(draft.data)

        if draft.data.msg_to is not None and len(draft.data.msg_to) != 0:
            uuid_to = draft.data.msg_to if g.user.is_internal else draft.data.survey
            saver.save_msg_status(uuid_to, draft.data.msg_id, Labels.DRAFT_INBOX.value)

        uuid_from = draft.data.msg_from if g.user.is_respondent else draft.data.survey
        saver.save_msg_status(uuid_from, draft.data.msg_id, Labels.DRAFT.value)

        saver.save_msg_event(draft.data.msg_id, 'Draft_Saved')


class DraftById(Resource):
    """Return a draft for user"""

    @staticmethod
    def get(draft_id):
        """Get draft by id"""
        # check user is authorised to view message
        message_service = Retriever()
        draft_data = message_service.retrieve_draft(draft_id, g.user)
        etag = DraftById.generate_etag(draft_data)
        draft_data = DraftById.get_to_and_from_details(draft_data)
        resp = jsonify(draft_data)
        resp.headers['ETag'] = etag

        return resp

    @staticmethod
    def generate_etag(draft_data):
        hash_object = hashlib.sha1(str(sorted(draft_data.items())).encode())
        etag = hash_object.hexdigest()

        return etag

    @staticmethod
    def get_to_and_from_details(draft):
        uuids = [draft['msg_from']]
        if draft['msg_to'] is not None:
            uuids.append(draft['msg_to'][0])
        user_details = user_by_uuid.get_details_by_uuids(uuids)
        for user in user_details:
            if draft['msg_from'] == user['id']:
                draft['msg_from'] = user
            if draft['msg_to'][0] == user['id']:
                draft['msg_to'] = [user]
        return draft


class DraftList(Resource):
    """Return a list of drafts for the user"""

    @staticmethod
    def get():
        """Get message list with options"""
        string_query_args, page, limit, ru, survey, cc, label, business, desc = get_options(request.args)

        message_service = Retriever()
        status, result = message_service.retrieve_message_list(page, limit, g.user, label=Labels.DRAFT.value)

        if status:
            resp = paginated_list_to_json(result, page, limit, request.host_url,
                                                       g.user, string_query_args, DRAFT_LIST_ENDPOINT)
            resp.status_code = 200
            return resp


class DraftModifyById(Resource):
    """Update message status by id"""

    def put(self, draft_id):
        """Handles modifying of drafts"""
        data = request.get_json()
        if 'msg_id' not in data:
            raise (BadRequest(description="Draft put requires msg_id"))
        if data['msg_id'] != draft_id:
            raise (BadRequest(description="Conflicting msg_id's"))
        is_draft = Retriever().check_msg_id_is_a_draft(draft_id, g.user)
        if is_draft[0] is False:
            raise (BadRequest(description="Draft put requires valid draft"))

        not_modified = self.etag_check(request.headers, is_draft[1])

        if not_modified is False:
            res = Response(response="Draft has been modified since last check", status=409,
                           mimetype="text/html")
            return res

        draft = DraftSchema().load(data)
        if draft.errors == {}:
            Modifier().replace_current_draft(draft_id, draft.data)

            message_service = Retriever()
            modified_draft = message_service.retrieve_draft(draft_id, g.user)

            hash_object = hashlib.sha1(str(sorted(modified_draft.items())).encode())
            etag = hash_object.hexdigest()
            resp = jsonify({'status': 'OK', 'msg_id': draft_id})
            resp.headers['ETag'] = etag
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(draft.errors)
            resp.status_code = 400
            return resp

    @staticmethod
    def etag_check(headers, current_draft):
        """Check etag to make sure draft has not been modified since get request"""
        if headers.get('ETag'):
            hash_object = hashlib.sha1(str(sorted(current_draft.items())).encode())
            current_etag = hash_object.hexdigest()
            if current_etag == headers.get('ETag'):
                return True
            return False
        else:
            return True
