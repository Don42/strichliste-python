import numbers
from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

user_parser = reqparse.RequestParser()
user_parser.add_argument('name')
user_parser.add_argument('mailAddress')

transaction_parser = reqparse.RequestParser()
user_parser.add_argument('value')

list_parser = reqparse.RequestParser()
user_parser.add_argument('offset')
user_parser.add_argument('limit')


class Setting(Resource):

    def get(self):
        return {'boundaries': {'upper': 42, 'lower': -23}}


class UserList(Resource):

    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        return {'overallCount': 0, 'limit': limit, 'offset': offset, 'entries': []}

    def post(self):
        args = user_parser.parse_args()
        name = args.get('name')
        mail_address = args.get('mailAddress')
        if name is None or mail_address is None:
            return create_error(400, "name missing")

        return {'id': 1, 'name': name, 'mailAddress': mail_address,
                'balance': 0, 'lastTransaction': None}


class User(Resource):

    def get(self, user_id):
        return create_error(404, "user {} not found".format(user_id))


class UserTransactionList(Resource):

    def get(self, user_id):
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        return create_error(404, "user {} not found".format(user_id))

    def post(self, user_id):
        args = user_parser.parse_args()
        if not {'value'}.issubset():
            return create_error(400, "value missing")
        value = args['value']
        if not isinstance(value, numbers.Number):
            return create_error(400, "not a number: {}".format(value))
        if value == 0:
            return create_error(400, "value must not be zero")
        return create_error(404, "user {} not found".format(user_id))


class UserTransaction(Resource):

    def get(self, user_id, transaction_id):
        return create_error(404, "user {} not found".format(user_id))


def create_error(code: int, msg: str):
    return {'message': msg}, code


class Transaction(Resource):

    def get(self):
        return {'overallCount': 0, 'limit': None, 'offset': None, 'entries': []}

api.add_resource(Setting, '/settings')
api.add_resource(UserList, '/user')
api.add_resource(User, '/user/<user_id>')
api.add_resource(UserTransactionList, '/user/<user_id>/transaction/<transaction_id>')
api.add_resource(UserTransaction, '/user/<user_id>/transaction')
api.add_resource(Transaction, '/transaction')

if __name__ == '__main__':
    app.run(debug=True)
