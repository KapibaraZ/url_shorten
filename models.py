from datetime import datetime

from app import db


class Shortcodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), unique=True)
    shortcode = db.Column(db.String(6), unique=True)
    created = db.Column(db.DateTime, default=datetime.now())
    last_redirect = db.Column(db.DateTime, default=datetime.now())
    redirect_count = db.Column(db.Integer, default=0)
