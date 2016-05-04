import requests


class Lsd:
    def __init__(self, tenant, host, port, content='application/leaplog-results+json'):
        self.__tenant = tenant
        self.__host = host
        self.__port = port
        self.__content = content

        # test lsd connection
        self.leaplog('?(<invalid:uri>, <invalid:uri>, <invalid:uri>, <lsd:demo:graph>).')

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

        r = requests.get(url, params=payload, headers=headers)
        r.raise_for_status()
        result = r.json()

        return result

    def rulsets(self):
        url = 'http://{0}:{1}/rulesets'.format(self.__host, self.__port)
        headers = {
            'Authorization': self.__tenant,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }

        r = requests.get(url, headers=headers)
        r.raise_for_status()
        result = r.json()

        return result

    def ruleset(self, ruleset):
        url = 'http://{0}:{1}/rulesets'.format(self.__host, self.__port)
        headers = {
            'Authorization': self.__tenant,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }

        r = requests.post(url, json=ruleset, headers=headers)
        r.raise_for_status()
        result = r.json()

        return result

    def __headers(self):
        return {
            'Authorization': self.__tenant,
            'Accept': self.__content,
            'Accept-Encoding': 'gzip'
        }