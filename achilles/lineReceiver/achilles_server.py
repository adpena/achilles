#!/usr/bin/env python3

from sys import stderr, path
from os import getenv
from os.path import dirname, abspath, join
from dotenv import load_dotenv
import getpass
from types import GeneratorType

import dill

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint

from multiprocess import current_process


class AchillesServer(LineReceiver):
    MAX_LENGTH = 999999999999999999999999999999999

    def __init__(self, factory):
        self.factory = factory
        print("Starting factory:", self.factory)
        self.HOST = (
            self.factory.HOST
        )  # The server's hostname or IP address - standard loopback interface address (localhost)
        self.PORT = (
            self.factory.PORT
        )  # Port to listen on (non-privileged ports are > 1023)
        self.CPU_COUNT = 0
        self.IP = ""
        self.DATETIME_CONNECTED = ""
        self.AUTHENTICATED = False
        self.CLIENT_ID = self.factory.totalProtocols

        current_process().authkey = b"176778741"

    def connectionMade(self):
        # print("Starting connection #:", self.factory.numProtocols)
        self.factory.numProtocols = self.factory.numProtocols + 1
        self.factory.totalProtocols = self.factory.totalProtocols + 1
        # print("Number of connections:", self.factory.numProtocols)
        self.factory.clients.append(self)
        packet = dill.dumps(
            {
                "GREETING": f"Welcome! There are currently {self.factory.numProtocols} open connections.\n",
                "CLIENT_ID": self.CLIENT_ID,
            }
        )
        self.sendLine(packet)

    def connectionLost(self, reason):
        self.factory.numProtocols = self.factory.numProtocols - 1
        print(f"Connection lost: {reason}")
        print(f"{self.factory.numProtocols} clients connected.")
        self.factory.clients.remove(self)

    def lineReceived(self, data):
        data = dill.loads(data)
        # print("RECEIVED:", data)
        if "USERNAME" in data and "SECRET_KEY" in data:
            if (
                data["USERNAME"] == self.factory.USERNAME
                and data["SECRET_KEY"] == self.factory.SECRET_KEY
            ):
                # The user is authenticated to distribute commands.
                self.AUTHENTICATED = True
                self.IP = data["IP"]
                self.CLIENT_ID = "CONTROLLER"
                self.CPU_COUNT = data["CPU_COUNT"]
                self.DATETIME_CONNECTED = data["DATETIME_CONNECTED"]
                self.sendLine(dill.dumps({"AUTHENTICATED": self.AUTHENTICATED}))
                print(f"User {data['USERNAME']} is authenticated.")
                self.factory.achilles_controller = self
                self.factory.totalProtocols = self.factory.totalProtocols - 1

                # for client in self.factory.clients:
                # print(client.__dict__)
            else:
                self.sendLine(dill.dumps({"AUTHENTICATED": self.AUTHENTICATED}))
                stderr.write(
                    "This USERNAME and SECRET_KEY cannot be authenticated. Closing connection."
                )
                self.transport.loseConnection()
                # for client in self.factory.clients:
                # print(client.__dict__)
        elif "IP" in data and "CPU_COUNT" in data and self.AUTHENTICATED is False:
            # print("Clients:", self.factory.clients)
            self.IP = data["IP"]
            self.CPU_COUNT = data["CPU_COUNT"]
            self.DATETIME_CONNECTED = data["DATETIME_CONNECTED"]
            self.CLIENT_ID = data["CLIENT_ID"]
            # for client in self.factory.clients:
            # print(client.__dict__)
        elif self.AUTHENTICATED is True and "FUNC" in data:
            func = data["FUNC"]
            args = data["ARGS"]
            args_path = data["ARGS_PATH"]
            modules = data["MODULES"]
            callback = data["CALLBACK"]
            reducer = data["REDUCER"]
            group = data["GROUP"]
            response_mode = data["RESPONSE_MODE"]
            chunksize = data["CHUNKSIZE"]
            output_queue = data["OUTPUT_QUEUE"]
            self.factory.response_mode = response_mode
            self.factory.chunksize = chunksize

            self.startJob(
                func, args, args_path, modules, callback, reducer, group, output_queue
            )
        elif self.AUTHENTICATED is False and "READY" in data:
            # print(f"CLIENT STATUS: {data}")
            pass

        elif self.AUTHENTICATED is True and "VERIFY" in data:
            self.proceedWithJob()

        elif "RESULT" in data:
            self.argsBufferDel(data, self.factory.args_buffer)
            # print("RESULTS PACKET:", data)
            if self.factory.response_mode == "OBJECT":
                try:
                    loadBalance(self.factory.args, self)
                except StopIteration:
                    self.handleStopIteration(response_mode="OBJECT")

            elif (
                self.factory.response_mode == "STREAM"
                or self.factory.response_mode == "SQLITE"
            ):
                try:
                    loadBalance(self.factory.args, self)
                except StopIteration:
                    self.handleStopIteration(response_mode="STREAM")

        elif "GET_CLUSTER_STATUS" in data and self.AUTHENTICATED is True:
            packet = {"CLUSTER_STATUS": True}
            for client in self.factory.clients:
                packet[str(client.CLIENT_ID)] = {}
                packet[str(client.CLIENT_ID)]["CLIENT_ID"] = str(client.CLIENT_ID)
                packet[str(client.CLIENT_ID)]["HOST"] = str(client.HOST)
                packet[str(client.CLIENT_ID)]["PORT"] = str(client.PORT)
                packet[str(client.CLIENT_ID)]["CPU_COUNT"] = str(client.CPU_COUNT)
                packet[str(client.CLIENT_ID)]["IP"] = str(client.IP)
                packet[str(client.CLIENT_ID)]["DATETIME_CONNECTED"] = str(
                    client.DATETIME_CONNECTED
                )
                packet[str(client.CLIENT_ID)]["AUTHENTICATED"] = str(
                    client.AUTHENTICATED
                )

            self.factory.achilles_controller.sendLine(dill.dumps(packet))

        elif "KILL_CLUSTER" in data and self.AUTHENTICATED is True:
            for client in self.factory.clients:
                client.sendLine(dill.dumps({"KILL_NODE": "KILL_NODE"}))

            for client in self.factory.clients:
                client.transport.loseConnection()

        elif "KILLED_CLUSTER" in data:
            reactor.stop()

        else:
            print("UNEXPECTED", data)

    def startJob(
        self,
        func,
        args=(),
        args_path="",
        modules=None,
        callback=None,
        reducer=None,
        group="",
        output_queue=None,
    ):
        # Here is where the magic happens. Hungry consumers - feed them once and they keep
        # asking for more until the args are exhausted.

        # Flush settings in case another job has already been completed in this achilles_server's lifecycle.
        self.factory.args_path = ""
        self.factory.results = []
        self.factory.args_buffer = {}
        self.factory.args_counter = 0

        self.factory.callback = callback
        self.factory.reducer = reducer

        # print("MAP FUNC:", func)
        # print("MAP ARGS:", args)
        ip_list = []
        ip_map = []
        workers_list = []
        cpu_total = 0
        try:
            self.factory.args = iter(args(args_path))
        except TypeError:
            try:
                self.factory.args = iter(args)
            except TypeError:
                self.factory.args = iter(args())
        for client in self.factory.clients:
            if client.IP not in ip_list:
                ip_list.append(client.IP)
                ip_map.append((client.IP, client.CPU_COUNT))
                # Int may be unnecessary - check data type.
                cpu_total += int(client.CPU_COUNT)
            if client.AUTHENTICATED is False:
                workers_list.append(client)
        print("IP LIST:", ip_list)
        print("CPU TOTAL:", cpu_total)
        print("CLIENTS CONNECTED:", self.factory.numProtocols)
        self.factory.ipMap = ip_map
        self.factory.workers = workers_list
        self.factory.lastCounter = len(self.factory.workers) - 1
        for client in self.factory.workers:
            client.sendLine(
                dill.dumps(
                    {
                        "START_JOB": True,
                        "FUNC": func,
                        "CALLBACK": callback,
                        "REDUCER": reducer,
                        "OUTPUT_QUEUE": output_queue,
                    }
                )
            )
        self.factory.achilles_controller.sendLine(dill.dumps({"PROCEED": True}))

    def proceedWithJob(self):
        for worker in self.factory.workers:
            try:
                loadBalance(self.factory.args, worker)
            except StopIteration:
                self.handleStopIteration(self.factory.response_mode)

    def argsBufferDel(self, result_packet, args_buffer):
        del args_buffer[result_packet["ARGS_COUNTER"]]

    def reassignArgFromBuffer(self, args_buffer):
        args_counter, args_packet = next(iter(args_buffer.items()))
        packet = dill.dumps(args_packet)
        self.sendLine(packet)

    def handleStopIteration(self, response_mode):
        if response_mode == "STREAM":
            if len(self.factory.workers) > 1:
                if self.factory.lastCounter == 0:
                    try:
                        self.reassignArgFromBuffer(self.factory.args_buffer)
                    except StopIteration:
                        print(
                            "Final results packet has been transmitted to the achilles_controller."
                        )
                        self.factory.achilles_controller.sendLine(
                            dill.dumps({"JOB_FINISHED": True})
                        )
                else:
                    self.factory.lastCounter = self.factory.lastCounter - 1
            elif len(self.factory.workers) == 1:
                try:
                    self.reassignArgFromBuffer(self.factory.args_buffer)
                except StopIteration:
                    print(
                        "Final results packet has been transmitted to the achilles_controller."
                    )
                    self.factory.achilles_controller.sendLine(
                        dill.dumps({"JOB_FINISHED": True})
                    )

        elif response_mode == "OBJECT":
            if len(self.factory.workers) > 1:
                if self.factory.lastCounter == 0:
                    try:
                        self.reassignArgFromBuffer(self.factory.args_buffer)
                    except StopIteration:
                        self.factory.achilles_controller.sendLine(
                            dill.dumps({"FINAL_RESULT": True})
                        )
                        print(
                            "Final results packet has been transmitted to the achilles_controller."
                        )

                else:
                    self.factory.lastCounter = self.factory.lastCounter - 1
            elif len(self.factory.workers) == 1:
                try:
                    self.reassignArgFromBuffer(self.factory.args_buffer)
                except StopIteration:
                    self.factory.achilles_controller.sendLine(
                        dill.dumps({"FINAL_RESULT": True})
                    )
                    print(
                        "Final results packet has been transmitted to the achilles_controller."
                    )


def loadBalance(args_iterable, worker):
    test_arg = next(args_iterable)
    if type(test_arg) is list:
        packet = {"ARG": test_arg, "ARGS_COUNTER": int(worker.factory.args_counter)}
        argsBufferAdd(packet, worker.factory.args_buffer)

        worker.sendLine(dill.dumps(packet))
        """print(
            f"Packet with arg {worker.factory.args_counter} sent to {worker.CLIENT_ID}"
        )"""
        worker.factory.args_counter = worker.factory.args_counter + 1
    else:
        cpu_count = int(worker.CPU_COUNT)
        args_counter = worker.factory.args_counter
        packet = {"ARG": [test_arg], "ARGS_COUNTER": args_counter}

        worker.factory.args_counter = worker.factory.args_counter + 1

        balancer = worker.factory.chunksize * cpu_count - 1
        for i in range(balancer):
            try:
                packet["ARG"].append(next(worker.factory.args))
                worker.factory.args_counter = worker.factory.args_counter + 1
            except StopIteration:
                break

        argsBufferAdd(packet, worker.factory.args_buffer)
        worker.sendLine(dill.dumps(packet))
        # print(f"Packet with arg {args_counter} sent to {worker.CLIENT_ID}")


def argsBufferAdd(arg_packet, args_buffer):
    args_buffer = args_buffer
    args_buffer[arg_packet["ARGS_COUNTER"]] = arg_packet
    return args_buffer


class AchillesServerFactory(Factory):

    protocol = AchillesServer
    numProtocols = 0
    totalProtocols = 0
    clients = []
    workers = []
    achilles_controller = None
    args = None
    args_buffer = {}
    args_path = ""
    args_counter = 0
    results = []
    lastCounter = 0
    ipMap = []
    response_mode = None
    HOST = ""
    PORT = 0
    USERNAME = ""
    SECRET_KEY = ""

    def __init__(self, host, port, username, secret_key):
        AchillesServerFactory.HOST = host
        AchillesServerFactory.PORT = port
        AchillesServerFactory.USERNAME = username
        AchillesServerFactory.SECRET_KEY = secret_key

        current_process().authkey = b"176778741"

    def buildProtocol(self, addr):
        return AchillesServer(factory=AchillesServerFactory)


def runAchillesServer(host=None, port=None, username=None, secret_key=None):
    if (
        host is not None
        and port is not None
        and username is not None
        and secret_key is not None
    ):
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
            username = getenv("USERNAME")
            secret_key = getenv("SECRET_KEY")

        except BaseException as e:
            print(f"No .env configuration file found ({e})...")
            host, port, username, secret_key = genConfig()

    endpoint = TCP4ServerEndpoint(reactor, port)
    endpoint.listen(AchillesServerFactory(host, port, username, secret_key))
    print(f"ALERT: achilles_server initiated at {host}:{port}\n")
    print("Listening for connections...")
    reactor.run()


def genConfig(host=None, port=None, username=None, secret_key=None):
    if __name__ != "__main__":
        import achilles

        dotenv_path = abspath(dirname(achilles.__file__)) + "\\lineReceiver\\"
    else:
        basedir = abspath(dirname(__file__))
        dotenv_path = join(basedir, ".env")

    if (
        host is not None
        and port is not None
        and username is not None
        and secret_key is not None
    ):
        pass
    else:
        host = input("Enter HOST IP address:\t")
        port = int(input("Enter host PORT to listen on:\t"))
        username = input("Enter USERNAME to require for authentication:\t")
        secret_key = getpass.getpass(
            "Enter SECRET_KEY to require for authentication:\t"
        )
    with open(dotenv_path + ".env", "w") as config_file:
        config_file.writelines(f"HOST={host}\n")
        config_file.writelines(f"PORT={port}\n")
        config_file.writelines(f"USERNAME='{username}'\n")
        config_file.writelines(f"SECRET_KEY='{secret_key}'\n")
        config_file.close()
        print(
            f"Successfully generated .env configuration file at {dotenv_path}. Use achilles_server.genConfig() to overwrite."
        )
    return host, port, username, secret_key


if __name__ == "__main__":
    runAchillesServer()
