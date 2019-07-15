#!/usr/bin/env python3

import socket
import asyncio
import time
import random
import cloudpickle
from os import getenv
from sys import stderr, stdout

from multiprocessing import Pool, Process, Queue
from concurrent.futures import ProcessPoolExecutor

from dotenv import load_dotenv

from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor, defer
import multiprocessing
from datetime import datetime

class CortexNode(Protocol):
    def __init__(self):
        load_dotenv()

        self.HOST = getenv('HOST')  # The server's hostname or IP address
        self.PORT = int(getenv('PORT'))        # The port used by the server
        self.USERNAME = getenv('USERNAME')
        self.SECRET_KEY = getenv('SECRET_KEY')
        self.connected = False
        self.client_id = -1
        self.func = None
        self.args = []
        self.job_in_progress = False


    def dataReceived(self, data):
        # pqueue.put(data)
        self.handleData(data)

    def handleData(self, data):
        data = cloudpickle.loads(data)
        if 'GREETING' in data:
            greeting = data['GREETING']
            client_id = data['CLIENT_ID']
            self.client_id = client_id
            print('GREETING:', greeting)
            print('CLIENT_ID', client_id)
            packet = cloudpickle.dumps({
                'IP': socket.gethostbyname(socket.gethostname()),
                'CPU_COUNT': multiprocessing.cpu_count(),
                'DATETIME_CONNECTED': datetime.now(),
                'CLIENT_ID': self.client_id,
            })
            self.transport.write(packet)
        elif 'START_JOB' in data:
            func = data['FUNC']
            self.func = func
            self.job_in_progress = True
            packet = cloudpickle.dumps({
                'CLIENT_ID': self.client_id,
                'READY': True
            })
            print('START_JOB RESPONSE:', packet)
            self.transport.write(packet)
        elif 'ARG' in data:
            with Pool(multiprocessing.cpu_count()) as p:
                result = p.map(self.func, data['ARG'])
            packet = cloudpickle.dumps({
                'ARGS_COUNTER': data['ARGS_COUNTER'],
                'RESULT': result
            })
            print('RESPONSE PACKET:', packet)
            self.transport.write(packet)


def reader_proc(queue):
    while True:
        data = queue.get()
        data = cloudpickle.loads(data)
        if 'GREETING' in data:
            print(data)

        elif 'FUNC' in data:
            print(data)

        elif data == 'ABORT':
            break
        else:
            print(data)


def runCortexNode():
    load_dotenv()
    endpoint = TCP4ClientEndpoint(reactor, getenv('HOST'), int(getenv('PORT')))
    d = connectProtocol(endpoint, CortexNode())

    reactor.run()


if __name__ == '__main__':
    pqueue = Queue()
    rqueue = Queue()

    reader_p = Process(target=reader_proc, args=(pqueue,))
    reader_p.daemon = True
    reader_p.start()

    runCortexNode()
