from base64 import b64encode
from flask_sqlalchemy import SQLAlchemy
from hashlib import blake2b
import datetime
import random
import re

from flask import Flask, abort, jsonify, redirect, request, render_template

from config import Configuration
from form import ShorterUrlsForm
from models import Shortcodes
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)
# CsrfProtect(app)
app.config.from_object(Configuration)
db = SQLAlchemy(app)

REGEX = re.compile(
        r'^(?:http)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

DIGEST_SIZE = 6
redirects = {}
used_codes = []
shortened = {"url": "https://www.energyworx.com/", "shortcode": "ewx123"}


def url_valid(url):
    """Validates a url by parsing it with a regular expression.

    Parameters:
    url - string representing a url to be validated.

    Return values:
    Boolean, indicating the validity of the url.
    """
    return re.match(REGEX, url) is not None


def shorten(url):
    """Shortens a url by generating a 9 byte hash, and then
    converting it to a 12 character long base 64 url friendly string.

    Parameters:
    url - the url to be shortened.

    Return values:
    String, the unique shortened url, acting as a key for the entered long url.
    """
    url_hash = blake2b(str.encode(url), digest_size=DIGEST_SIZE)

    while url_hash in shortened:
        url += str(random.randint(0, 9))
        url_hash = blake2b(str.encode(url), digest_size=DIGEST_SIZE)

    b64 = b64encode(url_hash.digest(), altchars=b'-_')
    return b64.decode('utf-8')


def bad_request(message, code):
    """Takes a supplied message and attaches it to a HttpResponse with code 400.

    Parameters:
    message - string containing the error message.

    Return values:
    An object with a message string and a status_code set to 400.
    """
    response = jsonify({'message': message})
    response.status_code = code
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        json = request.json
        from pprint import pprint
        pprint(json)
        print(json['url'])
        if json['shortcode']:
            url = json['shortcode']
        else:
            url = shorten(json['url'])
        sc = Shortcodes.query.filter(Shortcodes.shortcode == url).first
        if sc is not None:
            sc.redirect_count += 1
            sc.last_redirect = datetime.datetime.now().isoformat()
        else:
            shortcode = Shortcodes(shortcode=url)
            db.session.add(shortcode)
        db.session.commit()
        print(url)
    return jsonify({"shortcode": 'adhsfj'}), 201
#     form = ShorterUrlsForm(request.form)
#
#     if form.validate_on_submit():
#
#         original_url = form.original.data
#         form.shorter_url.data = shorten(original_url)
#     return render_template(
#         "index.html",
#         form=form,
# )


@app.route('/shorten_url', methods=['GET', 'POST'])
def shorten_url():

    # if not request.json:
    #     return bad_request('Url must be provided in json format.')
    #
    # if 'url' not in request.json:
    #     return bad_request('Url parameter not found.')
    #
    # url = request.json['url']
    # # For redirection purposes, we want to append http at some point.
    # if url[:4] != 'http':
    #     url = 'http://' + url
    #
    # if not url_valid(url):
    #     return bad_request('Provided url is not valid.')
    #
    # shortened_url = shorten(url)
    # shortened[shortened_url] = url

    return jsonify({'shortened_url': 'ahahahah'}), 201


@app.route('/<shortcode>', methods=['GET'])
def shorten_url_get(shortcode):
    if not Shortcodes.query.filter(Shortcodes.shortcode == shortcode):
        return bad_request("Shortcode not found", 404)
    form = ShorterUrlsForm(request.form)

    if form.validate_on_submit():

        original_url = form.original.data
        form.shorter_url.data = shorten(original_url)
        return jsonify({'url': original_url}), 302


@app.route('/<shortcode>/stats', methods=['GET'])
def get_stats(shortcode):
    """GET endpoint that takes an alias (shortened url) and redirects if successfull.
    Otherwise returns a bad request.

    Arguments:
    alias, the string representing a shortened url.

    Return values:
    A Flask redirect, with code 302.
    """
    sc = Shortcodes.query.filter(Shortcodes.shortcode == shortcode).first()
    if sc is not None:
        return bad_request("Shortcode not found", 404)
    
    return jsonify({"created": sc.created,
                    "lastRedirect": sc.last_redirect,
                    "redirectCount": sc.redirect_count}), 302


if __name__ == '__main__':
    app.run(debug=True)
