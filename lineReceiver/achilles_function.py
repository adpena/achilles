#!/usr/bin/env python3

import ast

from requests import get
from html2text import html2text


def achilles_args(args_path):
    args_counter = -1
    with open(args_path, 'r') as args:
        for arg in args:
            args_counter = args_counter + 1
            yield args_counter, ast.literal_eval(arg)


def achilles_function(arg):
    return arg ** 2


def achilles_function2(arg):
    r = get(
        arg,
        headers={"User-Agent": "Mozilla/5.0", "referrer": "https://l.facebook.com/"},
    )
    raw_html = r.text
    markdown_text = html2text(raw_html)

    return markdown_text
