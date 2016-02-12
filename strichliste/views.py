from datetime import datetime, timedelta

import flask
import sqlalchemy.exc
from flask import current_app, jsonify
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

import strichliste.middleware
from database import db
from strichliste import middleware, models
from strichliste.config import Config

from flask_restful import reqparse

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', type=str, location='json')
user_parser.add_argument('mailAddress', type=str, location='json')

transaction_parser = reqparse.RequestParser()
transaction_parser.add_argument('value', location='json')

list_parser = reqparse.RequestParser()
list_parser.add_argument('offset', type=int, location='args', default=None)
list_parser.add_argument('limit', type=int, location='args', default=None)

HEADERS = {'Content-Type': 'application/json; charset=utf-8'}


class Settings(Resource):

    def get(self):
        config = Config()
        return make_response({'boundaries': {'account': {'upper': config.upper_account_boundary,
                                                         'lower': config.lower_account_boundary},
                                             'transaction': {'upper': config.upper_transaction_boundary,
                                                             'lower': config.lower_transaction_boundary}
                                             }
                              }, 200)


class Metrics(Resource):

    def get(self):
        today = datetime.utcnow().date()
        data = dict(today=today.isoformat())

        data['countTransactions'] = models.Transaction.query.count()
        data['overallBalance'] = strichliste.middleware.get_global_balance()
        data['countUsers'] = models.User.query.count()
        data['avgBalance'] = strichliste.middleware.get_average_balance()
        data['days'] = [strichliste.middleware.get_day_metrics(today - timedelta(days=x)) for x in range(3, -1, -1)]
        return make_response(data, 200)


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
        return make_response(transaction.dict(), 200)


class Transaction(Resource):

    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        count = models.Transaction.query.count()
        result = models.Transaction.query.offset(offset).limit(limit).all()
        entries = [x.dict() for x in result]
        return make_response({'overallCount': count, 'limit': limit,
                              'offset': offset, 'entries': entries}, 200)


class UserList(Resource):

    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        users = middleware.get_users(limit, offset)
        return make_response(users, 200)

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

        return make_response({'id': user.id, 'name': user.name, 'mailAddress': user.mailAddress,
                              'balance': 0, 'lastTransaction': None}, 201)


class User(Resource):

    def get(self, user_id):
        try:
            user = middleware.get_user(user_id)
            return make_response(user, 200)
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
        return make_response(transactions, 200)

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

        config = Config()
        max_transaction = config.upper_transaction_boundary
        min_transaction = config.lower_transaction_boundary
        if value == 0:
            current_app.logger.warning("Could not create transaction: Invalid input")
            return make_error_response("value must not be zero", 400)
        elif value > max_transaction:
            current_app.logger.warning("Could not create transaction: Transaction boundary exceeded")
            return make_error_response(
                    "transaction value of {} exceeds the transaction maximum of {}".format(value, max_transaction),
                    403)
        elif value < min_transaction:
            current_app.logger.warning("Could not create transaction: Transaction boundary exceeded")
            return make_error_response(
                    "transaction value of {} falls below the transaction minimum of {}".format(value, min_transaction),
                    403)

        user = models.User.query.get(user_id)
        if user is None:
            current_app.logger.warning("Could not create transaction: User ID not found - user_id='{}'".format(user_id))
            return make_error_response("user {} not found".format(user_id), 404)

        max_account = config.upper_account_boundary
        min_account = config.lower_account_boundary
        new_balance = user.balance + value
        if new_balance > max_account:
            current_app.logger.warning("Could not create transaction: Account boundary exceeded")
            return make_error_response(
                    ("transaction value of {trans_val} leads to an overall account balance of {new} "
                     "which goes beyond the upper account limit of {limit}".format(trans_val=value,
                                                                                   new=new_balance,
                                                                                   limit=max_account)),
                    403
            )
        elif new_balance < min_account:
            current_app.logger.warning("Could not create transaction: Account boundary exceeded")
            return make_error_response(
                    ("transaction value of {trans_val} leads to an overall account balance of {new} "
                     "which goes below the lower account limit of {limit}").format(trans_val=value,
                                                                                   new=new_balance,
                                                                                   limit=min_account),
                    403
            )

        transaction = models.Transaction(userId=user_id, value=value)
        try:
            db.session.add(transaction)
            db.session.commit()
            current_app.logger.info("Transaction created - id='{id}', user_id='{user_id}'".format(
                    id=transaction.id,
                    user_id=transaction.userId))
        except sqlalchemy.exc.IntegrityError as e:
            current_app.logger.error("Could not create transaction: {e} - user_id='{user_id}, value='{value}''".format(
                e=e,
                user_id=user.id,
                value=transaction.userId
            ))
            return make_error_response("user {} not found".format(user_id), 404)

        return make_response(transaction.dict(), 201)


def make_error_response(msg: str, code: int = 400):
    return make_response({'message': msg}, code)


def make_response(data, code=200, headers=None):
    resp = flask.make_response(jsonify(data), code)
    resp.headers.extend(HEADERS)
    if headers is not None:
        resp.headers.extend(headers)
    return resp