import logging
import time

import bert


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
