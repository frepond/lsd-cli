import ujson as json
import logging
import time

import requests

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
        self.__test_connection()

    @timing
    def leaplog(self, query, program=None, ruleset=None, prefix_mapping=None, r=None, pr=None,
                w=None, cw=None, pw=None, basic_quorum=None, ts=None, timeout=None, limit=1000):
        url = 'http://{0}:{1}/leaplog'.format(self.__host, self.__port)
        payload = {
            'query': query,
            'program': program,
            'ruleset': ruleset,
            'prefix_mapping': prefix_mapping,
            'consistency_options': {
                'r': r,
                'pr': pr,
                'basic_quorum': basic_quorum
            },
            'timeout': timeout,
            'limit': limit,
            'ts': ts
        }
        payload = {k: v for k, v in payload.items() if v}
        payload['consistency_options'] = {
            k: v for k, v in payload['consistency_options'].items() if v}
        headers = self.__headers()

        logging.debug('leaplog payload: %s', payload)

        r = self.__session.post(url, json=payload, headers=headers)
        self.__check_error(r)

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

        self.__check_error(r)

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
        self.__check_error(r)

        r.encoding = 'UTF-8'
        result = json.loads(r.text)

        return result

    @timing
    def create_graph(self, uri, description, type=None, is_active=None, is_mutable=None,
                     basic_quorum=None, cw=None, n=None, pr=None, pw=None, r=None, w=None):
        url = 'http://{0}:{1}/graphs'.format(self.__host, self.__port)
        payload = {
            'uri': uri,
            'description': description,
            'type': type,
            'is_active': is_active,
            'is_mutable': is_mutable,
            'consistency_options': {
                'basic_quorum': basic_quorum,
                'cw': cw,
                'n': n,
                'pr': pr,
                'pw': pw,
                'r': r,
                'w': w
            }
        }

        payload = {k: v for k, v in payload.items() if v}
        payload['consistency_options'] = {
            k: v for k, v in payload['consistency_options'].items() if v}
        headers = {
            'Authorization': self.__tenant,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }

        logging.debug('graphs payload: %s', payload)

        r = self.__session.post(url, json=payload, headers=headers)
        self.__check_error(r)

        if r.status_code == 204:
            result = None
        else:
            r.encoding = 'UTF-8'
            result = json.loads(r.text)

        return result

    def __test_connection(self):
        url = 'http://{0}:{1}/'.format(self.__host, self.__port)
        headers = {
            'Authorization': self.__tenant,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }

        r = self.__session.get(url, headers=headers)
        self.__check_error(r)

        return

    def __headers(self):
        return {
            'Authorization': self.__tenant,
            'Accept': self.__content,
            'Accept-Encoding': 'gzip'
        }

    def __check_error(self, r):
        try:
            r.raise_for_status()
        except:
            raise Exception('Error: ' + r.text)
