
class User:

    user_urn = None

    def __init__(self, user_urn):
        self.user_urn = user_urn

    @property
    def is_internal(self):
        if 'internal' in self.user_urn:
            return True
        else:
            return False

    @property
    def is_respondent(self):
        if 'respondent' in self.user_urn:
            return True
        else:
            return False
