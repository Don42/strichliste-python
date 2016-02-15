from flask_restful import Api

import strichliste.views
from strichliste.database import db
from strichliste.flask import create_app
from strichliste.outputs import output_json


def main():
    app = create_app('./strichliste.conf')
    api = Api(app)

    api.add_resource(strichliste.views.Settings, '/settings')
    api.add_resource(strichliste.views.Metrics, '/metrics')
    api.add_resource(strichliste.views.UserList, '/user')
    api.add_resource(strichliste.views.User, '/user/<int:user_id>')
    api.add_resource(strichliste.views.UserTransactionList, '/user/<int:user_id>/transaction')
    api.add_resource(strichliste.views.UserTransaction, '/user/<int:user_id>/transaction/<int:transaction_id>')
    api.add_resource(strichliste.views.Transaction, '/transaction')
    api.representation('application/json')(output_json)

    db.create_all(app=app)
    app.run(port=8080, debug=True)

if __name__ == '__main__':
    main()
