from achilles.lineReceiver.achilles_main import (
    map,
    imap,
    imap_unordered,
    setupGlobals,
    killCluster,
)


def achilles_args():
    import ast

    with open(
        "C:\\Users\\Shadow\\Documents\\GitHub\\achilles\\examples\\square_nums\\achilles_args.txt",
        "r",
    ) as args:
        first_arg = args.readline()
        if type(ast.literal_eval(first_arg)) is list:
            yield ast.literal_eval(first_arg)
            for arg in args:
                yield ast.literal_eval(arg)
        else:
            yield int(first_arg)
            for arg in args:
                yield int(arg)


def achilles_function(arg):
    return arg ** 2


def achilles_callback(result):
    return result ** 2


if __name__ == "__main__":

    # streaming unordered results, based on multiprocessing.Pool.imap_unordered()
    for result in imap_unordered(
        achilles_function, achilles_args, achilles_callback, chunksize=50
    ):
        print(result)

    # streaming ordered results, based on multiprocessing.Pool.imap()
    for result in imap(
        achilles_function,
        iter([x for x in range(500)]),
        achilles_callback,
        chunksize=50,
    ):
        print(result)

    # blocking on final results, based on multiprocessing.Pool.map()
    results = map(achilles_function, achilles_args, achilles_callback, chunksize=50)
    print("FINAL RESULT:", results)

    # killCluster() presents user with CLI seeking verification of intent to kill the achilles cluster
    # killCluster(command_verified=True) proceeds without presenting user with input() interface

    # killCluster(command_verified=True)
