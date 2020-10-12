from datetime import datetime

import sqlalchemy
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

    if request.method == 'POST':
        json = request.json
        url = json['url']
        if not url_valid(url):
            return bad_request('Provided url is not valid.', 400)

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
        except sqlalchemy.exc.IntegrityError:
            return bad_request('url already exists', 400)
        except Exception as err:
            return jsonify({'error': 'Service is temporarily unavailable'}), 500
        else:
            return jsonify({'shortened_url': shortcode}), 201


@app.route('/<shortcode>', methods=['GET'])
def shorten_url_get(shortcode):
    if not short_code_valid(shortcode):
        return bad_request('Shortcode invalide', 412)
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
    if not short_code_valid(shortcode):
        return bad_request('Shortcode invalide', 412)
    try:
        sc = Shortcodes.query.filter(Shortcodes.shortcode == shortcode).first()
    except Exception:
        return jsonify({'error': 'Service is temporarily unavailable'}), 500
    else:
        if sc is None:
            return bad_request("Shortcode not found", 404)

        return jsonify({"created": sc.created,
                        "lastRedirect": sc.last_redirect,
                        "redirectCount": sc.redirect_count}), 200
