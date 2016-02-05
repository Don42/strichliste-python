from flask import current_app
from flask_restful import Resource

from endpoints import make_error_response, make_response, list_parser
from endpoints.v1.utils import make_transaction_float
import strichliste.models as models


class UserTransaction(Resource):

    def get(self, user_id, transaction_id):
        user = models.User.query.get(user_id)
        if user is None:
            current_app.logger.warning("Could not find transaction: User ID not found - user_id='{}'".format(user_id))
            return make_error_response("user {} not found".format(user_id), 404)
        transaction = models.Transaction.query.get(transaction_id)
        if transaction is None or transaction.userId != user.id:
            current_app.logger.warning(("Could not find transaction: User ID does not match - "
                                        "user_id='{}', transaction_id='{}'").format(user_id, transaction_id))
            return make_error_response("transaction {} not found".format(transaction_id), 404)
        return make_response(make_transaction_float(transaction), 200)


class Transaction(Resource):

    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        count = models.Transaction.query.count()
        result = models.Transaction.query.offset(offset).limit(limit).all()
        entries = [make_transaction_float(x) for x in result]
        return make_response({'overallCount': count, 'limit': limit,
                              'offset': offset, 'entries': entries}, 200)
