from flask_restful import Api

import endpoints.v1 as v1
import endpoints.v2 as v2
from database import db
from endpoints.v1.setting import Setting
from strichliste.flask import create_app


def main():
    app = create_app('./strichliste.conf')
    api = Api(app)

    api.add_resource(Setting, '/settings')
    api.add_resource(v1.UserList, '/user')
    api.add_resource(v1.User, '/user/<int:user_id>')
    api.add_resource(v1.UserTransactionList, '/user/<int:user_id>/transaction')
    api.add_resource(v1.UserTransaction, '/user/<int:user_id>/transaction/<int:transaction_id>')
    api.add_resource(v1.Transaction, '/transaction')

    api.add_resource(v2.UserListV2, '/v2/user')
    api.add_resource(v2.UserV2, '/v2/user/<int:user_id>')
    api.add_resource(v2.UserTransactionListV2, '/v2/user/<int:user_id>/transaction')
    api.add_resource(v2.UserTransactionV2, '/v2/user/<int:user_id>/transaction/<int:transaction_id>')
    api.add_resource(v2.TransactionV2, '/v2/transaction')

    db.create_all(app=app)
    app.run(port=8080, debug=True)

if __name__ == '__main__':
    main()
