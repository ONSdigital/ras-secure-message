
class User:
    """Determines whether the user is internal or external"""

    user_uuid = None
    role = None

    def __init__(self, user_uuid, role):
        self.user_uuid = user_uuid
        self.role = role

    @property
    def is_internal(self):
        return bool(self.role == 'internal')

    @property
    def is_respondent(self):
        return bool(self.role == 'respondent')
