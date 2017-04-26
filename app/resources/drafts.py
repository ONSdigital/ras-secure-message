from flask_restful import Resource
from flask import request, jsonify
from app.repository.saver import Saver
from app.validation.labels import Labels
from app.validation.domain import DraftSchema
from app.validation.user import User


class Drafts(Resource):
    """Rest endpoint for draft messages"""
    def get(self):
        pass

    def post(self):
        draft = DraftSchema().load(request.get_json())

        if draft.errors == {}:
            self.save_draft(draft)
            resp = jsonify({'status': 'OK'})
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

        Drafts._save_draft_status(saver, draft.data.msg_id, draft.data.urn_from, draft.data.survey, Labels.DRAFT.value)

    @staticmethod
    def _save_draft_status(saver, msg_id, person, survey, label):
        """Save labels with correct actor for internal and respondent"""

        actor = survey if User(person).is_internal else person
        if person is not None and len(person) != 0:
            saver.save_msg_status(actor, msg_id, label)
