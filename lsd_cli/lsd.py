import logging
import socket
import struct
import sys
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
        self.__connect()
        self.__credentials = self.__get_credentials()

    @timing
    def leaplog(self, query, program=None, ruleset=None, prefix_mapping=None, r=Atom('quorum'), pr=3,
                basic_quorum=True, sloppy_quorum=True, timeout=Atom('infinity'), limit=Atom('infinity')):
        func = Atom('evaluate')
        params = [self.__credentials, query, [],
                  [(Atom('r'), r), (Atom('pr'), pr), (Atom('basic_quorum'), basic_quorum),
                   (Atom('sloppy_quorum'), sloppy_quorum), (Atom('limit'), limit),
                   (Atom('timeout'), timeout)]]
        result = self.__bert_call(func, params)

        logging.debug('leaplog result: %s', result)

        return result

    def __connect(self):
        self.__conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.__conn.connect((self.__host, self.__port))

    def __get_credentials(self):
        func = Atom('new')
        params = [(Atom('lsd_credentials'), 'leapsight', [], []), []]
        result = self.__bert_call(func, params)
        logging.debug('credentials: %s', result)

        return result

    def __bert_call(self, operation, params):
        operation = (Atom(operation), params)
        enc_op = encode(operation)

        self.__conn.sendall(struct.pack(">l", len(enc_op)))
        self.__conn.sendall(enc_op)
        received = self.__recv()

        return decode(received)

    def __recv(self):
        # data length is packed into 4 bytes
        total_len = 0
        total_data = []
        size = sys.maxsize
        size_data = sock_data = b''
        recv_size = 8192

        while total_len < size:
            sock_data = self.__conn.recv(recv_size)

            if not total_data:
                if len(sock_data) > 4:
                    size_data += sock_data
                    size = struct.unpack('>l', size_data[:4])[0]
                    recv_size = size
                    if recv_size > 524288:
                        recv_size = 524288
                    total_data.append(size_data[4:])
                else:
                    size_data += sock_data
            else:
                total_data.append(sock_data)

            total_len = sum([len(i) for i in total_data])

        return b''.join(total_data)
