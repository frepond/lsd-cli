import time

import requests

import json

cli_time = 0.0
lsd_time = 0.0
tuples = 0


def timing(f):
    def func_wrapper(*args, **kwargs):
        global cli_time
        global lsd_time
        global tuples
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        cli_time = ((time2 - time1) * 1000.0)
        try:
            lsd_time = ret['elapsed_time'] / 1000.0
            tuples = ret['size']
        except:
            lsd_time = 0.0
            if ret:
                tuples = len(ret)
            else:
                tuples = 0

        return ret

    return func_wrapper


class Lsd:

    def __init__(self, tenant, host, port, content='application/leaplog-results+json'):
        self.__tenant = tenant
        self.__host = host
        self.__port = port
        self.__content = content
        self.__session = requests.Session()
        self.__session.trust_env = False

        # test lsd connection
        self.leaplog(
            '?(<invalid:uri>, <invalid:uri>, <invalid:uri>, <lsd:demo:graph>).')

    @timing
    def leaplog(self, query, basic_quorum='true', sloppy_quorum='true',
                r='quorum', pr='3', limit='infinity'):
        url = 'http://{0}:{1}/leaplog'.format(self.__host, self.__port)
        payload = {
            'query': query,
            'basic_quorum': basic_quorum,
            'sloppy_quorum': sloppy_quorum,
            'r': r,
            'pr': pr,
            'limit': limit
        }
        headers = self.__headers()

        r = self.__session.get(url, params=payload, headers=headers)
        r.raise_for_status()

        if r.status_code == 204:
            result = None
        else:
            r.encoding = 'UTF-8'
            result = json.loads(r.text)

        return result

    @timing
    def rulesets(self):
        url = 'http://{0}:{1}/rulesets'.format(self.__host, self.__port)
        headers = {
            'Authorization': self.__tenant,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }

        r = self.__session.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = 'UTF-8'
        result = json.loads(r.text)

        return result

    @timing
    def create_ruleset(self, uri, source):
        url = 'http://{0}:{1}/rulesets'.format(self.__host, self.__port)
        headers = {
            'Authorization': self.__tenant,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }

        ruleset = {
            'uri': uri,
            'source': source
        }

        r = self.__session.post(url, json=ruleset, headers=headers)
        r.raise_for_status()
        r.encoding = 'UTF-8'
        result = json.loads(r.text)

        return result

    def __headers(self):
        return {
            'Authorization': self.__tenant,
            'Accept': self.__content,
            'Accept-Encoding': 'gzip'
        }
