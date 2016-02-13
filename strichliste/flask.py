import logging
import logging.handlers
import time

from strichliste.database import db
from flask import Flask
from strichliste import error_handlers
from strichliste.config import Config

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


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
    app.config['SQLALCHEMY_DATABASE_URI'] = config.db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['APP_LOGFILE'] = config.log_path
    db.init_app(app)

    initialize_logger(app)

    app.errorhandler(404)(error_handlers.page_not_found)
    return app

