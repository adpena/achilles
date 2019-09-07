#!/usr/bin/env python3

import socket
import dill
from sys import stderr, path
import sqlite3
import json

from dotenv import load_dotenv
import yaml
from os import getenv
from os.path import abspath, dirname, join
import getpass

from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
from multiprocess import cpu_count, Process, Queue, Manager
from datetime import datetime


class AchillesController(LineReceiver):
    MAX_LENGTH = 999999999999999999999999999999999

    def __init__(
        self,
        host,
        port,
        username,
        secret_key,
        achilles_function=None,
        achilles_args=None,
        achilles_callback=None,
        achilles_reducer=None,
        response_mode="OBJECT",
        globals_dict=None,
        chunksize=1,
        command=None,
        command_verified=False,
    ):

        self.HOST = host  # The server's hostname or IP address
        self.PORT = port  # The port used by the server
        self.USERNAME = username
        self.SECRET_KEY = secret_key
        self.response_mode = response_mode
        self.sqlite_db_created = False
        self.sqlite_db = ""
        self.abs_counter = 0
        self.achilles_function = achilles_function
        self.achilles_args = achilles_args
        self.achilles_callback = achilles_callback
        self.achilles_reducer = achilles_reducer
        self.globals_dict = globals_dict
        self.chunksize = chunksize
        self.command = command
        self.command_verified = command_verified

    def lineReceived(self, data):
        data = dill.loads(data)
        if "GREETING" in data:
            greeting = data["GREETING"]
            # print("GREETING:", greeting)
            packet = dill.dumps(
                {
                    "IP": socket.gethostbyname(socket.gethostname()),
                    "CPU_COUNT": cpu_count(),
                    "DATETIME_CONNECTED": datetime.now(),
                    "USERNAME": self.USERNAME,
                    "SECRET_KEY": self.SECRET_KEY,
                }
            )
            self.sendLine(packet)

        elif "AUTHENTICATED" in data:
            if data["AUTHENTICATED"] is True:
                print(
                    f"ALERT: Connection to achilles_server at {self.HOST}:{self.PORT} and authentication successful.\n"
                )
                if self.command == "KILL_CLUSTER":
                    self.kill_cluster()
                elif self.command == "GET_CLUSTER_STATUS":
                    self.get_cluster_status()
                elif self.achilles_function is None and self.achilles_args is None:
                    self.command_interface()
                else:
                    self.init_achilles_compute()
            else:
                stderr.write("WARNING: Authentication failed.")
                self.transport.loseConnection()

        elif "PROCEED" in data:
            if self.achilles_function is None and self.achilles_args is None:
                proceed = input("Press ENTER if ready to proceed:\t")
                if proceed == "":
                    print(
                        "PROCEEDING WITH DISTRIBUTING ARGUMENTS AMONGST THE CONNECTED NODES..."
                    )
                    self.sendLine(dill.dumps({"VERIFY": True}))
                else:
                    stderr.write("ALERT: Job cancelled.")
                    self.command_interface()
            else:
                self.sendLine(dill.dumps({"VERIFY": True}))

        elif "RESULT" in data and self.response_mode == "STREAM":
            if self.achilles_function is None and self.achilles_args is None:
                # If STREAM is your chosen response mode, handle results packets here.
                print(data)
            else:
                self.globals_dict["OUTPUT_QUEUE"].put(data)

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
                            self.abs_counter = self.abs_counter + 1

                c.close()

        elif "FINAL_RESULT" in data:
            if self.achilles_function is None and self.achilles_args is None:
                print("FINAL RESULT:", data["FINAL_RESULT"])
                self.command_interface()
            else:
                # print("FINAL RESULT:", data["FINAL_RESULT"])
                self.globals_dict["OUTPUT_QUEUE"].put(data["FINAL_RESULT"])
                self.transport.loseConnection()
                reactor.stop()

        elif "JOB_FINISHED" in data:
            if self.globals_dict is not None:
                self.globals_dict["OUTPUT_QUEUE"].put("JOB_FINISHED")
            else:
                self.transport.loseConnection()
                reactor.stop()

            self.transport.loseConnection()

        elif "CLUSTER_STATUS" in data:
            if False:
                print("CLUSTER STATUS:", data)
                self.command_interface()
            else:
                self.globals_dict["OUTPUT_QUEUE"].put(data)
                self.transport.loseConnection()
                reactor.crash()

        elif "KILL_NODE" in data:
            stderr.write(
                "ALERT: All achilles_nodes have been disconnected from the cluster. The achilles_server is still running and accepting connections."
            )
            reactor.crash()

        else:
            print(data)
            self.command_interface()

    def achilles_compute(
        self, achilles_config_path=None, response_mode="", chunksize=1
    ):
        if __name__ != "__main__":
            import achilles

            achilles_function_path = (
                abspath(dirname(achilles.__file__)) + "\\lineReceiver\\"
            )
            # print(achilles_function_path)
            path.append(achilles_function_path)
        else:
            achilles_function_path = abspath(dirname(__file__))
            # print(achilles_function_path)
            path.append(achilles_function_path)

        if self.achilles_function is None and self.achilles_args is None:
            from achilles.lineReceiver.achilles_function import (
                achilles_function,
                achilles_args,
                achilles_callback,
                achilles_reducer,
            )

            achilles_config_path = f"{achilles_function_path}\\{achilles_config_path}"
            with open(achilles_config_path, "r") as f:
                achilles_config = yaml.load(f, Loader=yaml.Loader)
                try:
                    args_path = (
                        f"{achilles_function_path}\\{achilles_config['ARGS_PATH']}"
                    )
                except KeyError:
                    args_path = None
                try:
                    achilles_args = achilles_config["ARGS"]
                except KeyError:
                    achilles_args = achilles_args
                modules = achilles_config["MODULES"]
                group = achilles_config["GROUP"]

        else:
            achilles_function = self.achilles_function
            achilles_args = self.achilles_args
            achilles_callback = self.achilles_callback
            achilles_reducer = self.achilles_reducer
            args_path = None
            modules = None
            group = None

        self.response_mode = response_mode

        packet = dill.dumps(
            {
                "FUNC": achilles_function,
                "ARGS": achilles_args,
                "ARGS_PATH": args_path,
                "MODULES": modules,
                "CALLBACK": achilles_callback,
                "REDUCER": achilles_reducer,
                "GROUP": group,
                "RESPONSE_MODE": response_mode,
                "CHUNKSIZE": chunksize,
            }
        )
        self.sendLine(packet)

    def get_cluster_status(self):
        packet = dill.dumps({"GET_CLUSTER_STATUS": "GET_CLUSTER_STATUS"})
        self.sendLine(packet)
        print("ALERT: Requested cluster status.")

    def kill_cluster(self):
        if self.command_verified is True:
            packet = dill.dumps({"KILL_CLUSTER": "KILL_CLUSTER"})
            self.sendLine(packet)
        else:
            confirm_kill_cluster = input(
                "WARNING: Are you absolutely sure that you want to kill the cluster? Enter YES to proceed:\t"
            )
            if confirm_kill_cluster == "YES":
                packet = dill.dumps({"KILL_CLUSTER": "KILL_CLUSTER"})
                self.sendLine(packet)
            else:
                stderr.write("ALERT: kill_cluster aborted.\n")
                self.command_interface()

    def command_interface(self):
        command = input("Achilles cluster is ready to accept commands:\t")
        if command == "achilles_compute":
            self.init_achilles_compute()
        elif command == "cluster_status":
            self.get_cluster_status()
        elif command == "kill_cluster":
            self.kill_cluster()
        elif command == "help":
            print("\n-------\nCommands:")
            print("achilles_compute, cluster_status, kill_cluster, help\n-------\n")
            self.command_interface()
        else:
            stderr.write(
                "Sorry, that command is not recognized. Type 'help' for a list of commands.\n"
            )
            self.command_interface()

    def init_achilles_compute(self):
        if self.achilles_function is None and self.achilles_args is None:
            achilles_config_path = input(
                "Enter path to achilles_config.yaml to begin job:\t"
            )
            self.response_mode = input(
                f"Enter desired response mode (OBJECT, SQLITE, or STREAM):\t"
            )
        else:
            achilles_config_path = None
        if self.response_mode in ["OBJECT", "SQLITE", "STREAM"]:
            self.achilles_compute(
                achilles_config_path=achilles_config_path,
                response_mode=self.response_mode,
                chunksize=self.chunksize,
            )
        else:
            stderr.write(
                "Sorry, that response mode is not recognized. Please choose OBJECT, SQLITE or STREAM.\n"
            )
            self.init_achilles_compute()
