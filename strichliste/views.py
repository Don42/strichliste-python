from datetime import datetime, timedelta

from flask import current_app
from flask_restful import Resource, reqparse
from werkzeug.exceptions import BadRequest

from strichliste import middleware, models
from strichliste.config import Config

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', type=str, location='json')
user_parser.add_argument('mailAddress', type=str, location='json')

transaction_parser = reqparse.RequestParser()
transaction_parser.add_argument('value', location='json')

list_parser = reqparse.RequestParser()
list_parser.add_argument('offset', type=int, location='args', default=None)
list_parser.add_argument('limit', type=int, location='args', default=None)

HEADERS = {'Content-Type': 'application/json; charset=utf-8'}


def make_error_response(msg, code: int = 400):
    """

    :param msg: Should be either an exception object or a string
    :param code: HTTP Response Code
    :return: Result pair to return to the requesting client
    """
    return {'message': str(msg)}, code


class Settings(Resource):
    def get(self):
        config = Config()
        return {'boundaries': {'account': {'upper': config.upper_account_boundary,
                                           'lower': config.lower_account_boundary},
                               'transaction': {'upper': config.upper_transaction_boundary,
                                               'lower': config.lower_transaction_boundary}
                               }
                }, 200


class Metrics(Resource):
    def get(self):
        today = datetime.utcnow().date()
        data = dict(today=today.isoformat())

        data['countTransactions'] = models.Transaction.query.count()
        data['overallBalance'] = strichliste.middleware.get_global_balance()
        data['countUsers'] = models.User.query.count()
        data['avgBalance'] = strichliste.middleware.get_average_balance()
        data['days'] = [strichliste.middleware.get_day_metrics(today - timedelta(days=x)) for x in range(3, -1, -1)]
        return data, 200


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
        return transaction.dict(), 200


class Transaction(Resource):
    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        count = models.Transaction.query.count()
        result = models.Transaction.query.offset(offset).limit(limit).all()
        entries = [x.dict() for x in result]
        return {'overallCount': count, 'limit': limit,
                'offset': offset, 'entries': entries}, 200


class UserList(Resource):
    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        users = middleware.get_users(limit, offset)
        return users, 200

    def post(self):
        args = user_parser.parse_args()
        name = args.get('name')
        mail_address = args.get('mailAddress')
        if name is None or mail_address is None:
            current_app.logger.warning("Could not create user: name missing")
            return make_error_response("name missing", 400)

        try:
            user = middleware.insert_user(name, mail_address)
            current_app.logger.info("User created - user_id='{user_id}', name='{name}'".format(user_id=user.id,
                                                                                               name=user.name))
        except middleware.DuplicateUser as e:
            return make_error_response("user {} already exists".format(e.user_name), 409)

        return {'id': user.id, 'name': user.name, 'mailAddress': user.mailAddress,
                'balance': 0, 'lastTransaction': None}, 201


class User(Resource):
    def get(self, user_id):
        try:
            user = middleware.get_user(user_id)
            return user, 200
        except KeyError:
            return make_error_response("user {} not found".format(user_id), 404)


class UserTransactionList(Resource):
    def get(self, user_id):
        args = list_parser.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        try:
            transactions = middleware.get_users_transactions(user_id, limit=limit, offset=offset)
        except KeyError:
            current_app.logger.warning("User ID not found - user_id='{}'".format(user_id))
            return make_error_response("user {} not found".format(user_id), 404)
        return transactions, 200

    def post(self, user_id):
        try:
            args = transaction_parser.parse_args()
        except BadRequest:
            current_app.logger.warning("Could not create transaction: Invalid input")
            return make_error_response("Error parsing json", 400)
        if 'value' not in args or args['value'] is None:
            current_app.logger.warning("Could not create transaction: Invalid input")
            return make_error_response("value missing", 400)
        try:
            value = int(args['value'])
        except ValueError:
            current_app.logger.warning("Could not create transaction: Invalid input")
            return make_error_response("not a number: {}".format(args['value']), 400)

        try:
            transaction = middleware.insert_transaction(user_id, value)
        except middleware.TransactionValueZero as e:
            current_app.logger.warning("Could not create transaction: Invalid input")
            return make_error_response(e, 400)
        except middleware.TransactionValueHigh as e:
            current_app.logger.warning("Could not create transaction: Transaction high boundary exceeded")
            return make_error_response(e, 403)
        except middleware.TransactionValueLow as e:
            current_app.logger.warning("Could not create transaction: Transaction low boundary exceeded")
            return make_error_response(e, 403)
        except KeyError:
            current_app.logger.warning("Could not create transaction: User ID not found - user_id='{}'".format(user_id))
            return make_error_response("user {} not found".format(user_id), 404)
        except middleware.TransactionResultHigh as e:
            current_app.logger.warning("Could not create transaction: Account boundary exceeded")
            return make_error_response(e, 403)
        except middleware.TransactionResultLow as e:
            current_app.logger.warning("Could not create transaction: Account boundary exceeded")
            return make_error_response(e, 403)
        except middleware.DatabaseError as e:
            current_app.logger.error("Could not create transaction: {e} - user_id='{user_id}, value='{value}''".format(
                e=e,
                user_id=user_id,
                value=value
            ))
            return make_error_response("Database Error", 403)
        else:
            current_app.logger.info("Transaction created - id='{id}', user_id='{user_id}'".format(
                id=transaction.id,
                user_id=transaction.userId))

        return transaction.dict(), 201
