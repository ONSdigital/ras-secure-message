#!flask/bin/python
from app.application import app
app.run(debug=True, host='0.0.0.0', port=5050)
