from achilles.lineReceiver.achilles_main import map


def achilles_function(arg):
    return arg ** 2


def achilles_callback(result):
    return result ** 2


if __name__ == "__main__":
    results = map(
        achilles_function,
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        achilles_callback,
        chunksize=1,
    )
    print(results)
