import behave
from app.application import app
from flask import json
from datetime import timezone, datetime
from nose.tools import assert_equal


@behave.given('a message is sent without a Thread id')
def step_impl(context):
    url = "http://localhost:5050/message/send"
    headers = {'Content-Type': 'application/json'}
    data = {'msg_to': 'richard',
            'msg_from': 'torrance',
            'subject': 'MyMessage',
            'body': 'hello',
            'thread_id': '',
            'archive_status': False,
            'read_status': False,
            'sent_date': datetime.now(timezone.utc),
            'read_date': datetime.now(timezone.utc)}

    context.response = app.test_client().post(url, data=json.dumps(data), headers=headers)


@behave.then('a 201 status code is the response')
def step_impl(context):
    assert_equal(context.response.status_code, int(201))

if __name__ == '__main__':
    from behave import __main__ as behave_executable
    behave_executable.main(None)
