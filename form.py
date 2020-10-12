from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class ShorterUrlsForm(FlaskForm):
    # todo CONSTRAINTS FOR ORIGINAL URL
    original = StringField('original')
    shorter_url = StringField('shorter_url')
    button = SubmitField(label="CLick here")
