from achilles.lineReceiver.achilles_main import imap


def achilles_function(arg):
    return arg ** 2


def achilles_callback(result):
    result_data = result["RESULT"]
    for i in range(len(result_data)):
        result_data[i] = result_data[i] ** 2
    return result


if __name__ == "__main__":

    for result in imap(
        achilles_function,
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        achilles_callback,
        chunk_size=1,
    ):
        print(result)
