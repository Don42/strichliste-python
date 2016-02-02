import time
import logging
import logging.handlers

from configparser import ConfigParser
from flask import Flask
from database import db

from strichliste import error_handlers

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class Config():
    def __init__(self, config_path):
        config = ConfigParser()
        config.read(config_path)
        self.upper_account_boundary = config.getint('limits', 'account_upper', fallback=100) * 100
        self.lower_account_boundary = config.getint('limits', 'account_lower', fallback=-10) * 100
        self.upper_transaction_boundary = config.getint('limits', 'transaction_upper', fallback=9999) * 100
        self.lower_transaction_boundary = config.getint('limits', 'transaction_lower', fallback=-9999) * 100
        self.db_path = config.get('base', 'db_path', fallback='/tmp/strichliste.db')
        if ':///' not in self.db_path:
            self.db_path = 'sqlite:///' + self.db_path
        self.log_path = config.get('logging', 'path', fallback='/tmp/strichliste.log')


def initialize_logger(app):
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)

    logging.Formatter.converter = time.gmtime
    formatter = logging.Formatter(LOGGING_FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    file_handler = logging.handlers.RotatingFileHandler(app.config['APP_LOGFILE'])
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(stream_handler)
    app.logger.addHandler(file_handler)

    app.logger.debug("App created")


def create_app(config_path):
    app = Flask(__name__)
    config = Config(config_path)
    app.config['app_config'] = config
    app.config['SQLALCHEMY_DATABASE_URI'] = config.db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['APP_LOGFILE'] = config.log_path
    db.init_app(app)

    initialize_logger(app)

    app.errorhandler(404)(error_handlers.page_not_found)
    return app

