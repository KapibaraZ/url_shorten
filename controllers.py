from datetime import datetime

from flask import jsonify, request
from werkzeug.utils import redirect

from models import Shortcodes
from utils import bad_request, url_valid, shorten, short_code_valid
from app import app, db


@app.route('/')
def healthcheck():
    try:
        Shortcodes.query.first()
    except Exception:
        return bad_request('Oooo, shit, man!', 500)
    else:
        return jsonify({'response': 'OK'}), 200


@app.route('/shorten_url', methods=['POST'])
def shorten_url():

    if not request.json:
        return bad_request('Url must be provided in json format.', 400)

    if 'url' not in request.json:
        return bad_request('Url parameter not found.', 400)

    url = request.json['url']

    if url[:4] != 'http':
        url = 'http://' + url

    if not url_valid(url):
        return bad_request('Provided url is not valid.', 400)

    if request.method == 'POST':
        json = request.json
        url = json['url']
        if 'shortcode' in json:
            try:
                sc = Shortcodes.query.filter(
                    Shortcodes.shortcode == json['shortcode']
                ).first()
                if sc:
                    return bad_request('Shortcode already in used', 409)
            except Exception:
                return jsonify(
                    {'error': 'Service is temporarily unavailable'}), 500
            else:
                shortcode = json['shortcode']
        else:
            shortcode = shorten(url)
        if not short_code_valid(shortcode):
            return bad_request('Shortcode invalide', 412)

        sc = Shortcodes(url=url, shortcode=shortcode)
        try:
            db.session.add(sc)
            db.session.commit()
        #     better add detail exception
        except Exception:
            return jsonify({'error': 'Service is temporarily unavailable'}), 500
        else:
            return jsonify({'shortened_url': shortcode}), 201


@app.route('/<shortcode>', methods=['GET'])
def shorten_url_get(shortcode):
    try:
        sc = Shortcodes.query.filter(Shortcodes.shortcode == shortcode).first()
        if not sc:
            return bad_request("Shortcode not found", 404)
        sc.redirect_count += 1
        sc.last_redirect = datetime.now()
        db.session.commit()
        #     better add detail exception
    except Exception:
        return jsonify({'error': 'Service is temporarily unavailable'}), 500
    else:
        return redirect(sc.url)


@app.route('/<shortcode>/stats', methods=['GET'])
def get_stats(shortcode):
    try:
        sc = Shortcodes.query.filter(Shortcodes.shortcode == shortcode).first()
        #     better add detail exception
    except Exception:
        return jsonify({'error': 'Service is temporarily unavailable'}), 500
    else:
        if sc is None:
            return bad_request("Shortcode not found", 404)

        return jsonify({"created": sc.created,
                        "lastRedirect": sc.last_redirect,
                        "redirectCount": sc.redirect_count}), 200
