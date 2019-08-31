#!/usr/bin/env python3

# from requests import get
# from html2text import html2text


def achilles_args(args_path):
    import ast

    with open(args_path, "r") as args:
        for arg in args:
            arg = arg.strip()
            print(ast.literal_eval(arg))
            for a in ast.literal_eval(arg):
                print(a)
            yield ast.literal_eval(arg)


def achilles_function(arg):
    return arg ** 2


def achilles_callback(result):
    return result ** 2


def achilles_reducer(list_of_results):
    sum_of_results = [0]
    for result in list_of_results:
        sum_of_results[0] += result
    return sum_of_results


"""def achilles_function2(arg):
    r = get(
        arg,
        headers={"User-Agent": "Mozilla/5.0", "referrer": "https://l.facebook.com/"},
    )
    raw_html = r.text
    markdown_text = html2text(raw_html)

    return markdown_text"""
