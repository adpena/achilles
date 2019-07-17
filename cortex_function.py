from requests import get
from html2text import html2text


def cortex_function(arg):
    return arg**2



def cortex_function2(arg):
    r = get(
        arg,
        headers={"User-Agent": "Mozilla/5.0", "referrer": "https://l.facebook.com/"},
    )
    raw_html = r.text
    markdown_text = html2text(raw_html)

    return markdown_text
