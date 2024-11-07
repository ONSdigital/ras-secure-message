#!flask/bin/python
import os

from secure_message.application import create_app

DEV_PORT = os.getenv("DEV_PORT", 5050)
app = create_app("DevConfig")
app.run(debug=False, host="0.0.0.0", port=int(DEV_PORT))
