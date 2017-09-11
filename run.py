#!flask/bin/python
import os

os.environ['JWT_SECRET'] = 'vrwgLNWEffe45thh545yuby'
os.environ['JWT_ALGORITHM'] = 'HS256'
os.environ['SECURITY_USER_NAME'] = 'test_user'
os.environ['SECURITY_USER_PASSWORD'] = 'test_password'
os.environ['NOTIFY_VIA_LOGGING'] = '1'
os.environ['NOTIFICATION_API_KEY'] = 'test_notification_api_key'
os.environ['SERVICE_ID'] = 'test_service_id'
os.environ['NOTIFICATION_TEMPLATE_ID'] = 'test_notification_template_id'
os.environ['RAS_SM_PATH'] = './'

from app.application import app

DEV_PORT = os.getenv('DEV_PORT', 5050)
app.run(debug=True, host='0.0.0.0', port=int(DEV_PORT))