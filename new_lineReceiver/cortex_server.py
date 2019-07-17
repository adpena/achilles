#!/usr/bin/env python3
import cloudpickle
from sys import stderr
from os import getenv
from dotenv import load_dotenv

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint


class CortexServer(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        print("Starting factory:", self.factory)
        self.HOST = getenv(
            "HOST"
        )  # The server's hostname or IP address - standard loopback interface address (localhost)
        self.PORT = int(
            getenv("PORT")
        )  # Port to listen on (non-privileged ports are > 1023)
        self.USERNAME = getenv("USERNAME")
        self.SECRET_KEY = getenv("SECRET_KEY")
        self.CPU_COUNT = 0
        self.IP = ""
        self.DATETIME_CONNECTED = ""
        self.AUTHENTICATED = False
        self.CLIENT_ID = self.factory.totalProtocols

    def connectionMade(self):
        print("Starting connection #:", self.factory.numProtocols)
        self.factory.numProtocols = self.factory.numProtocols + 1
        self.factory.totalProtocols = self.factory.totalProtocols + 1
        print("Number of connections:", self.factory.numProtocols)
        self.factory.clients.append(self)
        packet = cloudpickle.dumps(
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
        data = cloudpickle.loads(data)
        print("RECEIVED:", data)
        if "USERNAME" in data and "SECRET_KEY" in data:
            if (
                data["USERNAME"] == self.USERNAME
                and data["SECRET_KEY"] == self.SECRET_KEY
            ):
                # The user is authenticated to distribute commands.
                self.AUTHENTICATED = True
                self.IP = data["IP"]
                self.CPU_COUNT = data["CPU_COUNT"]
                self.DATETIME_CONNECTED = data["DATETIME_CONNECTED"]
                self.sendLine(
                    cloudpickle.dumps({"AUTHENTICATED": self.AUTHENTICATED})
                )
                print(f"User {data['USERNAME']} is authenticated.")
                self.factory.cortex = self

                # for client in self.factory.clients:
                # print(client.__dict__)
            else:
                self.sendLine(
                    cloudpickle.dumps({"AUTHENTICATED": self.AUTHENTICATED})
                )
                stderr.write(
                    "This USERNAME and SECRET_KEY cannot be authenticated. Closing connection."
                )
                self.transport.loseConnection()
                # for client in self.factory.clients:
                # print(client.__dict__)
        elif "IP" in data and "CPU_COUNT" in data and self.AUTHENTICATED is False:
            print(data)
            print("Clients:", self.factory.clients)
            self.IP = data["IP"]
            self.CPU_COUNT = data["CPU_COUNT"]
            self.DATETIME_CONNECTED = data["DATETIME_CONNECTED"]
            self.CLIENT_ID = data["CLIENT_ID"]
            # for client in self.factory.clients:
            # print(client.__dict__)
        elif self.AUTHENTICATED is True and "FUNC" in data:
            func = data["FUNC"]
            args = data["ARGS"]
            dep_funcs = data["DEP_FUNCS"]
            modules = data["MODULES"]
            callback = data["CALLBACK"]
            callback_args = data["CALLBACK_ARGS"]
            group = data["GROUP"]
            response_mode = data["RESPONSE_MODE"]
            self.factory.response_mode = response_mode

            self.startJob(func, args)
        elif self.AUTHENTICATED is False and "READY" in data:
            print(f"CLIENT STATUS: {data}")

        elif self.AUTHENTICATED is True and "VERIFY" in data:
            for worker in self.factory.workers:
                try:
                    packet = cloudpickle.dumps(
                        {
                            "ARG": next(self.factory.args),
                            "ARGS_COUNTER": self.factory.args_counter,
                        }
                    )
                    worker.sendLine(packet)
                    print(
                        f"Packet with arg {self.factory.args_counter} sent to {worker.CLIENT_ID}"
                    )
                    self.factory.args_counter = self.factory.args_counter + 1

                except StopIteration:
                    print("The arguments iterable was empty.")

        elif "RESULT" in data:
            print("RESULTS PACKET:", data)
            if self.factory.response_mode == "OBJECT":
                self.factory.results.append(data)
                try:
                    packet = cloudpickle.dumps(
                        {
                            "ARG": next(self.factory.args),
                            "ARGS_COUNTER": self.factory.args_counter,
                        }
                    )
                    self.sendLine(packet)
                    print(
                        f"Packet with arg {self.factory.args_counter} sent to {self.CLIENT_ID}"
                    )
                    self.factory.args_counter = self.factory.args_counter + 1
                except StopIteration:
                    print("The arguments have been exhausted.")
                    if len(self.factory.workers) > 1:
                        if self.factory.lastCounter == 1:
                            self.factory.cortex.sendLine(
                                cloudpickle.dumps(
                                    {
                                        "FINAL_RESULT": self.factory.gatherResults(
                                            self.factory
                                        )
                                    }
                                )
                            )

                        else:
                            self.factory.lastCounter = self.factory.lastCounter - 1
                    elif len(self.factory.workers) == 1:
                        self.factory.cortex.sendLine(
                            cloudpickle.dumps(
                                {
                                    "FINAL_RESULT": self.factory.gatherResults(
                                        self.factory
                                    )
                                }
                            )
                        )
            elif (
                self.factory.response_mode == "STREAM"
                or self.factory.response_mode == "SQLITE"
            ):
                self.factory.cortex.sendLine(cloudpickle.dumps(data))
                try:
                    packet = cloudpickle.dumps(
                        {
                            "ARG": next(self.factory.args),
                            "ARGS_COUNTER": self.factory.args_counter,
                        }
                    )
                    self.sendLine(packet)
                    print(
                        f"Packet with arg {self.factory.args_counter} sent to {self.CLIENT_ID}"
                    )
                    self.factory.args_counter = self.factory.args_counter + 1
                except StopIteration:
                    print("The arguments have been exhausted.")
                    if len(self.factory.workers) > 1:
                        if self.factory.lastCounter == 1:
                            print(
                                "Final results packet has been transmitted to the cortex."
                            )

                        else:
                            self.factory.lastCounter = self.factory.lastCounter - 1
                    elif len(self.factory.workers) == 1:
                        print(
                            "Final results packet has been transmitted to the cortex."
                        )

        elif "GET_CLUSTER_STATUS" in data:
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

            self.factory.cortex.sendLine(cloudpickle.dumps(packet))

        elif "KILL_CLUSTER" in data:
            for client in self.factory.clients:
                client.sendLine(cloudpickle.dumps({"KILL_NODE": "KILL_NODE"}))

            for client in self.factory.clients:
                client.transport.loseConnection()

        elif "KILLED_CLUSTER" in data:
            reactor.stop()

        else:
            print(data)

    def startJob(self, func, args=()):
        # Here is where the magic happens. Hungry consumers - feed them once and they keep
        # asking for more until the args are exhausted.

        # Flush settings in case another job has already been completed in this lifecycle.
        self.factory.args_counter = 0
        self.factory.results = []

        print("MAP FUNC:", func)
        print("MAP ARGS:", args)
        ip_list = []
        ip_map = []
        workers_list = []
        cpu_total = 0
        self.factory.args = iter(args)
        for client in self.factory.clients:
            if client.IP not in ip_list:
                ip_list.append(client.IP)
                ip_map.append((client.IP, client.CPU_COUNT))
                # Int may be unnecessary - check data type.
                cpu_total += int(client.CPU_COUNT)
            if client.AUTHENTICATED is False:
                workers_list.append(client)
        print("IP LIST:", ip_list)
        print("CPU TOTAL", cpu_total)
        print("CLIENTS CONNECTED:", self.factory.numProtocols)
        print(workers_list)
        self.factory.ipMap = ip_map
        self.factory.workers = workers_list
        self.factory.lastCounter = len(self.factory.workers) - 1
        for client in self.factory.workers:
            client.sendLine(cloudpickle.dumps({"START_JOB": True, "FUNC": func}))
        self.factory.cortex.sendLine(cloudpickle.dumps({"PROCEED": True}))


class CortexServerFactory(Factory):

    protocol = CortexServer
    numProtocols = 0
    totalProtocols = 0
    clients = []
    workers = []
    cortex = None
    args = None
    args_counter = 0
    results = []
    lastCounter = 0
    ipMap = []
    response_mode = None

    def buildProtocol(self, addr):
        return CortexServer(factory=CortexServerFactory)

    def gatherResults(self):
        final_results = []
        self.results = sorted(self.results, key=lambda k: k["ARGS_COUNTER"])
        for result in self.results:
            final_results.append(result["RESULT"])
        return final_results


def runCortexServer():
    load_dotenv()
    port = int(getenv("PORT"))
    endpoint = TCP4ServerEndpoint(reactor, port)
    endpoint.listen(CortexServerFactory())
    print(f"ALERT: cortex_server initiated on HOST {getenv('HOST')} at PORT {port}")
    reactor.run()


if __name__ == "__main__":
    runCortexServer()
