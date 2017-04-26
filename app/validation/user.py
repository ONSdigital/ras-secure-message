
class User:
    """Determines whether the user is internal or external"""

    user_urn = None

    def __init__(self, user_urn):
        self.user_urn = user_urn

    @property
    def is_internal(self):
        return bool('internal' in self.user_urn)

    @property
    def is_respondent(self):
        return bool('respondent' in self.user_urn)
