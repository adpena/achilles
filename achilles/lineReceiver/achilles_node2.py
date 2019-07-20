#!/usr/bin/env python3

import socket
import cloudpickle
from os import getenv
from os.path import dirname, abspath, join

from multiprocessing import Pool
from dotenv import load_dotenv

from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
import multiprocessing
from datetime import datetime


class AchillesNode(LineReceiver):
    MAX_LENGTH = 999999

    def __init__(self, host, port):

        self.HOST = host  # The server's hostname or IP address
        self.PORT = port  # The port used by the server
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
                p.close()
            packet = cloudpickle.dumps(
                {"ARGS_COUNTER": data["ARGS_COUNTER"], "RESULT": result}
            )
            print("RESPONSE PACKET:", packet)
            self.sendLine(packet)
        elif "KILL_NODE" in data:
            self.sendLine(cloudpickle.dumps({"KILLED_CLUSTER": "KILLED_CLUSTER"}))
            self.transport.loseConnection()
            reactor.stop()


def runAchillesNode():
    try:
        if __name__ != "__main__":
            import achilles

            dotenv_path = dirname(achilles.__file__) + "\\lineReceiver\\.env"
        else:
            basedir = abspath(dirname(__file__))
            dotenv_path = join(basedir, ".env")
        load_dotenv(dotenv_path, override=True)
        port = int(getenv("PORT"))
        host = getenv("HOST")

    except BaseException as e:
        print(
            f"No .env configuration file found ({e}). Follow the prompts below to generate one:"
        )
        host, port = genConfig()

    endpoint = TCP4ClientEndpoint(reactor, host, port)
    d = connectProtocol(endpoint, AchillesNode(host, port))

    reactor.run()


def genConfig():
    if __name__ != "__main__":
        import achilles

        dotenv_path = dirname(achilles.__file__) + "\\lineReceiver\\.env"
    else:
        basedir = abspath(dirname(__file__))
        dotenv_path = join(basedir, ".env")
    host = input("Enter HOST IP address:\t")
    port = int(input("Enter HOST port to connect to:\t"))
    with open(dotenv_path, "w") as config_file:
        config_file.writelines(f"HOST={host}\n")
        config_file.writelines(f"PORT={port}\n")
        config_file.close()
        print(
            f"Successfully generated .env configuration file at {dotenv_path}.env. Use achilles_node.genConfig() to overwrite."
        )
    return host, port


if __name__ == "__main__":
    runAchillesNode()
