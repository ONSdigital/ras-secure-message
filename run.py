#!flask/bin/python
import os

os.environ['JWT_SECRET'] = os.getenv('JWT_SECRET', 'vrwgLNWEffe45thh545yuby')
os.environ['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
os.environ['SECURITY_USER_NAME'] = os.getenv('SECURITY_USER_NAME', 'test_user')
os.environ['SECURITY_USER_PASSWORD'] = os.getenv('SECURITY_USER_PASSWORD', 'test_password')
os.environ['NOTIFY_VIA_GOV_NOTIFY'] = os.getenv('NOTIFY_VIA_GOV_NOTIFY', '0')
os.environ['NOTIFICATION_API_KEY'] = os.getenv('NOTIFICATION_API_KEY', 'test_notification_api_key')
os.environ['SERVICE_ID'] = os.getenv('SERVICE_ID', 'test_service_id')
os.environ['NOTIFICATION_TEMPLATE_ID'] = os.getenv('NOTIFICATION_TEMPLATE_ID', 'test_notification_template_id')
os.environ['RAS_SM_PATH'] = os.getenv('RAS_SM_PATH', './')

from secure_message.application import app

DEV_PORT = os.getenv('DEV_PORT', 5050)
app.run(debug=True, host='0.0.0.0', port=int(DEV_PORT))
