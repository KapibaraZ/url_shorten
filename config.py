import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Configuration(object):
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # TODO sqlite3
    SQLALCHEMY_DATABASE_URI = 'mysql+myqslconnector://root:1@localhost/dbtest1'
