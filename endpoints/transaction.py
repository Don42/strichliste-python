from endpoints import create_error
from flask_restful import Resource


class UserTransaction(Resource):

    def get(self, user_id, transaction_id):
        return create_error(404, "user {} not found".format(user_id))


class Transaction(Resource):

    def get(self):
        return {'overallCount': 0, 'limit': None, 'offset': None, 'entries': []}