import ujson as json
import logging
import time

import requests

cli_time = 0.0
lsd_time = 0.0
tuples = 0


def timing(fun):
    """Computes basic LSD opration statistics."""
    def _func_wrapper(*args, **kwargs):
        global cli_time
        global lsd_time
        global tuples
        time1 = time.time()
        ret = fun(*args, **kwargs)
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

    return _func_wrapper


class Lsd:
    """Barebones LSD leaplog API client"""

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
    def leaplog(self, program, ruleset=None, prefix_mapping=None, r=None, pr=None,
                w=None, cw=None, pw=None, basic_quorum=None, ts=None, timeout=None, limit=1000):
        """Excute a leaplog query or program in LSD.

        :param program: the leaplog program to evaluate.
        :param ruleset: the ruleset to evaluate the program with.
        :param prefix_mappings: the prefix mappings used in the propgram.
        """
        url = 'http://{0}:{1}/leaplog'.format(self.__host, self.__port)
        payload = {
            'program': program,
            'ruleset': ruleset,
            'prefix_mapping': prefix_mapping,
            'consistency_options': {
                'r': r,
                'pr': pr,
                'w': w,
                'cw': cw,
                'pw': pw,
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
        """List the rulesets defined in LSD."""
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
        """Creates a new rulset under a given URI.

        :param uri: the URI under which the ruleset is registered.
        :param source: the source code containg the ruleset statements.
        """
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
        """Creates a new grpah in LSD.

        :param uri: the URI of the new graph.
        :param description: the description of the new graph.
        :param type: the type of graph to be created. One of in_memory|disk|memory_disk.
                     Default: memory.
        :param is_active: whether the graph is active or not from the moment of creation.
                          Default: true.
        :param mutable: whether the graph is read-only or not. Default: false.
        """
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
