from secure_message.common.utilities import MessageArgs


BRES_SURVEY = "33333333-22222-3333-4444-88dc018a1a4c"


def get_args(page=1, limit=100, surveys=None, cc="", ru="", label="", desc=True, ce="", is_closed=False):
    return MessageArgs(page=page,
                       limit=limit,
                       surveys=surveys,
                       cc=cc,
                       ru_id=ru,
                       label=label,
                       desc=desc,
                       ce=ce,
                       is_closed=is_closed)
