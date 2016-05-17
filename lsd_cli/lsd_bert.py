import logging
import socket
import struct
import sys
import time
from datetime import datetime
from io import BlockingIOError

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
            lsd_time = ret.time / 1000.0
            tuples = ret.tuples
        except Exception as e:
            lsd_time = 0.0
            tuples = 0

        return ret

    return func_wrapper


def check_connection(f):
    def func_wrapper(*args, **kwargs):
        args[0].check_connection()
        ret = f(*args, **kwargs)

        return ret

    return func_wrapper


class Lsd:

    def __init__(self, tenant, host, port):
        self.tenant = tenant
        self.host = host
        self.port = port
        self.__connect()
        self.__credentials = self.__get_credentials()

    @timing
    def leaplog(self, query, program=None, ruleset=None, prefix_mapping=None, r=Atom('quorum'), pr=3,
                basic_quorum=True, sloppy_quorum=True, timeout=Atom('infinity'), limit=Atom('infinity')):
        func = 'evaluate'
        params = [self.__credentials, query, [],
                  [(Atom('r'), r), (Atom('pr'), pr), (Atom('basic_quorum'), basic_quorum),
                   (Atom('sloppy_quorum'), sloppy_quorum), (Atom('limit'), limit),
                   (Atom('timeout'), timeout)]]
        result = self.__ok(self.__bert_call(func, params))

        return LSDResultSet(result)

    def check_connection(self):
        try:
            logging.debug("Test connection...!")
            self.__bert_call('ping', None)
            logging.debug("Connected!")
        except BlockingIOError:
            logging.debug("Connected!")
            pass
        except Exception as e:
            logging.exception(e)
            logging.debug("Reconnecting!")
            self.__connect()


    def __connect(self):
        self.__conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.__conn.connect((self.host, self.port))

    def __get_credentials(self):
        func = 'new'
        params = ['leapsight']
        result = self.__ok(self.__bert_call(func, params))

        logging.debug('credentials: %s', result)

        return result

    def __ok(self, response):
        (status, result) = response

        if status == Atom('ok'):
            return result
        else:
            raise Exception(response)

    def __bert_call(self, operation, params):
        if params:
            operation = (Atom(operation), params)
        else:
            operation = Atom(operation)

        enc_op = encode(operation)

        self.__conn.sendall(struct.pack(">l", len(enc_op)))
        self.__conn.sendall(enc_op)
        received = self._recv()

        return decode(received)

    def _recv(self):
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


class LSDVar:
    def __init__(self, encoded):
        if encoded[0] == Atom('var'):
            self.var = encoded[1].decode()
        else:
            raise Exception('Not a lsd var')

    def __repr__(self):
        return self.var


class LSDTuple:
    def __init__(self, encoded):
        if encoded[0] == Atom('lsd_tuple'):
            self.tuple = [self.__decode_elem(elem) for elem in encoded[1:]]

        else:
            logging.error('Not a lsd tuple: %s', encoded)
            raise Exception('Not a lsd tuple')

    def __iter__(self):
        return iter(self.tuple)

    def __decode_elem(self, elem):
        if isinstance(elem, tuple):
            return self.__decode_complex_type(elem)
        elif isinstance(elem, Atom):
            return elem.__str__()
        else:
            return elem

    def __decode_complex_type(self, elem):
        if elem[0] == Atom('lsd_uri'):
            result = '<{}>'.format(elem[1].decode())
        elif elem[0] == Atom('lsd_plain_literal'):
            result = elem[1].decode()
        elif elem[0] == Atom('lsd_typed_literal'):
            result = self.__decode_typed_literal(elem)

        return result

    def __decode_typed_literal(self, elem):
        elem_type = elem[2].__str__()

        if elem_type == 'xsd_dateTime':
            result = datetime(elem[1][0][0], elem[1][0][1], elem[1][0][2],
                              elem[1][1][0], elem[1][1][1], elem[1][1][2])
        else:
            result = elem[1]

        return result


class LSDResultSet:
    def __init__(self, encoded):
        if encoded[0] == Atom('lsd_result_set'):
            self.vars = self.__extract_vars(encoded[1])
            self.rows = self.__extract_rows(encoded[2])
            self.time = encoded[5]
            self.tuples = encoded[4]
        else:
            raise Exception('Not a lsd result set')

    def __iter__(self):
        return iter(self.rows)

    def __extract_vars(self, enc_vars):
        lsd_vars = []

        if enc_vars:
            for enc_var in enc_vars:
                lsd_vars.append(LSDVar(enc_var))

        return lsd_vars

    def __extract_rows(self, enc_rows):
        lsd_rows = []

        if enc_rows:
            for enc_row in enc_rows:
                lsd_rows.append(LSDTuple(enc_row))

        return lsd_rows
