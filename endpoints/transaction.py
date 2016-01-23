import json

from flask_restful import Resource
from flask import make_response

from endpoints import create_error, list_parser, HEADERS
import strichliste.models as models


class UserTransaction(Resource):

    def get(self, user_id, transaction_id):
        user = models.User.query.get(user_id)
        if user is None:
            return create_error(404, "user {} not found".format(user_id))
        transaction = models.Transaction.query.get(transaction_id)
        if transaction is None or transaction.userId != user.id:
            return create_error(404, "transaction {} not found".format(transaction_id))
        resp = make_response(json.dumps(transaction.dict()), 200)
        resp.headers.extend(HEADERS)
        return resp


class Transaction(Resource):

    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        count = models.Transaction.query.count()
        result = models.Transaction.query.all()
        entries = [x.dict() for x in result]
        resp = make_response(json.dumps({'overallCount': count, 'limit': limit,
                                         'offset': offset, 'entries': entries}), 200)
        resp.headers.extend(HEADERS)
        return resp
