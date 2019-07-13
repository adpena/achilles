#!/usr/bin/env python3
import cloudpickle
from sys import stderr, stdout, path
from os import getenv
from dotenv import load_dotenv

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint


class CortexServer(Protocol):
    def __init__(self, factory):
        self.factory = factory
        print("Starting factory:", self.factory)
        self.HOST = getenv('HOST')              # The server's hostname or IP address - standard loopback interface address (localhost)
        self.PORT = int(getenv('PORT'))         # Port to listen on (non-privileged ports are > 1023)
        self.USERNAME = getenv('USERNAME')
        self.SECRET_KEY = getenv('SECRET_KEY')
        self.CPU_COUNT = 0
        self.IP = ''
        self.DATETIME_CONNECTED = ''
        self.AUTHENTICATED = False
        self.CLIENT_ID = self.factory.totalProtocols

    def connectionMade(self):
        print('Starting connection #:', self.factory.numProtocols)
        self.factory.numProtocols = self.factory.numProtocols + 1
        self.factory.totalProtocols = self.factory.totalProtocols + 1
        print('Number of connections:', self.factory.numProtocols)
        self.factory.clients.append(self)
        packet = {
            'GREETING': f"Welcome! There are currently {self.factory.numProtocols} open connections.\n",
            'CLIENT_ID': self.CLIENT_ID

        }
        self.transport.write(cloudpickle.dumps(
            packet
        ))

    def connectionLost(self, reason):
        self.factory.numProtocols = self.factory.numProtocols - 1
        print(f"Connection lost: {reason}")
        print(f"{self.factory.numProtocols} clients connected.")
        self.factory.clients.remove(self)

    def dataReceived(self, data):
        data = cloudpickle.loads(data)
        if 'USERNAME' in data and 'SECRET_KEY' in data:
            if data['USERNAME'] == self.USERNAME and data['SECRET_KEY'] == self.SECRET_KEY:
                # The user is authenticated to distribute commands.
                self.AUTHENTICATED = True
                self.IP = data['IP']
                self.CPU_COUNT = data['CPU_COUNT']
                self.DATETIME_CONNECTED = data['DATETIME_CONNECTED']
                self.transport.write(cloudpickle.dumps({
                    'AUTHENTICATED': self.AUTHENTICATED,
                }))
                print(f"User {data['USERNAME']} is authenticated.")
                # for client in self.factory.clients:
                    # print(client.__dict__)
            else:
                self.transport.write({
                    'AUTHENTICATED': self.AUTHENTICATED,
                })
                stderr.write('This USERNAME and SECRET_KEY cannot be authenticated. Closing connection.')
                self.transport.loseConnection()
                # for client in self.factory.clients:
                    # print(client.__dict__)
        elif 'IP' in data and 'CPU_COUNT' in data and self.AUTHENTICATED is False:
            print(data)
            print("Clients:", self.factory.clients)
            self.IP = data['IP']
            self.CPU_COUNT = data['CPU_COUNT']
            self.DATETIME_CONNECTED = data['DATETIME_CONNECTED']
            self.CLIENT_ID = data['CLIENT_ID']
            # for client in self.factory.clients:
                # print(client.__dict__)
        elif self.AUTHENTICATED is True:
            func = data['FUNC']
            args = data['ARGS']
            dep_funcs = data['DEP_FUNCS']
            modules = data['MODULES']
            callback = data['CALLBACK']
            callback_args = data['CALLBACK_ARGS']
            group = data['GROUP']
            '''self.distribute(func=func, args=args, dep_funcs=dep_funcs, modules=modules, callback=callback,
                                    callback_args=callback_args, group=group)'''
            # Relics of testing
            # print(kwargs)
            print(args)
            self.map(func, args)
        elif 'RESULTS' in data:
            print('RESULTS PACKET:', data)

        else:
            print(data)
            for client in self.factory.clients:
                print(client.__dict__)

    def chunker(self, seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    def map(self, func, args=[], dep_funcs=(), modules=(), callback=None, callback_args=(), group='default'):
        # Here is where the magic happens.
        print('MAP FUNC:', func)
        print('MAP ARGS:', args)
        ip_list = []
        ip_map = []
        workers_list = []
        cpu_total = 0
        for client in self.factory.clients:
            if client.IP not in ip_list:
                ip_list.append(client.IP)
                ip_map.append((client.IP, client.CPU_COUNT))
                # Int may be unnecessary - check data type.
                cpu_total += int(client.CPU_COUNT)
            if client.AUTHENTICATED is False:
                workers_list.append(client)
        print('IP LIST:', ip_list)
        print('CPU TOTAL', cpu_total)
        print('CLIENTS CONNECTED:', self.factory.numProtocols)
        split_args = []
        client_counter = 0
        print(workers_list)
        for i in range(len(args)):

            if client_counter < len(workers_list):
                print(client_counter)
                packet = {
                    'FUNC': func,
                    'ARG': args[i],
                    'DEP_FUNCS': dep_funcs,
                    'MODULES': modules,
                    'CALLBACK': callback,
                    'CALLBACK_ARGS': callback_args,
                    'GROUP': group,
                }
                workers_list[client_counter].transport.write(cloudpickle.dumps(
                    packet
                ))
                print(f'Regular packet: {packet} sent to worker {workers_list[client_counter].CLIENT_ID}')
                client_counter = client_counter + 1

            else:
                client_counter = 0
                packet = {
                    'FUNC': func,
                    'ARG': args[i],
                    'DEP_FUNCS': dep_funcs,
                    'MODULES': modules,
                    'CALLBACK': callback,
                    'CALLBACK_ARGS': callback_args,
                    'GROUP': group,
                }
                workers_list[client_counter].transport.write(cloudpickle.dumps(
                    packet
                ))
                print(f'Reset packet: {packet} sent to worker {workers_list[client_counter].CLIENT_ID}')
                client_counter = client_counter + 1


class CortexServerFactory(Factory):

    protocol = CortexServer
    numProtocols = 0
    totalProtocols = 0
    clients = []

    def buildProtocol(self, addr):
        return CortexServer(factory=CortexServerFactory)


def runCortexServer(port=None):
    load_dotenv()
    port = int(getenv('PORT'))
    endpoint = TCP4ServerEndpoint(reactor, port)
    endpoint.listen(CortexServerFactory())
    reactor.run()

if __name__ == '__main__':
    runCortexServer()
