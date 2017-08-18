import cfenv
import re

RegexType = type(re.compile(''))


class ONSCloudFoundry(object):

    def __init__(self):
        #   Monkey patch cfenv so it can handle a list match
        cfenv.match = my_match
        self._cf_env = cfenv.AppEnv()
        self._host = self._cf_env.uris[0].split(':') if self.detected else 'localhost'
        self._protocol = 'https' if self.detected else 'http'

    @property
    def detected(self):
        return self._cf_env.app

    @property
    def port(self):
        return self._cf_env.port

    @property
    def host(self):
        return self._host

    @property
    def protocol(self):
        return self._protocol

    def database(self):
        return self._cf_env.get_service(tags='database')

    def credentials(self):
        return self._cf_env.get_credential('uri')

def my_match(target, pattern):
        """
        This is a customised version of "match" that also handles matching based
        on 'target' possibly being a list.
        """

        if target is None:
            return False
        if isinstance(pattern, RegexType):
            return pattern.search(target)
        if isinstance(target, list):
            return pattern in target
        return pattern == target