from flask_restful import Resource
from flask import request, jsonify
from app.repository.saver import Saver
from app.validation.labels import Labels
from app.validation.domain import DraftSchema
from app.validation.user import User
from werkzeug.exceptions import BadRequest
from app.repository.database import Status
from app.repository.modifier import Modifier
from app.repository.retriever import Retriever
from flask import g


class Drafts(Resource):
    """Rest endpoint for draft messages"""

    def post(self):
        """Handles saving of new draft"""
        post_data = request.get_json()
        if 'msg_id' in post_data:
            raise (BadRequest(description="Message can not include msg_id"))
        draft = DraftSchema().load(post_data)

        if draft.errors == {}:
            self.save_draft(draft)
            resp = jsonify({'status': 'OK', 'msg_id': draft.data.msg_id})
            resp.status_code = 201
            return resp
        else:
            res = jsonify(draft.errors)
            res.status_code = 400
            return res

    @staticmethod
    def save_draft(draft, saver=Saver()):
        saver.save_message(draft.data)

        if draft.data.urn_to is not None and len(draft.data.urn_to) != 0:
            Drafts._save_draft_status(saver, draft.data.msg_id, draft.data.urn_to, draft.data.survey,
                                      Labels.DRAFT.value)

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
        resp = message_service.retrieve_draft(draft_id, user_urn)
        return jsonify(resp)


class DraftModifyById(Resource):
    """Update message status by id"""

    def put(self, draft_id):
        """Handles modifying of drafts"""
        data = request.get_json()
        if 'msg_id' not in data:
            raise (BadRequest(description="Draft put requires msg_id"))
        if data['msg_id'] != draft_id:
            raise (BadRequest(description="Conflicting msg_id's"))
        is_draft = self.check_valid_draft(draft_id)
        if is_draft is False:
            raise (BadRequest(description="Draft put requires valid draft"))
        draft = DraftSchema().load(data)
        if draft.errors == {}:
            self.replace_draft(draft_id, draft.data)
            resp = jsonify({'status': 'OK', 'msg_id': draft_id})
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(draft.errors)
            resp.status_code = 400
            return resp

    @staticmethod
    def check_valid_draft(draft_id):
        """Check msg_id is that of a valid draft"""
        db_model = Status()
        result = db_model.query.filter_by(msg_id=draft_id, label=Labels.DRAFT.value).first()
        if result is None:
            return False
        else:
            return True

    @staticmethod
    def replace_draft(draft_id, draft):
        modifier = Modifier()
        modifier.replace_current_draft(draft_id, draft)
