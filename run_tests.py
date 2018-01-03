import unittest
import os
import sys


if __name__ == "__main__":
    os.environ['JWT_SECRET'] = 'testsecret'
    os.environ['JWT_ALGORITHM'] = 'HS256'
    os.environ['SECURITY_USER_NAME'] = 'admin'
    os.environ['SECURITY_USER_PASSWORD'] = 'secret'
    os.environ['NOTIFY_VIA_GOV_NOTIFY'] = '0'
    os.environ['NOTIFICATION_API_KEY'] = 'test_notification_api_key'
    os.environ['SERVICE_ID'] = 'test_service_id'
    os.environ['NOTIFICATION_TEMPLATE_ID'] = 'test_notification_template_id'
    os.environ['RAS_SM_PATH'] = './'
    from behave import __main__ as behave_executable
    behave = behave_executable.main()

    test_dirs = os.listdir('./tests')
    suites_list = []
    loader = unittest.TestLoader()
    for directory in test_dirs:
        if directory == "app":
            test_path = f"./tests/{directory}"
            suite = loader.discover(test_path)
            suites_list.append(suite)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            i = len(result.failures) + len(result.errors)
            if i != 0 or behave == 1:
                sys.exit(1)
