#!flask/bin/python
import os

from secure_message.application import create_app

DEV_PORT = os.getenv("DEV_PORT", 5050)
app = create_app("DevConfig")
app.run(debug=True, host="", port=int(DEV_PORT))
