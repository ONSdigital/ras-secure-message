import hashlib
import logging

from flask import g, Response
from flask import request, jsonify
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
from app.common.labels import Labels
from app.repository.saver import Saver
from app.validation.domain import DraftSchema
from app.validation.user import User
from app.repository.modifier import Modifier
from app.repository.retriever import Retriever
from flask import g, Response


logger = logging.getLogger(__name__)


class Drafts(Resource):
    def post(self):
        """Handles saving of new draft"""
        post_data = request.get_json()
        draft = DraftSchema().load(post_data)

        if 'msg_id' in post_data:
            raise (BadRequest(description="Message can not include msg_id"))

        if draft.errors == {}:
            self._save_draft(draft)
            user_urn = g.user_urn
            message_service = Retriever()
            saved_draft = message_service.retrieve_draft(draft.data.msg_id, user_urn)

            hash_object = hashlib.sha1(str(sorted(saved_draft.items())).encode())
            etag = hash_object.hexdigest()
            resp = jsonify({'status': 'OK', 'msg_id': draft.data.msg_id})
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

        if draft.data.urn_to is not None and len(draft.data.urn_to) != 0:
            Drafts._save_draft_status(saver, draft.data.msg_id, draft.data.urn_to, draft.data.survey,
                                      Labels.DRAFT_INBOX.value)

        saver.save_msg_event(draft.data.msg_id, 'Draft_Saved')

        Drafts._save_draft_status(saver, draft.data.msg_id, draft.data.urn_from, draft.data.survey, Labels.DRAFT.value)

    @staticmethod
    def _save_draft_status(saver, msg_id, person, survey, label):
        """Save labels with correct actor for internal and respondent"""

        actor = survey if User(person).is_internal else person
        if person is not None and len(person) != 0:
            saver.save_msg_status(actor, msg_id, label)


class DraftById(Resource):
    """Get and update message by id"""

    @staticmethod
    def get(draft_id):
        """Get message by id"""
        user_urn = g.user_urn
        # check user is authorised to view message
        message_service = Retriever()
        draft_data = message_service.retrieve_draft(draft_id, user_urn)
        etag = DraftById.generate_etag(draft_id, user_urn, draft_data)
        resp = jsonify(draft_data)
        resp.headers['ETag'] = etag

        return resp

    @staticmethod
    def generate_etag(draft_id, user_urn, draft_data):
        hash_object = hashlib.sha1(str(sorted(draft_data.items())).encode())
        etag = hash_object.hexdigest()

        return etag


class DraftModifyById(Resource):
    """Update message status by id"""

    def put(self, draft_id):
        """Handles modifying of drafts"""
        data = request.get_json()
        if 'msg_id' not in data:
            raise (BadRequest(description="Draft put requires msg_id"))
        if data['msg_id'] != draft_id:
            raise (BadRequest(description="Conflicting msg_id's"))
        is_draft = Retriever().check_msg_id_is_a_draft(draft_id, g.user_urn)
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

            user_urn = g.user_urn
            message_service = Retriever()
            modified_draft = message_service.retrieve_draft(draft_id, user_urn)

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
        if headers.get('etag'):
            hash_object = hashlib.sha1(str(sorted(current_draft.items())).encode())
            current_etag = hash_object.hexdigest()
            if current_etag == headers.get('etag'):
                return True
            return False
        else:
            return True
