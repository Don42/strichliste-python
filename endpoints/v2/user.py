import sqlalchemy.exc
from flask import current_app
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

import strichliste.middleware as middleware
import strichliste.models as models
from database import db
from endpoints import list_parser, user_parser, transaction_parser, make_error_response, make_response
from strichliste.config import Config


class UserListV2(Resource):

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

        user = models.User(name=name, mailAddress=mail_address)
        try:
            db.session.add(user)
            db.session.commit()
            current_app.logger.info("User created - user_id='{user_id}', name='{name}'".format(user_id=user.id,
                                                                                               name=user.name))
        except sqlalchemy.exc.IntegrityError:
            current_app.logger.warning("Could not create duplicate user - user='{}'".format(user.name))
            return make_error_response("user {} already exists".format(user.name), 409)

        return make_response({'id': user.id, 'name': user.name,
                              'mailAddress': user.mailAddress,
                              'balance': 0, 'lastTransaction': None},
                             201)


class UserV2(Resource):

    def get(self, user_id):
        try:
            user = models.User.query.get(user_id)
            if user is None:
                current_app.logger.warning("Could not find user: User ID not found - user_id='{}'".format(user_id))
                return make_error_response("user {} not found".format(user_id), 404)
            out_dict = user.dict()
            out_dict['transactions'] = [x.dict() for x in user.transactions]
            return make_response(out_dict, 200)
        except sqlalchemy.exc.SQLAlchemyError as e:
            current_app.logger.error("Unexpected SQLAlchemyError: {error} - user_id='{user_id}".format(error=e,
                                                                                                       user_id=user_id))
            return make_error_response("Internal Error", 500)


class UserTransactionListV2(Resource):

    def get(self, user_id):
        args = list_parser.parse_args()
        limit = args.get('limit')
        offset = args.get('offset')
        try:
            transactions = middleware.get_users_transactions(user_id, limit=limit, offset=offset)
        except KeyError:
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

