#!/usr/bin/env python3

import socket
import cloudpickle
from sys import stderr
import sqlite3
import json

from dotenv import load_dotenv
import yaml
from os import getenv

from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
import multiprocessing
from datetime import datetime


class Cortex(LineReceiver):
    MAX_LENGTH = 999999

    def __init__(self):
        load_dotenv()

        self.HOST = getenv("HOST")  # The server's hostname or IP address
        self.PORT = int(getenv("PORT"))  # The port used by the server
        self.USERNAME = getenv("USERNAME")
        self.SECRET_KEY = getenv("SECRET_KEY")
        self.response_mode = None
        self.sqlite_db_created = False
        self.sqlite_db = ""
        self.args_count = 0
        self.abs_counter = 0

    def lineReceived(self, data):
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
            self.sendLine(packet)

        elif "AUTHENTICATED" in data:
            if data["AUTHENTICATED"] is True:
                print("ALERT: Authentication successful!\n")
                self.command_interface()
            else:
                stderr.write("WARNING: Authentication failed.")
                self.transport.loseConnection()

        elif "PROCEED" in data:
            proceed = input("Press ENTER if ready to proceed:\t")
            if proceed == "":
                print(
                    "PROCEEDING WITH DISTRIBUTING ARGUMENTS AMONGST THE CONNECTED NODES..."
                )
                self.sendLine(cloudpickle.dumps({"VERIFY": True}))
            else:
                stderr.write("ALERT: Job cancelled.")
                self.command_interface()

        elif "RESULT" in data and self.response_mode == "STREAM":
            # If STREAM is your chosen response mode, handle results packets here.
            print(data)
            # Prematurely calls command_interface in certain instances when the last results packet is returned while jobs remain outstanding.
            # if data["ARGS_COUNTER"] == self.args_count - 1:
            # self.command_interface()

        elif "RESULT" in data and self.response_mode == "SQLITE":
            if self.sqlite_db_created is False:
                self.sqlite_db = datetime.now().strftime("%Y%m%d %H%M%S") + ".db"
                conn = sqlite3.connect(self.sqlite_db)
                c = conn.cursor()
                c.execute(
                    "CREATE TABLE results (args_counter real, abs_counter real, result text)"
                )
                self.sqlite_db_created = True
                if len(data["RESULT"]) == 1:
                    try:
                        instruction = f"""INSERT INTO results VALUES ({data['ARGS_COUNTER']}, {self.abs_counter}, {data['RESULT'][0]})"""
                        # print(instruction)
                        c.execute(instruction)
                        self.abs_counter = self.abs_counter + 1
                    except BaseException:
                        instruction = f"""INSERT INTO results VALUES ({data['ARGS_COUNTER']}, {self.abs_counter}, {json.dumps(data['RESULT'][0])})"""
                        # print(instruction)
                        c.execute(instruction)
                        self.abs_counter = self.abs_counter + 1
                    # finally:
                    # if data["ARGS_COUNTER"] == self.args_count - 1:
                    # self.command_interface()
                else:
                    for i in range(len(data["RESULT"])):
                        try:
                            instruction = f"""INSERT INTO results VALUES ({data['ARGS_COUNTER']}, {self.abs_counter}, {data['RESULT'][i]})"""
                            # print(instruction)
                            c.execute(instruction)
                            self.abs_counter = self.abs_counter + 1
                        except BaseException:
                            instruction = f"""INSERT INTO results VALUES ({data['ARGS_COUNTER']}, {self.abs_counter}, {json.dumps(data['RESULT'][i])})"""
                            # print(instruction)
                            c.execute(instruction)
                            self.abs_counter + self.abs_counter + 1

                    # if data["ARGS_COUNTER"] == self.args_count - 1:
                    # self.command_interface()
                c.close()

            else:
                conn = sqlite3.connect(self.sqlite_db)
                c = conn.cursor()
                if len(data["RESULT"]) == 1:
                    try:
                        instruction = f"""INSERT INTO results VALUES ({data['ARGS_COUNTER']}, {self.abs_counter}, {data['RESULT'][0]})"""
                        # print(instruction)
                        c.execute(instruction)
                        self.abs_counter = self.abs_counter + 1
                    except BaseException:
                        instruction = f"""INSERT INTO results VALUES ({data['ARGS_COUNTER']}, {self.abs_counter}, {json.dumps(data['RESULT'][0])})"""
                        # print(instruction)
                        c.execute(instruction)
                        self.abs_counter = self.abs_counter + 1
                    # finally:
                    # if data["ARGS_COUNTER"] == self.args_count - 1:
                    # self.command_interface()
                else:
                    for i in range(len(data["RESULT"])):
                        try:
                            instruction = f"""INSERT INTO results VALUES ({data['ARGS_COUNTER']}, {self.abs_counter}, {data['RESULT'][i]})"""
                            # print(instruction)
                            c.execute(instruction)
                            self.abs_counter = self.abs_counter + 1
                        except BaseException:
                            instruction = f"""INSERT INTO results VALUES ({data['ARGS_COUNTER']}, {self.abs_counter}, {json.dumps(data['RESULT'][i])})"""
                            # print(instruction)
                            c.execute(instruction)
                            self.abs_counter + self.abs_counter + 1
                    # if data["ARGS_COUNTER"] == self.args_count - 1:
                    # self.command_interface()
                c.close()

        elif "FINAL_RESULT" in data:
            print("FINAL RESULT:", data["FINAL_RESULT"])
            self.command_interface()

        elif "CLUSTER_STATUS" in data:
            print("CLUSTER STATUS:", data)
            self.command_interface()

        elif "KILL_NODE" in data:
            stderr.write(
                "ALERT: All cortex_nodes have been disconnected from the cluster. The cortex_server is running and accepting connections."
            )
            reactor.stop()

        else:
            print(data)
            self.command_interface()

    def cortex_compute(
        self,
        cortex_config_path="",
        args=(),
        dep_funcs=(),
        modules=(),
        callback=None,
        callback_args=(),
        group="default",
        response_mode="",
    ):
        cortex_config_path = cortex_config_path
        with open(cortex_config_path, "r") as f:
            cortex_config = yaml.load(f, Loader=yaml.Loader)

        args = cortex_config["ARGS"]
        self.args_count = len(args)
        self.response_mode = response_mode
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
                "RESPONSE_MODE": response_mode,
            }
        )
        self.sendLine(packet)

    def get_cluster_status(self):
        packet = cloudpickle.dumps({"GET_CLUSTER_STATUS": "GET_CLUSTER_STATUS"})
        self.sendLine(packet)
        print("ALERT: Requested cluster status.")

    def kill_cluster(self):
        confirm_kill_cluster = input(
            "WARNING: Are you absolutely sure that you want to kill the cluster? Enter YES to proceed."
        )
        if confirm_kill_cluster == "YES":
            packet = cloudpickle.dumps({"KILL_CLUSTER": "KILL_CLUSTER"})
            self.sendLine(packet)
        else:
            stderr.write("ALERT: kill_cluster aborted.")
            self.command_interface()

    def command_interface(self):
        command = input("Cortex cluster is ready to accept commands:\t")
        if command == "cortex_compute":
            cortex_config_path = input(
                "Enter path to cortex_config.yaml to begin job:\t"
            )
            response_mode = input(
                f"Enter desired response mode (OBJECT, SQLITE, or STREAM):\t"
            )
            self.cortex_compute(
                cortex_config_path=cortex_config_path, response_mode=response_mode
            )
        elif command == "cluster_status":
            self.get_cluster_status()
        elif command == "kill_cluster":
            self.kill_cluster()
        elif command == "help":
            print("\n-------\nCommands:")
            print("cortex_compute, cluster_status, kill_cluster, help\n-------\n")
            self.command_interface()
        else:
            print(
                "Sorry, that command is not recognized. Type 'help' for a list of commands."
            )
            self.command_interface()


def runCortex():
    load_dotenv()
    endpoint = TCP4ClientEndpoint(reactor, getenv("HOST"), int(getenv("PORT")))
    d = connectProtocol(endpoint, Cortex())

    reactor.run()


if __name__ == "__main__":
    runCortex()
