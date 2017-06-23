import unittest
from app.resources import user_by_uuid
from werkzeug.exceptions import BadRequest
from app import application
from app.application import app
from sqlalchemy import create_engine
from flask import json


class PartyTestCase(unittest.TestCase):

    def test_get_user_details_by_uuid(self):
        """Test that user details are returned using uuids"""

        list_uuids = ['f62dfda8-73b0-4e0e-97cf-1b06327a6712']

        user_details = user_by_uuid.get_details_by_uuids(list_uuids)

        self.assertEqual(user_details[list_uuids[0]]['firstname'], "Bhavana")
        self.assertEqual(user_details[list_uuids[0]]['surname'], "Lincoln")
        self.assertEqual(user_details[list_uuids[0]]['telephone'], "+443069990888")
        self.assertEqual(user_details[list_uuids[0]]['status'], "ACTIVE")

    def test_get_user_details_by_uuids(self):
        """Test that user details are returned using uuids"""

        list_uuids = ['f62dfda8-73b0-4e0e-97cf-1b06327a6712', '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'dd5a38ff-1ecb-4634-94c8-2358df33e614']

        user_details = user_by_uuid.get_details_by_uuids(list_uuids)

        self.assertEqual(user_details[list_uuids[0]]['firstname'], "Bhavana")
        self.assertEqual(user_details[list_uuids[1]]['firstname'], "Chandana")
        self.assertEqual(user_details[list_uuids[2]]['firstname'], "Ida")

    def test_get_user_details_by_invalid_uuid(self):
        """Test that function returns error when invalid uuid present"""

        list_uuids = ['f62dfda8-73b0-4e0e-97cf-1b06327a6778']

        with self.assertRaises(BadRequest):
            user_by_uuid.get_details_by_uuids(list_uuids)

    def test_message_by_id_replaces_uuids(self):
        data = {'msg_to': 'BRES',
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'survey': "BRES"}

        self.headers = {'Content-Type': 'application/json', 'Authorization': "eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00ifQ.XMrQ2QMNcoWqv6Pm4KGPZRPAHMSNuCRrmdp-glDvf_9gDzYDoXkxbZEBqy6_pdMTIFINUWUABYa7PdLLuJh5uoU9L7lmvJKEYCq0e5rS076KLRc5pFKHJesgJLNijj7scLke3y4INkd0px82SHhnbek0bGLeu3i8FgRt4vD0Eu8TWODM7kEfAT_eRmvPBM1boyOqrpyhYgE9p0_NklwloFXdYZKjTvHxlHtbiuYmvXSTFkbbp_t8T1xZmDrfgS2EDWTFEagzyKBFFAH4Z5QRUUJPiuAxI3lSNS2atFFtDWiZRhuuhRyJzNA4vqTpmFPUE6h_iggkcbiUPofSBx3CUw.QK4lX7z2vN6jryJz.G9C1zoAvWHfAJywiuijq6E78xCMZ5NOAZD1g3e6PTWhveQKNecBJAPgXyRDVgljgIwSq_vBY2AVTIE5xWapwF3oLZyiC0T0H2LrjlpKFUa51-VU_-Yj8u4ax0iLvyWyRRepQneYJ0riF4zbmcGf1vCCEO3WOwcD5wXBFVXVH6wPqExmI2tjWWLdz2F7oK1Wnh1pbQX_EW5rYb2I4mPuc2J6ijXAr73qcJLAzJbjDo1uk.QrPCckVYuNlcWeCwQmws9A"}

        self.app = application.app.test_client()

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        resp = self.app.post("http://localhost:5050/message/send", data=json.dumps(data), headers=self.headers)
        resp_data = json.loads(resp.data)
        msg_id = resp_data['msg_id']

        message_resp = self.app.get("http://localhost:5050/message/{}".format(msg_id), headers=self.headers)
        message = json.loads(message_resp.data)

        self.assertEqual(message['msg_from'], {'telephone': '+443069990289', 'firstname': 'Vana', 'email': 'vana123@aol.com', 'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'status': 'ACTIVE', 'surname': 'Oorschot'})
        self.assertEqual(message['msg_to'], {"id": "", "firstname": "BRES", "surname": "", "email": "", "telephone": "", "status": ""})

    def test_messages_get_replaces_uuids_with_user_details(self):
        data = {'msg_to': 'BRES',
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'survey': "BRES"}

        self.app = application.app.test_client()

        self.headers = {'Content-Type': 'application/json',
                        'Authorization': "eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00ifQ.XMrQ2QMNcoWqv6Pm4KGPZRPAHMSNuCRrmdp-glDvf_9gDzYDoXkxbZEBqy6_pdMTIFINUWUABYa7PdLLuJh5uoU9L7lmvJKEYCq0e5rS076KLRc5pFKHJesgJLNijj7scLke3y4INkd0px82SHhnbek0bGLeu3i8FgRt4vD0Eu8TWODM7kEfAT_eRmvPBM1boyOqrpyhYgE9p0_NklwloFXdYZKjTvHxlHtbiuYmvXSTFkbbp_t8T1xZmDrfgS2EDWTFEagzyKBFFAH4Z5QRUUJPiuAxI3lSNS2atFFtDWiZRhuuhRyJzNA4vqTpmFPUE6h_iggkcbiUPofSBx3CUw.QK4lX7z2vN6jryJz.G9C1zoAvWHfAJywiuijq6E78xCMZ5NOAZD1g3e6PTWhveQKNecBJAPgXyRDVgljgIwSq_vBY2AVTIE5xWapwF3oLZyiC0T0H2LrjlpKFUa51-VU_-Yj8u4ax0iLvyWyRRepQneYJ0riF4zbmcGf1vCCEO3WOwcD5wXBFVXVH6wPqExmI2tjWWLdz2F7oK1Wnh1pbQX_EW5rYb2I4mPuc2J6ijXAr73qcJLAzJbjDo1uk.QrPCckVYuNlcWeCwQmws9A"}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        self.app.post("http://localhost:5050/message/send", data=json.dumps(data), headers=self.headers)
        self.app.post("http://localhost:5050/message/send", data=json.dumps(data), headers=self.headers)

        messages_get = self.app.get("http://localhost:5050/messages", headers=self.headers)
        get_return = json.loads(messages_get.data)
        messages = get_return['messages']

        for message in messages:
            self.assertEqual(message['msg_from'], {'firstname': 'Vana', 'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'status': 'ACTIVE', 'telephone': '+443069990289', 'surname': 'Oorschot', 'email': 'vana123@aol.com'})

    def test_draft_get_return_user_details_for_to_and_from(self):
        data = {'msg_to': 'BRES',
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'survey': "BRES"}

        self.app = application.app.test_client()

        self.headers = {'Content-Type': 'application/json',
                        'Authorization': "eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00ifQ.XMrQ2QMNcoWqv6Pm4KGPZRPAHMSNuCRrmdp-glDvf_9gDzYDoXkxbZEBqy6_pdMTIFINUWUABYa7PdLLuJh5uoU9L7lmvJKEYCq0e5rS076KLRc5pFKHJesgJLNijj7scLke3y4INkd0px82SHhnbek0bGLeu3i8FgRt4vD0Eu8TWODM7kEfAT_eRmvPBM1boyOqrpyhYgE9p0_NklwloFXdYZKjTvHxlHtbiuYmvXSTFkbbp_t8T1xZmDrfgS2EDWTFEagzyKBFFAH4Z5QRUUJPiuAxI3lSNS2atFFtDWiZRhuuhRyJzNA4vqTpmFPUE6h_iggkcbiUPofSBx3CUw.QK4lX7z2vN6jryJz.G9C1zoAvWHfAJywiuijq6E78xCMZ5NOAZD1g3e6PTWhveQKNecBJAPgXyRDVgljgIwSq_vBY2AVTIE5xWapwF3oLZyiC0T0H2LrjlpKFUa51-VU_-Yj8u4ax0iLvyWyRRepQneYJ0riF4zbmcGf1vCCEO3WOwcD5wXBFVXVH6wPqExmI2tjWWLdz2F7oK1Wnh1pbQX_EW5rYb2I4mPuc2J6ijXAr73qcJLAzJbjDo1uk.QrPCckVYuNlcWeCwQmws9A"}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        draft_resp = self.app.post("http://localhost:5050/draft/save", data=json.dumps(data), headers=self.headers)
        draft_details = json.loads(draft_resp.data)
        draft_id = draft_details['msg_id']

        draft_get = self.app.get("http://localhost:5050/draft/{}".format(draft_id), headers=self.headers)
        draft = json.loads(draft_get.data)

        self.assertEqual(draft['msg_from'], {'telephone': '+443069990289', 'firstname': 'Vana', 'email': 'vana123@aol.com', 'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'status': 'ACTIVE', 'surname': 'Oorschot'})

    def test_drafts_get_return_user_details_in_to_and_from(self):
        data = {'msg_to': 'BRES',
                'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'survey': "BRES"}

        self.app = application.app.test_client()

        self.headers = {'Content-Type': 'application/json',
                        'Authorization': "eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00ifQ.XMrQ2QMNcoWqv6Pm4KGPZRPAHMSNuCRrmdp-glDvf_9gDzYDoXkxbZEBqy6_pdMTIFINUWUABYa7PdLLuJh5uoU9L7lmvJKEYCq0e5rS076KLRc5pFKHJesgJLNijj7scLke3y4INkd0px82SHhnbek0bGLeu3i8FgRt4vD0Eu8TWODM7kEfAT_eRmvPBM1boyOqrpyhYgE9p0_NklwloFXdYZKjTvHxlHtbiuYmvXSTFkbbp_t8T1xZmDrfgS2EDWTFEagzyKBFFAH4Z5QRUUJPiuAxI3lSNS2atFFtDWiZRhuuhRyJzNA4vqTpmFPUE6h_iggkcbiUPofSBx3CUw.QK4lX7z2vN6jryJz.G9C1zoAvWHfAJywiuijq6E78xCMZ5NOAZD1g3e6PTWhveQKNecBJAPgXyRDVgljgIwSq_vBY2AVTIE5xWapwF3oLZyiC0T0H2LrjlpKFUa51-VU_-Yj8u4ax0iLvyWyRRepQneYJ0riF4zbmcGf1vCCEO3WOwcD5wXBFVXVH6wPqExmI2tjWWLdz2F7oK1Wnh1pbQX_EW5rYb2I4mPuc2J6ijXAr73qcJLAzJbjDo1uk.QrPCckVYuNlcWeCwQmws9A"}

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')

        self.app.post("http://localhost:5050/draft/save", data=json.dumps(data), headers=self.headers)
        self.app.post("http://localhost:5050/draft/save", data=json.dumps(data), headers=self.headers)

        drafts_get = self.app.get("http://localhost:5050/drafts", headers=self.headers)
        drafts_data = json.loads(drafts_get.data)
        drafts = drafts_data['messages']

        for draft in drafts:
            self.assertEqual(draft['msg_from'], {'telephone': '+443069990289', 'firstname': 'Vana', 'email': 'vana123@aol.com', 'id': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'status': 'ACTIVE', 'surname': 'Oorschot'})
            self.assertEqual(draft['msg_to'][0], {"id": "", "firstname": "BRES", "surname": "", "email": "", "telephone": "", "status": ""})


if __name__ == '__main__':
    unittest.main()
