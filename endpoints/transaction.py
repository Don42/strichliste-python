import json

from flask_restful import Resource

from endpoints import make_error_response, make_response, list_parser
import strichliste.models as models


class UserTransaction(Resource):

    def get(self, user_id, transaction_id):
        user = models.User.query.get(user_id)
        if user is None:
            return make_error_response("user {} not found".format(user_id), 404)
        transaction = models.Transaction.query.get(transaction_id)
        if transaction is None or transaction.userId != user.id:
            return make_error_response("transaction {} not found".format(transaction_id), 404)
        return make_response(transaction.dict(), 200)


class Transaction(Resource):

    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        count = models.Transaction.query.count()
        result = models.Transaction.query.all()
        entries = [x.dict() for x in result]
        return make_response({'overallCount': count, 'limit': limit,
                              'offset': offset, 'entries': entries}, 200)
