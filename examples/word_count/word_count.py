from achilles.lineReceiver.cythonized.achilles_main import imap_unordered


def achilles_function(sentence):
    import re

    word_count = {}
    words_in_sentence = re.findall(r"\w+", sentence)
    for word in words_in_sentence:
        if word not in word_count:
            word_count[word] = 1
        else:
            word_count[word] += 1

    return word_count


def achilles_args():
    import json

    with open(
        "C:\\Users\\Shadow\\Documents\\GitHub\\achilles\\examples\\word_count\\review.json",
        "r",
        encoding="utf-8",
        newline="",
    ) as reviews:
        for review in reviews:
            review_json = json.loads(review)
            review_text = review_json["text"]
            review_text = review_text.replace("\r", "")
            review_text = review_text.replace("\n", "")
            sentences_in_review = review_text.split(".")
            for sentence in sentences_in_review:
                yield sentence


def achilles_reducer(list_of_results):
    summary_word_count = {}
    for result in list_of_results:
        for k, v in result.items():
            if k in summary_word_count:
                summary_word_count[k] += v
            else:
                summary_word_count[k] = v
    return summary_word_count


if __name__ == "__main__":
    import time

    start_time = time.time()
    print(start_time)
    word_count_final = {}

    for result in imap_unordered(
        achilles_function, achilles_args, reducer=achilles_reducer, chunksize=75
    ):
        for k, v in result["RESULT"].items():
            if k in word_count_final:
                word_count_final[k] += v
            else:
                word_count_final[k] = v
        # print(result)
        print(word_count_final)

    print(word_count_final)
    print("--- %s seconds ---" % (time.time() - start_time))
