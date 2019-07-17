#!/usr/bin/env python3

import socket
import cloudpickle
from os import getenv

from multiprocessing import Pool
from dotenv import load_dotenv

from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
import multiprocessing
from datetime import datetime


class CortexNode(LineReceiver):
    def __init__(self):
        load_dotenv()

        self.HOST = getenv("HOST")  # The server's hostname or IP address
        self.PORT = int(getenv("PORT"))  # The port used by the server
        self.USERNAME = getenv("USERNAME")
        self.SECRET_KEY = getenv("SECRET_KEY")
        self.connected = False
        self.client_id = -1
        self.func = None
        self.args = []

    def lineReceived(self, data):
        self.handleData(data)

    def handleData(self, data):
        data = cloudpickle.loads(data)
        if "GREETING" in data:
            greeting = data["GREETING"]
            client_id = data["CLIENT_ID"]
            self.client_id = client_id
            print("GREETING:", greeting)
            print("CLIENT_ID", client_id)
            packet = cloudpickle.dumps(
                {
                    "IP": socket.gethostbyname(socket.gethostname()),
                    "CPU_COUNT": multiprocessing.cpu_count(),
                    "DATETIME_CONNECTED": datetime.now(),
                    "CLIENT_ID": self.client_id,
                }
            )
            self.sendLine(packet)
        elif "START_JOB" in data:
            func = data["FUNC"]
            self.func = func
            packet = cloudpickle.dumps({"CLIENT_ID": self.client_id, "READY": True})
            print("START_JOB RESPONSE:", packet)
            self.sendLine(packet)
        elif "ARG" in data:
            print("ARG:", data["ARG"])
            with Pool(multiprocessing.cpu_count()) as p:
                result = p.map(self.func, data["ARG"])
            packet = cloudpickle.dumps(
                {"ARGS_COUNTER": data["ARGS_COUNTER"], "RESULT": result}
            )
            print("RESPONSE PACKET:", packet)
            self.sendLine(packet)
        elif "KILL_NODE" in data:
            self.sendLine(
                cloudpickle.dumps({"KILLED_CLUSTER": "KILLED_CLUSTER"})
            )
            self.transport.loseConnection()
            reactor.stop()


def runCortexNode():
    load_dotenv()
    endpoint = TCP4ClientEndpoint(reactor, getenv("HOST"), int(getenv("PORT")))
    d = connectProtocol(endpoint, CortexNode())

    reactor.run()


if __name__ == "__main__":
    runCortexNode()
