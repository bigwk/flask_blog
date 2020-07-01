import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = '1f24d781a530c1893803b5de9d23a8f8324de2d4ff58b65ff5f3534d214ae949'

    #
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://wangkui:@localhost/flask_blog'
