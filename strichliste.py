import pathlib as pl

from flask import Flask
from flask_restful import Api

import database

from endpoints.setting import Setting
from endpoints.transaction import UserTransaction, Transaction
from endpoints.user import UserList, User, UserTransactionList

DB_PATH = pl.Path('strichliste.db')

if not DB_PATH.exists():
    database.create_database(DB_PATH)

session = database.get_database(DB_PATH)

app = Flask(__name__)
api = Api(app)

api.add_resource(Setting, '/settings',
                 resource_class_kwargs={'db': session})
api.add_resource(UserList, '/user',
                 resource_class_kwargs={'db': session})
api.add_resource(User, '/user/<user_id>',
                 resource_class_kwargs={'db': session})
api.add_resource(UserTransactionList,
                 '/user/<user_id>/transaction/<transaction_id>',
                 resource_class_kwargs={'db': session})
api.add_resource(UserTransaction, '/user/<user_id>/transaction',
                 resource_class_kwargs={'db': session})
api.add_resource(Transaction, '/transaction',
                 resource_class_kwargs={'db': session})


if __name__ == '__main__':
    app.run(debug=True)
