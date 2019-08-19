from achilles.lineReceiver.achilles_main import map, imap, imap_unordered, setupGlobals


def achilles_args():
    import ast

    args_counter = 0
    with open(
        "C:\\Users\\Shadow\\Documents\\GitHub\\achilles\\examples\\square_nums\\achilles_args.txt",
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

    # Non-blocking, based on multiprocessing.Pool.imap_unordered().
    for result in imap_unordered(
        achilles_function,
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        achilles_callback,
        globals_dict=globals_dict,
        chunk_size=5,
    ):
        print(result)

    # Non-blocking, based on multiprocessing.Pool.imap().
    for result in imap(
        achilles_function,
        achilles_args,
        achilles_callback,
        globals_dict=globals_dict,
        chunk_size=25,
    ):
        print(result)

    # Blocking, based on multiprocessing.Pool.map().
    results = map(
        achilles_function,
        achilles_args,
        achilles_callback,
        globals_dict=globals_dict,
        chunk_size=1,
    )
    print("FINAL RESULT:", results)
    for result in results:
        print(result)
