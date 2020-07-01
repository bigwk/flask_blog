import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'your key'

    #
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'your database'
