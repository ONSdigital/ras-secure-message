import logging

logger = logging.getLogger(__name__)


class CaseServiceMock:
    @staticmethod
    def store_case_event(case_id, user_uuid):
        return 'OK', 200
