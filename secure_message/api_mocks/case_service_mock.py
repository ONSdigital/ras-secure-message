class CaseServiceMock:
    @staticmethod
    def store_case_event(case_id, user_uuid):  # NOQA
        return 'OK', 200
