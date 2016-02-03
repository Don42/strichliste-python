from flask_restful import Api

from endpoints.setting import Setting
from endpoints.transaction import UserTransaction, Transaction
from endpoints.user import UserList, User, UserTransactionList
from strichliste.flask import create_app
from database import db


def main():
    app = create_app('./strichliste.conf')
    api = Api(app)

    api.add_resource(Setting, '/settings')
    api.add_resource(UserList, '/user')
    api.add_resource(User, '/user/<int:user_id>')
    api.add_resource(UserTransactionList, '/user/<int:user_id>/transaction')
    api.add_resource(UserTransaction, '/user/<int:user_id>/transaction/<int:transaction_id>')
    api.add_resource(Transaction, '/transaction')

    db.create_all(app=app)
    app.run(port=8080, debug=True)

if __name__ == '__main__':
    main()
