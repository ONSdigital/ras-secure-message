import unittest
import os
import sys


if __name__ == "__main__":
    os.environ['APP_SETTINGS'] = 'TestConfig'

    from behave import __main__ as behave_executable
    behave_errors = behave_executable.main()
    if behave_errors:
        sys.exit(1)

    test_dirs = os.listdir('./tests')
    suites_list = []
    loader = unittest.TestLoader()
    for directory in test_dirs:
        if directory == "app":
            test_path = f"./tests/{directory}"
            suite = loader.discover(test_path)
            suites_list.append(suite)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            if result.failures or result.errors:
                sys.exit(1)

