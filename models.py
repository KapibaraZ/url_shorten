from main import db
from datetime import datetime


class Shortcodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortcode = db.Column(db.String(140), unique=True)
    created = db.Column(db.DateTime, default=datetime.now().isoformat())
    last_redirect = db.Column(db.DateTime, default=datetime.now().isoformat())
    redirect_count = db.Column(db.Integer, default=0)

