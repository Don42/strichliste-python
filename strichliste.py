from endpoints.setting import Setting
from endpoints.transaction import UserTransaction, Transaction
from endpoints.user import UserList, User, UserTransactionList
from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

api.add_resource(Setting, '/settings')
api.add_resource(UserList, '/user')
api.add_resource(User, '/user/<user_id>')
api.add_resource(UserTransactionList, '/user/<user_id>/transaction/<transaction_id>')
api.add_resource(UserTransaction, '/user/<user_id>/transaction')
api.add_resource(Transaction, '/transaction')

if __name__ == '__main__':
    app.run(debug=True)
