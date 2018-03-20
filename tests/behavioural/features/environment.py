from flask import current_app

from secure_message.application import create_app


def before_scenario(context, scenario):
    if "ignore" in scenario.effective_tags:
        scenario.skip("Not Implemented")
        return


def before_all(context):
    context.app = create_app(config='TestConfig')
    with context.app.app_context():
        context.client = current_app.test_client()
