#!/usr/bin/env python3

from achilles.lineReceiver.achilles_controller import AchillesController

from dotenv import load_dotenv
from os import getenv
from os.path import abspath, dirname, join
import getpass

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor
import multiprocess


def runAchillesController(
    achilles_function=None,
    achilles_args=None,
    achilles_callback=None,
    response_mode="OBJECT",
    host=None,
    port=None,
    username=None,
    secret_key=None,
    globals_dict=None,
    chunk_size=1,
    command=None,
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
            response_mode,
            globals_dict,
            chunk_size,
            command,
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


def readInputQueue(input_queue, output_queue, callback=None):
    while input_queue:
        result = input_queue.get()
        if result != "JOB_FINISHED":
            if callback is not None:
                # print("RESULT", result)
                callback_result = callback(result)
                # print("CR", callback_result)
                output_queue.put(callback_result)
            else:
                # print(result)
                output_queue.put(result)
        else:
            output_queue.put(result)
            break


def imap_unordered(
    achilles_function,
    achilles_args,
    achilles_callback=None,
    response_mode="STREAM",
    host=None,
    port=None,
    username=None,
    secret_key=None,
    chunk_size=1,
    globals_dict=None,
    runAchillesController=runAchillesController,
    abspath=abspath,
    dirname=dirname,
    multiprocess=multiprocess,
    readInputQueue=readInputQueue,
):

    if globals_dict is None:
        manager = multiprocess.Manager()

        globals_dict = {
            "FINAL_RESULT": None,
            "INPUT_QUEUE": manager.Queue(),
            "OUTPUT_QUEUE": manager.Queue(),
        }
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

    p = multiprocess.Process(
        target=readInputQueue,
        args=(
            globals_dict["INPUT_QUEUE"],
            globals_dict["OUTPUT_QUEUE"],
            achilles_callback,
        ),
    )
    p.start()
    # print('Queues started, readInputQueue initiated.')
    a = multiprocess.Process(
        target=runAchillesController,
        args=(
            achilles_function,
            achilles_args,
            achilles_callback,
            response_mode,
            host,
            port,
            username,
            secret_key,
            globals_dict,
            chunk_size,
        ),
    )

    a.start()
    while globals_dict["OUTPUT_QUEUE"].empty():
        result = globals_dict["OUTPUT_QUEUE"].get()
        if result != "JOB_FINISHED":
            yield result
        else:
            break

    p.join()
    a.terminate()


def imap(
    achilles_function,
    achilles_args,
    achilles_callback=None,
    response_mode="STREAM",
    host=None,
    port=None,
    username=None,
    secret_key=None,
    chunk_size=1,
    globals_dict=None,
    runAchillesController=runAchillesController,
    abspath=abspath,
    dirname=dirname,
    multiprocess=multiprocess,
    readInputQueue=readInputQueue,
):

    if globals_dict is None:
        manager = multiprocess.Manager()

        globals_dict = {
            "FINAL_RESULT": None,
            "INPUT_QUEUE": manager.Queue(),
            "OUTPUT_QUEUE": manager.Queue(),
        }
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

    p = multiprocess.Process(
        target=readInputQueue,
        args=(
            globals_dict["INPUT_QUEUE"],
            globals_dict["OUTPUT_QUEUE"],
            achilles_callback,
        ),
    )
    p.start()
    # print('Queues started, readInputQueue initiated.')
    a = multiprocess.Process(
        target=runAchillesController,
        args=(
            achilles_function,
            achilles_args,
            achilles_callback,
            response_mode,
            host,
            port,
            username,
            secret_key,
            globals_dict,
            chunk_size,
        ),
    )

    a.start()
    sent_first_arg = False
    expected_args_counter = 0
    result_buffer = []
    try:
        test_arg_counter, test_arg = next(achilles_args())
        test_arg_type = type(test_arg)
    except TypeError:
        test_arg = next(iter(achilles_args))
        test_arg_type = type(test_arg)
    while True:
        result = globals_dict["OUTPUT_QUEUE"].get()
        # print(result)
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

    p.join()
    a.terminate()


def getResult(result_buffer, expected_args_counter):
    for result in result_buffer:
        if result["ARGS_COUNTER"] == expected_args_counter:
            del result_buffer[result_buffer.index(result)]
            return result
        else:
            pass


def map(
    achilles_function,
    achilles_args,
    achilles_callback=None,
    response_mode="OBJECT",
    chunk_size=1,
    globals_dict=None,
    host=None,
    port=None,
    username=None,
    secret_key=None,
    runAchillesController=runAchillesController,
    abspath=abspath,
    dirname=dirname,
    multiprocess=multiprocess,
    readInputQueue=readInputQueue,
):

    if globals_dict is None:
        manager = multiprocess.Manager()

        globals_dict = {
            "FINAL_RESULT": None,
            "INPUT_QUEUE": manager.Queue(),
            "OUTPUT_QUEUE": manager.Queue(),
        }
    if (
        host is not None
        and port is not None
        and username is not None
        and secret_key is not None
    ):
        runAchillesController(
            achilles_function=achilles_function,
            achilles_args=achilles_args,
            achilles_callback=achilles_callback,
            response_mode=response_mode,
            globals_dict=globals_dict,
            chunk_size=chunk_size,
            host=host,
            port=port,
            username=username,
            secret_key=secret_key,
        )
    else:
        runAchillesController(
            achilles_function=achilles_function,
            achilles_args=achilles_args,
            achilles_callback=achilles_callback,
            response_mode=response_mode,
            globals_dict=globals_dict,
            chunk_size=chunk_size,
        )

    return globals_dict["FINAL_RESULT"]


def setupGlobals():
    manager = multiprocess.Manager()

    globals_dict = {
        "FINAL_RESULT": None,
        "INPUT_QUEUE": manager.Queue(),
        "OUTPUT_QUEUE": manager.Queue(),
    }
    return globals_dict


def killCluster(
    command="KILL_CLUSTER",
    host=None,
    port=None,
    username=None,
    secret_key=None,
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
        )
    else:
        runAchillesController(command=command)


def achilles_args():
    import ast

    args_counter = 0
    with open(
        "C:\\Users\\Shadow\\Documents\\GitHub\\achilles\\achilles\\lineReceiver\\achilles_args.txt",
        "r",
    ) as args:
        first_arg = args.readline()
        if type(ast.literal_eval(first_arg)) is list:
            yield args_counter, ast.literal_eval(first_arg)
            args_counter = args_counter + 1
            for arg in args:
                yield args_counter, ast.literal_eval(arg)
                args_counter = args_counter + 1
        else:
            yield args_counter, int(first_arg)
            args_counter = args_counter + 1
            for arg in args:
                yield args_counter, int(arg)
                args_counter = args_counter + 1


def achilles_function(arg):
    return arg ** 2


def achilles_callback(result):
    result_data = result["RESULT"]
    for i in range(len(result_data)):
        result_data[i] = result_data[i] ** 2
    return result


if __name__ == "__main__":

    globals_dict = setupGlobals()

    # Non-blocking map function imap_unordered().
    for result in imap_unordered(
        achilles_function,
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        achilles_callback,
        globals_dict=globals_dict,
        chunk_size=25,
    ):
        print(result)

    # Non-blocking map function imap().
    for result in imap(
        achilles_function,
        [x for x in range(1000)],
        achilles_callback,
        globals_dict=globals_dict,
        chunk_size=25,
    ):
        print(result)

    # Blocking map function using map().
    results = map(
        achilles_function,
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        achilles_callback,
        globals_dict=globals_dict,
        chunk_size=1,
    )
    print("FINAL RESULT:", results)
    for result in results:
        print(result)
