from configparser import ConfigParser, NoOptionError, NoSectionError
import pathlib as pl

from flask_restful import Api

from endpoints.setting import Setting
from endpoints.transaction import UserTransaction, Transaction
from endpoints.user import UserList, User, UserTransactionList
from strichliste.flask import create_app
from database import db

DB_PATH = pl.Path('strichliste.db')


class Config():
    def __init__(self, config_path):
        config = ConfigParser()
        config.read(config_path)
        self.upper_account_boundary = config.getint('limits', 'account_upper', fallback=100) * 100
        self.lower_account_boundary = config.getint('limits', 'account_lower', fallback=-10) * 100
        self.upper_transaction_boundary = config.getint('limits', 'transaction_upper', fallback=9999) * 100
        self.lower_transaction_boundary = config.getint('limits', 'transaction_lower', fallback=-9999) * 100


def main():
    app = create_app()
    app.config['app_config'] = Config('./strichliste.ini')
    api = Api(app)

    Setting.app = app
    UserList.app = app
    UserTransactionList.app = app
    User.app = app
    UserTransaction.app = app
    Transaction.app = app

    api.add_resource(Setting, '/settings')
    api.add_resource(UserList, '/user')
    api.add_resource(User, '/user/<user_id>')
    api.add_resource(UserTransactionList, '/user/<user_id>/transaction')
    api.add_resource(UserTransaction, '/user/<user_id>/transaction/<transaction_id>')
    api.add_resource(Transaction, '/transaction')

    if not DB_PATH.exists():
        db.create_all(app=app)
    app.run(debug=True)

if __name__ == '__main__':
    main()
