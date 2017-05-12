#!flask/bin/python
import logging
from app.application import app
app.run(debug=True, host='0.0.0.0', port=8080)

app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.INFO)
