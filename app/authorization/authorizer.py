
def authorized_to_view_message(user, message):
    # check if user is respondent or internal
    # is respondent call party service with user_uuid to get all business associations for that user
    # check response is what is expected     (format of what the party service gives back needs to be agreed)
    # check message ru_id is in the returned data for business associations
    # return true if it is else raise 403 forbidden error
    return True
