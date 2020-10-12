from datetime import datetime

from flask import jsonify, request
from werkzeug.utils import redirect

from models import Shortcodes
from utils import bad_request, url_valid, shorten
from app import app, db

# TODO healthcheck


@app.route('/shorten_url', methods=['POST'])
def shorten_url():

    if not request.json:
        return bad_request('Url must be provided in json format.', 401)

    if 'url' not in request.json:
        return bad_request('Url parameter not found.', 401)

    url = request.json['url']
    # For redirection purposes, we want to append http at some point.
    if url[:4] != 'http':
        url = 'http://' + url

    if not url_valid(url):
        return bad_request('Provided url is not valid.', 401)

    if request.method == 'POST':
        json = request.json
        url = json['url']
        shortcode = json['shortcode'] if 'shortcode' in json else shorten(url)

        sc = Shortcodes(
            url=url,
            shortcode=shortcode
        )
        # TODO try except for db
        db.session.add(sc)
        db.session.commit()
    return jsonify({'shortened_url': 'ahahahah'}), 201


@app.route('/<shortcode>', methods=['GET'])
def shorten_url_get(shortcode):
    sc = Shortcodes.query.filter(Shortcodes.shortcode == shortcode).first()
    if not sc:
        return bad_request("Shortcode not found", 404)
    sc.redirect_count += 1
    sc.last_redirect = datetime.now()
    db.session.commit()
    return redirect(sc.url)


@app.route('/<shortcode>/stats', methods=['GET'])
def get_stats(shortcode):
    sc = Shortcodes.query.filter(Shortcodes.shortcode == shortcode).first()

    if sc is None:
        return bad_request("Shortcode not found", 404)

    return jsonify({"created": sc.created,
                    "lastRedirect": sc.last_redirect,
                    "redirectCount": sc.redirect_count}), 200


if __name__ == '__main__':
    app.run(debug=True)
