from secure_message.application import create_app

# This is a duplicate of run.py, with minor modifications to support gunicorn execution.

app = create_app()
