#!/usr/bin/env python3

import socket
import pickle
import cloudpickle
from os import getenv
from sys import stderr

from multiprocessing import Pool

from dotenv import load_dotenv

from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
import multiprocessing
from datetime import datetime
from sys import stdout

class CortexNode(Protocol):
    def __init__(self):
        load_dotenv()

        self.HOST = getenv('HOST')  # The server's hostname or IP address
        self.PORT = int(getenv('PORT'))        # The port used by the server
        self.USERNAME = getenv('USERNAME')
        self.SECRET_KEY = getenv('SECRET_KEY')
        self.connected = False
        self.client_id = -1

    def dataReceived(self, data):
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
            })
            self.transport.write(packet)
        elif 'FUNC' in data:
            func = data['FUNC']
            arg = data['ARG']
            print('ARGS:', arg)
            with Pool(multiprocessing.cpu_count()) as p:
                results = p.map(func, arg)
            packet = cloudpickle.dumps({
                'CLIENT_ID': self.client_id,
                'RESULTS': results
            })
            self.transport.write(packet)
        else:
            print(data)


def runCortexNode():
    load_dotenv()
    endpoint = TCP4ClientEndpoint(reactor, getenv('HOST'), int(getenv('PORT')))
    d = connectProtocol(endpoint, CortexNode())

    reactor.run()


if __name__ == '__main__':
    runCortexNode()
