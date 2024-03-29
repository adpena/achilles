#!/usr/bin/env python3

from achilles.lineReceiver.achilles_controller import AchillesController

from dotenv import load_dotenv
from os import getenv
from os.path import abspath, dirname, join
import getpass
import time

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
import multiprocess


def runAchillesController(
    achilles_function=None,
    achilles_args=None,
    achilles_callback=None,
    achilles_reducer=None,
    response_mode="OBJECT",
    host=None,
    port=None,
    username=None,
    secret_key=None,
    globals_dict=None,
    chunksize=1,
    command=None,
    command_verified=False,
    TCP4ClientEndpoint=TCP4ClientEndpoint,
    reactor=reactor,
    connectProtocol=connectProtocol,
    AchillesController=AchillesController,
    abspath=abspath,
    dirname=dirname,
):
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
            else:
                basedir = abspath(dirname(__file__))
                dotenv_path = join(basedir, ".env")
            load_dotenv(dotenv_path, override=True)
            port = int(getenv("PORT"))
            host = getenv("HOST")
            username = getenv("USERNAME")
            secret_key = getenv("SECRET_KEY")

        except BaseException as e:
            try:
                host, port, username, secret_key = genConfig()
            except NameError:
                host = host
                port = port
                username = username
                secret_key = secret_key
                # print(f'Passed host {host}, port {port}, username {username}, secret_key {secret_key} assignment.')

    endpoint = TCP4ClientEndpoint(reactor, host, port)
    d = connectProtocol(
        endpoint,
        AchillesController(
            host,
            port,
            username,
            secret_key,
            achilles_function,
            achilles_args,
            achilles_callback,
            achilles_reducer,
            response_mode,
            globals_dict,
            chunksize,
            command,
            command_verified,
        ),
    )

    reactor.run()


def genConfig(host=None, port=None, username=None, secret_key=None):
    if __name__ != "__main__":
        import achilles

        dotenv_path = abspath(dirname(achilles.__file__)) + "\\lineReceiver\\.env"
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
        port = int(input("Enter HOST port to listen on:\t"))
        username = input("Enter USERNAME to require for authentication:\t")
        secret_key = getpass.getpass(
            "Enter SECRET_KEY to require for authentication:\t"
        )
    with open(dotenv_path, "w") as config_file:
        config_file.writelines(f"HOST={host}\n")
        config_file.writelines(f"PORT={port}\n")
        config_file.writelines(f"USERNAME='{username}'\n")
        config_file.writelines(f"SECRET_KEY='{secret_key}'\n")
        config_file.close()
        print(
            f"Successfully generated .env configuration file at {dotenv_path}. Use achilles_controller.genConfig() to overwrite."
        )
    return host, port, username, secret_key


def imap_unordered(
    func,
    args,
    callback=None,
    reducer=None,
    response_mode="STREAM",
    host=None,
    port=None,
    username=None,
    secret_key=None,
    chunksize=1,
    globals_dict=None,
    runAchillesController=runAchillesController,
    abspath=abspath,
    dirname=dirname,
    multiprocess=multiprocess,
):

    if globals_dict is None:

        globals_dict = setupGlobals()

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
            else:
                basedir = abspath(dirname(__file__))
                dotenv_path = join(basedir, ".env")
            load_dotenv(dotenv_path, override=True)
            port = int(getenv("PORT"))
            host = getenv("HOST")
            username = getenv("USERNAME")
            secret_key = getenv("SECRET_KEY")
        except (KeyError, NameError):
            host = host
            port = port
            username = username
            secret_key = secret_key

    a = multiprocess.Process(
        target=runAchillesController,
        args=(
            func,
            args,
            callback,
            reducer,
            response_mode,
            host,
            port,
            username,
            secret_key,
            globals_dict,
            chunksize,
        ),
    )

    a.start()
    while True:
        result = globals_dict["OUTPUT_QUEUE"].get()
        if result != "JOB_FINISHED":
            yield result
        else:
            break

    a.terminate()


def imap(
    func,
    args,
    callback=None,
    response_mode="STREAM",
    host=None,
    port=None,
    username=None,
    secret_key=None,
    chunksize=1,
    globals_dict=None,
    runAchillesController=runAchillesController,
    abspath=abspath,
    dirname=dirname,
    multiprocess=multiprocess,
):

    if globals_dict is None:
        globals_dict = setupGlobals()

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
            else:
                basedir = abspath(dirname(__file__))
                dotenv_path = join(basedir, ".env")
            load_dotenv(dotenv_path, override=True)
            port = int(getenv("PORT"))
            host = getenv("HOST")
            username = getenv("USERNAME")
            secret_key = getenv("SECRET_KEY")
        except (KeyError, NameError):
            host = host
            port = port
            username = username
            secret_key = secret_key

    reducer = None

    a = multiprocess.Process(
        target=runAchillesController,
        args=(
            func,
            args,
            callback,
            reducer,
            response_mode,
            host,
            port,
            username,
            secret_key,
            globals_dict,
            chunksize,
        ),
    )

    a.start()
    sent_first_arg = False
    expected_args_counter = 0
    result_buffer = []
    try:
        test_arg = next(args())
        test_arg_type = type(test_arg)
    except TypeError:
        test_arg = next(iter(args))
        test_arg_type = type(test_arg)
    while True:
        result = globals_dict["OUTPUT_QUEUE"].get()
        if result != "JOB_FINISHED":
            if test_arg_type is not list:
                if sent_first_arg is False:
                    if result["ARGS_COUNTER"] == 0:
                        sent_first_arg = True
                        expected_args_counter = expected_args_counter + len(
                            result["RESULT"]
                        )
                        yield result
                    else:
                        # print("NOT YET:", result)
                        result_buffer.append(result)
                        continue
                else:
                    if result["ARGS_COUNTER"] == expected_args_counter:
                        expected_args_counter = expected_args_counter + len(
                            result["RESULT"]
                        )
                        yield result
                    else:
                        returned = getResult(result_buffer, expected_args_counter)
                        result_buffer.append(result)
                        if (
                            returned is not None
                            and returned["ARGS_COUNTER"] == expected_args_counter
                        ):
                            expected_args_counter = expected_args_counter + len(
                                result["RESULT"]
                            )
                            yield returned

                        else:
                            continue

            else:
                if sent_first_arg is False:
                    if result["ARGS_COUNTER"] == 0:
                        sent_first_arg = True
                        expected_args_counter = expected_args_counter + 1
                        yield result
                    else:
                        # print("NOT YET:", result)
                        result_buffer.append(result)
                        continue
                else:
                    if result["ARGS_COUNTER"] == expected_args_counter:
                        expected_args_counter = expected_args_counter + 1
                        yield result
                    else:
                        returned = getResult(result_buffer, expected_args_counter)
                        result_buffer.append(result)
                        if (
                            returned is not None
                            and returned["ARGS_COUNTER"] == expected_args_counter
                        ):
                            expected_args_counter = expected_args_counter + 1
                            yield returned

                        else:
                            continue

        else:
            # print(result)
            # print("Result buffer:", result_buffer)

            if len(result_buffer) >= 1:
                result_buffer = sorted(result_buffer, key=lambda k: k["ARGS_COUNTER"])
                for result in result_buffer:
                    yield result
                break
            else:
                break

    a.terminate()


def getResult(result_buffer, expected_args_counter):
    for result in result_buffer:
        if result["ARGS_COUNTER"] == expected_args_counter:
            del result_buffer[result_buffer.index(result)]
            return result
        else:
            pass


def map(
    func,
    args,
    callback=None,
    reducer=None,
    response_mode="OBJECT",
    chunksize=1,
    globals_dict=None,
    host=None,
    port=None,
    username=None,
    secret_key=None,
    runAchillesController=runAchillesController,
    abspath=abspath,
    dirname=dirname,
    multiprocess=multiprocess,
):

    if globals_dict is None:
        globals_dict = setupGlobals()

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
            else:
                basedir = abspath(dirname(__file__))
                dotenv_path = join(basedir, ".env")
            load_dotenv(dotenv_path, override=True)
            port = int(getenv("PORT"))
            host = getenv("HOST")
            username = getenv("USERNAME")
            secret_key = getenv("SECRET_KEY")
        except (KeyError, NameError):
            host = host
            port = port
            username = username
            secret_key = secret_key

    a = multiprocess.Process(
        target=runAchillesController,
        args=(
            func,
            args,
            callback,
            reducer,
            response_mode,
            host,
            port,
            username,
            secret_key,
            globals_dict,
            chunksize,
        ),
    )

    a.start()
    a.join()
    while True:
        final_result = globals_dict["OUTPUT_QUEUE"].get()
        if final_result is not None:
            # print("FINAL_RESULT:", final_result)
            a.terminate()
            return final_result
        else:
            # print(final_result)
            time.sleep(0.1)


def setupGlobals():
    multiprocess.current_process().authkey = b"176778741"

    manager = multiprocess.Manager()

    globals_dict = {"OUTPUT_QUEUE": manager.Queue()}
    return globals_dict


def killCluster(
    command="KILL_CLUSTER",
    host=None,
    port=None,
    username=None,
    secret_key=None,
    command_verified=False,
    runAchillesController=runAchillesController,
):

    if (
        host is not None
        and port is not None
        and username is not None
        and secret_key is not None
    ):
        runAchillesController(
            command=command,
            host=host,
            port=port,
            username=username,
            secret_key=secret_key,
            command_verified=command_verified,
        )
    else:
        runAchillesController(command=command, command_verified=command_verified)


def getClusterStatus(
    command="GET_CLUSTER_STATUS",
    host=None,
    port=None,
    username=None,
    secret_key=None,
    globals_dict=None,
    runAchillesController=runAchillesController,
):

    if globals_dict is None:
        globals_dict = setupGlobals()

    if (
        host is not None
        and port is not None
        and username is not None
        and secret_key is not None
    ):
        a = multiprocess.Process(
            target=runAchillesController,
            args=(
                None,
                None,
                None,
                None,
                None,
                host,
                port,
                username,
                secret_key,
                globals_dict,
                None,
                command,
            ),
        )
        a.start()

    else:
        try:
            if __name__ != "__main__":
                import achilles

                dotenv_path = (
                    abspath(dirname(achilles.__file__)) + "\\lineReceiver\\.env"
                )
            else:
                basedir = abspath(dirname(__file__))
                dotenv_path = join(basedir, ".env")
            load_dotenv(dotenv_path, override=True)
            port = int(getenv("PORT"))
            host = getenv("HOST")
            username = getenv("USERNAME")
            secret_key = getenv("SECRET_KEY")
        except (KeyError, NameError):
            host = host
            port = port
            username = username
            secret_key = secret_key

        a = multiprocess.Process(
            target=runAchillesController,
            args=(
                None,
                None,
                None,
                None,
                None,
                host,
                port,
                username,
                secret_key,
                globals_dict,
                None,
                command,
            ),
        )
        a.start()

    while True:
        cluster_status = globals_dict["OUTPUT_QUEUE"].get()
        if cluster_status is not None:
            # print("CLUSTER_STATUS", cluster_status)
            a.terminate()
            return cluster_status
        else:
            # print(cluster_status)
            time.sleep(0.1)


if __name__ == "__main__":
    runAchillesController()
