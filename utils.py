import random
import re
from base64 import b64encode
from hashlib import blake2b

from flask import jsonify

REGEX_URL = re.compile(
        r'^(?:http)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

DIGEST_SIZE = 6
shortened = {}


def url_valid(url):
    return isinstance(url, str) and re.match(REGEX_URL, url) is not None


def shorten(url):
    url_hash = blake2b(str.encode(url), digest_size=DIGEST_SIZE)

    while url_hash in shortened:
        url += str(random.randint(0, 9))
        url_hash = blake2b(str.encode(url), digest_size=DIGEST_SIZE)

    b64 = b64encode(url_hash.digest(), altchars=b'-_')
    return b64.decode('utf-8')


# TODO def bad_request(name_message, text_message, code):
def bad_request(message, code):
    response = jsonify({'message': message})
    response.status_code = code
    return response


def short_code_valid(shortcode):
    # TODO size !!!
    return (
        re.match(r'[a-zA-Z0-9_]', shortcode) and
        len(shortcode) == DIGEST_SIZE
    )
