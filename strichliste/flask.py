import time
import logging
import logging.handlers

from configparser import ConfigParser
from flask import Flask
from database import db

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


def initialize_logger(app):
    logging.Formatter.converter = time.gmtime
    formatter = logging.Formatter(LOGGING_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.logger.debug("App created")


def create_app(config_path):
    app = Flask(__name__)
    config = Config(config_path)
    app.config['app_config'] = config
    app.config['SQLALCHEMY_DATABASE_URI'] = config.db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    initialize_logger(app)
    return app

