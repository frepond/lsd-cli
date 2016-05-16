import socket
import logging
import time

from bert import *


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

    def __init__(self, tenant, host, port):
        self.__tenant = tenant
        self.__host = host
        self.__port = port
        self.__conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__conn.connect((host, port))

    @timing
    def leaplog(self, query, program=None, ruleset=None, prefix_mapping=None, r='quorum', pr='3',
                basic_quorum='true', sloppy_quorum='true', timeout='infinity', limit='infinity'):
        func = Atom('evaluate')
        op = (func, [query, ruleset],
              [('r', r), ('pr', pr), ('basic_quorum', basic_quorum),
               ('sloppy_quorum', sloppy_quorum), ('limit', limit)])
        enc_op = encode(op)

        self.__conn.sendall(enc_op)
        received = self.__recv_timeout()
        logging.debug(received)

        return decode(received)

    def __recv_timeout(self, timeout=2):
        #make socket non blocking
        self.__conn.setblocking(0)

        #total data partwise in an array
        total_data=[];
        data='';

        #beginning time
        begin=time.time()
        while 1:
            #if you got some data, then break after timeout
            if total_data and time.time()-begin > timeout:
                break

            #if you got no data at all, wait a little longer, twice the timeout
            elif time.time()-begin > timeout*2:
                break

            #recv something
            try:
                data = self.__conn.recv(8192)
                if data:
                    total_data.append(data)
                    #change the beginning time for measurement
                    begin=time.time()
                else:
                    #sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass

        #join all parts to make final string
        return ''.join(total_data)