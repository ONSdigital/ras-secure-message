from flask_restful import Resource
from flask import request, jsonify
from app.repository.saver import Saver
from app.validation.labels import Labels
from app.validation.domain import DraftSchema


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
            saver.save_msg_status(draft.data.urn_to, draft.data.msg_id, Labels.DRAFT_INBOX.value)
        saver.save_msg_status(draft.data.urn_from, draft.data.msg_id, Labels.DRAFT.value)
