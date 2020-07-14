import os
basedir = os.path.abspath(os.path.dirname(__file__))

try:
    import ConfigParser
except:
    import configparser as ConfigParser

config = ConfigParser.ConfigParser()


def load_service_config():
    config_filename = os.path.join(os.path.dirname(__file__), 'config.ini').replace(r'\\', '/')
    config.read(config_filename)
    return config


service_config = load_service_config()

class Config(object):
    SECRET_KEY = service_config.get('app', 'SECRET_KEY')
    #
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or service_config.get('sqlalchemy', 'SQLALCHEMY_DATABASE_URI')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or service_config.get('mail', 'MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or service_config.get('mail', 'MAIL_PASSWORD')
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or service_config.get('mail', 'MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or service_config.get('mail', 'MAIL_PORT'))
    MAIL_USE_SSL_FLAG = os.environ.get('MAIL_USE_SSL') or service_config.get('mail', 'MAIL_USE_SSL')
    MAIL_USE_SSL = True if MAIL_USE_SSL_FLAG == 'true' else False