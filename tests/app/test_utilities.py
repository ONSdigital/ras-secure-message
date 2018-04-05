from secure_message.common.utilities import MessageArgs


BRES_SURVEY = "33333333-22222-3333-4444-88dc018a1a4c"


def get_args(page=1, limit=100, survey="", cc="", ru="", label="", desc=True, ce=""):
    return MessageArgs(page=page, limit=limit, ru_id=ru, surveys=list(survey), cc=cc, label=label,
                       desc=desc, ce=ce)
