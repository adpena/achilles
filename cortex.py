# A special cortex client that can send commands to the cortex_server.
#!/usr/bin/env python3

import socket
import pickle
import cloudpickle
from os import getenv
from sys import stderr

from dotenv import load_dotenv
import yaml

from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
import multiprocessing
from datetime import datetime
from sys import stdout
from yaml import load, dump


class Cortex(Protocol):
    def __init__(self):
        load_dotenv()

        self.HOST = getenv("HOST")  # The server's hostname or IP address
        self.PORT = int(getenv("PORT"))  # The port used by the server
        self.USERNAME = getenv("USERNAME")
        self.SECRET_KEY = getenv("SECRET_KEY")

    def dataReceived(self, data):
        data = cloudpickle.loads(data)
        if "GREETING" in data:
            greeting = data["GREETING"]
            print("GREETING:", greeting)
            packet = cloudpickle.dumps(
                {
                    "IP": socket.gethostbyname(socket.gethostname()),
                    "CPU_COUNT": multiprocessing.cpu_count(),
                    "DATETIME_CONNECTED": datetime.now(),
                    "USERNAME": self.USERNAME,
                    "SECRET_KEY": self.SECRET_KEY,
                }
            )
            self.transport.write(packet)

        elif "AUTHENTICATED" in data:
            if data["AUTHENTICATED"] is True:
                stdout.write("ALERT: Authentication successful!\n")
                cortex_config_path = input(
                    "Enter path to cortex_config.yaml to begin job:\t"
                )
                self.cortex_compute(cortex_config_path=cortex_config_path)

            else:
                stderr.write("WARNING: Authentication failed.")
                self.transport.loseConnection()
        elif "PROCEED" in data:
            proceed = input("Press ENTER when the job is ready to proceed:\t")
            print(
                "PROCEEDING WITH DISTRIBUTING ARGUMENTS AMONGST THE CONNECTED NODES..."
            )
            self.transport.write(cloudpickle.dumps({"VERIFY": True}))

        elif "FINAL_RESULT" in data:
            print("FINAL RESULT:", data["FINAL_RESULT"])

        else:
            print(data)

    def cortex_compute(
        self,
        cortex_config_path="",
        func=None,
        args=(),
        dep_funcs=(),
        modules=(),
        callback=None,
        callback_args=(),
        group="default",
    ):
        cortex_config_path = cortex_config_path
        with open(cortex_config_path, "r") as f:
            cortex_config = yaml.load(f, Loader=yaml.Loader)

        func = cortex_config["FUNC"]
        print("FUNC:", func)
        args = cortex_config["ARGS"]
        print("ARGS:", args)
        dep_funcs = cortex_config["DEP_FUNCS"]
        modules = cortex_config["MODULES"]
        callback = cortex_config["CALLBACK"]
        callback_args = cortex_config["CALLBACK_ARGS"]
        group = cortex_config["GROUP"]
        from cortex_function import cortex_function

        packet = cloudpickle.dumps(
            {
                "FUNC": cortex_function,
                "ARGS": args,
                "DEP_FUNCS": dep_funcs,
                "MODULES": modules,
                "CALLBACK": callback,
                "CALLBACK_ARGS": callback_args,
                "GROUP": group,
                "IP": socket.gethostbyname(socket.gethostname()),
                "CPU_COUNT": multiprocessing.cpu_count(),
                "DATETIME_CONNECTED": datetime.now(),
            }
        )
        self.transport.write(packet)


def runCortex():
    load_dotenv()
    endpoint = TCP4ClientEndpoint(reactor, getenv("HOST"), int(getenv("PORT")))
    d = connectProtocol(endpoint, Cortex())

    reactor.run()


if __name__ == "__main__":
    runCortex()
