from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

user_parser = reqparse.RequestParser()
user_parser.add_argument('name')
user_parser.add_argument('mailAddress')


class Setting(Resource):

    def get(self):
        return {'boundaries': {'upper': 42, 'lower': -23}}


class UserList(Resource):

    def get(self):
        return {'overallCount': 0, 'limit': None, 'offset': None, 'entries': []}

    def post(self):
        args = user_parser.parse_args()
        print(args)
        return {'id': 1, 'name': 'gert', 'balance': 0, 'lastTransaction': None}


class User(Resource):

    def get(self, user_id):
        return {'message': "user {} not found".format(user_id)}, 404


class UserTransaction(Resource):

    def get(self, user_id):
        return {'message': "user {} not found".format(user_id)}, 404

    def post(self, user_id):
        return {'message': "user {} not found".format(user_id)}, 404


class Transaction(Resource):

    def get(self):
        return {'overallCount': 0, 'limit': None, 'offset': None, 'entries': []}

api.add_resource(Setting, '/settings')
api.add_resource(UserList, '/user')
api.add_resource(User, '/user/<user_id>')
api.add_resource(UserTransaction, '/user/<user_id>/transaction')
api.add_resource(Transaction, '/transaction')

if __name__ == '__main__':
    app.run(debug=True)
