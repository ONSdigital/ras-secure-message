import unittest
import os
import sys

if __name__ == "__main__":
    os.environ['JWT_SECRET'] = 'testsecret'
    os.environ['SECURITY_USER_NAME'] = 'test_user'
    os.environ['SECURITY_USER_PASSWORD'] = 'test_password'
    os.environ['NOTIFY_VIA_LOGGING'] = '1'

    from behave import __main__ as behave_executable
    behave = behave_executable.main()

    test_dirs = os.listdir('./tests')
    suites_list = []
    loader = unittest.TestLoader()
    for directory in test_dirs:
        if directory == "app":
            test_path = "./tests/{}".format(directory)
            suite = loader.discover(test_path)
            suites_list.append(suite)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            i = len(result.failures) + len(result.errors)
            if i != 0 or behave == 1:
                sys.exit(1)
