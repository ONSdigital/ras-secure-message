from secure_message.services.service_toggles import party


class User:
    """Determines whether the user is internal or external"""

    def __init__(self, user_uuid, role):
        self.user_uuid = user_uuid
        self.role = role

    @property
    def is_internal(self):
        return bool(self.role == 'internal')

    @property
    def is_respondent(self):
        return bool(self.role == 'respondent')

    @staticmethod
    def is_valid_internal_user(uuid):
        return 200       # Todo add internal userlookup

    @staticmethod
    def is_valid_respondent(uuid):
        _, status_code = party.get_user_details(uuid)
        return status_code == 200
