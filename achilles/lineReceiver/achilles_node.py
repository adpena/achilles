#!/usr/bin/env python3

from sys import path
from os import getenv
from os.path import dirname, abspath, join
from dotenv import load_dotenv
from datetime import datetime

from multiprocess import Pool, cpu_count
import multiprocess

import socket
import dill

from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor


class AchillesNode(LineReceiver):
    MAX_LENGTH = 999999999999999999999999999

    def __init__(self, host, port):

        self.HOST = host  # The server's hostname or IP address
        self.PORT = port  # The port used by the server
        self.connected = False
        self.client_id = -1
        self.func = None
        self.callback = None
        self.reducer = None
        self.output_queue = None

        multiprocess.current_process().authkey = b"12345"

    def lineReceived(self, data):
        self.handleData(data)

    def handleData(self, data):
        # print(data)
        data = dill.loads(data)
        if "GREETING" in data:
            greeting = data["GREETING"]
            client_id = data["CLIENT_ID"]
            self.client_id = client_id
            print(
                "GREETING:",
                f"{greeting}\nConnected to achilles_server running at {self.HOST}:{self.PORT}",
            )
            print("CLIENT_ID:", client_id)
            packet = dill.dumps(
                {
                    "IP": socket.gethostbyname(socket.gethostname()),
                    "CPU_COUNT": cpu_count(),
                    "DATETIME_CONNECTED": datetime.now(),
                    "CLIENT_ID": self.client_id,
                }
            )
            self.sendLine(packet)
        elif "START_JOB" in data:
            func = data["FUNC"]
            self.func = func
            callback = data["CALLBACK"]
            self.callback = callback
            reducer = data["REDUCER"]
            self.reducer = reducer
            output_queue = data["OUTPUT_QUEUE"]
            self.output_queue = data["OUTPUT_QUEUE"]
            packet = dill.dumps({"CLIENT_ID": self.client_id, "READY": True})
            # print("START_JOB RESPONSE:", packet)
            self.sendLine(packet)
        elif "ARG" in data:
            # print("ARG:", data["ARG"])
            with Pool(cpu_count()) as p:
                result = p.map(self.func, data["ARG"])
                if self.callback is not None:
                    result = p.map(self.callback, result)
                else:
                    pass
                p.close()
            if self.reducer is not None:
                result = self.reducer(result)
            else:
                pass
            self.output_queue.put(
                {"ARGS_COUNTER": data["ARGS_COUNTER"], "RESULT": result}
            )
            packet = dill.dumps({"ARGS_COUNTER": data["ARGS_COUNTER"], "RESULT": True})
            # print("RESPONSE PACKET:", packet)
            self.sendLine(packet)
        elif "KILL_NODE" in data:
            self.sendLine(dill.dumps({"KILLED_CLUSTER": "KILLED_CLUSTER"}))
            self.transport.loseConnection()
            reactor.stop()


def runAchillesNode(host=None, port=None):
    if host is not None and port is not None:
        pass
    else:
        try:
            if __name__ != "__main__":
                import achilles

                dotenv_path = (
                    abspath(dirname(achilles.__file__)) + "\\lineReceiver\\.env"
                )

                achilles_function_path = (
                    abspath(dirname(achilles.__file__)) + "\\lineReceiver\\"
                )
                path.append(achilles_function_path)

            else:
                basedir = abspath(dirname(__file__))
                dotenv_path = join(basedir, ".env")

                achilles_function_path = abspath(dirname(__file__))
                path.append(achilles_function_path)
            load_dotenv(dotenv_path, override=True)
            port = int(getenv("PORT"))
            host = getenv("HOST")

        except BaseException as e:
            print(f"No .env configuration file found ({e})...")
            host, port = genConfig()

    endpoint = TCP4ClientEndpoint(reactor, host, port)
    d = connectProtocol(endpoint, AchillesNode(host, port))

    reactor.run()


def genConfig(host=None, port=None):
    if __name__ != "__main__":
        import achilles

        dotenv_path = abspath(dirname(achilles.__file__)) + "\\lineReceiver\\.env"
    else:
        basedir = abspath(dirname(__file__))
        dotenv_path = join(basedir, ".env")
    if host is not None and port is not None:
        pass
    else:
        host = input("Enter HOST IP address:\t")
        port = int(input("Enter HOST port to connect to:\t"))
    with open(dotenv_path, "w") as config_file:
        config_file.writelines(f"HOST={host}\n")
        config_file.writelines(f"PORT={port}\n")
        config_file.close()
        print(
            f"Successfully generated .env configuration file at {dotenv_path}. Use achilles_node.genConfig() to overwrite."
        )
    return host, port


if __name__ == "__main__":
    runAchillesNode()
