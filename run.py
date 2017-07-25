#!flask/bin/python
import os
from app.application import app

DEV_PORT = os.getenv('DEV_PORT', 5050)
app.run(debug=True, host='0.0.0.0', port=int(DEV_PORT))
